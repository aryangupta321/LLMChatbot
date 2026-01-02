"""
Conversation State Manager

Manages conversation states and transitions for chatbot interactions.
Replaces fragile string-based state tracking with proper state machine.
"""

import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, Optional, List
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class ConversationState(Enum):
    """Possible states in a conversation"""
    GREETING = "greeting"
    ISSUE_GATHERING = "issue_gathering"
    TROUBLESHOOTING = "troubleshooting"
    AWAITING_CONFIRMATION = "awaiting_confirmation"
    ESCALATION_OPTIONS = "escalation_options"
    CALLBACK_COLLECTION = "callback_collection"
    TICKET_COLLECTION = "ticket_collection"
    RESOLVED = "resolved"
    ESCALATED = "escalated"
    ABANDONED = "abandoned"


class TransitionTrigger(Enum):
    """Events that trigger state transitions"""
    GREETING_RECEIVED = "greeting_received"
    ISSUE_DESCRIBED = "issue_described"
    TROUBLESHOOTING_STARTED = "troubleshooting_started"
    STEP_ACKNOWLEDGED = "step_acknowledged"
    SOLUTION_CONFIRMED = "solution_confirmed"
    SOLUTION_FAILED = "solution_failed"
    USER_FRUSTRATED = "user_frustrated"
    ESCALATION_REQUESTED = "escalation_requested"
    CALLBACK_REQUESTED = "callback_requested"
    TICKET_REQUESTED = "ticket_requested"
    AGENT_TRANSFER = "agent_transfer"
    INFO_COLLECTED = "info_collected"
    TIMEOUT = "timeout"
    RESET = "reset"


@dataclass
class ConversationSession:
    """Represents a single conversation session with state tracking"""
    session_id: str
    state: ConversationState = ConversationState.GREETING
    category: str = "other"
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    message_count: int = 0
    troubleshooting_attempts: int = 0
    escalation_attempts: int = 0
    user_info: Dict[str, str] = field(default_factory=dict)
    state_history: List[Dict] = field(default_factory=list)
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.now()
        self.message_count += 1
    
    def is_stale(self, timeout_minutes: int = 30) -> bool:
        """Check if conversation is stale (no activity for timeout_minutes)"""
        return datetime.now() - self.last_activity > timedelta(minutes=timeout_minutes)
    
    def add_state_transition(self, old_state: ConversationState, new_state: ConversationState, trigger: TransitionTrigger):
        """Record state transition in history"""
        self.state_history.append({
            "timestamp": datetime.now().isoformat(),
            "from": old_state.value,
            "to": new_state.value,
            "trigger": trigger.value
        })
        logger.info(f"[State] {self.session_id}: {old_state.value} -> {new_state.value} (trigger: {trigger.value})")


class StateManager:
    """Manages conversation states and transitions"""
    
    # Define valid state transitions
    TRANSITIONS = {
        ConversationState.GREETING: {
            TransitionTrigger.GREETING_RECEIVED: ConversationState.ISSUE_GATHERING,
            TransitionTrigger.ISSUE_DESCRIBED: ConversationState.TROUBLESHOOTING,
            TransitionTrigger.ESCALATION_REQUESTED: ConversationState.ESCALATION_OPTIONS,
        },
        ConversationState.ISSUE_GATHERING: {
            TransitionTrigger.ISSUE_DESCRIBED: ConversationState.TROUBLESHOOTING,
            TransitionTrigger.ESCALATION_REQUESTED: ConversationState.ESCALATION_OPTIONS,
        },
        ConversationState.TROUBLESHOOTING: {
            TransitionTrigger.STEP_ACKNOWLEDGED: ConversationState.TROUBLESHOOTING,
            TransitionTrigger.SOLUTION_CONFIRMED: ConversationState.AWAITING_CONFIRMATION,
            TransitionTrigger.SOLUTION_FAILED: ConversationState.ESCALATION_OPTIONS,
            TransitionTrigger.USER_FRUSTRATED: ConversationState.ESCALATION_OPTIONS,
            TransitionTrigger.ESCALATION_REQUESTED: ConversationState.ESCALATION_OPTIONS,
        },
        ConversationState.AWAITING_CONFIRMATION: {
            TransitionTrigger.SOLUTION_CONFIRMED: ConversationState.RESOLVED,
            TransitionTrigger.SOLUTION_FAILED: ConversationState.ESCALATION_OPTIONS,
            TransitionTrigger.TROUBLESHOOTING_STARTED: ConversationState.TROUBLESHOOTING,
        },
        ConversationState.ESCALATION_OPTIONS: {
            TransitionTrigger.AGENT_TRANSFER: ConversationState.ESCALATED,
            TransitionTrigger.CALLBACK_REQUESTED: ConversationState.CALLBACK_COLLECTION,
            TransitionTrigger.TICKET_REQUESTED: ConversationState.TICKET_COLLECTION,
        },
        ConversationState.CALLBACK_COLLECTION: {
            TransitionTrigger.INFO_COLLECTED: ConversationState.RESOLVED,
        },
        ConversationState.TICKET_COLLECTION: {
            TransitionTrigger.INFO_COLLECTED: ConversationState.ESCALATED,
        },
    }
    
    def __init__(self):
        self.sessions: Dict[str, ConversationSession] = {}
        logger.info("StateManager initialized")
    
    def create_session(self, session_id: str, category: str = "other") -> ConversationSession:
        """Create a new conversation session"""
        if session_id in self.sessions:
            logger.warning(f"[State] Session {session_id} already exists, returning existing session")
            return self.sessions[session_id]
        
        session = ConversationSession(session_id=session_id, category=category)
        self.sessions[session_id] = session
        logger.info(f"[State] Created new session {session_id} (category: {category})")
        return session
    
    def get_session(self, session_id: str) -> Optional[ConversationSession]:
        """Get an existing session"""
        return self.sessions.get(session_id)
    
    def transition(self, session_id: str, trigger: TransitionTrigger) -> bool:
        """Attempt to transition a session to a new state
        
        Args:
            session_id: Session ID
            trigger: Event that triggers the transition
            
        Returns:
            True if transition was successful, False otherwise
        """
        session = self.sessions.get(session_id)
        if not session:
            logger.error(f"[State] Session {session_id} not found for transition")
            return False
        
        current_state = session.state
        
        # Check if transition is valid
        if current_state not in self.TRANSITIONS:
            logger.warning(f"[State] No transitions defined for state {current_state.value}")
            return False
        
        valid_transitions = self.TRANSITIONS[current_state]
        if trigger not in valid_transitions:
            logger.warning(
                f"[State] Invalid transition: {current_state.value} -> {trigger.value}. "
                f"Valid triggers: {[t.value for t in valid_transitions.keys()]}"
            )
            return False
        
        # Perform transition
        new_state = valid_transitions[trigger]
        session.add_state_transition(current_state, new_state, trigger)
        session.state = new_state
        session.update_activity()
        
        # Track specific counters
        if trigger == TransitionTrigger.TROUBLESHOOTING_STARTED:
            session.troubleshooting_attempts += 1
        elif trigger in [TransitionTrigger.ESCALATION_REQUESTED, TransitionTrigger.AGENT_TRANSFER]:
            session.escalation_attempts += 1
        
        return True
    
    def update_activity(self, session_id: str):
        """Update last activity timestamp for a session"""
        session = self.sessions.get(session_id)
        if session:
            session.update_activity()
    
    def set_user_info(self, session_id: str, key: str, value: str):
        """Store user information for a session"""
        session = self.sessions.get(session_id)
        if session:
            session.user_info[key] = value
            logger.debug(f"[State] Session {session_id}: Set {key} = {value}")
    
    def get_user_info(self, session_id: str, key: str) -> Optional[str]:
        """Retrieve user information from a session"""
        session = self.sessions.get(session_id)
        if session:
            return session.user_info.get(key)
        return None
    
    def is_in_troubleshooting(self, session_id: str) -> bool:
        """Check if session is in troubleshooting state"""
        session = self.sessions.get(session_id)
        return session and session.state == ConversationState.TROUBLESHOOTING
    
    def is_awaiting_info(self, session_id: str) -> bool:
        """Check if session is awaiting user information"""
        session = self.sessions.get(session_id)
        return session and session.state in [
            ConversationState.CALLBACK_COLLECTION,
            ConversationState.TICKET_COLLECTION
        ]
    
    def should_offer_escalation(self, session_id: str) -> bool:
        """Determine if we should offer escalation options
        
        Offers escalation if:
        - User has tried troubleshooting multiple times
        - User explicitly requests help
        - Conversation is stale
        """
        session = self.sessions.get(session_id)
        if not session:
            return False
        
        # Check for multiple troubleshooting attempts
        if session.troubleshooting_attempts >= 3:
            logger.info(f"[State] Session {session_id}: Offering escalation (3+ troubleshooting attempts)")
            return True
        
        # Check for stale conversation
        if session.is_stale(timeout_minutes=15):
            logger.info(f"[State] Session {session_id}: Offering escalation (stale conversation)")
            return True
        
        return False
    
    def cleanup_stale_sessions(self, timeout_minutes: int = 30):
        """Remove stale sessions to prevent memory leaks"""
        stale_sessions = [
            sid for sid, session in self.sessions.items()
            if session.is_stale(timeout_minutes)
        ]
        
        for session_id in stale_sessions:
            logger.info(f"[State] Cleaning up stale session {session_id}")
            del self.sessions[session_id]
        
        if stale_sessions:
            logger.info(f"[State] Cleaned up {len(stale_sessions)} stale sessions")
    
    def end_session(self, session_id: str, final_state: ConversationState):
        """End a session and move to final state"""
        session = self.sessions.get(session_id)
        if session:
            old_state = session.state
            session.state = final_state
            session.add_state_transition(
                old_state, 
                final_state, 
                TransitionTrigger.RESET
            )
            logger.info(f"[State] Session {session_id} ended with state: {final_state.value}")
    
    def get_session_summary(self, session_id: str) -> Optional[Dict]:
        """Get summary of session state"""
        session = self.sessions.get(session_id)
        if not session:
            return None
        
        return {
            "session_id": session.session_id,
            "state": session.state.value,
            "category": session.category,
            "message_count": session.message_count,
            "troubleshooting_attempts": session.troubleshooting_attempts,
            "escalation_attempts": session.escalation_attempts,
            "duration_seconds": (datetime.now() - session.created_at).total_seconds(),
            "is_stale": session.is_stale(),
            "user_info": session.user_info,
            "state_history": session.state_history
        }


# Global state manager instance
state_manager = StateManager()


# Utility functions for detecting state transitions from user messages
def detect_trigger_from_message(message: str, current_state: ConversationState) -> Optional[TransitionTrigger]:
    """Detect what trigger should fire based on user message and current state
    
    Args:
        message: User message text (lowercase)
        current_state: Current conversation state
        
    Returns:
        Appropriate TransitionTrigger or None
    """
    message_lower = message.lower()
    
    # Escalation requests
    escalation_phrases = [
        "connect me to agent", "human agent", "talk to human", "speak to agent",
        "not resolved", "not fixed", "didn't work", "not working", "still stuck"
    ]
    if any(phrase in message_lower for phrase in escalation_phrases):
        return TransitionTrigger.ESCALATION_REQUESTED
    
    # Resolution confirmation
    resolution_keywords = ["resolved", "fixed", "working now", "solved", "all set", "thank you", "thanks"]
    if current_state == ConversationState.AWAITING_CONFIRMATION:
        if any(keyword in message_lower for keyword in resolution_keywords):
            return TransitionTrigger.SOLUTION_CONFIRMED
    
    # Troubleshooting acknowledgments
    acknowledgment_words = ["ok", "okay", "yes", "done", "completed", "tried"]
    if current_state == ConversationState.TROUBLESHOOTING:
        if any(word in message_lower for word in acknowledgment_words):
            return TransitionTrigger.STEP_ACKNOWLEDGED
    
    # Issue description (longer messages in gathering state)
    if current_state in [ConversationState.GREETING, ConversationState.ISSUE_GATHERING]:
        if len(message.split()) > 5:  # Substantial message
            return TransitionTrigger.ISSUE_DESCRIBED
        else:
            return TransitionTrigger.GREETING_RECEIVED
    
    # Callback request
    if "call" in message_lower or "callback" in message_lower or "option 2" in message_lower:
        return TransitionTrigger.CALLBACK_REQUESTED
    
    # Ticket request
    if "ticket" in message_lower or "option 3" in message_lower:
        return TransitionTrigger.TICKET_REQUESTED
    
    # Agent transfer (Option 1)
    if "instant chat" in message_lower or "option 1" in message_lower or message_lower.strip() == "1":
        return TransitionTrigger.AGENT_TRANSFER
    
    return None


# Usage example
if __name__ == "__main__":
    # Create a test session
    manager = StateManager()
    
    # Simulate a conversation flow
    session_id = "test_session_123"
    
    # 1. User starts conversation
    session = manager.create_session(session_id, category="quickbooks")
    print(f"Created session: {session.state.value}")
    
    # 2. User describes issue
    manager.transition(session_id, TransitionTrigger.ISSUE_DESCRIBED)
    print(f"After issue described: {session.state.value}")
    
    # 3. Bot provides troubleshooting steps
    manager.transition(session_id, TransitionTrigger.TROUBLESHOOTING_STARTED)
    print(f"In troubleshooting: {session.state.value}")
    
    # 4. User tries steps
    manager.transition(session_id, TransitionTrigger.STEP_ACKNOWLEDGED)
    print(f"Step acknowledged: {session.state.value}")
    
    # 5. Issue not resolved
    manager.transition(session_id, TransitionTrigger.SOLUTION_FAILED)
    print(f"Solution failed: {session.state.value}")
    
    # 6. User requests callback
    manager.transition(session_id, TransitionTrigger.CALLBACK_REQUESTED)
    print(f"Callback requested: {session.state.value}")
    
    # 7. Info collected
    manager.set_user_info(session_id, "name", "John Doe")
    manager.set_user_info(session_id, "phone", "123-456-7890")
    manager.transition(session_id, TransitionTrigger.INFO_COLLECTED)
    print(f"Info collected: {session.state.value}")
    
    # Print summary
    summary = manager.get_session_summary(session_id)
    print("\nSession Summary:")
    print(f"  State: {summary['state']}")
    print(f"  Messages: {summary['message_count']}")
    print(f"  Troubleshooting attempts: {summary['troubleshooting_attempts']}")
    print(f"  User info: {summary['user_info']}")
    print(f"\nState History:")
    for transition in summary['state_history']:
        print(f"  {transition['from']} -> {transition['to']} ({transition['trigger']})")
