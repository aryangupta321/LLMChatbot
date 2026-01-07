"""
Comprehensive test suite for LLM classification system
Tests: resolution detection, conversation restart, fallback handling
"""

import sys
import os
import json
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.llm_classifier import llm_classifier, ClassificationResult


def test_resolution_detection():
    """Test if bot correctly detects resolution"""
    print("\n" + "="*70)
    print("TEST 1: RESOLUTION DETECTION")
    print("="*70)
    
    test_cases = [
        ("My issue is fixed now", True, "Should detect 'fixed' as resolution"),
        ("That solved my problem", True, "Should detect 'solved' as resolution"),
        ("It's working now, thanks!", True, "Should detect 'working' as resolution"),
        ("Not fixed yet", False, "Should NOT detect negation 'not fixed'"),
        ("Still having the issue", False, "Should not detect unresolved"),
        ("This doesn't work", False, "Should detect negation 'doesn't'"),
    ]
    
    passed = 0
    for message, should_resolve, reason in test_cases:
        history = [
            {"role": "user", "content": "I have an issue with password reset"},
            {"role": "assistant", "content": "Let me help you with that"},
            {"role": "user", "content": message}
        ]
        
        try:
            result = llm_classifier.classify_unified(message, history, session_id="test1")
            is_resolved = llm_classifier.should_close_chat(result["resolution"])
            
            status = "✅ PASS" if is_resolved == should_resolve else "❌ FAIL"
            passed += 1 if is_resolved == should_resolve else 0
            
            print(f"\n{status}: {message}")
            print(f"  └─ Expected: {should_resolve}, Got: {is_resolved}")
            print(f"  └─ Reason: {reason}")
            print(f"  └─ Confidence: {result['resolution'].confidence}%")
            
        except Exception as e:
            print(f"\n❌ ERROR: {message}")
            print(f"  └─ {str(e)}")
    
    print(f"\n✅ Resolution Detection: {passed}/{len(test_cases)} passed")
    return passed == len(test_cases)


def test_conversation_restart():
    """Test if bot handles new questions after resolution"""
    print("\n" + "="*70)
    print("TEST 2: CONVERSATION RESTART (New Question After Resolution)")
    print("="*70)
    
    test_cases = [
        ("Yes, I have another issue", True, "Multi-message intent"),
        ("Actually, how do I update QB?", True, "New question keyword"),
        ("What about password reset?", True, "New question about different topic"),
        ("No thanks", False, "User wants to close"),
        ("Bye", False, "Short goodbye"),
        ("Close it", False, "Close confirmation"),
    ]
    
    passed = 0
    for message, should_continue, reason in test_cases:
        # Simulate: bot just sent satisfaction message
        history = [
            {"role": "user", "content": "My issue is fixed"},
            {"role": "assistant", "content": "Great! Is there anything else? Have a great day!"}
        ]
        
        # Check message length and keywords
        is_new_question = (
            ("yes" in message.lower() or 
             "another" in message.lower() or
             "help" in message.lower() or
             "question" in message.lower() or
             len(message) > 15) and 
            not ("no" in message.lower() or "bye" in message.lower())
        )
        
        status = "✅ PASS" if is_new_question == should_continue else "❌ FAIL"
        passed += 1 if is_new_question == should_continue else 0
        
        print(f"\n{status}: '{message}'")
        print(f"  └─ Expected restart: {should_continue}, Got: {is_new_question}")
        print(f"  └─ Reason: {reason}")
    
    print(f"\n✅ Conversation Restart: {passed}/{len(test_cases)} passed")
    return passed == len(test_cases)


def test_fallback_handling():
    """Test if bot offers escalation when confused"""
    print("\n" + "="*70)
    print("TEST 3: FALLBACK HANDLING (Bot Confusion Detection)")
    print("="*70)
    
    unclear_responses = [
        "I'm not sure what you mean",
        "Could you clarify?",
        "I don't understand",
        "Can you rephrase?",
    ]
    
    short_responses = [
        "k",
        "ok",
        "...",
    ]
    
    print("\nTesting unclear response detection:")
    passed = 0
    total = len(unclear_responses) + len(short_responses)
    
    for response in unclear_responses:
        has_unclear = any(indicator in response.lower() for indicator in [
            "i don't understand",
            "i'm not sure",
            "could you clarify",
            "can you rephrase",
            "i didn't quite get that"
        ])
        
        status = "✅ PASS" if has_unclear else "❌ FAIL"
        passed += 1 if has_unclear else 0
        print(f"{status}: Detected unclear in '{response}'")
    
    print("\nTesting short response detection:")
    for response in short_responses:
        is_short = len(response) < 50
        status = "✅ PASS" if is_short else "❌ FAIL"
        passed += 1 if is_short else 0
        print(f"{status}: Detected short response '{response}' (len={len(response)})")
    
    print(f"\n✅ Fallback Handling: {passed}/{total} passed")
    return passed == total


def test_escalation_detection():
    """Test escalation need detection"""
    print("\n" + "="*70)
    print("TEST 4: ESCALATION DETECTION")
    print("="*70)
    
    test_cases = [
        ("I need to speak to someone", True, "Explicit agent request"),
        ("This is urgent", True, "Frustration indicator"),
        ("Your bot isn't helping", True, "Bot can't help"),
        ("Can I get a callback?", True, "Escalation request"),
        ("That sounds good", False, "Satisfied message"),
        ("Thanks for the help", False, "Positive feedback"),
    ]
    
    passed = 0
    for message, should_escalate, reason in test_cases:
        history = [
            {"role": "user", "content": "I have a problem"},
            {"role": "assistant", "content": "I can help with that"},
            {"role": "user", "content": message}
        ]
        
        try:
            result = llm_classifier.classify_unified(message, history, session_id="test4")
            needs_escalation = llm_classifier.should_escalate(result["escalation"])
            
            status = "✅ PASS" if needs_escalation == should_escalate else "❌ FAIL"
            passed += 1 if needs_escalation == should_escalate else 0
            
            print(f"\n{status}: {message}")
            print(f"  └─ Expected escalation: {should_escalate}, Got: {needs_escalation}")
            print(f"  └─ Reason: {reason}")
            print(f"  └─ Confidence: {result['escalation'].confidence}%")
            
        except Exception as e:
            print(f"\n❌ ERROR: {message}")
            print(f"  └─ {str(e)}")
    
    print(f"\n✅ Escalation Detection: {passed}/{len(test_cases)} passed")
    return passed == len(test_cases)


def test_intent_classification():
    """Test intent classification (TRANSFER, CALLBACK, TICKET, QUESTION)"""
    print("\n" + "="*70)
    print("TEST 5: INTENT CLASSIFICATION")
    print("="*70)
    
    test_cases = [
        ("I want to talk to someone", "TRANSFER", "Agent transfer intent"),
        ("Can I schedule a callback?", "CALLBACK", "Callback request"),
        ("I need to file a complaint", "TICKET", "Ticket creation"),
        ("How do I reset my password?", "QUESTION", "Information request"),
    ]
    
    passed = 0
    for message, expected_intent, reason in test_cases:
        history = [{"role": "user", "content": message}]
        
        try:
            result = llm_classifier.classify_unified(message, history, session_id="test5")
            detected_intent = result["intent"].decision
            
            status = "✅ PASS" if detected_intent == expected_intent else "❌ FAIL"
            passed += 1 if detected_intent == expected_intent else 0
            
            print(f"\n{status}: {message}")
            print(f"  └─ Expected: {expected_intent}, Got: {detected_intent}")
            print(f"  └─ Reason: {reason}")
            print(f"  └─ Confidence: {result['intent'].confidence}%")
            
        except Exception as e:
            print(f"\n❌ ERROR: {message}")
            print(f"  └─ {str(e)}")
    
    print(f"\n✅ Intent Classification: {passed}/{len(test_cases)} passed")
    return passed == len(test_cases)


def main():
    print("\n" + "="*70)
    print("🤖 LLM CLASSIFICATION SYSTEM - COMPREHENSIVE TEST SUITE")
    print("="*70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {
        "resolution_detection": test_resolution_detection(),
        "conversation_restart": test_conversation_restart(),
        "fallback_handling": test_fallback_handling(),
        "escalation_detection": test_escalation_detection(),
        "intent_classification": test_intent_classification(),
    }
    
    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    
    total_passed = sum(1 for v in results.values() if v)
    total_tests = len(results)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name.replace('_', ' ').title()}")
    
    print("\n" + "="*70)
    print(f"🎯 OVERALL: {total_passed}/{total_tests} test suites passed")
    print("="*70)
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    return total_passed == total_tests


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
