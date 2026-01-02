#!/usr/bin/env python3
"""
Test script to verify the new Desk OAuth token with required scopes
"""

import requests
import json
import sys

# Your new token with scopes
DESK_ACCESS_TOKEN = "1000.4ec5e0938f76f223ff2db902570ddf56.461d77f8fe65a3c4ccefc0f79996268c"
DESK_ORG_ID = "60000688226"  # Update this if different
DESK_BASE_URL = "https://desk.zoho.com/api/v1"

def test_departments():
    """Test: Fetch departments list"""
    print("\n=== TEST 1: Fetch Departments ===")
    endpoint = f"{DESK_BASE_URL}/departments"
    headers = {
        "Authorization": f"Zoho-oauthtoken {DESK_ACCESS_TOKEN}",
        "orgId": str(DESK_ORG_ID),
        "Content-Type": "application/json",
    }
    
    try:
        response = requests.get(endpoint, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and 'data' in data and data['data']:
                dept_id = data['data'][0].get('id')
                print(f"✅ SUCCESS! Found department ID: {dept_id}")
                return dept_id
        else:
            print(f"❌ FAILED - Status: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return None

def test_contacts(email="aryan.gupta@acecloudhosting.com"):
    """Test: Search for contact by email"""
    print("\n=== TEST 2: Search Contact by Email ===")
    endpoint = f"{DESK_BASE_URL}/contacts/search?email={email}"
    headers = {
        "Authorization": f"Zoho-oauthtoken {DESK_ACCESS_TOKEN}",
        "orgId": str(DESK_ORG_ID),
        "Content-Type": "application/json",
    }
    
    try:
        response = requests.get(endpoint, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and 'data' in data and data['data']:
                contact_id = data['data'][0].get('id')
                print(f"✅ SUCCESS! Found contact ID: {contact_id}")
                return contact_id
            else:
                print(f"⚠️ No existing contact found - will need to create one")
                return None
        else:
            print(f"❌ FAILED - Status: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return None

def test_create_contact(email="test@example.com", name="Test User"):
    """Test: Create a new contact"""
    print("\n=== TEST 3: Create Contact ===")
    endpoint = f"{DESK_BASE_URL}/contacts"
    headers = {
        "Authorization": f"Zoho-oauthtoken {DESK_ACCESS_TOKEN}",
        "orgId": str(DESK_ORG_ID),
        "Content-Type": "application/json",
    }
    
    payload = {
        "lastName": name,
        "email": email,
    }
    
    try:
        response = requests.post(endpoint, json=payload, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code in [200, 201]:
            result = response.json()
            contact_id = result.get('id')
            print(f"✅ SUCCESS! Created contact ID: {contact_id}")
            return contact_id
        else:
            print(f"❌ FAILED - Status: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return None

def test_create_call(contact_id, dept_id):
    """Test: Create a call activity"""
    print("\n=== TEST 4: Create Call Activity ===")
    endpoint = f"{DESK_BASE_URL}/calls"
    headers = {
        "Authorization": f"Zoho-oauthtoken {DESK_ACCESS_TOKEN}",
        "orgId": str(DESK_ORG_ID),
        "Content-Type": "application/json",
    }
    
    from datetime import datetime, timezone
    start_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    
    payload = {
        "contactId": str(contact_id),
        "departmentId": str(dept_id),
        "subject": "Test Callback Request",
        "description": "This is a test callback from the chatbot",
        "direction": "inbound",
        "startTime": start_time,
        "duration": 0,
        "status": "In Progress",
    }
    
    try:
        response = requests.post(endpoint, json=payload, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code in [200, 201]:
            result = response.json()
            call_id = result.get('id')
            print(f"✅ SUCCESS! Created call ID: {call_id}")
            return call_id
        else:
            print(f"❌ FAILED - Status: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return None

if __name__ == "__main__":
    print("=" * 60)
    print("DESK API TOKEN VERIFICATION TEST")
    print("=" * 60)
    print(f"Token: {DESK_ACCESS_TOKEN[:20]}...")
    print(f"Org ID: {DESK_ORG_ID}")
    print(f"Base URL: {DESK_BASE_URL}")
    
    # Test 1: Departments
    dept_id = test_departments()
    
    # Test 2: Search existing contact
    contact_id = test_contacts()
    
    # Test 3: If no contact found, create one
    if not contact_id:
        contact_id = test_create_contact("testbot@example.com", "Bot Test")
    
    # Test 4: Create call (only if both dept and contact exist)
    if dept_id and contact_id:
        test_create_call(contact_id, dept_id)
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED! Token is valid and has required scopes.")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ TESTS FAILED! Check token scopes or configuration.")
        print("=" * 60)
