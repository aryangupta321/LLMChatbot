"""
Handler Registry

Manages registration and execution of all message handlers.
Provides a clean interface for routing messages to appropriate handlers.
"""

from typing import List, Optional, Dict, Any
from services.handlers.base import BaseHandler, HandlerResponse, FallbackHandler
from services.handlers.escalation_handlers import (
    ResolutionConfirmedHandler,
    ProblemNotResolvedHandler,
    AgentRequestHandler,
    InstantChatHandler,
    CallbackHandler,
    TicketHandler
)
from services.handlers.issue_handlers import (
    PasswordResetHandler,
    AppUpdateHandler,
    ContactRequestHandler
)
import logging

logger = logging.getLogger(__name__)


class HandlerRegistry:
    """
    Central registry for all message handlers
    
    Handlers are checked in priority order (lowest priority number first).
    The first handler that can_handle() a message will process it.
    """
    
    def __init__(self):
        self.handlers: List[BaseHandler] = []
        self._register_default_handlers()
        self._sort_handlers()
        logger.info(f"HandlerRegistry initialized with {len(self.handlers)} handlers")
    
    def _register_default_handlers(self):
        """Register all default handlers"""
        # Escalation & resolution handlers (priority 5-10)
        self.register(ResolutionConfirmedHandler())
        self.register(ProblemNotResolvedHandler())
        self.register(AgentRequestHandler())
        self.register(InstantChatHandler())
        self.register(CallbackHandler())
        self.register(TicketHandler())
        
        # Issue-specific handlers (priority 11-20)
        self.register(ContactRequestHandler())
        self.register(PasswordResetHandler())
        self.register(AppUpdateHandler())
        
        # Fallback handler (priority 100) - always checked last
        self.register(FallbackHandler())
    
    def register(self, handler: BaseHandler):
        """
        Register a new handler
        
        Args:
            handler: Handler instance to register
        """
        self.handlers.append(handler)
        logger.debug(f"Registered handler: {handler}")
    
    def _sort_handlers(self):
        """Sort handlers by priority (lowest number = highest priority)"""
        self.handlers.sort(key=lambda h: h.get_priority())
        logger.debug(f"Handler priority order: {[h.name for h in self.handlers]}")
    
    def find_handler(self, message: str, context: Dict[str, Any]) -> Optional[BaseHandler]:
        """
        Find the first handler that can process this message
        
        Args:
            message: User message text
            context: Context dict with state, history, etc.
            
        Returns:
            First matching handler or None
        """
        message_lower = message.lower()
        
        for handler in self.handlers:
            try:
                if handler.can_handle(message_lower, context):
                    logger.info(f"[HandlerRegistry] Matched: {handler.name}")
                    return handler
            except Exception as e:
                logger.error(f"[HandlerRegistry] Error in {handler.name}.can_handle(): {e}")
                continue
        
        return None
    
    def handle_message(self, message: str, context: Dict[str, Any]) -> Optional[HandlerResponse]:
        """
        Route message to appropriate handler and get response
        
        Args:
            message: User message text
            context: Context dict with:
                - state: Current conversation state
                - session_id: Session identifier
                - history: Conversation history list
                - category: Issue category from router
                - visitor: Visitor info dict
                - payload: Button payload if any
                
        Returns:
            HandlerResponse if a handler matched, None to use LLM
        """
        handler = self.find_handler(message, context)
        
        if not handler:
            logger.warning(f"[HandlerRegistry] No handler matched for message")
            return None
        
        try:
            response = handler.handle(message, context)
            logger.info(f"[HandlerRegistry] {handler.name} processed message")
            
            # Check if this is a fallback to LLM
            if response.metadata.get("use_llm"):
                return None
            
            return response
            
        except Exception as e:
            logger.error(f"[HandlerRegistry] Error in {handler.name}.handle(): {e}", exc_info=True)
            return None
    
    def get_handlers_summary(self) -> Dict[str, Any]:
        """Get summary of registered handlers"""
        return {
            "total_handlers": len(self.handlers),
            "handlers": [
                {
                    "name": h.name,
                    "priority": h.get_priority(),
                    "category": h.get_category()
                }
                for h in self.handlers
            ]
        }
    
    def list_handlers(self) -> List[str]:
        """Get list of handler names in priority order"""
        return [h.name for h in self.handlers]


# Global handler registry instance
handler_registry = HandlerRegistry()


# Usage example
if __name__ == "__main__":
    # Test the registry
    registry = HandlerRegistry()
    
    print("=== Handler Registry Test ===")
    print(f"\nRegistered Handlers ({len(registry.handlers)}):")
    for handler in registry.handlers:
        print(f"  - {handler.name} (priority: {handler.get_priority()})")
    
    # Test message routing
    test_messages = [
        ("issue is resolved", {}),
        ("not working", {}),
        ("connect me to agent", {}),
        ("option 1", {"payload": ""}),
        ("callback please", {}),
        ("forgot my password", {}),
        ("random question", {})
    ]
    
    print("\n=== Message Routing Tests ===")
    for msg, ctx in test_messages:
        handler = registry.find_handler(msg, ctx)
        print(f"\n'{msg}'")
        print(f"  → Handler: {handler.name if handler else 'None'}")
