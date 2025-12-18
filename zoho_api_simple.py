"""
Simple Zoho API Integration - Working Version
"""

import os
import logging
from typing import Dict

logger = logging.getLogger(__name__)


class ZohoSalesIQAPI:
    """Simple SalesIQ API Integration"""
    
    def __init__(self):
        self.enabled = bool(os.getenv("SALESIQ_ACCESS_TOKEN"))
        self.access_token = os.getenv("SALESIQ_ACCESS_TOKEN", "")
        self.department_id = os.getenv("SALESIQ_DEPARTMENT_ID", "")
        
        if self.enabled:
            logger.info(f"SalesIQ API configured - department: {self.department_id}")
        else:
            logger.warning("SalesIQ API not configured")
    
    def create_chat_session(self, visitor_id: str, conversation_history: str) -> Dict:
        """Test multiple SalesIQ endpoints to find working transfer method"""
        
        if not self.enabled:
            logger.info(f"SalesIQ: API disabled - simulating transfer for {visitor_id}")
            return {"success": True, "simulated": True, "message": "Transfer simulated"}
        
        logger.info(f"SalesIQ: Testing transfer endpoints for visitor {visitor_id}")
        
        import requests
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        # Test different endpoints that might work for transfers
        endpoints_to_test = [
            {
                "name": "Chat Transfer",
                "url": f"https://salesiq.zoho.in/api/v2/chats/{visitor_id}/transfer",
                "method": "POST",
                "payload": {"department_id": self.department_id, "message": "Bot transfer request"}
            },
            {
                "name": "Chat Status Update", 
                "url": f"https://salesiq.zoho.in/api/v2/chats/{visitor_id}",
                "method": "PATCH",
                "payload": {"status": "waiting_for_agent", "department_id": self.department_id}
            },
            {
                "name": "Create New Chat",
                "url": "https://salesiq.zoho.in/api/v2/chats",
                "method": "POST", 
                "payload": {"visitor_id": visitor_id, "department_id": self.department_id, "message": "Transfer from bot"}
            },
            {
                "name": "Conversations API",
                "url": "https://salesiq.zoho.in/api/v2/conversations",
                "method": "POST",
                "payload": {"visitor_id": visitor_id, "department_id": self.department_id, "status": "open"}
            }
        ]
        
        for endpoint in endpoints_to_test:
            try:
                logger.info(f"SalesIQ: Testing {endpoint['name']} - {endpoint['method']} {endpoint['url']}")
                
                response = requests.request(
                    endpoint["method"],
                    endpoint["url"], 
                    json=endpoint["payload"],
                    headers=headers,
                    timeout=10
                )
                
                logger.info(f"SalesIQ: {endpoint['name']} - Status: {response.status_code}")
                logger.info(f"SalesIQ: {endpoint['name']} - Response: {response.text[:200]}")
                
                if response.status_code in [200, 201]:
                    logger.info(f"SalesIQ: SUCCESS! {endpoint['name']} worked!")
                    return {
                        "success": True,
                        "method": endpoint['name'],
                        "endpoint": endpoint['url'],
                        "data": response.json() if response.text else {}
                    }
                    
            except Exception as e:
                logger.warning(f"SalesIQ: {endpoint['name']} failed - {str(e)}")
                continue
        
        # If all endpoints failed, return detailed info
        logger.error("SalesIQ: All transfer endpoints failed")
        return {
            "success": False,
            "message": "All transfer methods tested - none worked",
            "visitor_id": visitor_id,
            "department_id": self.department_id,
            "note": "Check SalesIQ API documentation or configure manual transfer rules"
        }
    
    def close_chat(self, session_id: str, reason: str = "resolved") -> Dict:
        """Log chat closure"""
        
        logger.info(f"SalesIQ: Chat closure requested for {session_id}, reason: {reason}")
        
        return {
            "success": True,
            "message": f"Chat {session_id} closure logged"
        }


class ZohoDeskAPI:
    """Simple Desk API Integration"""
    
    def __init__(self):
        self.enabled = False  # Keep disabled for now
        logger.info("Desk API disabled - ticket creation simulated")
    
    def create_callback_ticket(self, *args, **kwargs):
        logger.info("Desk: Callback ticket creation simulated")
        return {"success": True, "simulated": True, "ticket_number": "CB-SIM-001"}
    
    def create_support_ticket(self, *args, **kwargs):
        logger.info("Desk: Support ticket creation simulated")
        return {"success": True, "simulated": True, "ticket_number": "TK-SIM-001"}