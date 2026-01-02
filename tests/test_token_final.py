#!/usr/bin/env python3
"""Test the new Desk token with correct .in domain"""

import requests
from datetime import datetime, timezone

token = '1000.4ec5e0938f76f223ff2db902570ddf56.461d77f8fe65a3c4ccefc0f79996268c'
org_id = '60000688226'
base_url = 'https://desk.zoho.in/api/v1'

headers = {
    'Authorization': f'Zoho-oauthtoken {token}',
    'orgId': str(org_id),
    'Content-Type': 'application/json',
}

print('=== TEST 1: Fetch Departments ===')
resp = requests.get(f'{base_url}/departments', headers=headers, timeout=10)
print(f'Status: {resp.status_code}')
if resp.status_code == 200:
    data = resp.json()
    dept_id = data['data'][0]['id']
    dept_name = data['data'][0]['name']
    print(f'✅ Department found: {dept_id}')
    print(f'Department name: {dept_name}')
else:
    print(f'❌ Failed: {resp.json()}')
    exit()

print('\n=== TEST 2: Search Contact ===')
email = 'aryan.gupta@acecloudhosting.com'
resp = requests.get(f'{base_url}/contacts/search?email={email}', headers=headers, timeout=10)
print(f'Status: {resp.status_code}')
if resp.status_code == 200:
    data = resp.json()
    if data.get('data'):
        contact_id = data['data'][0]['id']
        print(f'✅ Contact found: {contact_id}')
    else:
        print(f'⚠️ No existing contact found, will create one')
        # Create contact
        payload = {'lastName': 'Gupta', 'email': email}
        resp = requests.post(f'{base_url}/contacts', json=payload, headers=headers, timeout=10)
        if resp.status_code in [200, 201]:
            contact_id = resp.json()['id']
            print(f'✅ Contact created: {contact_id}')
        else:
            print(f'❌ Failed to create: {resp.json()}')
            exit()
else:
    print(f'❌ Failed: {resp.json()}')
    exit()

print('\n=== TEST 3: Create Callback Call ===')
start_time = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.000Z')
payload = {
    'contactId': str(contact_id),
    'departmentId': str(dept_id),
    'subject': 'Callback Request - Aryan Gupta',
    'description': 'Customer requested callback\nPhone: 9876543210\nPreferred time: Tomorrow 2PM',
    'direction': 'inbound',
    'startTime': start_time,
    'duration': 0,
    'status': 'In Progress',
}
resp = requests.post(f'{base_url}/calls', json=payload, headers=headers, timeout=10)
print(f'Status: {resp.status_code}')
if resp.status_code in [200, 201]:
    result = resp.json()
    print(f'✅ Callback created successfully!')
    print(f'Call ID: {result.get("id")}')
    web_url = result.get('webUrl')
    if web_url:
        print(f'Web URL: {web_url}')
else:
    print(f'❌ Failed: {resp.json()}')
    exit()

print('\n' + '='*50)
print('✅ ALL TESTS PASSED! Token is working perfectly.')
print('='*50)
