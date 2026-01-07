"""
Gemini-based response generator for Ace Cloud Hosting chatbot.

Replaces OpenAI GPT-4o-mini with Gemini 2.5 Flash for:
- Response generation
- Troubleshooting conversations
- Knowledge-based answers

ADVANTAGES:
- 1M token context = NO truncation of conversation history
- 65K max output = Can generate longer, more detailed responses
- 50% cheaper = Lower operational costs
- Faster = Better user experience
- Newer knowledge (Jan 2025) = Better troubleshooting for recent issues
"""

import os
import logging
from typing import List, Dict, Tuple, Optional

logger = logging.getLogger(__name__)

# Import Gemini SDK
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("google-generativeai not installed. Run: pip install google-generativeai")


class GeminiResponseGenerator:
    """
    Generates responses using Gemini 2.5 Flash.
    
    IMPROVEMENTS OVER GPT-4o-mini:
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    │ Feature              │ Before   │ After   │
    ├──────────────────────┼──────────┼─────────┤
    │ Context Window       │ 128K     │ 1M      │
    │ Conversation History │ Truncated│ FULL    │
    │ Response Length      │ 400 tok  │ 1000 tok│
    │ Cost                 │ Higher   │ 50% less│
    │ Speed                │ 2-3s     │ 1-2s    │
    │ Knowledge Cutoff     │ Oct 2023 │ Jan 2025│
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """
    
    def __init__(self):
        if not GEMINI_AVAILABLE:
            raise ImportError("google-generativeai package not installed")
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not set in environment variables")
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Use Gemini 2.5 Flash for speed + cost efficiency
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self.model = genai.GenerativeModel(self.model_name)
        
        # Generation settings - can be higher with Gemini!
        self.default_temperature = float(os.getenv("GEMINI_TEMPERATURE", "0.7"))
        self.default_max_tokens = int(os.getenv("GEMINI_MAX_TOKENS", "1000"))  # Was 400!
        
        # Safety settings (optional)
        self.safety_settings = {
            "HARASSMENT": "BLOCK_NONE",
            "HATE_SPEECH": "BLOCK_NONE",
            "SEXUALLY_EXPLICIT": "BLOCK_NONE",
            "DANGEROUS_CONTENT": "BLOCK_NONE",
        }
        
        logger.info("=" * 60)
        logger.info("🚀 GEMINI RESPONSE GENERATOR INITIALIZED")
        logger.info("=" * 60)
        logger.info(f"  Model: {self.model_name}")
        logger.info(f"  Temperature: {self.default_temperature}")
        logger.info(f"  Max Tokens: {self.default_max_tokens}")
        logger.info(f"  Context: 1,000,000 tokens (NO TRUNCATION!)")
        logger.info("=" * 60)
    
    def generate_response(self, 
                         message: str, 
                         history: List[Dict], 
                         system_prompt: str,
                         category: str = "other",
                         temperature: float = None,
                         max_tokens: int = None) -> Tuple[str, int]:
        """
        Generate a response using Gemini.
        
        Args:
            message: User's current message
            history: FULL conversation history (no truncation needed!)
            system_prompt: Expert prompt with instructions
            category: Issue category for hints
            temperature: Override default temperature
            max_tokens: Override default max tokens
        
        Returns:
            Tuple of (response_text, tokens_used)
        """
        temp = temperature if temperature is not None else self.default_temperature
        max_tok = max_tokens if max_tokens is not None else self.default_max_tokens
        
        # Add category hint if applicable
        category_hints = {
            "login": "Focus on RDP connection, login issues, password resets, and SelfCare portal guidance.",
            "quickbooks": "Focus on QuickBooks errors, company file issues, freezing/hanging, and QB-specific troubleshooting.",
            "performance": "Focus on server performance, disk space, RAM/CPU usage, and system slowness.",
            "printing": "Focus on printer redirection, printing issues, and RDP printer settings.",
            "office": "Focus on Microsoft Office applications, Outlook, Excel, and Office 365 activation."
        }
        
        enhanced_prompt = system_prompt
        if category != "other" and category in category_hints:
            enhanced_prompt = f"{system_prompt}\n\n[CATEGORY: {category.upper()}] {category_hints[category]}"
            logger.info(f"[Gemini] Added category hint for: {category}")
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Build conversation - Include FULL history (no truncation!)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        # Build conversation context
        conversation_text = f"SYSTEM INSTRUCTIONS:\n{enhanced_prompt}\n\n"
        conversation_text += "CONVERSATION HISTORY (COMPLETE):\n"
        conversation_text += "=" * 50 + "\n"
        
        for msg in history:
            role = "USER" if msg.get("role") == "user" else "ASSISTANT"
            content = msg.get("content", "")
            conversation_text += f"{role}: {content}\n\n"
        
        conversation_text += "=" * 50 + "\n"
        conversation_text += f"CURRENT USER MESSAGE:\n{message}\n\n"
        conversation_text += "YOUR RESPONSE:"
        
        try:
            response = self.model.generate_content(
                conversation_text,
                generation_config={
                    "temperature": temp,
                    "max_output_tokens": max_tok,
                }
            )
            
            # Extract response text
            response_text = response.text.strip() if response.text else ""
            
            # Estimate token usage (Gemini doesn't always return exact counts)
            # Rough estimate: 1 token ≈ 4 characters
            input_tokens = len(conversation_text) // 4
            output_tokens = len(response_text) // 4
            total_tokens = input_tokens + output_tokens
            
            logger.info(f"[Gemini] Response generated: {len(response_text)} chars, ~{total_tokens} tokens")
            logger.debug(f"[Gemini] Token breakdown: ~{input_tokens} input, ~{output_tokens} output")
            
            return response_text, total_tokens
            
        except Exception as e:
            logger.error(f"[Gemini] Response generation failed: {e}")
            
            # Fallback response
            fallback = (
                "I apologize, but I'm having trouble processing your request right now. "
                "Please try again, or contact our support team directly:\n\n"
                "📞 Phone: 1-888-415-5240 (24/7)\n"
                "📧 Email: support@acecloudhosting.com"
            )
            return fallback, 0
    
    def generate_quick_response(self, prompt: str, max_tokens: int = 500) -> str:
        """
        Generate a quick response for simple prompts.
        Used for one-off generations without conversation context.
        """
        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.5,
                    "max_output_tokens": max_tokens,
                }
            )
            return response.text.strip() if response.text else ""
        except Exception as e:
            logger.error(f"[Gemini] Quick response failed: {e}")
            return ""


# Global singleton
try:
    gemini_generator = GeminiResponseGenerator()
    logger.info("✅ Gemini Response Generator is ACTIVE")
except Exception as e:
    logger.error(f"❌ Failed to initialize Gemini Response Generator: {e}")
    gemini_generator = None
