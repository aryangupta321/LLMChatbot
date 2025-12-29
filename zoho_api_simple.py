"""
Simple Zoho API Integration - Working Version
"""

import os
import logging
from typing import Dict

logger = logging.getLogger(__name__)


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
            logger.info(f"SalesIQ Visitor API v1 configured - department: {self.department_id}, app_id: {self.app_id}, screen: {self.screen_name}")
        else:
            logger.warning(f"SalesIQ Visitor API not fully configured - token: {bool(self.access_token)}, dept: {bool(self.department_id)}, app_id: {bool(self.app_id)}, screen: {bool(self.screen_name)}")
    
    def create_chat_session(
        self,
        visitor_id: str,
        conversation_history: str,
        app_id: str | None = None,
        department_id: str | None = None,
        visitor_info: Dict | None = None,
        custom_wait_time: int | None = None,
    ) -> Dict:
        """Create a conversation via Visitor API to route to an agent.
        Allows overriding app_id/department_id/visitor_info from inbound webhook payload.
        
        IMPORTANT: Cannot use bot preview visitor IDs (botpreview_...).
        Must use real visitor IDs from actual chat widget interactions.
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
        
        endpoint = f"{self.base_url}/conversations"
        logger.info(f"SalesIQ: Visitor API v1 call - POST {endpoint}")
        logger.info(
            f"SalesIQ: Payload - app_id={effective_app_id}, dept={effective_department_id}, visitor_user_id={visitor_user_id}, visitor_email={visitor_email}"
        )
        
        try:
            response = requests.post(endpoint, json=payload, headers=headers, timeout=10)
            logger.info(f"SalesIQ: Response Status: {response.status_code}")
            logger.info(f"SalesIQ: Response Body: {response.text[:500]}")
            
            if response.status_code in [200, 201]:
                try:
                    data = response.json()
                except Exception:
                    data = {"raw": response.text}
                return {"success": True, "endpoint": endpoint, "data": data}
            else:
                return {"success": False, "error": f"{response.status_code}", "details": response.text}
        except Exception as e:
            logger.error(f"SalesIQ: Visitor API exception: {str(e)}")
            return {"success": False, "error": "exception", "details": str(e)}
    
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
        self.access_token = os.getenv("DESK_ACCESS_TOKEN", "").strip()
        self.org_id = os.getenv("DESK_ORG_ID", "").strip()
        self.base_url = "https://desk.zoho.in/api/v1"
        self.enabled = bool(self.access_token and self.org_id)
        
        if self.enabled:
            logger.info(f"Desk API configured - org_id: {self.org_id}")
        else:
            logger.warning("Desk API not configured - ticket creation simulated")
    
    def create_callback_ticket(self, visitor_email: str, visitor_name: str, conversation_history: str, department_id: str = None, contact_id: str = None) -> Dict:
        """Create a callback request using Zoho Desk Calls API"""
        
        if not self.enabled:
            logger.info(f"Desk: Callback call creation simulated for {visitor_email}")
            return {"success": True, "simulated": True, "call_id": "CALL-SIM-001"}
        
        import requests
        from datetime import datetime, timezone
        
        headers = {
            "Authorization": f"Zoho-oauthtoken {self.access_token}",
            "orgId": str(self.org_id),
            "Content-Type": "application/json"
        }
        
        # Use current time as start time (ISO 8601 format)
        start_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
        
        # Build payload for Desk Calls API
        payload = {
            "subject": f"Callback Request - {visitor_name}",
            "description": f"Customer: {visitor_name}\nEmail: {visitor_email}\n\n{conversation_history}",
            "direction": "inbound",
            "startTime": start_time,
            "duration": "0",
            "status": "Scheduled",
            "priority": "High"
        }
        
        # Add department ID if provided
        if department_id:
            payload["departmentId"] = str(department_id)
        
        # Add contact ID if provided
        if contact_id:
            payload["contactId"] = str(contact_id)
        
        endpoint = f"{self.base_url}/calls"
        
        try:
            logger.info(f"Desk: Creating callback call - endpoint: {endpoint}")
            response = requests.post(endpoint, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            result = response.json()
            logger.info(f"Desk: Callback call created - ID: {result.get('id')}")
            return {"success": True, "call_id": result.get("id"), "web_url": result.get("webUrl")}
        except requests.exceptions.HTTPError as e:
            error_detail = e.response.text if hasattr(e.response, 'text') else str(e)
            logger.error(f"Desk: HTTP Error creating callback - {e.response.status_code}: {error_detail}")
            return {"success": False, "error": f"HTTP {e.response.status_code}: {error_detail}"}
        except Exception as e:
            logger.error(f"Desk: Error creating callback - {str(e)}")
            return {"success": False, "error": str(e)}
    
    def create_support_ticket(self, *args, **kwargs):
        logger.info("Desk: Support ticket creation simulated")
        return {"success": True, "simulated": True, "ticket_number": "TK-SIM-001"}