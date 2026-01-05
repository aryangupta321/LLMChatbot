# CRITICAL: SalesIQ and Desk APIs Are Disabled on Railway

## ❌ Current Issues

### 1. SalesIQ Chat Transfer: DISABLED
```
SalesIQ: API disabled - simulating transfer for aryan.gupta@acecloudhosting.com
```
**Root Cause**: Missing environment variables on Railway

### 2. Desk Callback: FIXED ✅
- Contact search now uses correct `email` parameter (was using `searchStr`)
- Deployed in commit a844de0

### 3. State Management: FIXED ✅
- Removed invalid `CLARIFYING` state reference
- PasswordResetHandler now uses `ISSUE_GATHERING` state

---

## ✅ SOLUTION: Set Railway Environment Variables

### Step 1: Go to Railway Dashboard
1. Open https://railway.app
2. Select your project: **LLMChatbot**
3. Click on your service
4. Go to **Variables** tab

### Step 2: Add These REQUIRED Variables

#### SalesIQ API (for Chat Transfer)
```
SALESIQ_ACCESS_TOKEN=your_salesiq_oauth_token_here
SALESIQ_DEPARTMENT_ID=2782000000002013
SALESIQ_APP_ID=2782000005628361
SALESIQ_SCREEN_NAME=rtdsportal
```

#### Zoho Desk API (for Callbacks)
```
DESK_ACCESS_TOKEN=your_desk_oauth_token_here
DESK_ORGANIZATION_ID=your_org_id_here
```

#### OpenAI API
```
OPENAI_API_KEY=your_openai_key
```

---

## 🔑 Where to Get Access Tokens

### SalesIQ Access Token
1. Go to: https://api-console.zoho.in/
2. Click **Self Client**
3. Select scopes:
   - `ZohoSalesIQ.conversations.ALL`
   - `ZohoSalesIQ.visitor.ALL`
4. Generate token
5. Copy the **Access Token** (NOT the Client ID/Secret)

### Desk Access Token
1. Go to: https://api-console.zoho.in/
2. Click **Self Client**
3. Select scopes:
   - `Desk.contacts.READ`
   - `Desk.contacts.CREATE`
   - `Desk.calls.CREATE`
4. Generate token
5. Copy the **Access Token**

---

## 🔍 How to Verify It's Working

After setting environment variables, Railway will redeploy automatically.

### Check Logs for These Messages:

**✅ SalesIQ ENABLED:**
```
SalesIQ Visitor API v1 ENABLED - department: 2782000000002013, app_id: 2782000005628361
```

**❌ SalesIQ DISABLED (current):**
```
SalesIQ Visitor API DISABLED - Missing config! token: False
```

**✅ Desk ENABLED:**
```
Desk API configured - org: your_org_id
```

---

## 📝 Quick Copy-Paste Format

Copy this and fill in your tokens:

```bash
# SalesIQ
SALESIQ_ACCESS_TOKEN=1000.xxxxxxxxxxxxxxxxxxxxxxxxxxxxx.yyyyyyyyyyyyyyyyyyyyyyyyyyyy
SALESIQ_DEPARTMENT_ID=2782000000002013
SALESIQ_APP_ID=2782000005628361
SALESIQ_SCREEN_NAME=rtdsportal

# Desk
DESK_ACCESS_TOKEN=1000.xxxxxxxxxxxxxxxxxxxxxxxxxxxxx.yyyyyyyyyyyyyyyyyyyyyyyyyyyy
DESK_ORGANIZATION_ID=YOUR_ORG_ID_HERE

# OpenAI
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxx
```

---

## ⚠️ Important Notes

1. **Access tokens expire** - regenerate if APIs stop working
2. **Don't share tokens** - they have full access to your accounts
3. **Railway auto-redeploys** when you change variables (takes 2-3 minutes)
4. **Bot preview sessions cannot transfer** - test with real visitor IDs only

---

## 🧪 Testing After Fix

1. **Test Callback Creation:**
   - Say "it's not working"
   - Click "📅 Schedule Callback"
   - Provide time and phone
   - Should see: "✓ Callback scheduled successfully"

2. **Test Chat Transfer:**
   - Say "transfer to agent" or "it's not working"
   - Click "📞 Instant Chat"
   - Should see: "✓ Your chat has been transferred to our support team"
   - **Note**: Use real visitor session, NOT bot preview

---

## 🎯 Current Status

| Feature | Status | Fix Commit |
|---------|--------|------------|
| False positive resolution | ✅ FIXED | 5ed0620 |
| past_messages TypeError | ✅ FIXED | 5ed0620 |
| Desk contact search | ✅ FIXED | a844de0 |
| CLARIFYING state error | ✅ FIXED | a844de0 |
| **SalesIQ disabled** | ❌ **NEEDS ENV VARS** | - |
| **Desk disabled** | ❌ **NEEDS ENV VARS** | - |

---

## 📞 Need Help?

If you're still having issues after setting env vars:
1. Check Railway logs for the "ENABLED" or "DISABLED" messages
2. Verify tokens are valid and not expired
3. Ensure you copied the full token (they're very long)
4. Make sure there are no extra spaces in the variable values
