# SalesIQ Widget Testing Guide - Visitor API v1

## 🎯 Summary of Changes

Your SalesIQ chat transfer was failing because:
1. ❌ Wrong API endpoint (Operator API v2 instead of Visitor API v1)
2. ❌ Wrong payload structure (flat fields instead of nested visitor object)
3. ❌ Using bot preview IDs (botpreview_...) which **CANNOT** be transferred

**All issues are NOW FIXED!** ✅

---

## 📋 How to Test (Step by Step)

### Step 1: Wait for Railway Deployment
✅ **Status**: Code committed and pushed to GitHub
- Commit: `44a4be4` - Fixed
- Previous: `7082ff8` - Visitor API v1 implementation  

**ACTION REQUIRED**: You need to manually restart Railway:
1. Go to: https://railway.app/dashboard
2. Click on "web" service
3. Click **Settings** (gear icon)
4. Click **RESTART**
5. Wait 2-3 minutes for the app to rebuild and deploy

---

### Step 2: Quick Test (After Railway Restart)
Once Railway is restarted and deployed, test the endpoint:

```powershell
# Test the visitor API
$result = Invoke-RestMethod -Uri "https://your-railway-domain.up.railway.app/test/salesiq-transfer" -Method GET
$result | ConvertTo-Json | Write-Host
```

**Expected Success Response:**
```json
{
  "user_id": "test.visitor@acecloudhosting.com",
  "result": {
    "success": true,
    "endpoint": "https://salesiq.zoho.in/api/visitor/v1/rtdsportal/conversations",
    "data": {
      "url": "/api/visitor/v1/rtdsportal/conversations",
      "object": "conversations",
      "data": {
        "id": "conversation_id_here",
        "wms_chat_id": "LD_xxx"
      }
    }
  }
}
```

---

### Step 3: Actual Widget Test on SalesIQ

#### ⚠️ **IMPORTANT: Bot Preview CANNOT be Transferred**
The SalesIQ bot preview in your dashboard uses `botpreview_...` IDs which are **internal testing only**. These cannot be transferred to agents.

#### ✅ **Solution: Use Real Visitors Instead**

**Option A: Test on Your Live Website** (RECOMMENDED)
1. Add the SalesIQ widget code to your actual website
2. Visit your website as a real user (not from dashboard preview)
3. Open the chat widget
4. Type a message
5. Click "📞 Instant Chat" button
6. You will be transferred to a real agent
7. Conversation appears in SalesIQ under that visitor

**Option B: Simulate Real Visitor via API**
Use the POST endpoint to simulate a real visitor transfer:

```powershell
$payload = @{
    visitor_user_id = "customer@yourdomain.com"
    conversation = "I need help with QuickBooks setup"
    app_id = "2782000012893013"
    department_id = "2782000000002013"
    visitor = @{
        name = "Customer Name"
        email = "customer@yourdomain.com"
    }
} | ConvertTo-Json

Invoke-RestMethod `
  -Uri "https://your-railway-domain.up.railway.app/test/salesiq-transfer" `
  -Method POST `
  -Body $payload `
  -ContentType "application/json" `
  | ConvertTo-Json | Write-Host
```

**Option C: Direct SalesIQ API Test (Postman)**
```
POST https://salesiq.zoho.in/api/visitor/v1/rtdsportal/conversations

Headers:
Authorization: Zoho-oauthtoken 1000.13cab6fc77c750790b7f03fa77df52cf.ea9099888c77b8d5b1561efaf340f0b0
Content-Type: application/json

Body:
{
  "app_id": "2782000012893013",
  "department_id": "2782000000002013",
  "question": "Test transfer from Postman",
  "visitor": {
    "user_id": "test.customer@example.com",
    "name": "Test Customer",
    "email": "test.customer@example.com"
  }
}
```

Expected response code: **201 Created**

---

## 🔍 Verification Checklist

After Railway restarts and you deploy:

### ✅ Check 1: API Endpoint is Correct
Look at Railway logs:
```
SalesIQ: Visitor API v1 call - POST https://salesiq.zoho.in/api/visitor/v1/rtdsportal/conversations
```

### ✅ Check 2: Payload Structure is Correct
Logs should show:
```
SalesIQ: Payload - app_id=2782000012893013, dept=2782000000002013, visitor_user_id=..., visitor_email=...
```

### ✅ Check 3: Response Status is 201 (Not 400)
```
SalesIQ: Response Status: 201
```

### ✅ Check 4: No More tag_ids Errors
You should NOT see:
```
"json_key":"tag_ids","message":"Either the request parameters are invalid or absent"
```

### ✅ Check 5: Conversation Created in SalesIQ
- Log into SalesIQ dashboard
- Go to **Conversations**
- Look for new conversation from test visitor email
- Should show in **Waiting** status

---

## 🚨 Troubleshooting

### Problem: Still seeing 400 error with tag_ids
**Solution**: Railway hasn't deployed the new code yet
- Go to Railway dashboard
- Click "Deployments" tab
- Verify you see the latest commit: `44a4be4`
- If not, click "Redeploy" on the latest deployment
- Wait 2-3 minutes

### Problem: Still seeing bot preview message
**Solution**: Test with real visitor email instead
- Don't test with `botpreview_...` IDs
- Use real email: `customer@acecloudhosting.com`
- Or use the `/test/salesiq-transfer` endpoint

### Problem: 1008/1009 OAuth errors
**Solution**: OAuth token issue
- Verify `SALESIQ_ACCESS_TOKEN` env var on Railway
- Token must have scope: `SalesIQ.Conversations.CREATE`
- Must be Org OAuth token (not User token)

### Problem: Conversation not appearing in SalesIQ
**Possible causes**:
1. Wrong app_id - use: `2782000012893013`
2. Wrong department_id - use: `2782000000002013`
3. OAuth token expired - generate new token
4. Invalid visitor email - must be non-empty

---

## 📊 What Got Fixed

### Code Changes
| File | Change | Status |
|------|--------|--------|
| zoho_api_simple.py | Changed to Visitor API v1 endpoint | ✅ Committed |
| zoho_api_simple.py | Fixed payload structure (nested visitor) | ✅ Committed |
| zoho_api_simple.py | Added bot preview validation | ✅ Committed |
| llm_chatbot.py | Updated webhook to use visitor email | ✅ Committed |
| llm_chatbot.py | Fixed test endpoints | ✅ Committed |
| llm_chatbot.py | Fixed string escape sequences | ✅ Committed |

### Environment Variables (No Changes Needed)
```
SALESIQ_ACCESS_TOKEN=1000.13cab6fc77c750790b7f03fa77df52cf.ea9099888c77b8d5b1561efaf340f0b0
SALESIQ_DEPARTMENT_ID=2782000000002013
SALESIQ_APP_ID=2782000012893013
SALESIQ_SCREEN_NAME=rtdsportal
```

Note: Removed need for SALESIQ_ORG_ID and SALESIQ_DEFAULT_TAG_ID (not needed for Visitor API)

---

## ✅ Final Steps

1. **Restart Railway** (critical!)
   - https://railway.app/dashboard → web service → Settings → Restart

2. **Wait 2-3 minutes** for deployment

3. **Test with /test/salesiq-transfer**
   ```powershell
   Invoke-RestMethod -Uri "https://your-app.up.railway.app/test/salesiq-transfer" -Method GET
   ```

4. **Verify in SalesIQ logs**
   - No `tag_ids` error
   - Status 201 (not 400)
   - Visitor API v1 endpoint

5. **Test with real visitor**
   - Real website widget, OR
   - POST endpoint with real email, OR
   - Postman direct test

Done! Transfer should work now! 🎉
