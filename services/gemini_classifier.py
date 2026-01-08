"""
Gemini-based LLM classification service for intent detection and decision making.

MAJOR UPGRADE from GPT-4o-mini:
- 1M token context window (vs 128K) = NO TRUNCATION NEEDED
- 65K max output tokens (vs 16K)
- 50% cheaper per token
- Faster responses (Flash model optimized for speed)
- Newer knowledge cutoff (January 2025)

This replaces the GPT-based llm_classifier.py for better context retention
and cost efficiency.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Literal
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Import OpenAI SDK for OpenRouter
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("openai not installed. Run: pip install openai")


@dataclass
class ClassificationResult:
    """Structured result from LLM classification"""
    decision: str  # Main classification result
    confidence: float  # 0-100
    reasoning: str  # Why this decision was made
    raw_response: str  # Full LLM response for debugging


class GeminiClassifier:
    """
    Uses Gemini 2.5 Flash to make intelligent decisions about user intent and conversation state.
    
    KEY ADVANTAGES OVER GPT-4o-mini:
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    │ Feature          │ GPT-4o-mini │ Gemini Flash │
    ├──────────────────┼─────────────┼──────────────┤
    │ Context Window   │ 128K tokens │ 1M tokens    │
    │ Max Output       │ 16K tokens  │ 65K tokens   │
    │ Truncation Needed│ YES         │ NO           │
    │ Cost per token   │ Higher      │ 50% cheaper  │
    │ Speed            │ Fast        │ Faster       │
    │ Knowledge        │ Oct 2023    │ Jan 2025     │
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    TRUNCATION REMOVED: With 1M context, we can keep FULL conversation history!
    """
    
    def __init__(self):
        if not OPENAI_AVAILABLE:
            raise ImportError("openai package not installed")
        
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY not set in environment variables")
        
        # Configure OpenRouter with OpenAI SDK
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        
        # Use Gemini 2.5 Flash Lite via OpenRouter (cheaper than Flash)
        self.model_name = "google/gemini-2.5-flash-lite"
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # GEMINI ADVANTAGES: These limits are now HUGE!
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        self.max_context_tokens = 1_000_000  # 1M tokens - 8x more than GPT!
        self.max_messages_for_context = None  # NO LIMIT - keep ALL messages
        self.max_output_tokens = 65_000  # 4x more than GPT!
        
        # Token budget per conversation (still reasonable for cost control)
        # With cheaper Gemini, we can afford higher limits
        self.max_tokens_per_conversation = int(os.getenv("LLM_MAX_TOKENS_PER_CHAT", "100000"))
        
        # Configurable confidence thresholds (same as before)
        self.resolution_threshold = float(os.getenv("LLM_RESOLUTION_CONFIDENCE", "85"))
        self.escalation_threshold = float(os.getenv("LLM_ESCALATION_CONFIDENCE", "70"))
        self.intent_threshold = float(os.getenv("LLM_INTENT_CONFIDENCE", "75"))
        
        # Hallucination prevention: Require minimum confidence
        self.min_confidence_for_action = float(os.getenv("LLM_MIN_CONFIDENCE", "60"))
        
        # Track token usage per session
        self.session_token_usage: Dict[str, int] = {}
        
        logger.info("=" * 60)
        logger.info("🚀 GEMINI CLASSIFIER INITIALIZED (via OpenRouter)")
        logger.info("=" * 60)
        logger.info(f"  Model: {self.model_name}")
        logger.info(f"  Base URL: https://openrouter.ai/api/v1")
        logger.info(f"  Context Window: 1,000,000 tokens (NO TRUNCATION!)")
        logger.info(f"  Max Output: 65,000 tokens")
        logger.info(f"  Max per Conversation: {self.max_tokens_per_conversation:,} tokens")
        logger.info(f"  Thresholds: resolution={self.resolution_threshold}%, escalation={self.escalation_threshold}%")
        logger.info(f"  Min Confidence: {self.min_confidence_for_action}%")
        logger.info("=" * 60)
    
    def _track_token_usage(self, session_id: str, tokens: int) -> bool:
        """Track token usage per session - now with higher limits!"""
        if session_id not in self.session_token_usage:
            self.session_token_usage[session_id] = 0
        
        self.session_token_usage[session_id] += tokens
        
        if self.session_token_usage[session_id] > self.max_tokens_per_conversation:
            logger.warning(f"[Token Limit] Session {session_id} exceeded {self.max_tokens_per_conversation:,} tokens")
            return False
        
        return True
    
    def _build_context(self, conversation_history: List[Dict], last_n: int = None) -> str:
        """
        Build context from conversation history.
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        🎉 GEMINI CHANGE: NO MORE TRUNCATION!
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        With 1M token context, we include ALL messages.
        This means:
        - Bot remembers ENTIRE conversation
        - No more "You mentioned earlier..." getting lost
        - Better continuity for complex troubleshooting
        - Higher resolution rates
        """
        if not conversation_history:
            return "(No previous messages)"
        
        # With Gemini's 1M context, use ALL messages if last_n is None
        if last_n is None:
            recent = conversation_history
            logger.debug(f"[Gemini] Using FULL history: {len(conversation_history)} messages (no truncation)")
        else:
            recent = conversation_history[-last_n:] if len(conversation_history) > last_n else conversation_history
        
        context_lines = []
        for msg in recent:
            role = "User" if msg.get("role") == "user" else "Bot"
            # Don't truncate individual messages either - Gemini can handle it!
            content = msg.get("content", "")
            context_lines.append(f"{role}: {content}")
        
        return "\n".join(context_lines)
    
    def _validate_confidence(self, confidence: float, decision: str, classification_type: str) -> bool:
        """Validate confidence to prevent hallucination-driven actions."""
        if confidence < self.min_confidence_for_action:
            logger.warning(f"[Hallucination Check] {classification_type} confidence too low: {confidence}% - Decision: {decision} - IGNORING")
            return False
        return True
    
    def _call_gemini(self, prompt: str, session_id: str = "unknown", max_tokens: int = 1000) -> str:
        """
        Make Gemini API call with structured prompts.
        
        Gemini advantages:
        - Native JSON mode with response_mime_type
        - Faster response times
        - Lower cost per token
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that responds in JSON format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Low for consistent classification
                max_tokens=max_tokens,
                response_format={"type": "json_object"}  # Force JSON output
            )
            
            # Track token usage from OpenRouter
            usage = response.usage
            if usage:
                input_tokens = usage.prompt_tokens
                output_tokens = usage.completion_tokens
                self._track_token_usage(session_id, input_tokens + output_tokens)
                logger.debug(f"[OpenRouter-Gemini] Tokens: {input_tokens} in, {output_tokens} out, Session total: {self.session_token_usage.get(session_id, 0):,}")
            
            response_text = response.choices[0].message.content.strip()
            return response_text
            
        except Exception as e:
            logger.error(f"[OpenRouter-Gemini] API call failed: {e}")
            raise
    
    def classify_unified(self, message: str, conversation_history: List[Dict], 
                        session_id: str = "unknown") -> Dict[str, ClassificationResult]:
        """
        Single Gemini call for all classifications: resolution, escalation, intent.
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        🎯 KEY IMPROVEMENT: Uses FULL conversation history!
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        With 1M context:
        - No truncation needed
        - Bot remembers everything
        - Better classification accuracy
        - Higher resolution rates
        
        Returns:
            {
                "resolution": ClassificationResult,
                "escalation": ClassificationResult,
                "intent": ClassificationResult
            }
        """
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Include ALL conversation history - no truncation!
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        context = self._build_context(conversation_history, last_n=None)
        
        prompt = f"""You are a conversation analyzer for Ace Cloud Hosting support chatbot. 

Analyze the user's message for these 3 aspects:

1. RESOLUTION: Is the user's issue resolved?
   - RESOLVED: User explicitly confirms issue is fixed AND expresses satisfaction
   - UNRESOLVED: User says issue persists, isn't working, or asks for more help
   - UNCERTAIN: Ambiguous response or acknowledgment without confirmation

2. ESCALATION: Does user need human agent?
   - NEEDS_HUMAN: User requests agent, is frustrated, or issue is too complex
   - BOT_CAN_HANDLE: Bot can continue helping
   - UNCERTAIN: Not clear yet

3. INTENT: What does user want?
   - TRANSFER: Instant chat with human agent NOW
   - CALLBACK: Schedule callback for later
   - TICKET: Create email-based support ticket
   - QUESTION: Asking informational question
   - OTHER: Unclear or doesn't fit categories

CRITICAL RULES:
- Detect negations: "not fixed", "not working", "still broken" = UNRESOLVED
- Consider FULL conversation history for context
- Reference earlier messages if relevant
- Don't ask questions already answered in history

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FULL CONVERSATION HISTORY (COMPLETE - NO TRUNCATION):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{context}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LATEST USER MESSAGE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"{message}"

Respond with valid JSON only:
{{
  "resolution": {{"decision": "RESOLVED|UNRESOLVED|UNCERTAIN", "confidence": 0-100, "reasoning": "brief"}},
  "escalation": {{"decision": "NEEDS_HUMAN|BOT_CAN_HANDLE|UNCERTAIN", "confidence": 0-100, "reasoning": "brief"}},
  "intent": {{"decision": "TRANSFER|CALLBACK|TICKET|QUESTION|OTHER", "confidence": 0-100, "reasoning": "brief"}}
}}"""

        try:
            raw_response = self._call_gemini(prompt, session_id, max_tokens=500)
            logger.debug(f"[Gemini] Unified raw response: {raw_response}")
            
            # Parse JSON response
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
            
            # Hallucination detection
            if not self._validate_confidence(resolution_conf, results['resolution'].decision, "Resolution"):
                results['resolution'] = ClassificationResult("UNCERTAIN", resolution_conf, "Low confidence", raw_response)
            
            if not self._validate_confidence(escalation_conf, results['escalation'].decision, "Escalation"):
                results['escalation'] = ClassificationResult("UNCERTAIN", escalation_conf, "Low confidence", raw_response)
            
            logger.info(f"[Gemini] UNIFIED - Resolution: {results['resolution'].decision} ({results['resolution'].confidence}%), "
                       f"Escalation: {results['escalation'].decision} ({results['escalation'].confidence}%), "
                       f"Intent: {results['intent'].decision} ({results['intent'].confidence}%)")
            
            return results
            
        except json.JSONDecodeError as e:
            logger.error(f"[Gemini] JSON parse error: {raw_response} - {e}")
            return {
                "resolution": ClassificationResult("UNCERTAIN", 0, "JSON parse error", raw_response),
                "escalation": ClassificationResult("UNCERTAIN", 0, "JSON parse error", raw_response),
                "intent": ClassificationResult("OTHER", 0, "JSON parse error", raw_response)
            }
        except Exception as e:
            logger.error(f"[Gemini] Classification failed: {e}")
            return {
                "resolution": ClassificationResult("UNCERTAIN", 0, f"Error: {str(e)}", ""),
                "escalation": ClassificationResult("UNCERTAIN", 0, f"Error: {str(e)}", ""),
                "intent": ClassificationResult("OTHER", 0, f"Error: {str(e)}", "")
            }
    
    def classify_resolution(self, message: str, conversation_history: List[Dict], 
                           session_id: str = "unknown") -> ClassificationResult:
        """Determine if user's issue is resolved using unified classification."""
        results = self.classify_unified(message, conversation_history, session_id)
        return results["resolution"]
    
    def classify_escalation_need(self, message: str, conversation_history: List[Dict],
                                 session_id: str = "unknown") -> ClassificationResult:
        """Determine if user needs human agent using unified classification."""
        results = self.classify_unified(message, conversation_history, session_id)
        return results["escalation"]
    
    def classify_intent(self, message: str, conversation_history: List[Dict],
                       session_id: str = "unknown") -> ClassificationResult:
        """Classify user's primary intent using unified classification."""
        results = self.classify_unified(message, conversation_history, session_id)
        return results["intent"]
    
    def classify_sentiment(self, message: str, session_id: str = "unknown") -> ClassificationResult:
        """Analyze user's emotional state/sentiment."""
        prompt = f"""You are a sentiment analyzer. Classify the user's emotional state.

Sentiment Types:
- SATISFIED: Happy, grateful, content, issue resolved
- FRUSTRATED: Annoyed, impatient, repeating issue
- ANGRY: Very upset, threatening, using profanity
- NEUTRAL: Calm, informational, no strong emotion

User Message: "{message}"

Respond with valid JSON only:
{{
  "decision": "SATISFIED|FRUSTRATED|ANGRY|NEUTRAL",
  "confidence": 0-100,
  "reasoning": "brief explanation"
}}"""

        try:
            raw_response = self._call_gemini(prompt, session_id, max_tokens=200)
            parsed = json.loads(raw_response)
            
            result = ClassificationResult(
                decision=parsed.get("decision", "NEUTRAL"),
                confidence=float(parsed.get("confidence", 0)),
                reasoning=parsed.get("reasoning", ""),
                raw_response=raw_response
            )
            
            logger.info(f"[Gemini] Sentiment: {result.decision} ({result.confidence}%)")
            return result
            
        except Exception as e:
            logger.error(f"[Gemini] Sentiment classification failed: {e}")
            return ClassificationResult("NEUTRAL", 0, f"Error: {str(e)}", "")
    
    def should_close_chat(self, classification: ClassificationResult) -> bool:
        """Decide if chat should be closed based on resolution classification."""
        return (
            classification.decision == "RESOLVED" and 
            classification.confidence >= self.resolution_threshold
        )
    
    def should_escalate(self, classification: ClassificationResult) -> bool:
        """Decide if chat should be escalated to human based on classification."""
        return (
            classification.decision == "NEEDS_HUMAN" and 
            classification.confidence >= self.escalation_threshold
        )
    
    def clear_session_tokens(self, session_id: str):
        """Clear token usage tracking for a session."""
        if session_id in self.session_token_usage:
            del self.session_token_usage[session_id]
            logger.debug(f"[Gemini] Cleared token tracking for session {session_id}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# GLOBAL SINGLETON - Replace the old llm_classifier
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Try to initialize Gemini, fall back to message if not available
try:
    gemini_classifier = GeminiClassifier()
    llm_classifier = gemini_classifier  # Alias for backward compatibility
    logger.info("✅ Gemini Classifier is ACTIVE via OpenRouter (replacing GPT-4o-mini)")
except Exception as e:
    logger.error(f"❌ Failed to initialize Gemini Classifier: {e}")
    gemini_classifier = None
    llm_classifier = None


# Convenience functions (backward compatible)
def classify_resolution(message: str, history: List[Dict], session_id: str = "unknown") -> ClassificationResult:
    """Convenience function for resolution classification"""
    if gemini_classifier:
        return gemini_classifier.classify_resolution(message, history, session_id)
    return ClassificationResult("UNCERTAIN", 0, "Classifier not available", "")


def classify_escalation(message: str, history: List[Dict], session_id: str = "unknown") -> ClassificationResult:
    """Convenience function for escalation classification"""
    if gemini_classifier:
        return gemini_classifier.classify_escalation_need(message, history, session_id)
    return ClassificationResult("UNCERTAIN", 0, "Classifier not available", "")


def classify_intent(message: str, history: List[Dict], session_id: str = "unknown") -> ClassificationResult:
    """Convenience function for intent classification"""
    if gemini_classifier:
        return gemini_classifier.classify_intent(message, history, session_id)
    return ClassificationResult("OTHER", 0, "Classifier not available", "")


def classify_sentiment(message: str, session_id: str = "unknown") -> ClassificationResult:
    """Convenience function for sentiment classification"""
    if gemini_classifier:
        return gemini_classifier.classify_sentiment(message, session_id)
    return ClassificationResult("NEUTRAL", 0, "Classifier not available", "")
