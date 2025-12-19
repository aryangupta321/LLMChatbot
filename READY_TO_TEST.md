# READY TO TEST - ACTION ITEMS

## ✅ What's Done
- Code fixed and committed to GitHub ✅
- Visitor API v1 implemented ✅  
- Bot preview validation added ✅
- Escape sequences fixed ✅
- All pushed to main branch ✅

## 🔴 What YOU Need to Do NOW

### Step 1: Restart Railway Service
This is **CRITICAL** - the code changes won't work until you do this!

1. Open: https://railway.app/dashboard
2. Click on your project
3. Click the **"web"** service
4. Click **Settings** (gear icon in top right)
5. Scroll down and click **RESTART**
6. Wait 2-3 minutes for the service to rebuild and deploy

### Step 2: Verify Deployment
After 2-3 minutes, check Railway logs:

1. Go to https://railway.app/dashboard
2. Click "web" service
3. Click **Logs** tab
4. You should see:
   ```
   Visitor API v1 call - POST https://salesiq.zoho.in/api/visitor/v1/rtdsportal/conversations
   ```

### Step 3: Test with /test/salesiq-transfer Endpoint
Run this PowerShell command:

```powershell
$result = Invoke-RestMethod -Uri "https://web-production-3032d.up.railway.app/test/salesiq-transfer" -Method GET
$result | ConvertTo-Json
```

**Expected Response** (SUCCESS - 201 Created):
```json
{
  "user_id": "test.visitor@acecloudhosting.com",
  "result": {
    "success": true,
    "endpoint": "https://salesiq.zoho.in/api/visitor/v1/rtdsportal/conversations",
    "data": {...}
  }
}
```

### Step 4: Test on SalesIQ Chat Widget

**⚠️ IMPORTANT**: Bot preview sessions (botpreview_...) cannot be transferred!

#### Option A: Real Website Widget (BEST)
1. Go to your actual website (with SalesIQ widget)
2. Open chat as a real user
3. Click "📞 Instant Chat" button
4. You should be transferred to support

#### Option B: Simulate via POST
```powershell
$payload = @{
    visitor_user_id = "customer@example.com"
    conversation = "Help needed"
    app_id = "2782000012893013"
    department_id = "2782000000002013"
    visitor = @{
        name = "Test Customer"
        email = "customer@example.com"
    }
} | ConvertTo-Json

Invoke-RestMethod `
  -Uri "https://web-production-3032d.up.railway.app/test/salesiq-transfer" `
  -Method POST `
  -Body $payload `
  -ContentType "application/json"
```

#### Option C: Postman Direct Test
```
POST https://salesiq.zoho.in/api/visitor/v1/rtdsportal/conversations

Headers:
Authorization: Zoho-oauthtoken 1000.13cab6fc77c750790b7f03fa77df52cf.ea9099888c77b8d5b1561efaf340f0b0
Content-Type: application/json

Body:
{
  "app_id": "2782000012893013",
  "department_id": "2782000000002013",
  "question": "Test transfer",
  "visitor": {
    "user_id": "test@example.com",
    "name": "Test User",
    "email": "test@example.com"
  }
}
```

Expected: **201 Created** response

---

## 🎯 What Changed

### The Problem
Your code was using **WRONG API** - Operator API v2 instead of Visitor API v1, causing `tag_ids` error

### The Solution
- ✅ Switched to correct Visitor API v1 endpoint: `/api/visitor/v1/...`
- ✅ Fixed payload structure with nested `visitor` object
- ✅ Uses real visitor email as user_id (not bot preview IDs)
- ✅ Added validation to reject invalid bot preview sessions

### Files Modified
1. `zoho_api_simple.py` - API integration
2. `llm_chatbot.py` - Webhook handler and test endpoints

---

## 📌 Key Facts

| Item | Value |
|------|-------|
| API Endpoint | `https://salesiq.zoho.in/api/visitor/v1/rtdsportal/conversations` |
| Auth Header | `Authorization: Zoho-oauthtoken {token}` |
| OAuth Scope | `SalesIQ.Conversations.CREATE` |
| Bot Preview Status | ❌ **CANNOT be transferred** |
| Real Visitor Email | ✅ **WORKS** |
| Payload Type | Nested visitor object (per official docs) |

---

## ❓ FAQ

**Q: Why is my bot preview not transferring?**
A: SalesIQ doesn't allow transfers for bot preview sessions. You must test with real visitors from your actual website widget or use a real email address.

**Q: I still see tag_ids error?**
A: Railway hasn't deployed the new code yet. Go to Railway dashboard and click **Restart** on the web service.

**Q: How do I know if it's working?**
A: Check Railway logs. Should show "201" status and "Visitor API v1" in the logs (not Operator API v2).

**Q: Can I test locally?**
A: Yes, see `LOCAL_TEST_RESULTS.md` - but you need valid OAuth token in env vars.

---

## 🚀 Timeline

| Step | Time | Action |
|------|------|--------|
| 1 | Now | Restart Railway service |
| 2 | +2-3 min | Service redeploys |
| 3 | +3-4 min | Test /test/salesiq-transfer endpoint |
| 4 | +4-5 min | Test with real visitor |
| 5 | +5-10 min | Verify conversation in SalesIQ |

**Total time: ~10 minutes**

---

## ✅ Success Indicators

You'll know it's working when you see:

1. Railway logs show: `Response Status: 201`
2. No more `tag_ids` error in logs
3. Visitor API v1 endpoint in logs (not Operator API v2)
4. New conversation appears in SalesIQ dashboard
5. Real visitor gets transferred to support team

---

## 🆘 Need Help?

Check these files for detailed info:
- `VISITOR_API_FIX_COMPLETE.md` - Technical details of the fix
- `LOCAL_TEST_RESULTS.md` - Local testing results
- `SALESIQ_WIDGET_TEST_GUIDE.md` - Complete testing guide

Git commits to verify:
- `44a4be4` - Fixed escape sequences
- `7082ff8` - Visitor API v1 implementation

Good luck! The fix is ready. Just restart Railway and test! 🎉
