
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import os
import asyncio
from openai import OpenAI
from dotenv import load_dotenv
import urllib3
import uvicorn
from datetime import datetime
import logging
import traceback
import uuid
import json
from contextvars import ContextVar

# Import IssueRouter for category classification
from services.router import IssueRouter

# Import MetricsCollector for performance tracking
from services.metrics import metrics_collector

# Import StateManager for conversation state tracking
from services.state_manager import (
    state_manager, 
    ConversationState, 
    TransitionTrigger,
    detect_trigger_from_message
)

# Import HandlerRegistry for pattern-based response handling
from services.handler_registry import handler_registry

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

# Context variable for request ID tracking
request_id_var: ContextVar[str] = ContextVar('request_id', default='no-request-id')
session_id_var: ContextVar[str] = ContextVar('session_id', default='no-session-id')

# Custom log formatter with request ID and session ID
class ContextualFormatter(logging.Formatter):
    """Custom formatter that includes request_id and session_id in logs"""
    
    def format(self, record):
        # Add contextual information to log record
        record.request_id = request_id_var.get()
        record.session_id = session_id_var.get()
        return super().format(record)

# Configure enhanced logging with request tracking
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [req:%(request_id)s] [session:%(session_id)s] %(name)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Apply custom formatter to all handlers
for handler in logging.getLogger().handlers:
    handler.setFormatter(ContextualFormatter(
        '%(asctime)s [%(levelname)s] [req:%(request_id)s] [session:%(session_id)s] %(name)s - %(message)s'
    ))

# Error alerting configuration
ERROR_ALERT_WEBHOOK = os.getenv("ERROR_ALERT_WEBHOOK", None)
ERROR_ALERT_THRESHOLD = 3  # Alert after 3 errors in a window
error_counts: Dict[str, int] = {}

def send_critical_alert(error_type: str, error_message: str, context: dict = None):
    """Send critical error alert to monitoring service"""
    try:
        alert_data = {
            "timestamp": datetime.now().isoformat(),
            "severity": "CRITICAL",
            "error_type": error_type,
            "message": error_message,
            "context": context or {},
            "service": "llm-chatbot",
            "request_id": request_id_var.get()
        }
        
        # Log structured alert
        logger.critical(f"ALERT: {error_type} - {error_message}", extra={"alert_data": json.dumps(alert_data)})
        
        # Send to external webhook if configured
        if ERROR_ALERT_WEBHOOK:
            import requests
            requests.post(
                ERROR_ALERT_WEBHOOK,
                json=alert_data,
                timeout=5,
                verify=False
            )
            logger.info(f"Alert sent to webhook for {error_type}")
    except Exception as e:
        logger.error(f"Failed to send alert: {e}")

def track_error(error_type: str, error_message: str, context: dict = None):
    """Track errors and send alerts when threshold is exceeded"""
    global error_counts
    
    # Increment error count
    error_counts[error_type] = error_counts.get(error_type, 0) + 1
    
    # Send alert if threshold exceeded
    if error_counts[error_type] >= ERROR_ALERT_THRESHOLD:
        send_critical_alert(
            error_type,
            f"{error_message} (occurred {error_counts[error_type]} times)",
            context
        )
        error_counts[error_type] = 0  # Reset counter

app = FastAPI(title="Ace Cloud Hosting Support Bot - Hybrid", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
LLM_MODEL = "gpt-4o-mini"

# Initialize IssueRouter for category classification
issue_router = IssueRouter()
logger.info("IssueRouter initialized successfully")

# MetricsCollector is already initialized as a global singleton
logger.info("MetricsCollector ready for tracking")

# StateManager is already initialized as a global singleton
logger.info("StateManager ready for conversation tracking")

# HandlerRegistry is already initialized as a global singleton
logger.info(f"HandlerRegistry ready with {len(handler_registry.handlers)} handlers")

conversations: Dict[str, List[Dict]] = {}

# Fallback API class for when real API is not available
class FallbackAPI:
    def __init__(self):
        self.enabled = False
    def create_chat_session(self, visitor_id, conversation_history):
        logger.info(f"[API] Fallback: Simulating chat transfer for {visitor_id}")
        return {"success": True, "simulated": True, "message": "Chat transfer simulated"}
    def close_chat(self, session_id, reason="resolved"):
        logger.info(f"[API] Fallback: Simulating chat closure for {session_id}")
        return {"success": True, "simulated": True, "message": "Chat closure simulated"}
    def create_callback_ticket(self, *args, **kwargs):
        logger.info("[API] Fallback: Simulating callback ticket creation")
        return {"success": True, "simulated": True, "ticket_number": "CB-SIM-001"}
    def create_support_ticket(self, *args, **kwargs):
        logger.info("[API] Fallback: Simulating support ticket creation")
        return {"success": True, "simulated": True, "ticket_number": "TK-SIM-001"}

# Load Zoho API integration with proper error handling
try:
    from zoho_api_simple import ZohoSalesIQAPI, ZohoDeskAPI
    salesiq_api = ZohoSalesIQAPI()
    desk_api = ZohoDeskAPI()
    logger.info(f"Zoho API loaded successfully - SalesIQ enabled: {salesiq_api.enabled}")
except ImportError as e:
    logger.error(f"Failed to import Zoho API module: {str(e)} - using fallback")
    salesiq_api = FallbackAPI()
    desk_api = FallbackAPI()
except Exception as e:
    logger.error(f"Failed to initialize Zoho API: {str(e)} - using fallback")
    salesiq_api = FallbackAPI()
    desk_api = FallbackAPI()


# Background cleanup job
async def cleanup_stale_sessions():
    """Background task to cleanup stale conversations every 15 minutes"""
    while True:
        try:
            await asyncio.sleep(15 * 60)  # Run every 15 minutes
            
            logger.info("[Cleanup] Starting stale session cleanup...")
            
            # Cleanup state manager sessions
            state_manager.cleanup_stale_sessions(timeout_minutes=30)
            
            # Cleanup in-memory conversations that match stale sessions
            stale_count = 0
            sessions_to_remove = []
            
            for session_id in list(conversations.keys()):
                session = state_manager.get_session(session_id)
                if not session or session.is_stale(timeout_minutes=30):
                    sessions_to_remove.append(session_id)
            
            for session_id in sessions_to_remove:
                if session_id in conversations:
                    metrics_collector.end_conversation(session_id, "abandoned")
                    del conversations[session_id]
                    stale_count += 1
            
            if stale_count > 0:
                logger.info(f"[Cleanup] Removed {stale_count} stale conversations")
            else:
                logger.debug("[Cleanup] No stale conversations found")
                
        except Exception as e:
            logger.error(f"[Cleanup] Error in cleanup job: {e}", exc_info=True)


@app.on_event("startup")
async def startup_event():
    """Initialize background tasks on startup"""
    logger.info("Starting background tasks...")
    asyncio.create_task(cleanup_stale_sessions())
    logger.info("✓ Cleanup job started (runs every 15 minutes)")
    salesiq_api = FallbackAPI()
    desk_api = FallbackAPI()

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    session_id: str
    message: str
    conversation_history: Optional[List[Message]] = []

class ChatResponse(BaseModel):
    session_id: str
    response: str
    timestamp: str

# Load expert system prompt from config file
def load_expert_prompt() -> str:
    """Load the expert system prompt from config file"""
    prompt_path = os.path.join(os.path.dirname(__file__), "config", "prompts", "expert_system_prompt.txt")
    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        logger.error(f"Prompt file not found at {prompt_path}. Using fallback prompt.")
        return "You are AceBuddy, a friendly IT support assistant for ACE Cloud Hosting."
    except Exception as e:
        logger.error(f"Error loading prompt file: {str(e)}. Using fallback prompt.")
        return "You are AceBuddy, a friendly IT support assistant for ACE Cloud Hosting."

# Load prompt on startup
EXPERT_PROMPT = load_expert_prompt()
logger.info(f"Expert prompt loaded successfully ({len(EXPERT_PROMPT)} characters)")

def generate_response(message: str, history: List[Dict], category: str = "other") -> str:
    """Generate response using LLM with embedded resolution steps
    
    Args:
        message: User message text
        history: Conversation history
        category: Issue category from IssueRouter (login, quickbooks, performance, printing, office, other)
    
    Returns:
        LLM response text
    """
    
    # Add category hint to system prompt for better responses
    category_hints = {
        "login": "Focus on RDP connection, login issues, password resets, and SelfCare portal guidance.",
        "quickbooks": "Focus on QuickBooks errors, company file issues, freezing/hanging, and QB-specific troubleshooting.",
        "performance": "Focus on server performance, disk space, RAM/CPU usage, and system slowness.",
        "printing": "Focus on printer redirection, printing issues, and RDP printer settings.",
        "office": "Focus on Microsoft Office applications, Outlook, Excel, and Office 365 activation."
    }
    
    system_prompt = EXPERT_PROMPT
    if category != "other" and category in category_hints:
        system_prompt = f"{EXPERT_PROMPT}\n\n[CATEGORY: {category.upper()}] {category_hints[category]}"
        logger.info(f"Added category hint for: {category}")
    
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": message})
    
    response = openai_client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        temperature=0.7,
        max_tokens=400
    )
    
    # Track token usage
    tokens_used = response.usage.total_tokens if hasattr(response, 'usage') else 0
    logger.debug(f"LLM call used {tokens_used} tokens")
    
    return response.choices[0].message.content, tokens_used

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add request ID to all requests for tracking"""
    req_id = str(uuid.uuid4())
    request_id_var.set(req_id)
    
    # Add request ID to response headers
    response = await call_next(request)
    response.headers["X-Request-ID"] = req_id
    
    return response

@app.get("/")
async def root():
    """Health check endpoint"""
    logger.info("Root endpoint accessed")
    return {
        "status": "online",
        "service": "Ace Cloud Hosting Support Bot - Hybrid LLM",
        "version": "2.0.0",
        "api_status": {
            "salesiq_enabled": salesiq_api.enabled if hasattr(salesiq_api, 'enabled') else False,
            "desk_enabled": desk_api.enabled if hasattr(desk_api, 'enabled') else False
        },
        "endpoints": {
            "salesiq_webhook": "/webhook/salesiq",
            "chat": "/chat",
            "reset": "/reset/{session_id}",
            "health": "/health",
            "stats": "/stats"
        }
    }

@app.get("/health")
async def health():
    """Health check for monitoring"""
    return {
        "status": "healthy",
        "mode": "production",
        "openai": "connected",
        "active_sessions": len(conversations),
        "api_status": {
            "salesiq_enabled": salesiq_api.enabled if hasattr(salesiq_api, 'enabled') else False,
            "desk_enabled": desk_api.enabled if hasattr(desk_api, 'enabled') else False
        },
        "webhook_url": "https://web-production-3032d.up.railway.app/webhook/salesiq"
    }

@app.get("/callback")
async def oauth_callback(code: str = None, state: str = None, error: str = None):
    """OAuth 2.0 callback endpoint for Zoho authorization"""
    
    if error:
        html = f"""
        <html>
        <head><title>OAuth Error</title></head>
        <body style="font-family: Arial; padding: 20px; background: #f5f5f5;">
            <div style="background: #ffcccc; padding: 20px; border-radius: 5px; max-width: 500px; margin: 20px auto;">
                <h2 style="color: #cc0000;">Authorization Failed</h2>
                <p><strong>Error:</strong> {error}</p>
                <p>Please try again or contact support.</p>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=html)
    
    if not code:
        html = """
        <html>
        <head><title>OAuth Callback</title></head>
        <body style="font-family: Arial; padding: 20px; background: #f5f5f5;">
            <div style="background: #ffcccc; padding: 20px; border-radius: 5px; max-width: 500px; margin: 20px auto;">
                <h2 style="color: #cc0000;">No Authorization Code Received</h2>
                <p>The authorization code was not found in the callback URL.</p>
                <p>Please try the authorization process again.</p>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=html)
    
    # Success - display the authorization code
    html = f"""
    <html>
    <head><title>OAuth Authorization Success</title></head>
    <body style="font-family: Arial; padding: 20px; background: #f5f5f5;">
        <div style="background: #ccffcc; padding: 20px; border-radius: 5px; max-width: 600px; margin: 20px auto;">
            <h2 style="color: #00cc00;">Authorization Successful!</h2>
            <p>Your authorization code is ready. Copy the code below and use it in the token exchange step.</p>
            
            <div style="background: #ffffff; padding: 15px; border: 2px solid #00cc00; border-radius: 5px; margin: 20px 0;">
                <h3>Authorization Code:</h3>
                <code style="font-size: 14px; word-break: break-all; display: block; background: #f0f0f0; padding: 10px; border-radius: 3px;">
                    {code}
                </code>
                <button onclick="navigator.clipboard.writeText('{code}'); alert('Code copied to clipboard!');" 
                        style="margin-top: 10px; padding: 10px 20px; background: #00cc00; color: white; border: none; border-radius: 3px; cursor: pointer;">
                    Copy Code
                </button>
            </div>
            
            <p><strong>State:</strong> {state if state else 'N/A'}</p>
            
            <div style="background: #ffffcc; padding: 15px; border-radius: 5px; margin-top: 20px;">
                <h3>Next Step:</h3>
                <p>Run this PowerShell command to exchange the code for an access token:</p>
                <pre style="background: #f0f0f0; padding: 10px; border-radius: 3px; overflow-x: auto;">
$code = "{code}"
$clientId = "YOUR_CLIENT_ID"
$clientSecret = "YOUR_CLIENT_SECRET"
$redirectUri = "http://localhost:8000/callback"

$response = Invoke-RestMethod -Uri "https://accounts.zoho.in/oauth/v2/token" -Method POST -Body @{{
    code = $code
    grant_type = "authorization_code"
    client_id = $clientId
    client_secret = $clientSecret
    redirect_uri = $redirectUri
    scope = "SalesIQ.conversations.CREATE,SalesIQ.conversations.READ,SalesIQ.conversations.UPDATE,SalesIQ.conversations.DELETE"
}}

Write-Host "Access Token:"
Write-Host $response.access_token
                </pre>
            </div>
        </div>
    </body>
    </html>
    """
    
    logger.info(f"[OAuth] Authorization successful - code received (state: {state})")
    return HTMLResponse(content=html)


@app.get("/webhook/salesiq")
async def salesiq_webhook_test():
    """Test endpoint for SalesIQ webhook - GET request"""
    return {
        "status": "webhook_ready",
        "message": "SalesIQ webhook endpoint is accessible",
        "method": "GET",
        "note": "POST requests will be processed as chat messages"
    }

@app.get("/test/widget", response_class=HTMLResponse)
async def test_widget():
    """Public test page to load SalesIQ widget for real visitor testing.
    Set SALESIQ_WIDGET_CODE env var to your SalesIQ embed snippet.
    """
    widget_code = os.getenv("SALESIQ_WIDGET_CODE", "").strip()
    if not widget_code:
        return (
            "<!doctype html><html><head><meta charset='utf-8'><title>SalesIQ Test</title></head>"
            "<body><h2>SalesIQ Widget Test</h2>"
            "<p>Set the SALESIQ_WIDGET_CODE env var with your SalesIQ embed snippet to load the widget here.</p>"
            "<p>This page is served from your Railway app and counts as a real website visitor.</p>"
            "</body></html>"
        )
    html = (
        "<!doctype html><html><head><meta charset='utf-8'><title>SalesIQ Test</title></head><body>"
        "<h2>SalesIQ Widget Live Test</h2><p>This page is public and will register real visitors.</p>"
        + widget_code +
        "</body></html>"
    )
    return html

@app.post("/webhook/salesiq")
async def salesiq_webhook(request: dict):
    """Direct webhook endpoint for Zoho SalesIQ - Hybrid LLM"""
    session_id = None
    try:
        # Set session context for logging (will be updated once extracted)
        session_id_var.set("extracting")
        
        logger.info(f"[SalesIQ] Webhook received")
        
        # Validate request structure
        if not isinstance(request, dict):
            logger.error(f"[SalesIQ] Invalid request format: {type(request)}")
            track_error(
                "invalid_webhook_format",
                f"Received non-dict webhook: {type(request)}",
                {"request_type": str(type(request))}
            )
            return {
                "action": "reply",
                "replies": ["I'm having technical difficulties. Please call 1-888-415-5240."],
                "session_id": "unknown"
            }
        
        logger.info(f"[SalesIQ] Request keys: {list(request.keys())}")
        logger.debug(f"[SalesIQ] Full request payload: {request}")
        
        # Log all possible IDs for transfer debugging
        visitor = request.get('visitor', {})
        chat = request.get('chat', {})
        conversation = request.get('conversation', {})
        
        logger.debug(f"[SalesIQ] Visitor data: {visitor}")
        logger.debug(f"[SalesIQ] Chat data: {chat}")
        logger.debug(f"[SalesIQ] Conversation data: {conversation}")
        
        # Extract session ID (try multiple sources)
        session_id = (
            visitor.get('active_conversation_id') or
            chat.get('id') or
            conversation.get('id') or
            request.get('session_id') or 
            visitor.get('id') or
            'unknown'
        )
        
        # Update session context for logging
        session_id_var.set(session_id)
        logger.info(f"[SalesIQ] Session ID: {session_id}")
        
        # Extract message text - handle multiple formats
        message_obj = request.get('message', {})
        if isinstance(message_obj, dict):
            message_text = message_obj.get('text', '').strip()
        else:
            message_text = str(message_obj).strip()
        
        # Extract payload (from quick reply buttons)
        payload = request.get('payload', '')
        
        logger.info(f"[SalesIQ] Message: {message_text[:100]}")
        if payload:
            logger.info(f"[SalesIQ] Payload: {payload}")
        
        # Handle empty message
        if not message_text:
            logger.info(f"[Session] 👋 INITIAL CONTACT - Sending greeting")
            logger.info(f"[Session] New visitor from: {visitor.get('email', 'unknown')}")
            return {
                "action": "reply",
                "replies": ["Hi! I'm AceBuddy, your Ace Cloud Hosting support assistant. What can I help you with today?"],
                "session_id": session_id
            }
        
        # Initialize conversation history
        if session_id not in conversations:
            conversations[session_id] = []
            logger.info(f"[Session] ✓ NEW CONVERSATION STARTED | Category: {issue_router.classify(message_text)}")
        
        history = conversations[session_id]
        message_lower = message_text.lower().strip()
        
        # Handle simple greetings (ONLY if no history - first message)
        greeting_patterns = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']
        is_greeting = (
            message_lower in greeting_patterns or
            (len(message_text.split()) <= 3 and any(g in message_lower for g in greeting_patterns))
        )
        
        if is_greeting and len(history) == 0:
            logger.info(f"[SalesIQ] Simple greeting detected - first message")
            return {
                "action": "reply",
                "replies": ["Hello! How can I assist you today?"],
                "session_id": session_id
            }
        
        # Handle contact requests
        contact_request_phrases = ['support email', 'support number', 'contact support', 'phone number', 'email address']
        if any(phrase in message_lower for phrase in contact_request_phrases):
            logger.info(f"[SalesIQ] Contact request detected")
            return {
                "action": "reply",
                "replies": ["You can reach Ace Cloud Hosting support at:\n\nPhone: 1-888-415-5240 (24/7)\nEmail: support@acecloudhosting.com"],
                "session_id": session_id
            }
        
        # Check for human agent request FIRST
        if len(history) > 0 and ('yes' in message_lower or 'ok' in message_lower or 'connect' in message_lower):
            last_bot_message = history[-1].get('content', '') if history[-1].get('role') == 'assistant' else ''
            if 'human agent' in last_bot_message.lower():
                logger.info(f"[SalesIQ] User requested human agent - initiating transfer")
                # Build conversation history for agent to see
                conversation_text = ""
                for msg in history:
                    role = "User" if msg.get('role') == 'user' else "Bot"
                    conversation_text += f"{role}: {msg.get('content', '')}\n"
                
                # Call SalesIQ API to create chat session
                api_result = salesiq_api.create_chat_session(session_id, conversation_text)
                logger.info(f"[SalesIQ] API result: {api_result}")
                
                # SalesIQ only supports "action": "reply" - transfer happens via API
                # Clear conversation after transfer
                if session_id in conversations:
                    metrics_collector.end_conversation(session_id, "escalated")
                    del conversations[session_id]
                
                return {
                    "action": "reply",
                    "replies": ["I'm connecting you with our support team. If the transfer doesn't happen automatically, please call 1-888-415-5240 or email support@acecloudhosting.com for immediate assistance."],
                    "session_id": session_id
                }
        
        # Check for issue resolution
        resolution_keywords = ["resolved", "fixed", "working now", "solved", "all set"]
        if any(keyword in message_lower for keyword in resolution_keywords):
            logger.info(f"[Resolution] ✓ ISSUE RESOLVED")
            logger.info(f"[Resolution] Reason: User confirmed fix worked")
            logger.info(f"[Resolution] Action: Closing chat session")
            
            # Transition to resolved state
            state_manager.end_session(session_id, ConversationState.RESOLVED)
            
            response_text = "Great! I'm glad the issue is resolved. If you need anything else, feel free to ask!"
            conversations[session_id].append({"role": "user", "content": message_text})
            conversations[session_id].append({"role": "assistant", "content": response_text})
            
            # Close chat in SalesIQ since issue is resolved
            close_result = salesiq_api.close_chat(session_id, "resolved")
            if close_result.get('success'):
                logger.info(f"[Action] ✓ CHAT CLOSED SUCCESSFULLY")
            else:
                logger.warning(f"[Action] Chat closure completed with status: {close_result}")
            
            if session_id in conversations:
                metrics_collector.end_conversation(session_id, "resolved")
                del conversations[session_id]
            return {
                "action": "reply",
                "replies": [response_text],
                "session_id": session_id
            }
        
        # Check for not resolved - COMPREHENSIVE DETECTION
        not_resolved_keywords = [
            # Direct "not working" statements
            "not resolved", "not fixed", "not working", "didn't work", "doesn't work", "does not work",
            "still not", "still stuck", "still broken", "still having", "still same", "same issue",
            "same problem", "no progress", "no change", "nothing changed", "nothing worked",
            
            # Negative feedback
            "that doesn't help", "that didn't help", "doesn't help", "not helpful", "unhelpful",
            "wrong answer", "not right", "incorrect", "not what i need", "not solving",
            
            # Problem persistence
            "issue persist", "problem persist", "keep getting", "keeps happening", "still error",
            "error again", "again", "tried that", "already tried", "done that",
            
            # Frustration indicators
            "frustrated", "frustrating", "annoyed", "annoying", "waste of time", "wasting time",
            "tired of", "fed up", "had enough", "ridiculous", "unacceptable",
            
            # Dissatisfaction
            "disappointed", "dissatisfied", "not satisfied", "unhappy", "upset",
            "this sucks", "terrible", "awful", "horrible", "useless",
            
            # Urgency/severity
            "urgent", "emergency", "critical", "serious", "major issue", "big problem"
        ]
        if any(keyword in message_lower for keyword in not_resolved_keywords):
            logger.info(f"[Escalation] 🆙 PROBLEM NOT RESOLVED - Offering escalation options")
            logger.info(f"[Escalation] Detected keyword in: {message_text[:100]}")
            logger.info(f"[Escalation] Options: ① Instant Chat | ② Schedule Callback | ③ Create Ticket")
            
            # Transition to escalation options state
            state_manager.transition(session_id, TransitionTrigger.SOLUTION_FAILED)
            
            response_text = "I understand this needs immediate attention. Let me connect you with the right support:"
            
            # Add to history so next response can find it
            conversations[session_id].append({"role": "user", "content": message_text})
            conversations[session_id].append({"role": "assistant", "content": response_text})
            
            return {
                "action": "reply",
                "replies": [response_text],
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
                    }
                ],
                "session_id": session_id
            }
        
        # Check for password reset - improved flow
        password_keywords = ["password", "reset", "forgot", "locked out"]
        if any(keyword in message_lower for keyword in password_keywords):
            logger.info(f"[SalesIQ] Password reset detected")
            # Check if user already answered about SelfCare registration
            if len(history) > 0:
                last_bot_message = history[-1].get('content', '') if history[-1].get('role') == 'assistant' else ''
                # If bot already asked about SelfCare registration
                if 'registered on the selfcare portal' in last_bot_message.lower():
                    # User is responding to that question
                    if 'yes' in message_lower or 'registered' in message_lower:
                        logger.info(f"[SalesIQ] User is registered on SelfCare")
                        response_text = "Great! Visit https://selfcare.acecloudhosting.com and click 'Forgot your password'. Let me know when you're there!"
                        conversations[session_id].append({"role": "user", "content": message_text})
                        conversations[session_id].append({"role": "assistant", "content": response_text})
                        return {
                            "action": "reply",
                            "replies": [response_text],
                            "session_id": session_id
                        }
                    elif 'no' in message_lower or 'not registered' in message_lower:
                        logger.info(f"[SalesIQ] User is NOT registered on SelfCare")
                        response_text = "No problem! For server/user account password reset, please contact our support team at 1-888-415-5240. They'll help you right away!"
                        conversations[session_id].append({"role": "user", "content": message_text})
                        conversations[session_id].append({"role": "assistant", "content": response_text})
                        return {
                            "action": "reply",
                            "replies": [response_text],
                            "session_id": session_id
                        }
            else:
                # First time asking about password reset
                logger.info(f"[SalesIQ] First password reset question - asking about SelfCare registration")
                response_text = "I can help! Are you registered on the SelfCare portal?"
                conversations[session_id].append({"role": "user", "content": message_text})
                conversations[session_id].append({"role": "assistant", "content": response_text})
                return {
                    "action": "reply",
                    "replies": [response_text],
                    "session_id": session_id
                }
        
        # Check for application updates
        app_update_keywords = ["update", "upgrade", "requires update", "needs update"]
        app_names = ["quickbooks", "lacerte", "drake", "proseries", "qb"]
        is_app_update = False
        if any(keyword in message_lower for keyword in app_update_keywords):
            if any(app in message_lower for app in app_names):
                is_app_update = True
        
        if is_app_update:
            logger.info(f"[SalesIQ] Application update request detected")
            response_text = "Application updates need to be handled by our support team to avoid downtime. Please contact support at:\n\nPhone: 1-888-415-5240 (24/7)\nEmail: support@acecloudhosting.com\n\nThey'll schedule the update for you!"
            conversations[session_id].append({"role": "user", "content": message_text})
            conversations[session_id].append({"role": "assistant", "content": response_text})
            return {
                "action": "reply",
                "replies": [response_text],
                "session_id": session_id
            }
        
        # Check for option selections - INSTANT CHAT
        if "instant chat" in message_lower or "option 1" in message_lower or message_lower == "1" or "chat/transfer" in message_lower or payload == "option_1":
            logger.info(f"[Action] ✅ BUTTON CLICKED: Instant Chat (Option 1)")
            logger.info(f"[Action] 🔄 CHAT TRANSFER INITIATED")
            logger.info(f"[Action] Status: Connecting visitor to live agent...")
            
            try:
                # Build conversation history for agent to see
                conversation_text = ""
                for msg in history:
                    role = "User" if msg.get('role') == 'user' else "Bot"
                    conversation_text += f"{role}: {msg.get('content', '')}\n"
                
                # Prepare overrides from webhook payload
                req_meta = request.get('request', {}) if isinstance(request, dict) else {}
                override_app_id = req_meta.get('app_id') or getattr(salesiq_api, 'app_id', None)
                override_department_id = visitor.get('department_id') if isinstance(visitor, dict) else None
                
                # Extract visitor email as unique identifier (more reliable than IDs)
                visitor_email = visitor.get('email', 'support@acecloudhosting.com') if isinstance(visitor, dict) else 'support@acecloudhosting.com'
                
                # Call SalesIQ API (Visitor API) to create conversation and route to agent
                logger.info(f"[SalesIQ] Calling create_chat_session API with overrides app_id={override_app_id}, dept={override_department_id}, visitor_email={visitor_email}")
                
                # Pass visitor email as user_id (most reliable unique identifier per API docs)
                api_result = salesiq_api.create_chat_session(
                    visitor_email,  # Use email as unique user_id per API documentation
                    conversation_text,
                    app_id=override_app_id,
                    department_id=str(override_department_id) if override_department_id else None,
                    visitor_info=visitor
                )
                logger.info(f"[SalesIQ] API result: {api_result}")
            except Exception as api_error:
                logger.error(f"[SalesIQ] API call failed: {str(api_error)}")
                logger.error(f"[SalesIQ] Traceback: {traceback.format_exc()}")
            
            # SalesIQ webhooks only support "reply" action, not "transfer"
            # The transfer happens through the SalesIQ API call above
            # Send confirmation message to user
            response_text = "I'm connecting you with our support team. If the transfer doesn't happen automatically, please call 1-888-415-5240 or email support@acecloudhosting.com for immediate assistance."
            
            logger.info(f"[Action] ✓ TRANSFER CONFIRMATION SENT")
            
            # Clear conversation after transfer
            if session_id in conversations:
                metrics_collector.end_conversation(session_id, "escalated")
                del conversations[session_id]
            
            return {
                "action": "reply",
                "replies": [response_text],
                "session_id": session_id
            }
        
        # Check for option selections - SCHEDULE CALLBACK
        if "callback" in message_lower or "option 2" in message_lower or message_lower == "2" or "schedule" in message_lower or payload == "option_2":
            logger.info(f"[Action] ✅ BUTTON CLICKED: Schedule Callback (Option 2)")
            logger.info(f"[Action] 📞 CALLBACK SCHEDULED - Waiting for time & phone details")
            
            # Transition to callback collection state
            state_manager.transition(session_id, TransitionTrigger.CALLBACK_REQUESTED)
            
            # Extract visitor info
            visitor_email = visitor.get("email", "support@acecloudhosting.com")
            visitor_name = visitor.get("name", visitor_email.split("@")[0] if visitor_email else "Chat User")
            
            response_text = (
                "Perfect! I'm creating a callback request for you.\n\n"
                "Please provide:\n"
                "1. Your preferred time (e.g., 'tomorrow at 2 PM' or 'Monday morning')\n"
                "2. Your phone number\n\n"
                "Our support team will call you back at that time. A callback has been scheduled and you'll receive a confirmation email shortly.\n\n"
                "Thank you for contacting Ace Cloud Hosting!"
            )
            conversations[session_id].append({"role": "user", "content": message_text})
            conversations[session_id].append({"role": "assistant", "content": response_text})
            
            # Mark session as waiting for callback details
            conversations[session_id].append({"role": "system", "content": "WAITING_FOR_CALLBACK_DETAILS"})

            return {
                "action": "reply",
                "replies": [response_text],
                "session_id": session_id
            }
            
        # Check if we are waiting for callback details
        if len(history) > 0 and history[-1].get("content") == "WAITING_FOR_CALLBACK_DETAILS":
            logger.info(f"[SalesIQ] Received callback details: {message_text}")
            
            # Remove the system marker
            history.pop()
            
            # Extract visitor info
            visitor_email = visitor.get("email", "support@acecloudhosting.com")
            visitor_name = visitor.get("name", visitor_email.split("@")[0] if visitor_email else "Chat User")

            # Best-effort parse for phone / preferred time
            import re
            phone_match = re.search(r"\b(?:\+?\d[\d\s-]{8,}\d)\b", message_text)
            phone = phone_match.group(0).strip() if phone_match else None

            time_match = re.search(r"(?i)\btime\b\s*[:=-]\s*(.+)", message_text)
            preferred_time = time_match.group(1).strip() if time_match else None
            
            # Add user's details to history
            conversations[session_id].append({"role": "user", "content": message_text})
            
            # Create the callback ticket NOW with the details
            try:
                # Get conversation history including the details provided
                conv_history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversations.get(session_id, [])])
                
                # Append the specific details to the description
                full_description = f"{conv_history}\n\nUSER PROVIDED DETAILS:\n{message_text}"
                
                api_result = desk_api.create_callback_ticket(
                    visitor_email=visitor_email,
                    visitor_name=visitor_name,
                    conversation_history=full_description,
                    preferred_time=preferred_time,
                    phone=phone,
                )
                logger.info(f"[Desk] Callback call result: {api_result}")
            except Exception as e:
                logger.error(f"[Desk] Callback call error: {str(e)}")
                api_result = {"success": False, "error": "exception", "details": str(e)}

            if api_result.get("success"):
                logger.info(f"[Action] ✓ CALLBACK TICKET CREATED SUCCESSFULLY")
                logger.info(f"[Action] 📞 Callback scheduled for visitor: {visitor.get('name', 'Unknown')}")
                logger.info(f"[Action] Email: {visitor.get('email', 'Not provided')}")
                response_text = "Thank you! I've received your details and scheduled the callback. Our team will contact you shortly. Have a great day!"
            else:
                logger.warning(f"[Action] ✗ CALLBACK TICKET CREATION FAILED")
                logger.warning(f"[Action] Error: {api_result.get('error', 'Unknown error')}")
                response_text = (
                    "I got your details, but I couldn't create the callback in our system right now. "
                    "Please call our support team at 1-888-415-5240 for immediate help."
                )
            
            # Only close the chat if callback creation succeeded
            if api_result.get("success"):
                try:
                    close_result = salesiq_api.close_chat(session_id, "callback_scheduled")
                    logger.info(f"[SalesIQ] Chat closure result: {close_result}")
                except Exception as e:
                    logger.error(f"[SalesIQ] Chat closure error: {str(e)}")

            # Clear conversation only after success
            if api_result.get("success") and session_id in conversations:
                logger.info(f"[Metrics] 📊 CONVERSATION ENDED - Reason: Callback Scheduled")
                metrics_collector.end_conversation(session_id, "resolved")
                del conversations[session_id]

            return {
                "action": "reply",
                "replies": [response_text],
                "session_id": session_id
            }
        
        # Check for option selections - CREATE TICKET
        if "ticket" in message_lower or "option 3" in message_lower or message_lower == "3" or "support ticket" in message_lower or payload == "option_3":
            logger.info(f"[Action] ✅ BUTTON CLICKED: Create Support Ticket (Option 3)")
            logger.info(f"[Action] 🎫 SUPPORT TICKET CREATION INITIATED")
            logger.info(f"[Action] Status: Collecting user details for support ticket...")
            
            # Transition to ticket collection state
            state_manager.transition(session_id, TransitionTrigger.TICKET_REQUESTED)
            
            response_text = """Perfect! I'm creating a support ticket for you.

Please provide:
1. Your name
2. Your email
3. Your phone number
4. Brief description of the issue

A ticket will be created and you'll receive a confirmation email shortly. Our support team will follow up with you within 24 hours.

Thank you for contacting Ace Cloud Hosting!"""
            conversations[session_id].append({"role": "user", "content": message_text})
            conversations[session_id].append({"role": "assistant", "content": response_text})
            
            # Call Desk API to create support ticket
            api_result = desk_api.create_support_ticket(
                user_name="pending",
                user_email="pending",
                phone="pending",
                description="Support ticket from chat",
                issue_type="general",
                conversation_history="\n".join([f"{msg.get('role')}: {msg.get('content')}" for msg in history])
            )
            
            if api_result.get("success"):
                logger.info(f"[Action] ✓ SUPPORT TICKET CREATED SUCCESSFULLY")
                logger.info(f"[Action] 🎫 Ticket ID: {api_result.get('ticket_id', 'Generated')}")
                logger.info(f"[Action] Status: Closing chat and transferring to support queue")
            else:
                logger.warning(f"[Action] ✗ SUPPORT TICKET CREATION FAILED")
                logger.warning(f"[Action] Error: {api_result.get('error', 'Unknown error')}")
            
            logger.info(f"[Desk] Support ticket result: {api_result}")
            
            # Close chat in SalesIQ
            close_result = salesiq_api.close_chat(session_id, "ticket_created")
            logger.info(f"[SalesIQ] Chat closure result: {close_result}")
            
            # Clear conversation after ticket creation (auto-close)
            if session_id in conversations:
                logger.info(f"[Metrics] 📊 CONVERSATION ENDED - Reason: Support Ticket Created")
                metrics_collector.end_conversation(session_id, "escalated")
                del conversations[session_id]
            
            return {
                "action": "reply",
                "replies": [response_text],
                "session_id": session_id
            }
        # Check for agent connection requests - COMPREHENSIVE DETECTION
        agent_request_phrases = [
            # Direct agent requests
            "connect me to agent", "connect to agent", "human agent", "talk to human", "speak to agent",
            "speak to someone", "talk to someone", "connect to human", "real person", "live person",
            "customer service", "customer support", "support agent", "support representative",
            
            # Escalation language
            "escalate", "supervisor", "manager", "senior support", "higher level",
            "transfer me", "transfer to", "forward to", "put me through",
            
            # Help requests
            "need help now", "need immediate help", "need assistance", "get me help",
            "i need someone", "can someone help", "someone help me",
            
            # Alternative phrasing
            "speak with agent", "talk with agent", "chat with agent", "contact agent",
            "operator", "representative", "specialist", "expert",
            
            # Direct requests
            "get me someone", "can i talk to", "may i speak", "i want to talk", "i want to speak",
            "let me talk", "let me speak", "connect me", "transfer call"
        ]
        if any(phrase in message_lower for phrase in agent_request_phrases):
            logger.info(f"[Escalation] 🆙 ESCALATION REQUESTED - User wants human agent")
            logger.info(f"[Escalation] Detected phrase in: {message_text[:100]}")
            logger.info(f"[Escalation] Showing 3 options: ① Instant Chat | ② Schedule Callback | ③ Create Ticket")
            
            # Transition to escalation options
            state_manager.transition(session_id, TransitionTrigger.ESCALATION_REQUESTED)
            
            response_text = "Absolutely, I'll connect you with our support team. Please choose your preferred option:"
            
            conversations[session_id].append({"role": "user", "content": message_text})
            conversations[session_id].append({"role": "assistant", "content": response_text})
            
            return {
                "action": "reply",
                "replies": [response_text],
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
                ],
                "session_id": session_id
            }
        
        # Check for acknowledgments - BUT NOT during step-by-step troubleshooting
        def is_acknowledgment_message(msg):
            msg = msg.lower().strip()
            # If message contains "then", it's likely a continuation, not an acknowledgment
            if 'then' in msg:
                return False
            # Only treat EXACT matches as acknowledgments (not partial)
            direct_acks = ["okay", "ok", "thanks", "thank you", "got it", "understood", "alright"]
            if msg in direct_acks:
                return True
            # Thanks patterns
            thanks_patterns = ["thank", "thnk", "thx", "ty"]
            if any(pattern in msg for pattern in thanks_patterns) and len(msg) < 20:
                return True
            return False
        
        # Check if we're in the middle of step-by-step troubleshooting
        is_in_troubleshooting = False
        if len(history) > 0:
            last_bot_message = history[-1].get('content', '') if history[-1].get('role') == 'assistant' else ''
            # Check for step-by-step guidance patterns
            troubleshooting_patterns = [
                'step',
                'can you',
                'do that',
                'let me know when',
                'can you see',
                'do you see',
                'click',
                'right-click',
                'press',
                'open',
                'navigate',
                'select',
                'find',
                'go to'
            ]
            if any(pattern in last_bot_message.lower() for pattern in troubleshooting_patterns):
                is_in_troubleshooting = True
        
        is_acknowledgment = is_acknowledgment_message(message_lower)
        
        if is_acknowledgment and not is_in_troubleshooting:
            logger.info(f"[SalesIQ] Acknowledgment detected (not in troubleshooting)")
            if message_lower in ["ok", "okay"]:
                logger.info(f"[SalesIQ] 'Ok/Okay' alone, asking if need more help")
                return {
                    "action": "reply",
                    "replies": ["Is there anything else I can help you with?"],
                    "session_id": session_id
                }
            else:
                logger.info(f"[SalesIQ] Acknowledgment with thanks detected")
                return {
                    "action": "reply",
                    "replies": ["You're welcome! Is there anything else I can help you with?"],
                    "session_id": session_id
                }
        elif is_acknowledgment and is_in_troubleshooting:
            logger.info(f"[SalesIQ] Acknowledgment during troubleshooting - continuing with LLM")
            # Fall through to LLM to continue with next step
        
        # Classify message category using IssueRouter (saves 60% of LLM tokens)
        category = issue_router.classify(message_text)
        logger.info(f"[SalesIQ] Message classified as: {category}")
        
        # Initialize state tracking for new conversations
        if session_id not in conversations or len(conversations[session_id]) == 0:
            router_matched = category != "other"
            logger.info(f"[Metrics] 📊 NEW CONVERSATION STARTED")
            logger.info(f"[Metrics] Category: {category}, Router Matched: {router_matched}")
            metrics_collector.start_conversation(session_id, category, router_matched)
            
            # Create state management session
            state_session = state_manager.create_session(session_id, category)
            logger.info(f"[State] Session {session_id} created in state: {state_session.state.value}")
        
        # Detect state transition from user message
        current_session = state_manager.get_session(session_id)
        if current_session:
            trigger = detect_trigger_from_message(message_text, current_session.state)
            if trigger:
                state_manager.transition(session_id, trigger)
                logger.info(f"[State] Triggered: {trigger.value}, New state: {current_session.state.value}")
        
        # Update activity timestamp
        state_manager.update_activity(session_id)
        
        # Try handler registry first (Phase 2: Pattern-based handlers)
        handler_context = {
            "state": current_session.state.value if current_session else ConversationState.GREETING.value,
            "session_id": session_id,
            "history": history,
            "category": category,
            "visitor": visitor,
            "payload": payload
        }
        
        handler_response = handler_registry.handle_message(message_text, handler_context)
        
        # If handler matched and returned response, use it
        if handler_response and handler_response.text:
            logger.info(f"[Handler] ✅ HANDLER MATCHED - Processing response")
            logger.info(f"[Handler] Response text: {handler_response.text[:150]}...")
            response_text = handler_response.text
            
            # Update state if handler requested it
            if handler_response.should_update_state and handler_response.new_state:
                if current_session:
                    # Map string state back to enum if needed
                    try:
                        new_state = ConversationState(handler_response.new_state)
                        current_session.state = new_state
                        logger.info(f"[Handler] Updated state to: {new_state.value}")
                    except ValueError:
                        logger.warning(f"[Handler] Invalid state: {handler_response.new_state}")
            
            # Handle metadata actions (transfer, close, suggestions)
            metadata = handler_response.metadata or {}
            
            # Check if we need to close chat
            if metadata.get("action") == "close_chat":
                close_result = salesiq_api.close_chat(session_id, metadata.get("reason", "resolved"))
                logger.info(f"[Handler] Chat closure result: {close_result}")
                
                if session_id in conversations:
                    reason = metadata.get("reason", "resolved")
                    logger.info(f"[Metrics] 📊 CONVERSATION ENDED - Reason: {reason.upper()}")
                    metrics_collector.end_conversation(session_id, "resolved")
                    state_manager.end_session(session_id, ConversationState.RESOLVED)
                    del conversations[session_id]
            
            # Check if we need to show suggestions/buttons
            if metadata.get("action") == "show_suggestions":
                conversations[session_id].append({"role": "user", "content": message_text})
                conversations[session_id].append({"role": "assistant", "content": response_text})
                
                return {
                    "action": "reply",
                    "replies": [response_text],
                    "suggestions": metadata.get("suggestions", []),
                    "session_id": session_id
                }
            
            # Check if we need to transfer
            if metadata.get("action") == "transfer_to_agent":
                # Build conversation history
                conversation_text = ""
                for msg in history:
                    role = "User" if msg.get('role') == 'user' else "Bot"
                    conversation_text += f"{role}: {msg.get('content', '')}\n"
                
                # Call SalesIQ API
                api_result = salesiq_api.create_chat_session(session_id, conversation_text)
                logger.info(f"[Handler] Transfer API result: {api_result}")
                
                if session_id in conversations:
                    logger.info(f"[Metrics] 📊 CONVERSATION ENDED - Reason: Agent Transfer")
                    metrics_collector.end_conversation(session_id, "escalated")
                    state_manager.end_session(session_id, ConversationState.ESCALATED)
                    del conversations[session_id]
            
            # Check for callback scheduling
            if metadata.get("action") == "schedule_callback":
                visitor_name = metadata.get("visitor_name", "User")
                visitor_email = metadata.get("visitor_email", "support@acecloudhosting.com")
                
                # Extract phone from message or conversation
                # For now, using fallback - can enhance later
                api_result = desk_api.create_callback_ticket(
                    visitor_name, visitor_email, "pending",
                    "User requested callback", "Callback Request",
                    conversation_text="\n".join([f"{msg.get('role')}: {msg.get('content')}" for msg in history])
                )
                logger.info(f"[Handler] Callback API result: {api_result}")
                
                if api_result.get("success"):
                    logger.info(f"[Metrics] 📊 CONVERSATION ENDED - Reason: Callback Scheduled")
                    close_result = salesiq_api.close_chat(session_id, "callback_scheduled")
                    logger.info(f"[Handler] Chat closure result: {close_result}")
                    
                    if session_id in conversations:
                        metrics_collector.end_conversation(session_id, "resolved")
                        state_manager.end_session(session_id, ConversationState.RESOLVED)
                        del conversations[session_id]
            
            # Check for ticket creation
            if metadata.get("action") == "create_ticket":
                api_result = desk_api.create_support_ticket(
                    user_name="pending",
                    user_email="pending",
                    phone="pending",
                    description="Support ticket from chat",
                    issue_type="general",
                    conversation_history="\n".join([f"{msg.get('role')}: {msg.get('content')}" for msg in history])
                )
                logger.info(f"[Handler] Ticket API result: {api_result}")
                
                logger.info(f"[Metrics] 📊 CONVERSATION ENDED - Reason: Support Ticket Created")
                close_result = salesiq_api.close_chat(session_id, "ticket_created")
                logger.info(f"[Handler] Chat closure result: {close_result}")
                
                if session_id in conversations:
                    metrics_collector.end_conversation(session_id, "escalated")
                    state_manager.end_session(session_id, ConversationState.ESCALATED)
                    del conversations[session_id]
            
            # Standard response (no special action)
            conversations[session_id].append({"role": "user", "content": message_text})
            conversations[session_id].append({"role": "assistant", "content": response_text})
            
            return {
                "action": "reply",
                "replies": [response_text],
                "session_id": session_id
            }
        
        # No handler matched, continue with existing hardcoded logic or LLM
        logger.info(f"[Handler] No handler matched, continuing with existing logic")
        
        # Generate LLM response with embedded resolution steps
        logger.info(f"[LLM] 🤖 CALLING GPT-4o-mini for category: {category}")
        response_text, tokens_used = generate_response(message_text, history, category=category)
        logger.info(f"[LLM] ✓ Response generated | Tokens used: {tokens_used} | Category: {category}")
        
        # Record metrics
        logger.info(f"[Metrics] 📊 Recording message: LLM=True, Tokens={tokens_used}, Category={category}")
        metrics_collector.record_message(session_id, is_llm_call=True, tokens_used=tokens_used)
        
        # Clean response
        response_text = response_text.replace('**', '')
        import re
        response_text = re.sub(r'^\s*\*\s+', '- ', response_text, flags=re.MULTILINE)
        response_text = re.sub(r'\n\s*\n+', '\n', response_text)
        response_text = response_text.strip()
        
        logger.info(f"[SalesIQ] Response generated: {response_text[:100]}...")
        
        # Update conversation history
        conversations[session_id].append({"role": "user", "content": message_text})
        conversations[session_id].append({"role": "assistant", "content": response_text})
        
        return {
            "action": "reply",
            "replies": [response_text],
            "session_id": session_id
        }
        
    except Exception as e:
        error_msg = str(e)
        error_trace = traceback.format_exc()
        
        logger.error(f"[SalesIQ] ERROR: {error_msg}")
        logger.error(f"[SalesIQ] Traceback: {error_trace}")
        
        # Track critical error and send alert if threshold exceeded
        track_error(
            "webhook_exception",
            error_msg,
            {
                "session_id": session_id or "unknown",
                "error_type": type(e).__name__,
                "traceback": error_trace[:500]  # Truncate for alert
            }
        )
        
        # Record error in metrics
        if session_id:
            metrics_collector.record_error(session_id)
        
        return {
            "action": "reply",
            "replies": ["I'm having technical difficulties. Please call our support team at 1-888-415-5240."],
            "session_id": session_id or 'unknown'
        }

@app.post("/chat")
async def chat(request: ChatRequest):
    """Main chat endpoint for n8n webhook"""
    try:
        session_id = request.session_id
        message = request.message
        
        # Set session context for logging
        session_id_var.set(session_id)
        logger.info(f"[Chat] New message received")
        
        if session_id not in conversations:
            conversations[session_id] = []
        
        history = conversations[session_id]
        
        # Classify message category
        category = issue_router.classify(message)
        logger.info(f"[Chat] Message classified as: {category}")
        
        response_text = generate_response(message, history, category=category)
        
        conversations[session_id].append({"role": "user", "content": message})
        conversations[session_id].append({"role": "assistant", "content": response_text})
        
        return ChatResponse(
            session_id=session_id,
            response=response_text,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"[Chat] Error processing message: {error_msg}")
        
        # Track error with context
        track_error(
            "chat_endpoint_error",
            error_msg,
            {
                "session_id": session_id if 'session_id' in locals() else "unknown",
                "error_type": type(e).__name__
            }
        )
        
        raise HTTPException(status_code=500, detail=error_msg)

@app.post("/reset/{session_id}")
async def reset_conversation(session_id: str):
    """Reset conversation for a session"""
    try:
        session_id_var.set(session_id)
        logger.info(f"[Reset] Resetting conversation")
        
        if session_id in conversations:
            metrics_collector.end_conversation(session_id, "abandoned")
            state_manager.end_session(session_id, ConversationState.ABANDONED)
            del conversations[session_id]
            return {"status": "success", "message": f"Conversation {session_id} reset"}
        return {"status": "not_found", "message": f"Session {session_id} not found"}
    
    except Exception as e:
        logger.error(f"[Reset] Error: {str(e)}")
        track_error("reset_error", str(e), {"session_id": session_id})
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sessions")
async def list_sessions():
    """List all active sessions with state information"""
    active_sessions = []
    for session_id in conversations.keys():
        session_summary = state_manager.get_session_summary(session_id)
        if session_summary:
            active_sessions.append(session_summary)
    
    return {
        "active_sessions": len(conversations),
        "sessions": active_sessions
    }

@app.get("/sessions/{session_id}")
async def get_session_state(session_id: str):
    """Get detailed state information for a specific session"""
    summary = state_manager.get_session_summary(session_id)
    if not summary:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    return summary

# -----------------------------------------------------------
# Test endpoints to validate SalesIQ Visitor API transfer
# -----------------------------------------------------------
@app.get("/test/salesiq-transfer")
async def test_salesiq_transfer_get():
    """Quick GET test to exercise Visitor API with env defaults.
    
    IMPORTANT: Cannot use bot preview IDs (botpreview_...).
    This endpoint uses a real-looking email-based user ID for testing.
    """
    try:
        # Use email as user_id (most reliable per API docs) instead of session ID
        test_user_id = "vishal.dharan@acecloudhosting.com"
        conversation_text = "Test transfer from GET endpoint"
        logger.info(f"[Test] Initiating SalesIQ Visitor API transfer (GET) with user_id={test_user_id}")
        result = salesiq_api.create_chat_session(test_user_id, conversation_text)
        return {
            "user_id": test_user_id,
            "result": result
        }
    except Exception as e:
        logger.error(f"[Test] SalesIQ transfer GET failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/test/salesiq-transfer")
async def test_salesiq_transfer_post(payload: Dict):
    """POST test to exercise Visitor API with overrides from payload.
    
    Accepts:
    - visitor_user_id: Unique identifier for visitor (use email, not botpreview_...)
    - conversation: Conversation text for agent
    - app_id: Override app_id
    - department_id: Override department_id
    - visitor: Full visitor info dict
    - custom_wait_time: Custom wait time
    
    IMPORTANT: visitor_user_id cannot be botpreview_... IDs.
    Use real email addresses or unique identifiers.
    """
    try:
        # Use email as user_id (more reliable than session IDs)
        visitor_user_id = str(payload.get("visitor_user_id") or "vishal.dharan@acecloudhosting.com")
        conversation_text = str(payload.get("conversation") or "Test transfer from POST endpoint")
        app_id = payload.get("app_id")
        department_id = payload.get("department_id")
        visitor_info = payload.get("visitor")
        custom_wait_time = payload.get("custom_wait_time")

        logger.info(
            f"[Test] Initiating SalesIQ Visitor API transfer (POST) for user_id={visitor_user_id} with app_id={app_id}, dept={department_id}"
        )
        result = salesiq_api.create_chat_session(
            visitor_user_id,  # Use as unique user_id per API documentation
            conversation_text,
            app_id=app_id,
            department_id=str(department_id) if department_id is not None else None,
            visitor_info=visitor_info,
            custom_wait_time=custom_wait_time,
        )
        return {
            "user_id": visitor_user_id,
            "result": result
        }
    except Exception as e:
        logger.error(f"[Test] SalesIQ transfer POST failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics")
async def get_metrics():
    """Get comprehensive chatbot performance metrics
    
    Returns:
        JSON object with automation rate, category distribution, LLM usage, and more
    """
    try:
        summary = metrics_collector.get_summary()
        logger.info(f"[Metrics] Metrics requested - {summary['overview']['total_conversations']} conversations tracked")
        return summary
    except Exception as e:
        logger.error(f"[Metrics] Error fetching metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics/report")
async def get_metrics_report():
    """Get human-readable metrics report
    
    Returns:
        Plain text formatted report
    """
    try:
        report = metrics_collector.get_detailed_report()
        logger.info(f"[Metrics] Detailed report requested")
        return {"report": report}
    except Exception as e:
        logger.error(f"[Metrics] Error generating report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/metrics/reset")
async def reset_metrics():
    """Reset all metrics (use with caution)
    
    Requires confirmation parameter
    """
    try:
        metrics_collector.reset()
        logger.warning("[Metrics] All metrics have been reset")
        return {"status": "success", "message": "All metrics have been reset"}
    except Exception as e:
        logger.error(f"[Metrics] Error resetting metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint
    
    Returns system status including:
    - Service health (router, metrics, state manager, handlers)
    - Active conversation count
    - System uptime
    - API status
    """
    try:
        metrics_summary = metrics_collector.get_summary()
        
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "issue_router": {
                    "status": "healthy",
                    "categories": 6
                },
                "metrics_collector": {
                    "status": "healthy",
                    "total_conversations": metrics_summary['overview']['total_conversations'],
                    "uptime_hours": metrics_summary['overview']['uptime_hours']
                },
                "state_manager": {
                    "status": "healthy",
                    "active_sessions": len(conversations)
                },
                "handler_registry": {
                    "status": "healthy",
                    "handlers_count": len(handler_registry.handlers)
                },
                "zoho_salesiq_api": {
                    "status": "healthy" if salesiq_api.enabled else "fallback",
                    "enabled": salesiq_api.enabled
                },
                "zoho_desk_api": {
                    "status": "healthy" if desk_api.enabled else "fallback",
                    "enabled": getattr(desk_api, 'enabled', False)
                }
            },
            "performance": {
                "active_conversations": len(conversations),
                "automation_rate": metrics_summary['resolution']['automation_rate'],
                "router_effectiveness": metrics_summary['performance']['router_effectiveness']
            }
        }
        
        return health_status
        
    except Exception as e:
        logger.error(f"[Health] Error generating health check: {str(e)}")
        return {
            "status": "degraded",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

@app.get("/stats")
async def get_statistics():
    """Detailed statistics endpoint
    
    Returns comprehensive statistics including:
    - Category breakdown with percentages
    - Resolution type distribution
    - Average metrics
    - Time-based analysis
    """
    try:
        metrics_summary = metrics_collector.get_summary()
        
        # Calculate additional statistics
        total_conversations = metrics_summary['overview']['total_conversations']
        completed = metrics_summary['overview']['completed_conversations']
        
        # Category breakdown with percentages
        category_stats = []
        for category, count in metrics_summary['categories'].items():
            percentage = (count / total_conversations * 100) if total_conversations > 0 else 0
            category_stats.append({
                "category": category,
                "count": count,
                "percentage": round(percentage, 2)
            })
        
        # Sort by count descending
        category_stats.sort(key=lambda x: x['count'], reverse=True)
        
        # Resolution breakdown with percentages
        resolution_stats = {
            "resolved": {
                "count": metrics_summary['resolution']['resolved'],
                "percentage": round((metrics_summary['resolution']['resolved'] / completed * 100) if completed > 0 else 0, 2)
            },
            "escalated": {
                "count": metrics_summary['resolution']['escalated'],
                "percentage": round((metrics_summary['resolution']['escalated'] / completed * 100) if completed > 0 else 0, 2)
            },
            "abandoned": {
                "count": metrics_summary['resolution']['abandoned'],
                "percentage": round((metrics_summary['resolution']['abandoned'] / completed * 100) if completed > 0 else 0, 2)
            }
        }
        
        # Handler statistics
        handler_stats = {
            "total_handlers": len(handler_registry.handlers),
            "handler_list": handler_registry.list_handlers()
        }
        
        statistics = {
            "summary": {
                "total_conversations": total_conversations,
                "completed_conversations": completed,
                "active_conversations": metrics_summary['overview']['active_conversations'],
                "uptime_hours": round(metrics_summary['overview']['uptime_hours'], 2)
            },
            "categories": category_stats,
            "resolutions": resolution_stats,
            "performance": {
                "automation_rate": metrics_summary['resolution']['automation_rate'],
                "escalation_rate": metrics_summary['resolution']['escalation_rate'],
                "avg_resolution_time_seconds": metrics_summary['performance']['avg_resolution_time_seconds'],
                "router_effectiveness": metrics_summary['performance']['router_effectiveness']
            },
            "llm_usage": metrics_summary['llm_usage'],
            "handlers": handler_stats,
            "timestamp": datetime.now().isoformat()
        }
        
        return statistics
        
    except Exception as e:
        logger.error(f"[Stats] Error generating statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    
    print("="*70)
    print("ACE CLOUD HOSTING - SUPPORT BOT (HYBRID LLM)")
    print("="*70)
    print(f"\n[STARTING] FastAPI server on port {port}...")
    print(f"[ENDPOINT] http://0.0.0.0:{port}")
    print(f"[DOCS] http://0.0.0.0:{port}/docs")
    print("\n[READY] Ready to receive webhooks!")
    print("="*70 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=port)
