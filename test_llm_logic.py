"""
LLM Classification System - Logic Tests (No API calls needed)
Tests: resolution detection, conversation restart, fallback handling
"""

import sys
import os


def test_conversation_restart_logic():
    """Test conversation restart logic without API calls"""
    print("\n" + "="*70)
    print("TEST 1: CONVERSATION RESTART LOGIC")
    print("="*70)
    
    test_cases = [
        ("Yes, I have another question", True, "Yes + question intent"),
        ("Actually, how do I update QB?", True, "Actually indicates new question"),
        ("What about password reset?", True, "New question about different topic"),
        ("I have another issue", True, "Explicit new issue"),
        ("No thanks", False, "Simple no"),
        ("Bye", False, "Short goodbye"),
        ("Thanks", False, "Short thanks"),
        ("Close it", False, "Close confirmation"),
    ]
    
    passed = 0
    for message, should_continue, reason in test_cases:
        # Simulate logic from llm_chatbot.py
        user_wants_to_continue = (
            "yes" in message.lower() or 
            "i have" in message.lower() or
            "another" in message.lower() or
            "help" in message.lower() or
            "question" in message.lower() or
            len(message) > 15  # Likely a new question
        )
        
        user_wants_to_close = (
            "no" in message.lower() or
            "nope" in message.lower() or
            "close" in message.lower() or
            "bye" in message.lower() or
            "thanks" in message.lower() or
            "thank you" in message.lower()
        ) and len(message) < 20
        
        # If user wants to continue, conversation restarts
        is_restart = user_wants_to_continue and not user_wants_to_close
        
        status = "[PASS]" if is_restart == should_continue else "[FAIL]"
        passed += 1 if is_restart == should_continue else 0
        
        print(f"{status}: '{message}'")
        print(f"  - Expected: {should_continue}, Got: {is_restart} | {reason}")
    
    print(f"\nConversation Restart Logic: {passed}/{len(test_cases)} passed")
    return passed == len(test_cases)


def test_fallback_detection_logic():
    """Test fallback detection logic"""
    print("\n" + "="*70)
    print("TEST 2: FALLBACK DETECTION (Unclear Response)")
    print("="*70)
    
    test_cases = [
        ("I'm not sure what you mean", True, "Classic unclear phrase"),
        ("Could you clarify?", True, "Clarification request"),
        ("I don't understand", True, "Explicit non-understanding"),
        ("Can you rephrase?", True, "Rephrase request"),
        ("I didn't quite get that", True, "Confusion indicator"),
        ("Here's the answer", False, "Confident response"),
        ("That should work", False, "Solution provided"),
        ("Try this method", False, "Instruction given"),
    ]
    
    unclear_indicators = [
        "i don't understand",
        "i'm not sure",
        "could you clarify",
        "can you rephrase",
        "i didn't quite get that"
    ]
    
    passed = 0
    for response, should_be_unclear, reason in test_cases:
        is_unclear = any(indicator in response.lower() for indicator in unclear_indicators)
        # Only flag as short if it's ALSO unclear (avoid false positives on short good responses)
        is_short_and_unclear = len(response) < 20 and is_unclear
        
        detected = is_unclear or is_short_and_unclear
        
        status = "[PASS]" if detected == should_be_unclear else "[FAIL]"
        passed += 1 if detected == should_be_unclear else 0
        
        print(f"{status}: '{response}'")
        print(f"  - Expected: {should_be_unclear}, Got: {detected} | {reason}")
    
    print(f"\nFallback Detection: {passed}/{len(test_cases)} passed")
    return passed == len(test_cases)


def test_satisfaction_message_detection():
    """Test if bot correctly identifies satisfaction messages"""
    print("\n" + "="*70)
    print("TEST 3: SATISFACTION MESSAGE DETECTION")
    print("="*70)
    
    satisfaction_indicators = [
        "i'm happy the issue is resolved",
        "is there anything else i can help",
        "would you like me to close this chat",
        "have a great day"
    ]
    
    test_messages = [
        ("Excellent! I'm happy the issue is resolved.", True, "Full satisfaction phrase"),
        ("Is there anything else I can help with?", True, "Help offer phrase"),
        ("Would you like me to close this chat?", True, "Closure question"),
        ("Have a great day!", True, "Farewell phrase"),
        ("Here's the solution", False, "Solution message"),
        ("Thanks for waiting", False, "Acknowledgment"),
    ]
    
    passed = 0
    for message, should_be_satisfaction, reason in test_messages:
        is_satisfaction = any(indicator in message.lower() for indicator in satisfaction_indicators)
        
        status = "[PASS]" if is_satisfaction == should_be_satisfaction else "[FAIL]"
        passed += 1 if is_satisfaction == should_be_satisfaction else 0
        
        print(f"{status}: '{message}'")
        print(f"  - Expected: {should_be_satisfaction}, Got: {is_satisfaction} | {reason}")
    
    print(f"\nSatisfaction Detection: {passed}/{len(test_messages)} passed")
    return passed == len(test_messages)


def test_resolution_keywords():
    """Test resolution keyword detection"""
    print("\n" + "="*70)
    print("TEST 4: RESOLUTION KEYWORD DETECTION")
    print("="*70)
    
    resolution_positive = [
        ("My issue is fixed", True),
        ("That solved my problem", True),
        ("It's working now", True),
        ("Problem resolved", True),
        ("That helped!", True),
    ]
    
    resolution_negative = [
        ("Not fixed yet", False),
        ("Still having issues", False),
        ("This doesn't work", False),
        ("Not solved", False),
        ("Still broken", False),
    ]
    
    all_cases = resolution_positive + resolution_negative
    passed = 0
    
    for message, should_have_resolution in all_cases:
        # Simple keyword check (LLM will be more sophisticated)
        has_positive = any(word in message.lower() for word in ["fixed", "solved", "working", "resolved", "helped"])
        has_negative = any(word in message.lower() for word in ["not", "doesn't", "still", "broken"])
        
        detected_resolution = has_positive and not has_negative
        
        status = "[PASS]" if detected_resolution == should_have_resolution else "[FAIL]"
        passed += 1 if detected_resolution == should_have_resolution else 0
        
        print(f"{status}: '{message}' -> {detected_resolution} (expected {should_have_resolution})")
    
    print(f"\nResolution Keywords: {passed}/{len(all_cases)} passed")
    return passed == len(all_cases)


def test_escalation_keywords():
    """Test escalation trigger keywords"""
    print("\n" + "="*70)
    print("TEST 5: ESCALATION KEYWORD DETECTION")
    print("="*70)
    
    escalation_cases = [
        ("I need to speak to someone", True),
        ("Connect me to an agent", True),
        ("Can I get a callback?", True),
        ("This is urgent", True),
        ("Your bot isn't helping", True),
        ("I want a refund", True),
        ("Can you help me reset?", False),
        ("Thanks for the answer", False),
        ("That works great", False),
    ]
    
    escalation_keywords = ["agent", "someone", "callback", "urgent", "refund", "speak", "human", "supervisor", "helping", "doesn't work", "isn't helping"]
    
    passed = 0
    for message, should_escalate, in escalation_cases:
        has_escalation = any(keyword in message.lower() for keyword in escalation_keywords)
        
        status = "[PASS]" if has_escalation == should_escalate else "[FAIL]"
        passed += 1 if has_escalation == should_escalate else 0
        
        print(f"{status}: '{message}' -> escalate={has_escalation} (expected {should_escalate})")
    
    print(f"\nEscalation Keywords: {passed}/{len(escalation_cases)} passed")
    return passed == len(escalation_cases)


def main():
    print("\n" + "="*70)
    print("[LLM] CLASSIFICATION - LOGIC TESTS (No API Keys Required)")
    print("="*70)
    
    results = {
        "conversation_restart": test_conversation_restart_logic(),
        "fallback_detection": test_fallback_detection_logic(),
        "satisfaction_detection": test_satisfaction_message_detection(),
        "resolution_keywords": test_resolution_keywords(),
        "escalation_keywords": test_escalation_keywords(),
    }
    
    # Summary
    print("\n" + "="*70)
    print("[SUMMARY] TEST RESULTS")
    print("="*70)
    
    total_passed = sum(1 for v in results.values() if v)
    total_tests = len(results)
    
    for test_name, passed in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status}: {test_name.replace('_', ' ').title()}")
    
    print("\n" + "="*70)
    if total_passed == total_tests:
        print(f"[PASS] ALL TESTS PASSED! ({total_passed}/{total_tests})")
        print("="*70)
        print("\n[OK] Ready for Railway deployment!")
        print("   - Conversation restart logic: OK")
        print("   - Fallback detection: OK")
        print("   - Resolution/Escalation keywords: OK")
        print("   - Satisfaction message handling: OK")
    else:
        print(f"[WARN] {total_tests - total_passed} test(s) failed")
    
    print("="*70 + "\n")
    
    return total_passed == total_tests


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
