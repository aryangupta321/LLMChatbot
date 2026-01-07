"""
LLM-based classification service for intent detection and decision making.
Replaces hardcoded keyword-based logic with context-aware AI classification.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Literal
from openai import OpenAI
from dataclasses import dataclass
import tiktoken

logger = logging.getLogger(__name__)

# Token counting for cost tracking and limits
def count_tokens(text: str, model: str = "gpt-4o-mini") -> int:
    """Count tokens in text for given model"""
    try:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except Exception as e:
        # Fallback: rough estimation (1 token ≈ 4 characters)
        return len(text) // 4

logger = logging.getLogger(__name__)

@dataclass
class ClassificationResult:
    """Structured result from LLM classification"""
    decision: str  # Main classification result
    confidence: float  # 0-100
    reasoning: str  # Why this decision was made
    raw_response: str  # Full LLM response for debugging


class LLMClassifier:
    """
    Uses LLM to make intelligent decisions about user intent and conversation state.
    Replaces brittle keyword matching with context-aware classification.
    
    OPTIMIZATION: Uses unified classification to reduce API calls from 3x to 1x per message.
    """
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o-mini"  # Fast and cost-effective
        
        # Model limits
        self.max_context_tokens = 128000  # gpt-4o-mini context window
        self.max_classification_tokens = 1000  # Max tokens for classification call
        self.max_messages_for_context = 10  # Limit context to last 10 messages
        
        # Token budget per conversation (prevent runaway costs)
        self.max_tokens_per_conversation = int(os.getenv("LLM_MAX_TOKENS_PER_CHAT", "20000"))
        
        # Configurable confidence thresholds
        self.resolution_threshold = float(os.getenv("LLM_RESOLUTION_CONFIDENCE", "85"))
        self.escalation_threshold = float(os.getenv("LLM_ESCALATION_CONFIDENCE", "70"))
        self.intent_threshold = float(os.getenv("LLM_INTENT_CONFIDENCE", "75"))
        
        # Enable unified classification to reduce API calls (3x → 1x)
        self.use_unified_classification = os.getenv("LLM_UNIFIED_CLASSIFICATION", "true").lower() == "true"
        
        # Hallucination prevention: Require minimum confidence
        self.min_confidence_for_action = float(os.getenv("LLM_MIN_CONFIDENCE", "60"))
        
        # Track token usage per session for cost control
        self.session_token_usage: Dict[str, int] = {}
        
        logger.info(f"LLM Classifier initialized - Model: {self.model} (128K context)")
        logger.info(f"Token Limits: {self.max_tokens_per_conversation} per conversation, {self.max_classification_tokens} per classification")
        logger.info(f"Thresholds: resolution={self.resolution_threshold}%, escalation={self.escalation_threshold}%, intent={self.intent_threshold}%")
        logger.info(f"Min Confidence for Action: {self.min_confidence_for_action}% (hallucination prevention)")
        logger.info(f"LLM Unified Classification: {'ENABLED (1 API call)' if self.use_unified_classification else 'DISABLED (3 API calls)'}")
    
    def _track_token_usage(self, session_id: str, tokens: int):
        """Track token usage per session to prevent cost explosion"""
        if session_id not in self.session_token_usage:
            self.session_token_usage[session_id] = 0
        
        self.session_token_usage[session_id] += tokens
        
        if self.session_token_usage[session_id] > self.max_tokens_per_conversation:
            logger.warning(f"[Token Limit] Session {session_id} exceeded {self.max_tokens_per_conversation} tokens (used: {self.session_token_usage[session_id]})")
            return False  # Exceeded limit
        
        return True  # Within limit
    
    def _truncate_conversation(self, conversation_history: List[Dict], max_messages: int = None) -> List[Dict]:
        """
        Truncate conversation to prevent token overflow.
        Keeps most recent messages and adds summary if truncated.
        """
        if not conversation_history:
            return []
        
        max_msgs = max_messages or self.max_messages_for_context
        
        if len(conversation_history) <= max_msgs:
            return conversation_history
        
        # Keep last N messages
        recent_messages = conversation_history[-max_msgs:]
        
        truncated_count = len(conversation_history) - max_msgs
        logger.info(f"[Token Management] Truncated {truncated_count} old messages, keeping last {max_msgs}")
        
        # Add context note about truncation
        summary_msg = {
            "role": "system",
            "content": f"[Previous {truncated_count} messages truncated for token limit]"
        }
        
        return [summary_msg] + recent_messages
    
    def _validate_confidence(self, confidence: float, decision: str, classification_type: str) -> bool:
        """
        Validate confidence score to prevent hallucination-driven actions.
        Returns True if confidence is acceptable, False if too low (likely hallucination).
        """
        if confidence < self.min_confidence_for_action:
            logger.warning(f"[Hallucination Check] {classification_type} confidence too low: {confidence}% (min: {self.min_confidence_for_action}%) - Decision: {decision} - IGNORING")
            return False
        
        return True
    
    def _call_llm(self, system_prompt: str, user_message: str, session_id: str = "unknown") -> str:
        """
        Make LLM API call with structured prompts.
        Includes token tracking and cost controls.
        Returns raw text response.
        """
        # Count tokens before calling
        input_text = system_prompt + user_message
        input_tokens = count_tokens(input_text, self.model)
        
        # Check if adding this call would exceed budget
        if not self._track_token_usage(session_id, input_tokens):
            logger.error(f"[Cost Control] Session {session_id} exceeded token budget - BLOCKING classification call")
            raise Exception(f"Token budget exceeded for session {session_id}")
        
        # Check if input is too large
        if input_tokens > self.max_classification_tokens:
            logger.warning(f"[Token Limit] Classification input too large: {input_tokens} tokens (max: {self.max_classification_tokens}) - Truncating")
            # Truncate user message to fit
            max_user_msg_chars = (self.max_classification_tokens - count_tokens(system_prompt, self.model)) * 4
            user_message = user_message[:max_user_msg_chars] + "..."
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.1,  # Low temperature for consistent classification
                max_tokens=150  # Keep responses short for classification
            )
            
            # Track output tokens
            output_tokens = response.usage.completion_tokens if hasattr(response, 'usage') else 150
            self._track_token_usage(session_id, output_tokens)
            
            logger.debug(f"[Token Usage] Input: {input_tokens}, Output: {output_tokens}, Session Total: {self.session_token_usage.get(session_id, 0)}")
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"LLM classification failed: {e}")
            raise
    
    def classify_unified(self, message: str, conversation_history: List[Dict], session_id: str = "unknown") -> Dict[str, ClassificationResult]:
        """
        OPTIMIZED: Single LLM call for all classifications (resolution, escalation, intent).
        Reduces API calls from 3x to 1x per message.
        
        Includes safeguards:
        - Token limit enforcement
        - Conversation truncation
        - Hallucination detection via confidence thresholds
        
        Returns:
            {
                "resolution": ClassificationResult,
                "escalation": ClassificationResult,
                "intent": ClassificationResult
            }
        """
        # Truncate conversation if too long
        truncated_history = self._truncate_conversation(conversation_history)
        context = self._build_context(truncated_history, last_n=4)
        
        system_prompt = """You are a conversation analyzer. Analyze the user's message for:

1. RESOLUTION: Is the user's issue resolved?
   - RESOLVED: User confirms issue is fixed AND expresses satisfaction
   - UNRESOLVED: User says issue persists or asks for more help
   - UNCERTAIN: Ambiguous response

2. ESCALATION: Does user need human agent?
   - NEEDS_HUMAN: User requests agent, is frustrated, or issue is too complex
   - BOT_CAN_HANDLE: Bot can continue helping
   - UNCERTAIN: Not clear yet

3. INTENT: What does user want?
   - TRANSFER: Instant chat with agent now
   - CALLBACK: Schedule callback later
   - TICKET: Email-based support ticket
   - QUESTION: Informational question
   - OTHER: Unclear

CRITICAL: Detect negations ("not fixed" = UNRESOLVED)

Output ONLY valid JSON:
{
  "resolution": {"decision": "RESOLVED|UNRESOLVED|UNCERTAIN", "confidence": 0-100, "reasoning": "brief"},
  "escalation": {"decision": "NEEDS_HUMAN|BOT_CAN_HANDLE|UNCERTAIN", "confidence": 0-100, "reasoning": "brief"},
  "intent": {"decision": "TRANSFER|CALLBACK|TICKET|QUESTION|OTHER", "confidence": 0-100, "reasoning": "brief"}
}"""

        user_prompt = f"""Conversation Context:
{context}

Latest User Message: "{message}"

Analyze all 3 aspects. Respond with JSON only."""

        try:
            raw_response = self._call_llm(system_prompt, user_prompt, session_id)
            logger.debug(f"[LLM Classifier] Unified raw response: {raw_response}")
            
            parsed = json.loads(raw_response)
            
            # Extract results with validation
            resolution_conf = float(parsed["resolution"].get("confidence", 0))
            escalation_conf = float(parsed["escalation"].get("confidence", 0))
            intent_conf = float(parsed["intent"].get("confidence", 0))
            
            results = {
                "resolution": ClassificationResult(
                    decision=parsed["resolution"].get("decision", "UNCERTAIN"),
                    confidence=resolution_conf,
                    reasoning=parsed["resolution"].get("reasoning", ""),
                    raw_response=raw_response
                ),
                "escalation": ClassificationResult(
                    decision=parsed["escalation"].get("decision", "UNCERTAIN"),
                    confidence=escalation_conf,
                    reasoning=parsed["escalation"].get("reasoning", ""),
                    raw_response=raw_response
                ),
                "intent": ClassificationResult(
                    decision=parsed["intent"].get("decision", "OTHER"),
                    confidence=intent_conf,
                    reasoning=parsed["intent"].get("reasoning", ""),
                    raw_response=raw_response
                )
            }
            
            # Hallucination detection: Warn if confidence is suspiciously low
            if not self._validate_confidence(resolution_conf, results['resolution'].decision, "Resolution"):
                results['resolution'].decision = "UNCERTAIN"
            
            if not self._validate_confidence(escalation_conf, results['escalation'].decision, "Escalation"):
                results['escalation'].decision = "UNCERTAIN"
            
            logger.info(f"[LLM Classifier] UNIFIED (1 call) - Resolution: {results['resolution'].decision} ({results['resolution'].confidence}%), Escalation: {results['escalation'].decision} ({results['escalation'].confidence}%), Intent: {results['intent'].decision} ({results['intent'].confidence}%)")
            
            return results
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse unified LLM JSON: {raw_response} - {e}")
            # Return safe defaults
            return {
                "resolution": ClassificationResult("UNCERTAIN", 0, "JSON parse error", raw_response),
                "escalation": ClassificationResult("UNCERTAIN", 0, "JSON parse error", raw_response),
                "intent": ClassificationResult("OTHER", 0, "JSON parse error", raw_response)
            }
        except Exception as e:
            logger.error(f"Unified classification failed: {e}")
            return {
                "resolution": ClassificationResult("UNCERTAIN", 0, f"Error: {str(e)}", ""),
                "escalation": ClassificationResult("UNCERTAIN", 0, f"Error: {str(e)}", ""),
                "intent": ClassificationResult("OTHER", 0, f"Error: {str(e)}", "")
            }
    
    def classify_resolution(self, message: str, conversation_history: List[Dict]) -> ClassificationResult:
        """
        Determine if user's issue is resolved.
        
        If unified classification is enabled, uses that (1 API call for all).
        Otherwise makes individual call (legacy mode).
        
        Returns:
            ClassificationResult with decision: "RESOLVED", "UNRESOLVED", or "UNCERTAIN"
        """
        # Use unified classification if enabled (saves 2 API calls)
        if self.use_unified_classification:
            results = self.classify_unified(message, conversation_history)
            return results["resolution"]
        
        # Legacy: Individual classification call
        # Build context from last 3 messages
        context = self._build_context(conversation_history, last_n=3)
        
        system_prompt = """You are a customer satisfaction analyzer. Determine if the user's issue is RESOLVED.

Rules:
- RESOLVED: User explicitly confirms issue is fixed/working/resolved AND expresses satisfaction
- UNRESOLVED: User says issue still exists OR is not working OR asks for more help
- UNCERTAIN: Ambiguous response or acknowledgment without confirmation

CRITICAL: Detect negations carefully:
- "not fixed" = UNRESOLVED
- "not working" = UNRESOLVED
- "still broken" = UNRESOLVED

Output ONLY valid JSON:
{
  "decision": "RESOLVED|UNRESOLVED|UNCERTAIN",
  "confidence": 0-100,
  "reasoning": "brief explanation"
}"""

        user_prompt = f"""Conversation Context:
{context}

Latest User Message: "{message}"

Is the user's issue RESOLVED? Respond with JSON only."""

        try:
            raw_response = self._call_llm(system_prompt, user_prompt)
            logger.debug(f"[LLM Classifier] Resolution raw response: {raw_response}")
            
            # Parse JSON response
            parsed = json.loads(raw_response)
            
            result = ClassificationResult(
                decision=parsed.get("decision", "UNCERTAIN"),
                confidence=float(parsed.get("confidence", 0)),
                reasoning=parsed.get("reasoning", ""),
                raw_response=raw_response
            )
            
            logger.info(f"[LLM Classifier] Resolution: {result.decision} (confidence: {result.confidence}%) - {result.reasoning}")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM JSON response: {raw_response} - {e}")
            # Fallback to uncertain
            return ClassificationResult(
                decision="UNCERTAIN",
                confidence=0,
                reasoning="JSON parse error",
                raw_response=raw_response
            )
        except Exception as e:
            logger.error(f"Resolution classification failed: {e}")
            return ClassificationResult(
                decision="UNCERTAIN",
                confidence=0,
                reasoning=f"Error: {str(e)}",
                raw_response=""
            )
    
    def classify_escalation_need(self, message: str, conversation_history: List[Dict]) -> ClassificationResult:
        """
        Determine if user needs human agent assistance.
        
        If unified classification is enabled, uses that (1 API call for all).
        Otherwise makes individual call (legacy mode).
        
        Returns:
            ClassificationResult with decision: "NEEDS_HUMAN", "BOT_CAN_HANDLE", or "UNCERTAIN"
        """
        # Use unified classification if enabled (saves API calls)
        if self.use_unified_classification:
            results = self.classify_unified(message, conversation_history)
            return results["escalation"]
        
        # Legacy: Individual classification call
        context = self._build_context(conversation_history, last_n=4)
        
        system_prompt = """You are an escalation analyzer. Determine if the user needs a human agent.

Escalate (NEEDS_HUMAN) if:
- User explicitly requests human/agent/person
- User is frustrated/angry after bot failed to help
- Issue is too complex for bot (technical, billing, account access)
- User repeated same issue 3+ times without resolution
- User threatens to cancel/leave

Bot can handle (BOT_CAN_HANDLE) if:
- Simple informational questions
- Standard troubleshooting not yet exhausted
- User hasn't expressed frustration
- Issue matches bot's knowledge base

Output ONLY valid JSON:
{
  "decision": "NEEDS_HUMAN|BOT_CAN_HANDLE|UNCERTAIN",
  "confidence": 0-100,
  "reasoning": "brief explanation"
}"""

        user_prompt = f"""Conversation Context:
{context}

Latest User Message: "{message}"

Does user need human agent? Respond with JSON only."""

        try:
            raw_response = self._call_llm(system_prompt, user_prompt)
            logger.debug(f"[LLM Classifier] Escalation raw response: {raw_response}")
            
            parsed = json.loads(raw_response)
            
            result = ClassificationResult(
                decision=parsed.get("decision", "UNCERTAIN"),
                confidence=float(parsed.get("confidence", 0)),
                reasoning=parsed.get("reasoning", ""),
                raw_response=raw_response
            )
            
            logger.info(f"[LLM Classifier] Escalation: {result.decision} (confidence: {result.confidence}%) - {result.reasoning}")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM JSON response: {raw_response} - {e}")
            return ClassificationResult(
                decision="UNCERTAIN",
                confidence=0,
                reasoning="JSON parse error",
                raw_response=raw_response
            )
        except Exception as e:
            logger.error(f"Escalation classification failed: {e}")
            return ClassificationResult(
                decision="UNCERTAIN",
                confidence=0,
                reasoning=f"Error: {str(e)}",
                raw_response=""
            )
    
    def classify_intent(self, message: str, conversation_history: List[Dict]) -> ClassificationResult:
        """
        Classify user's primary intent.
        
        If unified classification is enabled, uses that (1 API call for all).
        Otherwise makes individual call (legacy mode).
        
        Returns:
            ClassificationResult with decision: "TRANSFER", "CALLBACK", "TICKET", "QUESTION", or "OTHER"
        """
        # Use unified classification if enabled (saves API calls)
        if self.use_unified_classification:
            results = self.classify_unified(message, conversation_history)
            return results["intent"]
        
        # Legacy: Individual classification call
        context = self._build_context(conversation_history, last_n=2)
        
        system_prompt = """You are an intent classifier. Identify the user's primary intent.

Intent Types:
- TRANSFER: Wants to speak with human agent NOW (instant chat/call)
- CALLBACK: Wants someone to call them back later
- TICKET: Wants to create support ticket (email-based)
- QUESTION: Asking informational question (product, pricing, how-to)
- OTHER: Unclear or doesn't fit categories

Output ONLY valid JSON:
{
  "decision": "TRANSFER|CALLBACK|TICKET|QUESTION|OTHER",
  "confidence": 0-100,
  "reasoning": "brief explanation"
}"""

        user_prompt = f"""Conversation Context:
{context}

Latest User Message: "{message}"

What is the user's intent? Respond with JSON only."""

        try:
            raw_response = self._call_llm(system_prompt, user_prompt)
            logger.debug(f"[LLM Classifier] Intent raw response: {raw_response}")
            
            parsed = json.loads(raw_response)
            
            result = ClassificationResult(
                decision=parsed.get("decision", "OTHER"),
                confidence=float(parsed.get("confidence", 0)),
                reasoning=parsed.get("reasoning", ""),
                raw_response=raw_response
            )
            
            logger.info(f"[LLM Classifier] Intent: {result.decision} (confidence: {result.confidence}%) - {result.reasoning}")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM JSON response: {raw_response} - {e}")
            return ClassificationResult(
                decision="OTHER",
                confidence=0,
                reasoning="JSON parse error",
                raw_response=raw_response
            )
        except Exception as e:
            logger.error(f"Intent classification failed: {e}")
            return ClassificationResult(
                decision="OTHER",
                confidence=0,
                reasoning=f"Error: {str(e)}",
                raw_response=""
            )
    
    def classify_sentiment(self, message: str) -> ClassificationResult:
        """
        Analyze user's emotional state/sentiment.
        
        Returns:
            ClassificationResult with decision: "SATISFIED", "FRUSTRATED", "ANGRY", "NEUTRAL"
        """
        system_prompt = """You are a sentiment analyzer. Classify the user's emotional state.

Sentiment Types:
- SATISFIED: Happy, grateful, content, issue resolved
- FRUSTRATED: Annoyed, impatient, repeating issue
- ANGRY: Very upset, threatening, using profanity
- NEUTRAL: Calm, informational, no strong emotion

Output ONLY valid JSON:
{
  "decision": "SATISFIED|FRUSTRATED|ANGRY|NEUTRAL",
  "confidence": 0-100,
  "reasoning": "brief explanation"
}"""

        user_prompt = f'User Message: "{message}"\n\nWhat is the sentiment? Respond with JSON only.'

        try:
            raw_response = self._call_llm(system_prompt, user_prompt)
            logger.debug(f"[LLM Classifier] Sentiment raw response: {raw_response}")
            
            parsed = json.loads(raw_response)
            
            result = ClassificationResult(
                decision=parsed.get("decision", "NEUTRAL"),
                confidence=float(parsed.get("confidence", 0)),
                reasoning=parsed.get("reasoning", ""),
                raw_response=raw_response
            )
            
            logger.info(f"[LLM Classifier] Sentiment: {result.decision} (confidence: {result.confidence}%)")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM JSON response: {raw_response} - {e}")
            return ClassificationResult(
                decision="NEUTRAL",
                confidence=0,
                reasoning="JSON parse error",
                raw_response=raw_response
            )
        except Exception as e:
            logger.error(f"Sentiment classification failed: {e}")
            return ClassificationResult(
                decision="NEUTRAL",
                confidence=0,
                reasoning=f"Error: {str(e)}",
                raw_response=""
            )
    
    def _build_context(self, conversation_history: List[Dict], last_n: int = 3) -> str:
        """
        Build conversation context from history for classification.
        Returns formatted string of last N messages.
        """
        if not conversation_history:
            return "(No previous messages)"
        
        # Get last N messages
        recent = conversation_history[-last_n:] if len(conversation_history) > last_n else conversation_history
        
        context_lines = []
        for msg in recent:
            role = "User" if msg.get("role") == "user" else "Bot"
            content = msg.get("content", "")[:200]  # Truncate long messages
            context_lines.append(f"{role}: {content}")
        
        return "\n".join(context_lines)
    
    def should_close_chat(self, classification: ClassificationResult) -> bool:
        """
        Decide if chat should be closed based on resolution classification.
        Only close if high confidence resolution.
        """
        return (
            classification.decision == "RESOLVED" and 
            classification.confidence >= self.resolution_threshold
        )
    
    def should_escalate(self, classification: ClassificationResult) -> bool:
        """
        Decide if chat should be escalated to human based on classification.
        Escalate if confidence meets threshold.
        """
        return (
            classification.decision == "NEEDS_HUMAN" and 
            classification.confidence >= self.escalation_threshold
        )


# Global singleton instance
llm_classifier = LLMClassifier()


def classify_resolution(message: str, history: List[Dict]) -> ClassificationResult:
    """Convenience function for resolution classification"""
    return llm_classifier.classify_resolution(message, history)


def classify_escalation(message: str, history: List[Dict]) -> ClassificationResult:
    """Convenience function for escalation classification"""
    return llm_classifier.classify_escalation_need(message, history)


def classify_intent(message: str, history: List[Dict]) -> ClassificationResult:
    """Convenience function for intent classification"""
    return llm_classifier.classify_intent(message, history)


def classify_sentiment(message: str) -> ClassificationResult:
    """Convenience function for sentiment classification"""
    return llm_classifier.classify_sentiment(message)
