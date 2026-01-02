"""
Base Handler Pattern for Response Management

Abstract base class for all message handlers. Each handler is responsible
for detecting if it can handle a message and processing it appropriately.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class HandlerResponse:
    """Response from a handler"""
    text: str
    should_update_state: bool = True
    new_state: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BaseHandler(ABC):
    """Abstract base class for all message handlers"""
    
    def __init__(self):
        self.name = self.__class__.__name__
        logger.debug(f"Initialized handler: {self.name}")
    
    @abstractmethod
    def can_handle(self, message: str, context: Dict[str, Any]) -> bool:
        """
        Determine if this handler can process the message
        
        Args:
            message: User message text (lowercase recommended for matching)
            context: Additional context including state, history, category, etc.
            
        Returns:
            True if handler should process this message
        """
        pass
    
    @abstractmethod
    def handle(self, message: str, context: Dict[str, Any]) -> HandlerResponse:
        """
        Process the message and return a response
        
        Args:
            message: User message text
            context: Context dict with keys:
                - state: Current conversation state
                - session_id: Session identifier
                - history: Conversation history
                - category: Issue category from router
                - visitor: Visitor info dict
                - payload: Button payload if any
                
        Returns:
            HandlerResponse with text and optional state change
        """
        pass
    
    @abstractmethod
    def get_priority(self) -> int:
        """
        Return handler priority (lower = higher priority)
        
        Handlers with lower priority numbers are checked first.
        Use:
        - 1-10: Critical handlers (escalation, resolution)
        - 11-20: Specific issue handlers (password, updates)
        - 21-30: General handlers
        - 100: Fallback/default handlers
        
        Returns:
            Priority number (1 = highest priority)
        """
        pass
    
    def get_category(self) -> Optional[str]:
        """
        Return the issue category this handler belongs to
        
        Returns:
            Category string or None if not category-specific
        """
        return None
    
    def __repr__(self):
        return f"<{self.name} priority={self.get_priority()}>"


class FallbackHandler(BaseHandler):
    """Default handler that always matches and passes to LLM"""
    
    def can_handle(self, message: str, context: Dict[str, Any]) -> bool:
        """Always returns True - this is the last resort handler"""
        return True
    
    def handle(self, message: str, context: Dict[str, Any]) -> HandlerResponse:
        """Return None to signal that LLM should handle this"""
        logger.debug(f"[FallbackHandler] No specific handler matched, falling through to LLM")
        return HandlerResponse(
            text="",  # Empty text signals to use LLM
            should_update_state=False,
            metadata={"use_llm": True}
        )
    
    def get_priority(self) -> int:
        """Lowest priority - checked last"""
        return 100


# Utility functions for handlers

def check_keywords(message: str, keywords: list) -> bool:
    """Check if any keyword appears in message"""
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in keywords)


def check_exact_match(message: str, options: list) -> bool:
    """Check if message exactly matches any option"""
    message_lower = message.lower().strip()
    return message_lower in [opt.lower() for opt in options]


def extract_visitor_info(context: Dict[str, Any]) -> Dict[str, str]:
    """Extract visitor information from context"""
    visitor = context.get("visitor", {})
    return {
        "email": visitor.get("email", "support@acecloudhosting.com"),
        "name": visitor.get("name", visitor.get("email", "").split("@")[0] if visitor.get("email") else "Chat User")
    }
