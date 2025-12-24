
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import os
from openai import OpenAI
from dotenv import load_dotenv
import urllib3
import uvicorn
from datetime import datetime
import logging
import traceback

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import core modules
from core.config import settings
from core.prompts import load_expert_prompt

app = FastAPI(title=settings.APP_TITLE, version=settings.APP_VERSION)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
LLM_MODEL = settings.LLM_MODEL

conversations: Dict[str, List[Dict]] = {}

# Fallback API class for when real API is not available
class FallbackAPI:
    def __init__(self):
        self.enabled = False
    def create_chat_session(self, visitor_id, conversation_history, **kwargs):
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

# Expert system prompt - SHORT & INTERACTIVE
# Load Expert Prompt from file
EXPERT_PROMPT = load_expert_prompt()


def generate_response(message: str, history: List[Dict]) -> str:
    """Generate response using LLM with embedded resolution steps"""
    
    system_prompt = EXPERT_PROMPT
    
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": message})
    
    response = openai_client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        temperature=0.7,
        max_tokens=400
    )
    
    return response.choices[0].message.content

@app.get("/")
async def root():
    """Health check endpoint"""
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
            "health": "/health"
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
        logger.info(f"[SalesIQ] Webhook received")
        
        # Validate request structure
        if not isinstance(request, dict):
            logger.error(f"[SalesIQ] Invalid request format: {type(request)}")
            return {
                "action": "reply",
                "replies": ["I'm having technical difficulties. Please call 1-888-415-5240."],
                "session_id": "unknown"
            }
        
        logger.info(f"[SalesIQ] Request keys: {list(request.keys())}")
        logger.info(f"[SalesIQ] Full request payload: {request}")
        
        # Log all possible IDs for transfer debugging
        visitor = request.get('visitor', {})
        chat = request.get('chat', {})
        conversation = request.get('conversation', {})
        
        logger.info(f"[SalesIQ] Visitor data: {visitor}")
        logger.info(f"[SalesIQ] Chat data: {chat}")
        logger.info(f"[SalesIQ] Conversation data: {conversation}")
        
        # Extract session ID (try multiple sources)
        session_id = (
            visitor.get('active_conversation_id') or
            chat.get('id') or
            conversation.get('id') or
            request.get('session_id') or 
            visitor.get('id') or
            'unknown'
        )
        
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
            logger.info(f"[SalesIQ] Empty message, sending greeting")
            return {
                "action": "reply",
                "replies": ["Hi! I'm AceBuddy, your Ace Cloud Hosting support assistant. What can I help you with today?"],
                "session_id": session_id
            }
        
        # Initialize conversation history
        if session_id not in conversations:
            conversations[session_id] = []
        
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
                    del conversations[session_id]
                
                return {
                    "action": "reply",
                    "replies": ["I'm connecting you with our support team. If the transfer doesn't happen automatically, please call 1-888-415-5240 or email support@acecloudhosting.com for immediate assistance."],
                    "session_id": session_id
                }
        
        # Check for issue resolution
        resolution_keywords = ["resolved", "fixed", "working now", "solved", "all set"]
        if any(keyword in message_lower for keyword in resolution_keywords):
            logger.info(f"[SalesIQ] Issue resolved by user")
            response_text = "Great! I'm glad the issue is resolved. If you need anything else, feel free to ask!"
            conversations[session_id].append({"role": "user", "content": message_text})
            conversations[session_id].append({"role": "assistant", "content": response_text})
            
            # Close chat in SalesIQ since issue is resolved
            close_result = salesiq_api.close_chat(session_id, "resolved")
            logger.info(f"[SalesIQ] Chat closure result: {close_result}")
            
            if session_id in conversations:
                del conversations[session_id]
            return {
                "action": "reply",
                "replies": [response_text],
                "session_id": session_id
            }
        
        # Check for not resolved
        not_resolved_keywords = ["not resolved", "not fixed", "not working", "didn't work", "still not", "still stuck"]
        if any(keyword in message_lower for keyword in not_resolved_keywords):
            logger.info(f"[SalesIQ] Issue NOT resolved - offering 3 options with interactive buttons")
            response_text = "I understand this is frustrating. Here are 3 ways I can help:"
            
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
                    },
                    {
                        "text": "🎫 Create Ticket",
                        "action_type": "reply",
                        "action_value": "3"
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
            logger.info(f"[SalesIQ] User selected: Instant Chat Transfer")
            
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
            
            # Clear conversation after transfer
            if session_id in conversations:
                del conversations[session_id]
            
            return {
                "action": "reply",
                "replies": [response_text],
                "session_id": session_id
            }
        
        # Check for option selections - SCHEDULE CALLBACK
        if "callback" in message_lower or "option 2" in message_lower or message_lower == "2" or "schedule" in message_lower or payload == "option_2":
            logger.info(f"[SalesIQ] User selected: Schedule Callback")
            response_text = (
                "Perfect! I'm creating a callback request for you.\n\n"
                "Please provide:\n"
                "1. Your preferred time (e.g., 'tomorrow at 2 PM' or 'Monday morning')\n"
                "2. Your phone number\n\n"
                "Our support team will call you back at that time. A ticket has been created and you'll receive a confirmation email shortly.\n\n"
                "Thank you for contacting Ace Cloud Hosting!"
            )
            conversations[session_id].append({"role": "user", "content": message_text})
            conversations[session_id].append({"role": "assistant", "content": response_text})

            # Fire-and-forget: protect external calls so webhook never breaks
            try:
                api_result = desk_api.create_callback_ticket(
                    user_email="support@acecloudhosting.com",
                    phone="pending",
                    preferred_time="pending",
                    issue_summary="Callback request from chat"
                )
                logger.info(f"[Desk] Callback ticket result: {api_result}")
            except Exception as e:
                logger.error(f"[Desk] Callback ticket error: {str(e)}")

            try:
                close_result = salesiq_api.close_chat(session_id, "callback_scheduled")
                logger.info(f"[SalesIQ] Chat closure result: {close_result}")
            except Exception as e:
                logger.error(f"[SalesIQ] Chat closure error: {str(e)}")

            # Clear conversation after callback (auto-close)
            if session_id in conversations:
                del conversations[session_id]

            return {
                "action": "reply",
                "replies": [response_text],
                "session_id": session_id
            }
        
        # Check for option selections - CREATE TICKET
        if "ticket" in message_lower or "option 3" in message_lower or message_lower == "3" or "support ticket" in message_lower or payload == "option_3":
            logger.info(f"[SalesIQ] User selected: Create Support Ticket")
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
            logger.info(f"[Desk] Support ticket result: {api_result}")
            
            # Close chat in SalesIQ
            close_result = salesiq_api.close_chat(session_id, "ticket_created")
            logger.info(f"[SalesIQ] Chat closure result: {close_result}")
            
            # Clear conversation after ticket creation (auto-close)
            if session_id in conversations:
                del conversations[session_id]
            
            return {
                "action": "reply",
                "replies": [response_text],
                "session_id": session_id
            }
        #check for new request
        # Check for agent connection requests (legacy)
        agent_request_phrases = ["connect me to agent", "connect to agent", "human agent", "talk to human", "speak to agent"]
        if any(phrase in message_lower for phrase in agent_request_phrases):
            logger.info(f"[SalesIQ] User requesting human agent - offering options with interactive buttons")
            response_text = "I can help you with that. Here are your options:"
            
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
                    {
                        "text": "🎫 Create Ticket",
                        "action_type": "reply",
                        "action_value": "3"
                    }
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
        
        # Generate LLM response with embedded resolution steps
        logger.info(f"[SalesIQ] Calling OpenAI LLM with embedded resolution steps...")
        response_text = generate_response(message_text, history)
        
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
        logger.error(f"[SalesIQ] ERROR: {str(e)}")
        logger.error(f"[SalesIQ] Traceback: {traceback.format_exc()}")
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
        
        if session_id not in conversations:
            conversations[session_id] = []
        
        history = conversations[session_id]
        response_text = generate_response(message, history)
        
        conversations[session_id].append({"role": "user", "content": message})
        conversations[session_id].append({"role": "assistant", "content": response_text})
        
        return ChatResponse(
            session_id=session_id,
            response=response_text,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reset/{session_id}")
async def reset_conversation(session_id: str):
    """Reset conversation for a session"""
    if session_id in conversations:
        del conversations[session_id]
        return {"status": "success", "message": f"Conversation {session_id} reset"}
    return {"status": "not_found", "message": f"Session {session_id} not found"}

@app.get("/sessions")
async def list_sessions():
    """List all active sessions"""
    return {
        "active_sessions": len(conversations),
        "sessions": list(conversations.keys())
    }

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
