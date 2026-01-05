"""
Collection Handlers

Handles collecting information from users for callbacks and tickets.
"""

from services.handlers.base import BaseHandler, HandlerResponse
from services.state_manager import ConversationState
import logging
import re

logger = logging.getLogger(__name__)


class CallbackCollectionHandler(BaseHandler):
    """Handles collecting callback details (time and phone)"""
    
    def can_handle(self, message: str, context: dict) -> bool:
        # Only handle if we are in CALLBACK_COLLECTION state
        return context.get("state") == ConversationState.CALLBACK_COLLECTION.value
    
    def handle(self, message: str, context: dict) -> HandlerResponse:
        logger.info(f"[CallbackCollectionHandler] Processing callback details: {message}")
        
        # Extract phone number (simple regex for now)
        phone_match = re.search(r'[\d\-\(\)\+\s]{7,}', message)
        phone = phone_match.group(0).strip() if phone_match else None
        
        # Extract time (everything else)
        time_pref = message.replace(phone, "").strip() if phone else message
        
        # Get visitor details from context
        visitor = context.get("visitor", {})
        visitor_name = visitor.get("name", "Chat User")
        visitor_email = visitor.get("email", "support@acecloudhosting.com")
        
        # We have enough info to schedule
        return HandlerResponse(
            text="Thanks! I've scheduled your callback. You'll receive a confirmation email shortly.",
            should_update_state=True,
            new_state=ConversationState.RESOLVED.value,
            metadata={
                "action": "schedule_callback",
                "visitor_name": visitor_name,
                "visitor_email": visitor_email,
                "phone": phone,
                "preferred_time": time_pref
            }
        )
    
    def get_priority(self) -> int:
        return 10  # High priority when in this state
