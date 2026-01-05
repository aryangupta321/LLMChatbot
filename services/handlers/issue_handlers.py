"""
Issue-Specific Handlers

Handlers for specific common issues like password resets, app updates, etc.
"""

from services.handlers.base import BaseHandler, HandlerResponse, check_keywords
from services.state_manager import ConversationState
import logging

logger = logging.getLogger(__name__)


class PasswordResetHandler(BaseHandler):
    """Handles password reset requests"""
    
    PASSWORD_KEYWORDS = ["password", "reset password", "forgot password", "change password", "can't login"]
    
    def can_handle(self, message: str, context: dict) -> bool:
        return check_keywords(message, self.PASSWORD_KEYWORDS)
    
    def handle(self, message: str, context: dict) -> HandlerResponse:
        logger.info(f"[PasswordResetHandler] Password reset request detected")
        
        current_state = context.get("state")
        
        # Initial password inquiry
        if current_state == ConversationState.GREETING.value:
            return HandlerResponse(
                text="Are you registered on the SelfCare portal (https://selfcare.acecloudhosting.com)?",
                should_update_state=True,
                new_state=ConversationState.ISSUE_GATHERING.value,
                metadata={"waiting_for": "selfcare_confirmation"}
            )
        
        # User confirms registration
        if current_state == ConversationState.ISSUE_GATHERING.value:
            message_lower = message.lower()
            
            if "yes" in message_lower or "registered" in message_lower:
                response_text = (
                    "Great! Please follow these steps:\n\n"
                    "1. Go to https://selfcare.acecloudhosting.com\n"
                    "2. Click 'Forgot Password'\n"
                    "3. Enter your registered email\n"
                    "4. Check your email for reset link\n"
                    "5. Follow the link to create a new password\n\n"
                    "If you don't receive the email within 5 minutes, check your spam folder or contact support at 1-888-415-5240."
                )
                return HandlerResponse(
                    text=response_text,
                    should_update_state=True,
                    new_state=ConversationState.AWAITING_CONFIRMATION.value
                )
            
            elif "no" in message_lower or "not registered" in message_lower:
                response_text = (
                    "No problem! To reset your password, please:\n\n"
                    "1. Call our support team: 1-888-415-5240\n"
                    "2. Or email: support@acecloudhosting.com\n"
                    "3. Provide your account details for verification\n\n"
                    "Our team will assist you with password reset immediately."
                )
                return HandlerResponse(
                    text=response_text,
                    should_update_state=True,
                    new_state=ConversationState.ESCALATION_OPTIONS.value
                )
        
        # Default response
        return HandlerResponse(
            text="I can help you reset your password. Are you registered on the SelfCare portal?",
            should_update_state=False
        )
    
    def get_priority(self) -> int:
        return 15
    
    def get_category(self) -> str:
        return "login"


class AppUpdateHandler(BaseHandler):
    """Handles application update requests"""
    
    APP_UPDATE_KEYWORDS = ["update", "upgrade", "latest version", "new version"]
    APP_NAMES = ["quickbooks", "sage", "excel", "outlook", "word", "office"]
    
    def can_handle(self, message: str, context: dict) -> bool:
        message_lower = message.lower()
        has_update_keyword = check_keywords(message, self.APP_UPDATE_KEYWORDS)
        has_app_name = any(app in message_lower for app in self.APP_NAMES)
        return has_update_keyword and has_app_name
    
    def handle(self, message: str, context: dict) -> HandlerResponse:
        logger.info(f"[AppUpdateHandler] App update request detected")
        
        response_text = (
            "For application updates, here's what you need to do:\n\n"
            "1. Open the application on your hosted desktop\n"
            "2. Go to Help → Check for Updates\n"
            "3. If updates are available, click 'Update Now'\n"
            "4. Follow the installation wizard\n\n"
            "Important Notes:\n"
            "- Save all your work before updating\n"
            "- Updates may take 5-15 minutes\n"
            "- Your desktop will restart after update\n\n"
            "If you encounter any issues, contact support at 1-888-415-5240."
        )
        
        return HandlerResponse(
            text=response_text,
            should_update_state=True,
            new_state=ConversationState.AWAITING_CONFIRMATION.value
        )
    
    def get_priority(self) -> int:
        return 16


class ContactRequestHandler(BaseHandler):
    """Handles generic contact/support requests"""
    
    CONTACT_PHRASES = [
        "contact support", "reach support", "talk to support",
        "support number", "phone number", "email support"
    ]
    
    def can_handle(self, message: str, context: dict) -> bool:
        message_lower = message.lower()
        return any(phrase in message_lower for phrase in self.CONTACT_PHRASES)
    
    def handle(self, message: str, context: dict) -> HandlerResponse:
        logger.info(f"[ContactRequestHandler] Contact info request")
        
        response_text = (
            "Here are multiple ways to reach Ace Cloud Hosting support:\n\n"
            "📞 Phone: 1-888-415-5240\n"
            "📧 Email: support@acecloudhosting.com\n"
            "💬 Live Chat: Available on our website\n"
            "🌐 Portal: https://selfcare.acecloudhosting.com\n\n"
            "Support Hours: 24/7/365\n"
            "Average Response Time: < 2 hours\n\n"
            "Would you like me to connect you to an agent now?"
        )
        
        return HandlerResponse(
            text=response_text,
            should_update_state=False
        )
    
    def get_priority(self) -> int:
        return 12
