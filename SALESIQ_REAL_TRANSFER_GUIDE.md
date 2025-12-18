# SalesIQ Real Transfer for External LLM Bot

## 🎯 The Real Issue

**Zobot vs External Bot:**
- **Zobot** (SalesIQ internal): Has built-in transfer functions
- **External LLM Bot** (your webhook): Needs API calls to transfer

## 🔧 How External Bot Transfers Work

### **Method 1: Chat Session Transfer API**
```http
POST https://salesiq.zoho.in/api/v2/chats/{chat_id}/transfer
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "department_id": "2782000000002013",
  "message": "User requesting human assistance"
}
```

### **Method 2: Create Agent Chat Session**
```http
POST https://salesiq.zoho.in/api/v2/chats
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "visitor_id": "session_123",
  "department_id": "2782000000002013", 
  "status": "waiting",
  "message": "Transfer from bot"
}
```

### **Method 3: Update Chat Status**
```http
PATCH https://salesiq.zoho.in/api/v2/chats/{chat_id}
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "status": "waiting_for_agent",
  "department_id": "2782000000002013"
}
```

## 🔍 Finding the Correct API

**The issue:** We need to find the **exact API endpoint** that works for your SalesIQ setup.

**Let me create a test script** to try different endpoints:

```python
def test_salesiq_endpoints(session_id, access_token, department_id):
    """Test different SalesIQ transfer endpoints"""
    
    endpoints = [
        # Method 1: Direct transfer
        {
            "url": f"https://salesiq.zoho.in/api/v2/chats/{session_id}/transfer",
            "method": "POST",
            "payload": {"department_id": department_id}
        },
        
        # Method 2: Update chat status
        {
            "url": f"https://salesiq.zoho.in/api/v2/chats/{session_id}",
            "method": "PATCH", 
            "payload": {"status": "waiting_for_agent", "department_id": department_id}
        },
        
        # Method 3: Create new chat
        {
            "url": "https://salesiq.zoho.in/api/v2/chats",
            "method": "POST",
            "payload": {"visitor_id": session_id, "department_id": department_id}
        },
        
        # Method 4: Visitor API
        {
            "url": "https://salesiq.zoho.in/api/visitor/v1/rtdsportal/conversations",
            "method": "POST", 
            "payload": {
                "visitor": {"user_id": session_id},
                "department_id": department_id,
                "question": "Transfer request"
            }
        }
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.request(
                endpoint["method"],
                endpoint["url"],
                json=endpoint["payload"],
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            print(f"✅ {endpoint['method']} {endpoint['url']}")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code in [200, 201]:
                return endpoint  # Found working endpoint!
                
        except Exception as e:
            print(f"❌ {endpoint['url']}: {str(e)}")
    
    return None
```

## 🚀 Implementation Strategy

### **Step 1: Test API Endpoints**
Let me update the bot to **test multiple endpoints** and find the one that works:

### **Step 2: Get Chat ID**
The key issue might be that we need the **actual chat ID** from SalesIQ, not just the session ID.

**From your webhook payload, we should extract:**
- `chat_id` or `conversation_id`
- `visitor_id` 
- `session_id`

### **Step 3: Use Correct Transfer Method**
Once we find the working endpoint, implement real transfers.

## 🔍 What We Need to Check

### **1. Webhook Payload Analysis**
Let's see what **exact IDs** SalesIQ sends in the webhook:

```python
# In webhook handler, log all IDs
logger.info(f"Full request: {request}")
logger.info(f"Visitor: {request.get('visitor', {})}")
logger.info(f"Chat: {request.get('chat', {})}")
logger.info(f"Conversation: {request.get('conversation', {})}")
```

### **2. API Token Scopes**
Your token has:
- `SalesIQ.conversations.ALL` ✅
- `SalesIQ.operators.ALL` ✅

This should be sufficient for transfers.

### **3. Department Configuration**
- Department ID: `2782000000002013` ✅
- Make sure operators are **online** in this department
- Check department **availability hours**

## 🎯 Next Steps

1. **Update bot** to log all webhook data
2. **Test different API endpoints** systematically  
3. **Find the working transfer method**
4. **Implement real transfers**

## 💡 Alternative: Manual Transfer Trigger

**If API transfers don't work immediately:**

```python
# Send special message that triggers SalesIQ's built-in transfer
return {
    "action": "reply",
    "replies": ["TRANSFER_TO_AGENT"],  # Special keyword
    "session_id": session_id
}
```

**Then configure SalesIQ to:**
- Watch for "TRANSFER_TO_AGENT" message
- Automatically transfer when this message appears

---

**Let me implement the endpoint testing approach first to find what works!**