#!/usr/bin/env python3
"""
Test script to verify Railway deployment webhook
"""

import requests
import json

def test_railway_webhook():
    """Test the webhook endpoint on Railway"""
    
    railway_url = "https://web-production-3032d.up.railway.app"
    
    # Test data similar to what SalesIQ sends
    test_payload = {
        "visitor": {
            "id": "test_visitor_123",
            "active_conversation_id": "test_session_123"
        },
        "message": {
            "text": "Hello, I need help"
        },
        "chat": {
            "id": "test_chat_123"
        }
    }
    
    try:
        # Test root endpoint
        print("Testing Railway deployment...")
        response = requests.get(f"{railway_url}/")
        print(f"Root Status: {response.status_code}")
        print(f"Root Response: {response.json()}")
        print()
        
        # Test GET webhook endpoint
        print("Testing GET /webhook/salesiq...")
        response = requests.get(f"{railway_url}/webhook/salesiq")
        print(f"GET Status: {response.status_code}")
        print(f"GET Response: {response.json()}")
        print()
        
        # Test POST webhook endpoint
        print("Testing POST /webhook/salesiq...")
        response = requests.post(
            f"{railway_url}/webhook/salesiq",
            json=test_payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        print(f"POST Status: {response.status_code}")
        print(f"POST Response: {response.json()}")
        print()
        
        # Test health endpoint
        print("Testing /health...")
        response = requests.get(f"{railway_url}/health")
        print(f"Health Status: {response.status_code}")
        print(f"Health Response: {response.json()}")
        
        print("\n✅ All tests completed!")
        
    except requests.exceptions.Timeout:
        print("❌ Request timeout - server might be slow to respond")
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - check if Railway deployment is running")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_railway_webhook()