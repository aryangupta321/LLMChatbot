"""
Escalation and Resolution Handlers

Handles user requests for escalation options, resolution confirmation,
and problem acknowledgment.
"""

from services.handlers.base import BaseHandler, HandlerResponse, check_keywords, check_exact_match
from services.state_manager import ConversationState, TransitionTrigger
import logging

logger = logging.getLogger(__name__)


class ResolutionConfirmedHandler(BaseHandler):
    """Handles when user confirms issue is resolved"""
    
    RESOLUTION_KEYWORDS = ["resolved", "fixed", "working now", "solved", "all set"]
    
    def can_handle(self, message: str, context: dict) -> bool:
        return check_keywords(message, self.RESOLUTION_KEYWORDS)
    
    def handle(self, message: str, context: dict) -> HandlerResponse:
        logger.info(f"[ResolutionHandler] Issue resolved by user")
        
        return HandlerResponse(
            text="Great! I'm glad the issue is resolved. If you need anything else, feel free to ask!",
            should_update_state=True,
            new_state=ConversationState.RESOLVED.value,
            metadata={
                "action": "close_chat",
                "reason": "resolved"
            }
        )
    
    def get_priority(self) -> int:
        return 5  # High priority - check early


class ProblemNotResolvedHandler(BaseHandler):
    """Handles when user says issue is not resolved"""
    
    NOT_RESOLVED_KEYWORDS = [
        "not resolved", "not fixed", "not working", 
        "didn't work", "still not", "still stuck"
    ]
    
    def can_handle(self, message: str, context: dict) -> bool:
        return check_keywords(message, self.NOT_RESOLVED_KEYWORDS)
    
    def handle(self, message: str, context: dict) -> HandlerResponse:
        logger.info(f"[ProblemNotResolvedHandler] Issue NOT resolved - offering escalation options")
        
        response_text = "I understand this is frustrating. Here are 3 ways I can help:"
        
        return HandlerResponse(
            text=response_text,
            should_update_state=True,
            new_state=ConversationState.ESCALATION_OPTIONS.value,
            metadata={
                "action": "show_suggestions",
                "suggestions": [
                    {
                        "text": "📞 Instant Chat",
                        "action_type": "reply",
                        "action_value": "1"
                    },
                    {
                        "text": "📅 Schedule Callback",
                        "action_type": "reply",
                        "action_value": "2"
                    },
                    {
                        "text": "🎫 Create Support Ticket",
                        "action_type": "reply",
                        "action_value": "3"
                    }
                ]
            }
        )
    
    def get_priority(self) -> int:
        return 6  # High priority


class AgentRequestHandler(BaseHandler):
    """Handles direct requests to speak with an agent"""
    
    AGENT_REQUEST_PHRASES = [
        "connect me to agent", "connect to agent", "human agent",
        "talk to human", "speak to agent"
    ]
    
    def can_handle(self, message: str, context: dict) -> bool:
        message_lower = message.lower()
        return any(phrase in message_lower for phrase in self.AGENT_REQUEST_PHRASES)
    
    def handle(self, message: str, context: dict) -> HandlerResponse:
        logger.info(f"[AgentRequestHandler] User requesting human agent")
        
        return HandlerResponse(
            text="I can help you with that. Here are your options:",
            should_update_state=True,
            new_state=ConversationState.ESCALATION_OPTIONS.value,
            metadata={
                "action": "show_suggestions",
                "suggestions": [
                    {
                        "text": "📞 Instant Chat",
                        "action_type": "reply",
                        "action_value": "1"
                    },
                    {
                        "text": "📅 Schedule Callback",
                        "action_type": "reply",
                        "action_value": "2"
                    },
                    {
                        "text": "🎫 Create Support Ticket",
                        "action_type": "reply",
                        "action_value": "3"
                    }
                ]
            }
        )
    
    def get_priority(self) -> int:
        return 7


class InstantChatHandler(BaseHandler):
    """Handles Option 1 - Instant Chat Transfer"""
    
    def can_handle(self, message: str, context: dict) -> bool:
        message_lower = message.lower().strip()
        payload = context.get("payload", "")
        last_bot_message = ""
        
        history = context.get("history", [])
        if history and len(history) > 0:
            last_msg = history[-1]
            if last_msg.get("role") == "assistant":
                last_bot_message = last_msg.get("content", "").lower()
        
        # Check if user selected option 1
        return (
            ("instant chat" in message_lower) or
            ("option 1" in message_lower) or
            (message_lower == "1" and "options" in last_bot_message) or
            (payload == "option_1")
        )
    
    def handle(self, message: str, context: dict) -> HandlerResponse:
        logger.info(f"[InstantChatHandler] User selected instant chat transfer")
        
        return HandlerResponse(
            text="Connecting you to our support team now...",
            should_update_state=True,
            new_state=ConversationState.ESCALATED.value,
            metadata={
                "action": "transfer_to_agent",
                "transfer_type": "instant_chat"
            }
        )
    
    def get_priority(self) -> int:
        return 8


class CallbackHandler(BaseHandler):
    """Handles Option 2 - Schedule Callback"""
    
    def can_handle(self, message: str, context: dict) -> bool:
        message_lower = message.lower().strip()
        payload = context.get("payload", "")
        
        return (
            ("callback" in message_lower) or
            ("option 2" in message_lower) or
            (message_lower == "2") or
            ("schedule" in message_lower) or
            (payload == "option_2")
        )
    
    def handle(self, message: str, context: dict) -> HandlerResponse:
        logger.info(f"[CallbackHandler] User selected callback")
        
        visitor_email = context.get("visitor", {}).get("email", "support@acecloudhosting.com")
        visitor_name = context.get("visitor", {}).get("name", visitor_email.split("@")[0] if visitor_email else "Chat User")
        
        response_text = (
            f"Perfect! I'll schedule a callback for you.\n\n"
            f"Please provide:\n"
            f"1. Your preferred time (e.g., 'tomorrow at 2 PM' or 'Monday morning')\n"
            f"2. Your phone number\n\n"
            f"Example: Time: 9pm tomorrow\\nPhone: 1234567890"
        )
        
        return HandlerResponse(
            text=response_text,
            should_update_state=True,
            new_state=ConversationState.CALLBACK_COLLECTION.value,
            metadata={
                "visitor_name": visitor_name,
                "visitor_email": visitor_email
            }
        )
    
    def get_priority(self) -> int:
        return 9


class TicketHandler(BaseHandler):
    """Handles Option 3 - Create Support Ticket"""
    
    def can_handle(self, message: str, context: dict) -> bool:
        message_lower = message.lower().strip()
        payload = context.get("payload", "")
        
        return (
            ("ticket" in message_lower) or
            ("option 3" in message_lower) or
            (message_lower == "3") or
            ("support ticket" in message_lower) or
            (payload == "option_3")
        )
    
    def handle(self, message: str, context: dict) -> HandlerResponse:
        logger.info(f"[TicketHandler] User selected support ticket")
        
        response_text = (
            "Perfect! I'm creating a support ticket for you.\n\n"
            "Please provide:\n"
            "1. Your name\n"
            "2. Your email\n"
            "3. Your phone number\n"
            "4. Brief description of the issue\n\n"
            "A ticket will be created and you'll receive a confirmation email shortly. "
            "Our support team will follow up with you within 24 hours.\n\n"
            "Thank you for contacting Ace Cloud Hosting!"
        )
        
        return HandlerResponse(
            text=response_text,
            should_update_state=True,
            new_state=ConversationState.TICKET_COLLECTION.value,
            metadata={
                "action": "create_ticket"
            }
        )
    
    def get_priority(self) -> int:
        return 10
