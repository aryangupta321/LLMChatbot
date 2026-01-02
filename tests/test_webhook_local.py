#!/usr/bin/env python3
"""
Quick test script to verify webhook functionality
"""

import requests
import json

def test_webhook_locally():
    """Test the webhook endpoint locally"""
    
    # Test data similar to what SalesIQ sends
    test_payload = {
        "visitor": {
            "id": "test_visitor_123",
            "active_conversation_id": "test_session_123"
        },
        "message": {
            "text": "Hello, I need help with QuickBooks"
        },
        "chat": {
            "id": "test_chat_123"
        }
    }
    
    try:
        # Test GET endpoint first
        print("Testing GET /webhook/salesiq...")
        response = requests.get("http://localhost:8000/webhook/salesiq")
        print(f"GET Status: {response.status_code}")
        print(f"GET Response: {response.json()}")
        print()
        
        # Test POST endpoint
        print("Testing POST /webhook/salesiq...")
        response = requests.post(
            "http://localhost:8000/webhook/salesiq",
            json=test_payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"POST Status: {response.status_code}")
        print(f"POST Response: {response.json()}")
        print()
        
        # Test health endpoint
        print("Testing /health...")
        response = requests.get("http://localhost:8000/health")
        print(f"Health Status: {response.status_code}")
        print(f"Health Response: {response.json()}")
        
    except requests.exceptions.ConnectionError:
        print("❌ Server not running. Start with: python llm_chatbot.py")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_webhook_locally()