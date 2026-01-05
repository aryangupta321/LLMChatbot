"""
Simple Zoho API Integration - Working Version
"""

import os
import logging
import time
from typing import Dict, Optional, Any, Tuple

logger = logging.getLogger(__name__)

# Configuration constants
API_TIMEOUT = 10  # seconds
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds


class ZohoSalesIQAPI:
    """Simple SalesIQ API Integration (Visitor API)"""
    
    def __init__(self):
        # Load configuration
        self.access_token = os.getenv("SALESIQ_ACCESS_TOKEN", "").strip()
        self.department_id = os.getenv("SALESIQ_DEPARTMENT_ID", "").strip()
        self.app_id = os.getenv("SALESIQ_APP_ID", "").strip()
        self.screen_name = os.getenv("SALESIQ_SCREEN_NAME", "rtdsportal").strip()
        
        # Base URL for Visitor API v1 (official endpoint per API docs)
        self.base_url = f"https://salesiq.zoho.in/api/visitor/v1/{self.screen_name}"
        
        # Enable only if required config exists
        self.enabled = bool(self.access_token and self.department_id and self.app_id)
        if self.enabled:
            logger.info(f"SalesIQ Visitor API v1 ENABLED - department: {self.department_id}, app_id: {self.app_id}, screen: {self.screen_name}")
        else:
            logger.error(f"SalesIQ Visitor API DISABLED - Missing config! token: {bool(self.access_token)} (length: {len(self.access_token)}), dept: {bool(self.department_id)} ({self.department_id}), app_id: {bool(self.app_id)} ({self.app_id}), screen: {self.screen_name}")
    
    def create_chat_session(
        self,
        visitor_id: str,
        conversation_history: str,
        app_id: str | None = None,
        department_id: str | None = None,
        visitor_info: Dict | None = None,
        custom_wait_time: int | None = None,
        past_messages: list | None = None,
    ) -> Dict:
        """Create a conversation via Visitor API to route to an agent.
        Allows overriding app_id/department_id/visitor_info from inbound webhook payload.
        
        IMPORTANT: Cannot use bot preview visitor IDs (botpreview_...).
        Must use real visitor IDs from actual chat widget interactions.
        
        Args:
            past_messages: Optional list of message dicts in SalesIQ format for message-by-message history
        """
        
        if not self.enabled:
            logger.info(f"SalesIQ: API disabled - simulating transfer for {visitor_id}")
            return {"success": True, "simulated": True, "message": "Transfer simulated"}
        
        # Reject bot preview IDs - they cannot be transferred
        if str(visitor_id).startswith("botpreview_"):
            logger.warning(f"SalesIQ: Cannot transfer bot preview session {visitor_id}. Need real visitor ID from actual chat widget.")
            return {
                "success": False,
                "error": "invalid_visitor_id",
                "details": "Bot preview sessions cannot be transferred. This is a SalesIQ limitation. Test with real visitor ID only."
            }
        
        import requests
        
        headers = {
            "Authorization": f"Zoho-oauthtoken {self.access_token}",
            "Content-Type": "application/json"
        }
        
        # Effective configuration (prefer overrides from webhook)
        effective_app_id = str(app_id or self.app_id).strip()
        effective_department_id = str(department_id or self.department_id).strip()

        # Extract visitor details from visitor_info or use defaults
        visitor_user_id = str(visitor_id).strip()
        visitor_name = "Chat User"
        visitor_email = "support@acecloudhosting.com"
        
        if visitor_info:
            # Prefer "email" as user_id if available (most reliable unique ID)
            visitor_user_id = visitor_info.get("email") or visitor_info.get("user_id") or visitor_user_id
            visitor_name = visitor_info.get("name") or visitor_info.get("email", "Chat User")
            visitor_email = visitor_info.get("email", "support@acecloudhosting.com")

        # Visitor API v1 payload structure per official documentation
        payload: Dict = {
            "app_id": effective_app_id,
            "department_id": effective_department_id,
            "question": conversation_history or "User requested human assistance",
            "visitor": {
                "user_id": visitor_user_id,
                "name": visitor_name,
                "email": visitor_email
            }
        }
        
        # Add optional custom_wait_time if provided
        if custom_wait_time is not None:
            payload["custom_wait_time"] = custom_wait_time
        
        # Add past_messages for message-by-message history transfer if provided
        if past_messages:
            payload["past_messages"] = past_messages
            logger.info(f"SalesIQ: Including {len(past_messages)} past messages for message-by-message display")
        
        endpoint = f"{self.base_url}/conversations"
        logger.info(f"SalesIQ: Visitor API v1 call - POST {endpoint}")
        logger.info(
            f"SalesIQ: Payload - app_id={effective_app_id}, dept={effective_department_id}, visitor_user_id={visitor_user_id}, visitor_email={visitor_email}"
        )
        
        # Retry logic for transient failures
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = requests.post(endpoint, json=payload, headers=headers, timeout=API_TIMEOUT)
                logger.info(f"SalesIQ: Response Status: {response.status_code}")
                logger.info(f"SalesIQ: Response Body: {response.text[:500]}")
                
                if response.status_code in [200, 201]:
                    try:
                        data = response.json()
                    except Exception:
                        data = {"raw": response.text}
                    return {"success": True, "endpoint": endpoint, "data": data}
                elif response.status_code in [429, 503]:  # Rate limit or service unavailable
                    if attempt < MAX_RETRIES:
                        retry_delay = RETRY_DELAY * attempt
                        logger.warning(f"SalesIQ: Transient error {response.status_code}, retrying in {retry_delay}s (attempt {attempt}/{MAX_RETRIES})")
                        time.sleep(retry_delay)
                        continue
                    return {"success": False, "error": f"{response.status_code}", "details": response.text, "retryable": True}
                else:
                    # Non-retryable HTTP error
                    return {"success": False, "error": f"{response.status_code}", "details": response.text, "retryable": False}
                    
            except requests.exceptions.Timeout:
                if attempt < MAX_RETRIES:
                    logger.warning(f"SalesIQ: Timeout, retrying (attempt {attempt}/{MAX_RETRIES})")
                    time.sleep(RETRY_DELAY)
                    continue
                logger.error(f"SalesIQ: Request timeout after {MAX_RETRIES} attempts")
                return {"success": False, "error": "timeout", "details": f"Request timed out after {API_TIMEOUT}s", "retryable": True}
                
            except requests.exceptions.ConnectionError as e:
                if attempt < MAX_RETRIES:
                    logger.warning(f"SalesIQ: Connection error, retrying (attempt {attempt}/{MAX_RETRIES})")
                    time.sleep(RETRY_DELAY)
                    continue
                logger.error(f"SalesIQ: Connection error: {str(e)}")
                return {"success": False, "error": "connection_error", "details": str(e), "retryable": True}
                
            except Exception as e:
                logger.error(f"SalesIQ: Unexpected error: {str(e)}", exc_info=True)
                return {"success": False, "error": "exception", "details": str(e), "retryable": False}
        
        # Should not reach here, but safety fallback
        return {"success": False, "error": "max_retries_exceeded", "details": "All retry attempts failed", "retryable": False}
    
    def close_chat(self, session_id: str, reason: str = "resolved") -> Dict:
        """Log chat closure"""
        
        logger.info(f"SalesIQ: Chat closure requested for {session_id}, reason: {reason}")
        
        return {
            "success": True,
            "message": f"Chat {session_id} closure logged"
        }


class ZohoDeskAPI:
    """Zoho Desk API Integration for Callback Tickets"""
    
    def __init__(self):
        self.access_token = os.getenv("DESK_ACCESS_TOKEN", "").strip().strip('"').strip("'")

        # Support both env var names (Railway screenshot uses DESK_ORGANIZATION_ID)
        self.org_id = (
            os.getenv("DESK_ORG_ID", "").strip()
            or os.getenv("DESK_ORGANIZATION_ID", "").strip()
            or os.getenv("DESK_ORGANIZATIONID", "").strip()
        )

        # Allow overriding Desk domain if needed (default to .in for India)
        self.base_url = os.getenv("DESK_BASE_URL", "https://desk.zoho.in/api/v1").strip()
        self.default_department_id = os.getenv("DESK_DEPARTMENT_ID", "").strip() or None
        self.default_contact_id = os.getenv("DESK_CONTACT_ID", "").strip() or None
        self.enabled = bool(self.access_token and self.org_id)
        
        if self.enabled:
            logger.info(
                "Desk API configured - org_id: %s, base_url: %s, default_department_id: %s",
                self.org_id,
                self.base_url,
                self.default_department_id or "(auto)",
            )
        else:
            logger.warning(
                "Desk API not configured - simulated. token=%s orgId=%s (expects DESK_ACCESS_TOKEN and DESK_ORG_ID or DESK_ORGANIZATION_ID)",
                bool(self.access_token),
                bool(self.org_id),
            )

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Zoho-oauthtoken {self.access_token}",
            "orgId": str(self.org_id),
            "Content-Type": "application/json",
        }

    def _parse_data_list(self, payload: Any) -> list:
        if isinstance(payload, dict):
            data = payload.get("data")
            return data if isinstance(data, list) else []
        return payload if isinstance(payload, list) else []

    def _get_default_department_id(self) -> Optional[str]:
        if self.default_department_id:
            return str(self.default_department_id)

        import requests

        endpoint = f"{self.base_url}/departments"
        headers = self._headers()
        logger.info(f"Desk: GET {endpoint} with headers: Authorization=Zoho-oauthtoken {self.access_token[:20]}..., orgId={headers.get('orgId')}")
        
        try:
            resp = requests.get(endpoint, headers=headers, timeout=API_TIMEOUT)
            resp.raise_for_status()
            items = self._parse_data_list(resp.json())
            if not items:
                logger.error("Desk: No departments returned from %s", endpoint)
                return None
            dept_id = items[0].get("id") if isinstance(items[0], dict) else None
            if dept_id:
                logger.info("Desk: Using default departmentId=%s", dept_id)
                return str(dept_id)
            return None
            
        except requests.exceptions.Timeout:
            logger.error("Desk: Request timeout fetching departments (>%ss)", API_TIMEOUT)
            return None
            
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if hasattr(e, 'response') else None
            body = e.response.text if hasattr(e, 'response') else None
            logger.error("Desk: Failed to fetch departments: HTTP %s - %s", status, body or "")
            return None
            
        except Exception as e:
            logger.error("Desk: Unexpected error fetching departments: %s", str(e), exc_info=True)
            return None

    def _find_contact_id_by_email(self, email: str) -> Optional[str]:
        # If DESK_CONTACT_ID is set, use it directly
        if self.default_contact_id:
            logger.info(f"Desk: Using default contactId={self.default_contact_id}")
            return str(self.default_contact_id)
        
        if not email:
            return None

        import requests

        # Try listing all contacts and finding the email (search endpoint has permission issues)
        # This is less efficient but more reliable with limited API scopes
        endpoint = f"{self.base_url}/contacts"
        params = {"limit": 100}  # Get up to 100 contacts

        try:
            logger.info(f"Desk: Searching for contact with email: {email}")
            resp = requests.get(endpoint, headers=self._headers(), params=params, timeout=API_TIMEOUT)
            
            if resp.status_code == 404:
                logger.info(f"Desk: No contact found for email: {email}")
                return None
                
            resp.raise_for_status()
            items = self._parse_data_list(resp.json())
            
            if not items:
                logger.info(f"Desk: Contact search returned empty results for: {email}")
                return None
                
            # Find exact email match from results
            for item in items:
                if isinstance(item, dict) and item.get("email", "").lower() == email.lower():
                    contact_id = item.get("id")
                    if contact_id:
                        logger.info(f"Desk: Found contact ID {contact_id} for email: {email}")
                        return str(contact_id)
            
            logger.info(f"Desk: No exact email match found in search results for: {email}")
            return None
                    
        except requests.exceptions.Timeout:
            logger.warning("Desk: Timeout during contact lookup for email: %s", email)
            return None
            
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if hasattr(e, 'response') else None
            body = e.response.text if hasattr(e, 'response') else None
            logger.warning("Desk: Contact lookup failed: HTTP %s - %s", status, body or "")
            return None
            
        except Exception as e:
            logger.warning("Desk: Unexpected error during contact lookup: %s", str(e))
            return None

    def _create_contact(self, email: str, name: str, phone: Optional[str] = None) -> Optional[str]:
        """Create a new contact in Zoho Desk
        
        API: POST /api/v1/contacts
        Required fields: lastName, email (or phone)
        """
        import requests

        endpoint = f"{self.base_url}/contacts"
        
        # Split name into first and last name
        name_parts = (name or "").strip().split(None, 1) if name else []
        first_name = name_parts[0] if len(name_parts) > 0 else ""
        last_name = name_parts[1] if len(name_parts) > 1 else (email.split("@")[0] if email else "Customer")
        
        # If no name provided, use email prefix
        if not first_name and not last_name:
            last_name = email.split("@")[0] if email else "Customer"
        
        payload: Dict[str, Any] = {
            "lastName": last_name or "Customer",
            "email": email
        }
        
        if first_name:
            payload["firstName"] = first_name
            
        if phone:
            payload["phone"] = phone

        try:
            logger.info(f"Desk: Creating contact for email: {email}")
            resp = requests.post(endpoint, json=payload, headers=self._headers(), timeout=API_TIMEOUT)
            resp.raise_for_status()
            result = resp.json() if resp.content else {}
            contact_id = result.get("id") if isinstance(result, dict) else None
            if contact_id:
                logger.info(f"Desk: Created contact with ID: {contact_id}")
                return str(contact_id)
            
            logger.error(f"Desk: Contact creation response missing ID: {result}")
            return None
            
        except requests.exceptions.Timeout:
            logger.error("Desk: Timeout creating contact (>%ss)", API_TIMEOUT)
            return None
            
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if hasattr(e, 'response') else None
            body = e.response.text if hasattr(e, 'response') else None
            logger.error("Desk: Failed to create contact: HTTP %s - %s", status, body or "")
            return None
            
        except Exception as e:
            logger.error("Desk: Unexpected error creating contact: %s", str(e), exc_info=True)
            return None
    
    def create_callback_ticket(
        self,
        visitor_email: str,
        visitor_name: str,
        conversation_history: str,
        preferred_time: Optional[str] = None,
        phone: Optional[str] = None,
        desk_department_id: Optional[str] = None,
    ) -> Dict:
        """Create a callback request as a Zoho Desk Call activity (POST /calls).

        Desk requires:
        - orgId header
        - departmentId
        - contactId
        """
        
        if not self.enabled:
            logger.info(f"Desk: Callback call creation simulated for {visitor_email}")
            return {"success": True, "simulated": True, "call_id": "CALL-SIM-001"}
        
        import requests
        from datetime import datetime, timezone

        department_id = str(desk_department_id).strip() if desk_department_id else None
        if not department_id:
            department_id = self._get_default_department_id()

        contact_id = self._find_contact_id_by_email(visitor_email)
        if not contact_id:
            contact_id = self._create_contact(visitor_email, visitor_name, phone=phone)

        if not department_id:
            return {
                "success": False,
                "error": "missing_department_id",
                "details": "Desk departmentId is required. Set DESK_DEPARTMENT_ID. If /departments returns 403, re-generate Desk token with department read scope and ensure DESK_BASE_URL is correct.",
            }
        if not contact_id:
            return {
                "success": False,
                "error": "missing_contact_id",
                "details": "Desk contactId is required. If /contacts returns 403, re-generate Desk token with Desk.contacts.READ + Desk.contacts.CREATE (or allow contacts access for the portal).",
            }
        
        # Use current time as start time (ISO 8601)
        start_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")

        details_block = ""
        if preferred_time:
            details_block += f"\nPreferred time: {preferred_time}"
        if phone:
            details_block += f"\nPhone: {phone}"

        # Limit description to avoid 400 errors (max ~500 chars recommended)
        description = f"Callback requested by {visitor_name}\nEmail: {visitor_email}{details_block}"
        
        payload = {
            "contactId": str(contact_id),
            "departmentId": str(department_id),
            "subject": f"Callback Request - {visitor_name}",
            "description": description,
            "direction": "inbound",
            "startTime": start_time,
            "duration": 0,
            "status": "In Progress",
        }
        
        endpoint = f"{self.base_url}/calls"
        headers = self._headers()
        
        logger.info(f"Desk: Creating callback call - endpoint: {endpoint}")
        logger.info(f"Desk: Token length: {len(self.access_token)}, OrgId: {self.org_id}")
        logger.info(f"Desk: Payload: {payload}")
        
        # Retry logic for transient failures
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = requests.post(endpoint, json=payload, headers=headers, timeout=API_TIMEOUT)
                response.raise_for_status()
                result = response.json()
                logger.info(f"Desk: Callback call created - ID: {result.get('id')}")
                return {"success": True, "call_id": result.get("id"), "web_url": result.get("webUrl")}
                
            except requests.exceptions.Timeout:
                if attempt < MAX_RETRIES:
                    retry_delay = RETRY_DELAY * attempt
                    logger.warning(f"Desk: Timeout, retrying in {retry_delay}s (attempt {attempt}/{MAX_RETRIES})")
                    time.sleep(retry_delay)
                    continue
                logger.error(f"Desk: Request timeout after {MAX_RETRIES} attempts")
                return {"success": False, "error": "timeout", "details": f"Request timed out after {API_TIMEOUT}s", "retryable": True}
                
            except requests.exceptions.HTTPError as e:
                status_code = e.response.status_code if hasattr(e, 'response') else None
                error_detail = e.response.text if hasattr(e, 'response') else str(e)
                
                # Retry on transient errors
                if status_code in [429, 503] and attempt < MAX_RETRIES:
                    retry_delay = RETRY_DELAY * attempt
                    logger.warning(f"Desk: HTTP {status_code}, retrying in {retry_delay}s (attempt {attempt}/{MAX_RETRIES})")
                    time.sleep(retry_delay)
                    continue
                
                logger.error(f"Desk: HTTP Error creating callback - {status_code}: {error_detail}")
                return {"success": False, "error": f"HTTP {status_code}", "details": error_detail, "retryable": status_code in [429, 503]}
                
            except requests.exceptions.ConnectionError as e:
                if attempt < MAX_RETRIES:
                    retry_delay = RETRY_DELAY * attempt
                    logger.warning(f"Desk: Connection error, retrying in {retry_delay}s (attempt {attempt}/{MAX_RETRIES})")
                    time.sleep(retry_delay)
                    continue
                logger.error(f"Desk: Connection error: {str(e)}")
                return {"success": False, "error": "connection_error", "details": str(e), "retryable": True}
                
            except Exception as e:
                logger.error(f"Desk: Unexpected error creating callback: {str(e)}", exc_info=True)
                return {"success": False, "error": "exception", "details": str(e), "retryable": False}
        
        # Should not reach here, but safety fallback
        return {"success": False, "error": "max_retries_exceeded", "details": "All retry attempts failed", "retryable": False}
    
    def create_support_ticket(self, *args, **kwargs):
        logger.info("Desk: Support ticket creation simulated")
        return {"success": True, "simulated": True, "ticket_number": "TK-SIM-001"}