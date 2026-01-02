"""
Comprehensive Bot Testing Script
Tests system prompt and all 3 escalation options
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"
WEBHOOK_URL = f"{BASE_URL}/webhook/salesiq"

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_test(test_name):
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}TEST: {test_name}{RESET}")
    print(f"{BLUE}{'='*70}{RESET}")

def print_success(message):
    print(f"{GREEN}✓ {message}{RESET}")

def print_error(message):
    print(f"{RED}✗ {message}{RESET}")

def print_info(message):
    print(f"{YELLOW}ℹ {message}{RESET}")

def send_message(session_id, message_text, visitor_id="test-user"):
    """Send a message to the bot"""
    payload = {
        "session_id": session_id,
        "message": {"text": message_text},
        "visitor": {"id": visitor_id}
    }
    
    try:
        response = requests.post(WEBHOOK_URL, json=payload, timeout=10)
        return response.status_code, response.json()
    except Exception as e:
        print_error(f"Request failed: {str(e)}")
        return None, None

def test_health_check():
    """Test 1: Health check"""
    print_test("Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Health check passed")
            print_info(f"Status: {data.get('status')}")
            print_info(f"Active sessions: {data.get('active_sessions')}")
            return True
        else:
            print_error(f"Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Health check error: {str(e)}")
        return False

def test_greeting():
    """Test 2: Bot greeting"""
    print_test("Bot Greeting")
    
    session_id = "test-greeting-001"
    status, response = send_message(session_id, "Hello")
    
    if status == 200:
        print_success("Greeting received")
        reply = response.get('replies', [''])[0]
        print_info(f"Bot response: {reply[:100]}...")
        return True
    else:
        print_error(f"Greeting failed: {status}")
        return False

def test_quickbooks_frozen():
    """Test 3: QuickBooks Frozen Issue"""
    print_test("QuickBooks Frozen Issue")
    
    session_id = "test-qb-frozen-001"
    
    # Step 1: User reports QB frozen
    print_info("Step 1: User reports QB frozen")
    status, response = send_message(session_id, "My QuickBooks is frozen")
    
    if status != 200:
        print_error(f"Failed to send message: {status}")
        return False
    
    reply = response.get('replies', [''])[0]
    print_info(f"Bot asks: {reply[:100]}...")
    
    if "dedicated" not in reply.lower() and "shared" not in reply.lower():
        print_error("Bot should ask about server type")
        return False
    
    print_success("Bot correctly asks about server type")
    
    # Step 2: User specifies server type
    print_info("Step 2: User specifies dedicated server")
    status, response = send_message(session_id, "It's a dedicated server")
    
    if status != 200:
        print_error(f"Failed to send message: {status}")
        return False
    
    reply = response.get('replies', [''])[0]
    print_info(f"Bot provides step: {reply[:100]}...")
    
    if "task manager" not in reply.lower():
        print_error("Bot should provide Task Manager step")
        return False
    
    print_success("Bot provides correct resolution step")
    return True

def test_password_reset():
    """Test 4: Password Reset Issue"""
    print_test("Password Reset Issue")
    
    session_id = "test-password-001"
    
    # Step 1: User asks about password reset
    print_info("Step 1: User asks about password reset")
    status, response = send_message(session_id, "I need to reset my password")
    
    if status != 200:
        print_error(f"Failed to send message: {status}")
        return False
    
    reply = response.get('replies', [''])[0]
    print_info(f"Bot asks: {reply[:100]}...")
    
    if "selfcare" not in reply.lower() and "enrolled" not in reply.lower():
        print_error("Bot should ask about Selfcare enrollment")
        return False
    
    print_success("Bot correctly asks about Selfcare enrollment")
    
    # Step 2: User says they are enrolled
    print_info("Step 2: User says they are enrolled")
    status, response = send_message(session_id, "Yes, I'm enrolled")
    
    if status != 200:
        print_error(f"Failed to send message: {status}")
        return False
    
    reply = response.get('replies', [''])[0]
    print_info(f"Bot provides step: {reply[:100]}...")
    
    if "selfcare" not in reply.lower():
        print_error("Bot should provide Selfcare password reset steps")
        return False
    
    print_success("Bot provides correct password reset steps")
    return True

def test_escalation_instant_chat():
    """Test 5: Escalation - Instant Chat (Creates Human Session)"""
    print_test("Escalation - Instant Chat")
    
    session_id = "test-escalation-chat-001"
    
    # Simulate unresolved issue
    print_info("Step 1: User reports issue")
    send_message(session_id, "My server is not responding")
    
    print_info("Step 2: User says issue not resolved")
    status, response = send_message(session_id, "Still not working")
    
    if status != 200:
        print_error(f"Failed to send message: {status}")
        return False
    
    reply = response.get('replies', [''])[0]
    print_info(f"Bot offers options: {reply[:100]}...")
    
    if "instant chat" not in reply.lower():
        print_error("Bot should offer Instant Chat option")
        return False
    
    print_success("Bot offers Instant Chat option")
    
    # Step 3: User selects Instant Chat
    print_info("Step 3: User selects Instant Chat (Option 1)")
    status, response = send_message(session_id, "option 1")
    
    if status != 200:
        print_error(f"Failed to send message: {status}")
        return False
    
    action = response.get('action')
    transfer_to = response.get('transfer_to')
    conversation_history = response.get('conversation_history')
    
    print_info(f"Response action: {action}")
    print_info(f"Transfer to: {transfer_to}")
    
    if action != "transfer":
        print_error(f"Expected action 'transfer', got '{action}'")
        return False
    
    if transfer_to != "human_agent":
        print_error(f"Expected transfer_to 'human_agent', got '{transfer_to}'")
        return False
    
    if not conversation_history:
        print_error("Conversation history should be included")
        return False
    
    print_success("Instant Chat transfer works correctly")
    print_info(f"Conversation history length: {len(conversation_history)} chars")
    return True

def test_escalation_callback():
    """Test 6: Escalation - Schedule Callback (Auto-Closes)"""
    print_test("Escalation - Schedule Callback")
    
    session_id = "test-escalation-callback-001"
    
    # Simulate unresolved issue
    print_info("Step 1: User reports issue")
    send_message(session_id, "I can't access my account")
    
    print_info("Step 2: User says issue not resolved")
    status, response = send_message(session_id, "Still not working")
    
    if status != 200:
        print_error(f"Failed to send message: {status}")
        return False
    
    reply = response.get('replies', [''])[0]
    
    if "schedule callback" not in reply.lower():
        print_error("Bot should offer Schedule Callback option")
        return False
    
    print_success("Bot offers Schedule Callback option")
    
    # Step 3: User selects Schedule Callback
    print_info("Step 3: User selects Schedule Callback (Option 2)")
    status, response = send_message(session_id, "option 2")
    
    if status != 200:
        print_error(f"Failed to send message: {status}")
        return False
    
    action = response.get('action')
    reply = response.get('replies', [''])[0]
    
    print_info(f"Response action: {action}")
    print_info(f"Bot response: {reply[:100]}...")
    
    if action != "reply":
        print_error(f"Expected action 'reply', got '{action}'")
        return False
    
    if "callback" not in reply.lower():
        print_error("Bot should confirm callback request")
        return False
    
    print_success("Schedule Callback works correctly")
    
    # Step 4: Verify chat auto-closed (session cleared)
    print_info("Step 4: Verify chat auto-closed")
    time.sleep(1)
    
    # Try to send another message - should start fresh
    status, response = send_message(session_id, "Hello again")
    
    if status == 200:
        reply = response.get('replies', [''])[0]
        if "how can i assist" in reply.lower() or "hello" in reply.lower():
            print_success("Chat auto-closed and new session started")
            return True
        else:
            print_error("Chat should have been auto-closed")
            return False
    else:
        print_error(f"Failed to verify auto-close: {status}")
        return False

def test_escalation_ticket():
    """Test 7: Escalation - Create Support Ticket (Auto-Closes)"""
    print_test("Escalation - Create Support Ticket")
    
    session_id = "test-escalation-ticket-001"
    
    # Simulate unresolved issue
    print_info("Step 1: User reports issue")
    send_message(session_id, "My email is not working")
    
    print_info("Step 2: User says issue not resolved")
    status, response = send_message(session_id, "Still not working")
    
    if status != 200:
        print_error(f"Failed to send message: {status}")
        return False
    
    reply = response.get('replies', [''])[0]
    
    if "support ticket" not in reply.lower():
        print_error("Bot should offer Create Support Ticket option")
        return False
    
    print_success("Bot offers Create Support Ticket option")
    
    # Step 3: User selects Create Ticket
    print_info("Step 3: User selects Create Ticket (Option 3)")
    status, response = send_message(session_id, "option 3")
    
    if status != 200:
        print_error(f"Failed to send message: {status}")
        return False
    
    action = response.get('action')
    reply = response.get('replies', [''])[0]
    
    print_info(f"Response action: {action}")
    print_info(f"Bot response: {reply[:100]}...")
    
    if action != "reply":
        print_error(f"Expected action 'reply', got '{action}'")
        return False
    
    if "ticket" not in reply.lower():
        print_error("Bot should confirm ticket creation")
        return False
    
    print_success("Create Support Ticket works correctly")
    
    # Step 4: Verify chat auto-closed (session cleared)
    print_info("Step 4: Verify chat auto-closed")
    time.sleep(1)
    
    # Try to send another message - should start fresh
    status, response = send_message(session_id, "Hello again")
    
    if status == 200:
        reply = response.get('replies', [''])[0]
        if "how can i assist" in reply.lower() or "hello" in reply.lower():
            print_success("Chat auto-closed and new session started")
            return True
        else:
            print_error("Chat should have been auto-closed")
            return False
    else:
        print_error(f"Failed to verify auto-close: {status}")
        return False

def test_email_issue():
    """Test 8: Email/O365 Issue"""
    print_test("Email/O365 Issue")
    
    session_id = "test-email-001"
    
    print_info("Step 1: User reports email issue")
    status, response = send_message(session_id, "My Outlook is not connecting")
    
    if status != 200:
        print_error(f"Failed to send message: {status}")
        return False
    
    reply = response.get('replies', [''])[0]
    print_info(f"Bot response: {reply[:100]}...")
    
    if "internet" not in reply.lower() and "connection" not in reply.lower():
        print_error("Bot should provide troubleshooting steps")
        return False
    
    print_success("Bot provides email troubleshooting steps")
    return True

def test_disk_space_issue():
    """Test 9: Low Disk Space Issue"""
    print_test("Low Disk Space Issue")
    
    session_id = "test-disk-space-001"
    
    print_info("Step 1: User reports disk space issue")
    status, response = send_message(session_id, "My server has low disk space")
    
    if status != 200:
        print_error(f"Failed to send message: {status}")
        return False
    
    reply = response.get('replies', [''])[0]
    print_info(f"Bot response: {reply[:100]}...")
    
    if "temp" not in reply.lower() and "disk" not in reply.lower():
        print_error("Bot should provide disk cleanup steps")
        return False
    
    print_success("Bot provides disk space resolution steps")
    return True

def run_all_tests():
    """Run all tests"""
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}COMPREHENSIVE BOT TESTING SUITE{RESET}")
    print(f"{BLUE}{'='*70}{RESET}")
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Base URL: {BASE_URL}")
    
    tests = [
        ("Health Check", test_health_check),
        ("Bot Greeting", test_greeting),
        ("QuickBooks Frozen", test_quickbooks_frozen),
        ("Password Reset", test_password_reset),
        ("Escalation - Instant Chat", test_escalation_instant_chat),
        ("Escalation - Schedule Callback", test_escalation_callback),
        ("Escalation - Create Ticket", test_escalation_ticket),
        ("Email/O365 Issue", test_email_issue),
        ("Low Disk Space Issue", test_disk_space_issue),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print_error(f"Test crashed: {str(e)}")
            results[test_name] = False
        
        time.sleep(1)  # Delay between tests
    
    # Print summary
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}TEST SUMMARY{RESET}")
    print(f"{BLUE}{'='*70}{RESET}")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = f"{GREEN}PASS{RESET}" if result else f"{RED}FAIL{RESET}"
        print(f"{status} - {test_name}")
    
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"Total: {passed}/{total} tests passed")
    print(f"Success rate: {(passed/total)*100:.1f}%")
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    return passed == total

if __name__ == "__main__":
    import sys
    
    print_info("Make sure the bot is running: python fastapi_chatbot_hybrid.py")
    print_info("Waiting 2 seconds before starting tests...")
    time.sleep(2)
    
    success = run_all_tests()
    sys.exit(0 if success else 1)
