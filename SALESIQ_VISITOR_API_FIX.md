# SalesIQ Visitor API Fix - Official Implementation

## 🚨 Critical Fix: Using Official SalesIQ Visitor API

**Issue**: We were using wrong API endpoint - need to use official **Visitor API** from documentation
**Solution**: Implemented correct Visitor API with proper payload structure

---

## 📋 Official API Documentation Analysis

### **Correct Endpoint:**
```
POST https://salesiq.zoho.in/api/visitor/v1/{screen_name}/conversations
```

### **Required Configuration (From Your URLs):**
- **Screen Name**: `rtdsportal` (from your SalesIQ URL)
- **Department ID**: `2782000000002013` (from department URL)
- **App ID**: `2782000012893013` (from bot configuration URL)

### **Official Payload Structure:**
```json
{
  "visitor": {
    "user_id": "session_123",
    "name": "Chat User", 
    "email": "support@acecloudhosting.com",
    "platform": "WebBot",
    "current_page": "https://acecloudhosting.com/support",
    "page_title": "Support Chat"
  },
  "app_id": "2782000012893013",
  "question": "User: QuickBooks frozen\nBot: Are you on dedicated server?...",
  "department_id": "2782000000002013"
}
```

---

## 🔧 Implementation Fixed

### **Updated .env Configuration:**
```env
# Zoho SalesIQ Visitor API Configuration
SALESIQ_ACCESS_TOKEN=1000.21a18fe9ce30e588db59c39b4524a22a.87a0b3df50ec313a84b5e92479c659c3
SALESIQ_DEPARTMENT_ID=2782000000002013
SALESIQ_SCREEN_NAME=rtdsportal
SALESIQ_APP_ID=2782000012893013
```

### **Updated API Endpoint:**
```python
# Before (Wrong)
self.base_url = "https://salesiq.zoho.in/api/v2"
endpoint = f"{self.base_url}/chats"

# After (Correct - Official Visitor API)
self.base_url = "https://salesiq.zoho.in/api/visitor/v1/rtdsportal"
endpoint = f"{self.base_url}/conversations"
```

### **Updated Payload Structure:**
```python
# Before (Wrong)
payload = {
    "visitor_id": visitor_id,
    "department_id": self.department_id,
    "conversation_history": conversation_history,
    "transfer_to": "human_agent"
}

# After (Correct - Official Format)
payload = {
    "visitor": {
        "user_id": visitor_id,
        "name": "Chat User",
        "email": "support@acecloudhosting.com",
        "platform": "WebBot"
    },
    "app_id": self.app_id,
    "question": conversation_history,
    "department_id": self.department_id
}
```

---

## 🚀 Deploy Fixed Implementation

### **Step 1: Deploy Immediately**
```bash
git add .
git commit -m "Fix: Implement official SalesIQ Visitor API

- Updated to use correct Visitor API endpoint: /api/visitor/v1/rtdsportal/conversations
- Fixed payload structure to match official documentation
- Added required app_id and screen_name configuration
- Should resolve 'Unsupported URL' error in SalesIQ widget"

git push origin main
```

### **Step 2: Verify Health Check**
```
GET https://your-railway-app.railway.app/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "salesiq_api": "enabled",
  "salesiq_token": "configured",
  "department_id": "2782000000002013"
}
```

### **Step 3: Test SalesIQ Widget**
**Should no longer show "Unsupported URL" error**

---

## 🧪 Test Real Chat Transfer

### **In SalesIQ Widget:**
```
1. User: "QuickBooks is frozen"
2. Bot: "Are you on dedicated or shared server?"
3. User: "Dedicated"
4. Bot: "Step 1: Right-click taskbar..."
5. User: "Still not working"
6. Bot: Shows 3 options
7. User: "1" (instant chat)
8. Bot: "Connecting you with a support agent..."
```

### **Expected API Call:**
```http
POST https://salesiq.zoho.in/api/visitor/v1/rtdsportal/conversations
Authorization: Bearer 1000.21a18fe9ce30e588db59c39b4524a22a.87a0b3df50ec313a84b5e92479c659c3
Content-Type: application/json

{
  "visitor": {
    "user_id": "session_123",
    "name": "Chat User",
    "email": "support@acecloudhosting.com",
    "platform": "WebBot",
    "current_page": "https://acecloudhosting.com/support",
    "page_title": "Support Chat"
  },
  "app_id": "2782000012893013",
  "question": "User: QuickBooks frozen\nBot: Are you on dedicated server?...",
  "department_id": "2782000000002013"
}
```

### **Expected Success Response:**
```json
{
  "url": "/api/visitor/v1/rtdsportal/conversations",
  "object": "conversations",
  "data": {
    "id": "d2e4771bec859eb6cdeccd9e347dd512076189d2ceb67633",
    "wms_chat_id": "LD_2243210259183736169_1681358420",
    "question": "User: QuickBooks frozen...",
    "department": {
      "id": "2782000000002013"
    },
    "visitor": {
      "user_id": "session_123",
      "email": "support@acecloudhosting.com",
      "name": "Chat User"
    },
    "chat_status": {
      "state_key": "waiting",
      "status_code": 0,
      "state": 1,
      "status_key": "open"
    }
  }
}
```

---

## 📊 Expected Results

### **Railway Logs (Success):**
```
[SalesIQ] Visitor API configured - screen: rtdsportal, department: 2782000000002013
[SalesIQ] User selected: Instant Chat Transfer
[SalesIQ] Creating SalesIQ conversation for visitor session_123
[SalesIQ] Visitor API payload: user_id=session_123, department_id=2782000000002013
[SalesIQ] SalesIQ conversation created successfully
[SalesIQ] API result: {"success": true, "data": {...}}
```

### **SalesIQ Dashboard:**
- ✅ **New conversation appears** in operator queue
- ✅ **Assigned to Support(QB & App Hosting)** department
- ✅ **Full conversation history** in question field
- ✅ **Visitor info populated** correctly
- ✅ **Operator gets notification**

### **SalesIQ Widget:**
- ✅ **No "Unsupported URL" error**
- ✅ **Bot responds normally**
- ✅ **Chat transfer works**
- ✅ **Seamless handover to operator**

---

## 🔍 Key Differences

### **API Endpoint:**
- **Before**: `/api/v2/chats` ❌
- **After**: `/api/visitor/v1/rtdsportal/conversations` ✅

### **Payload Structure:**
- **Before**: Flat structure ❌
- **After**: Nested visitor object ✅

### **Required Fields:**
- **Before**: Missing app_id, screen_name ❌
- **After**: All required fields included ✅

### **OAuth Scope:**
- **Required**: `SalesIQ.Conversations.CREATE` ✅
- **Your Token Has**: `SalesIQ.conversations.ALL` ✅ (includes CREATE)

---

## 🎯 What This Fixes

### **1. Unsupported URL Error**
- **Cause**: Wrong API endpoint
- **Fix**: Using official Visitor API endpoint

### **2. API Payload Rejection**
- **Cause**: Incorrect payload structure
- **Fix**: Official payload format with visitor object

### **3. Missing Required Fields**
- **Cause**: Missing app_id and screen_name
- **Fix**: Added from your SalesIQ URLs

### **4. Chat Transfer Failure**
- **Cause**: API not creating conversations
- **Fix**: Proper conversation creation via Visitor API

---

## ✅ Final Configuration Summary

### **From Your SalesIQ URLs:**
- **Bot Config**: `https://salesiq.zoho.in/rtdsportal/settings/bot/zobot/2782000012893013/configuration`
  - **App ID**: `2782000012893013`
- **Department**: `https://salesiq.zoho.in/rtdsportal/settings/departments/edit/2782000000002013`
  - **Department ID**: `2782000000002013`
- **Screen Name**: `rtdsportal` (from URL path)

### **API Implementation:**
- **Endpoint**: `https://salesiq.zoho.in/api/visitor/v1/rtdsportal/conversations`
- **Method**: `POST`
- **Auth**: `Bearer 1000.21a18fe9ce30e588db59c39b4524a22a.87a0b3df50ec313a84b5e92479c659c3`
- **Scope**: `SalesIQ.Conversations.CREATE` ✅

---

**Deploy this fix immediately - it should resolve the "Unsupported URL" error and enable real chat transfers!** 🚀

**This is the correct implementation according to official SalesIQ Visitor API documentation.**