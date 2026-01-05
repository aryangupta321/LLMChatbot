# Railway Environment Variables Setup Guide

## 🚀 Quick Start - Required Variables for Chatbot to Work

Your chatbot needs these environment variables on Railway. Without them, **chats won't transfer** and **callbacks won't be created**.

---

## 📋 Required Environment Variables

### 1. **OPENAI_API_KEY** ⭐ CRITICAL
**Purpose:** OpenAI API key for generating bot responses  
**Status:** ✅ REQUIRED - Bot won't work without it  
**How to Get:**
- Go to https://platform.openai.com/account/api-keys
- Create new API key or use existing one
- Copy the key (starts with `sk-proj-`)

**Format:**
```
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Example:**
```
OPENAI_API_KEY=sk-proj-1234567890abcdef
```

---

### 2. **SALESIQ_ACCESS_TOKEN** ⭐ CRITICAL FOR CHAT TRANSFER
**Purpose:** Zoho SalesIQ OAuth token for transferring chats to agents  
**Status:** ✅ REQUIRED - Chats won't transfer without it  
**Validity:** Token expires - need to refresh periodically  

**How to Get:**
1. Go to Zoho SalesIQ account
2. Navigate to: **Admin → API & Integration → OAuth Tokens**
3. Generate new token with scope:
   ```
   SalesIQ.conversations.CREATE
   SalesIQ.conversations.READ
   SalesIQ.conversations.UPDATE
   ```
4. Copy the access token

**Format:**
```
SALESIQ_ACCESS_TOKEN=1000.abcdef1234567890wxyz
```

**Example:**
```
SALESIQ_ACCESS_TOKEN=1000.abc123def456ghi789
```

---

### 3. **SALESIQ_DEPARTMENT_ID** ⭐ CRITICAL FOR CHAT TRANSFER
**Purpose:** Default Zoho SalesIQ department where chats are routed  
**Status:** ✅ REQUIRED - Chats need a department to route to  

**How to Get:**
1. Log into Zoho SalesIQ
2. Go to: **Settings → Departments**
3. Click on your department (e.g., "Support")
4. Look for **Department ID** in the URL or department settings
5. Copy the numeric ID

**Format:**
```
SALESIQ_DEPARTMENT_ID=123456789
```

**Example:**
```
SALESIQ_DEPARTMENT_ID=1234567890
```

---

### 4. **SALESIQ_APP_ID** ⭐ CRITICAL FOR CHAT TRANSFER
**Purpose:** Zoho SalesIQ application/widget ID  
**Status:** ✅ REQUIRED - Identifies which widget the chat comes from  

**How to Get:**
1. Log into Zoho SalesIQ
2. Go to: **Settings → Apps** or **Widgets**
3. Find your chat widget (e.g., "Support Chat")
4. Look for **App ID** or **Widget ID**
5. Copy the numeric ID

**Format:**
```
SALESIQ_APP_ID=987654321
```

**Example:**
```
SALESIQ_APP_ID=9876543210
```

---

### 5. **SALESIQ_SCREEN_NAME** (Optional, but recommended)
**Purpose:** Screen name in Zoho SalesIQ portal  
**Status:** ⚠️ OPTIONAL - Defaults to "rtdsportal"  
**Current Default:** `rtdsportal`

**Format:**
```
SALESIQ_SCREEN_NAME=rtdsportal
```

**Where to Find:**
- Check your SalesIQ URL: `https://salesiq.zoho.in/screen/...`
- The screen name appears in the URL

---

## 📊 Summary Table

| Variable Name | Required? | Purpose | Example |
|---|---|---|---|
| `OPENAI_API_KEY` | ✅ YES | Generate responses | `sk-proj-xxx` |
| `SALESIQ_ACCESS_TOKEN` | ✅ YES | Transfer chats | `1000.abc123` |
| `SALESIQ_DEPARTMENT_ID` | ✅ YES | Route to department | `1234567890` |
| `SALESIQ_APP_ID` | ✅ YES | Identify widget | `9876543210` |
| `SALESIQ_SCREEN_NAME` | ⚠️ OPTIONAL | Portal name | `rtdsportal` |
| `SALESIQ_WIDGET_CODE` | ⚠️ OPTIONAL | Embed snippet | `<script>...` |
| `PORT` | ⚠️ OPTIONAL | Server port | `8000` |
| `ERROR_ALERT_WEBHOOK` | ⚠️ OPTIONAL | Error notifications | `https://...` |

---

## ⚙️ How to Set Variables on Railway

### Method 1: Railway Dashboard (Easiest)
1. Go to Railway: https://railway.app
2. Open your project
3. Click on your service/app
4. Go to **Variables** tab
5. Click **Add Variable**
6. Enter key and value for each variable:
   ```
   Key: OPENAI_API_KEY
   Value: sk-proj-xxxxxxx
   ```
7. Click **Add** 
8. Repeat for all 4 required variables
9. Deploy (Railway will auto-redeploy)

### Method 2: Using Railway CLI
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link to your project
railway link

# Add variable
railway variables add OPENAI_API_KEY=sk-proj-xxxxx
railway variables add SALESIQ_ACCESS_TOKEN=1000.xxxxx
railway variables add SALESIQ_DEPARTMENT_ID=1234567890
railway variables add SALESIQ_APP_ID=9876543210

# Deploy
railway deploy
```

### Method 3: Via Git (using .env)
1. Create `.env` file locally (NOT committed to git):
   ```
   OPENAI_API_KEY=sk-proj-xxxxx
   SALESIQ_ACCESS_TOKEN=1000.xxxxx
   SALESIQ_DEPARTMENT_ID=1234567890
   SALESIQ_APP_ID=9876543210
   ```
2. Copy to Railway's environment
3. **Note:** Keep `.env` in `.gitignore` for security

---

## 🔍 Verification Steps

### Step 1: Check if Variables are Set
Go to Railway dashboard:
1. Click on your service
2. Go to **Variables** tab
3. You should see all 4 required variables:
   - ✅ `OPENAI_API_KEY`
   - ✅ `SALESIQ_ACCESS_TOKEN`
   - ✅ `SALESIQ_DEPARTMENT_ID`
   - ✅ `SALESIQ_APP_ID`

### Step 2: Check Railway Logs
1. Click **Deployments** tab
2. Open latest deployment
3. Check **Logs** for:
   ```
   SalesIQ API configured - department: 1234567890, app_id: 9876543210
   ```
   ✅ This means variables are loaded correctly

### Step 3: Look for These Success Messages
```
[INFO] Zoho API loaded successfully - SalesIQ enabled: True
[INFO] SalesIQ API configured - department: 1234567890, app_id: 9876543210
[INFO] [SalesIQ] Transferring 5 messages to agent
```

### Step 4: Look for These ERROR Messages (fix them!)
```
❌ [WARNING] SalesIQ API not configured - token: False, department: True, app_id: True
```
This means `SALESIQ_ACCESS_TOKEN` is missing!

```
❌ [WARNING] SalesIQ API not configured - token: True, department: False, app_id: True
```
This means `SALESIQ_DEPARTMENT_ID` is missing!

```
❌ [WARNING] SalesIQ API not configured - token: True, department: True, app_id: False
```
This means `SALESIQ_APP_ID` is missing!

---

## 🐛 Troubleshooting

### Problem: Chats Not Transferring
**Check:**
1. ✅ Is `SALESIQ_ACCESS_TOKEN` set?
   ```
   [WARNING] SalesIQ API not configured - token: False
   ```
2. ✅ Is `SALESIQ_DEPARTMENT_ID` set?
   ```
   [WARNING] SalesIQ API not configured - department: False
   ```
3. ✅ Is `SALESIQ_APP_ID` set?
   ```
   [WARNING] SalesIQ API not configured - app_id: False
   ```
4. ✅ Check Railway logs - any error messages?

**Fix:** Add missing variables and redeploy

---

### Problem: Callbacks Not Created
**Check:**
1. ✅ Is `SALESIQ_ACCESS_TOKEN` set? (needed for Desk API too)
2. ✅ Callbacks are simulated by default
   ```
   [INFO] [API] Fallback: Simulating callback ticket creation
   ```
3. ✅ To enable real callback creation, you'd need `DESK_ORGANIZATION_ID`

**Note:** Callbacks currently use fallback (simulation) - this is OK for testing

---

### Problem: Responses Not Generated
**Check:**
1. ✅ Is `OPENAI_API_KEY` set?
   ```
   openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
   ```
2. ✅ Is key valid? Test it:
   ```
   curl https://api.openai.com/v1/models \
     -H "Authorization: Bearer sk-proj-xxxxx"
   ```

**Fix:** Make sure key is valid and set correctly

---

## 🔐 Security Best Practices

### ✅ DO:
- Store sensitive keys only in Railway environment variables
- Never commit `.env` file to Git
- Use `.gitignore` to exclude `.env`:
  ```
  # .gitignore
  .env
  .env.local
  *.pem
  ```
- Rotate keys periodically (especially OAuth tokens)
- Use separate keys for development vs. production

### ❌ DON'T:
- Put keys in source code
- Commit `.env` to Git
- Share keys in chat/email
- Use same key for multiple environments
- Leave tokens with no expiration

---

## 🔄 Token Refresh (Important!)

### SALESIQ_ACCESS_TOKEN Expires
OAuth tokens from Zoho eventually expire. When that happens, chats won't transfer.

**Signs token expired:**
```
[ERROR] SalesIQ API failed: 401 - {"error": "invalid_token"}
```

**How to refresh:**
1. Log into Zoho SalesIQ
2. Go to: **Admin → API & Integration → OAuth Tokens**
3. Generate NEW access token
4. Update `SALESIQ_ACCESS_TOKEN` on Railway with new token
5. Redeploy

**Pro tip:** Set a calendar reminder to refresh token every 3 months

---

## 📝 Copy-Paste Template

Use this template when setting up Railway variables:

```
OPENAI_API_KEY=sk-proj-YOUR_OPENAI_KEY_HERE
SALESIQ_ACCESS_TOKEN=1000.YOUR_SALESIQ_TOKEN_HERE
SALESIQ_DEPARTMENT_ID=YOUR_DEPARTMENT_ID_HERE
SALESIQ_APP_ID=YOUR_APP_ID_HERE
SALESIQ_SCREEN_NAME=rtdsportal
PORT=8000
```

---

## 🚀 Deployment Checklist

Before deploying to Railway, verify:

- [ ] `OPENAI_API_KEY` is set and valid
- [ ] `SALESIQ_ACCESS_TOKEN` is set and not expired
- [ ] `SALESIQ_DEPARTMENT_ID` is set
- [ ] `SALESIQ_APP_ID` is set
- [ ] All 4 variables visible in Railway dashboard
- [ ] Latest code pushed to main branch
- [ ] Railway auto-deploy is enabled
- [ ] Check logs after deploy for success messages
- [ ] Test chat transfer with real widget

---

## 📞 Testing Chat Transfer

### Test Endpoint (GET)
```bash
curl http://your-railway-app.railway.app/test/salesiq-transfer
```

**Success response:**
```json
{
  "user_id": "test@example.com",
  "result": {
    "success": true,
    "message": "Chat transfer initiated"
  },
  "past_messages_sent": 2
}
```

**Failure (missing tokens):**
```json
{
  "user_id": "test@example.com",
  "result": {
    "success": true,
    "simulated": true,
    "message": "Chat transfer initiated (simulated)"
  }
}
```
Note: If simulated=true, your variables aren't set!

---

## 📊 How the Bot Works With These Variables

```
Customer sends message
        ↓
OPENAI_API_KEY → Generate response
        ↓
Customer wants to transfer
        ↓
SALESIQ_ACCESS_TOKEN → Authenticate API call
        ↓
SALESIQ_APP_ID → Identify which widget
        ↓
SALESIQ_DEPARTMENT_ID → Route to correct team
        ↓
Chat transferred to agent ✅
```

---

## 🎯 Next Steps

1. **Gather all 4 required values:**
   - OpenAI API key
   - SalesIQ access token
   - SalesIQ department ID
   - SalesIQ app ID

2. **Set them on Railway Dashboard:**
   - Go to Variables tab
   - Add each variable
   - Save

3. **Verify in Logs:**
   - Check deployment logs
   - Look for success messages
   - Fix any warnings

4. **Test the chatbot:**
   - Send test message
   - Request chat transfer
   - Verify it appears in SalesIQ

5. **Monitor:**
   - Check logs regularly
   - Watch for token expiration
   - Refresh token every 3 months

---

## 💬 Still Having Issues?

### Check These Logs on Railway:
```bash
# Look for these in Railway logs:

# ✅ Success
[INFO] SalesIQ API configured - department: 1234567890, app_id: 9876543210
[INFO] [SalesIQ] Transferring 5 messages to agent

# ❌ Failures
[WARNING] SalesIQ API not configured - token: False
[ERROR] [SalesIQ] API call failed: 401
[ERROR] [SalesIQ] API call failed: 403
```

### Common Issues & Fixes:

| Issue | Cause | Fix |
|---|---|---|
| "API not configured" | Missing env variables | Add all 4 variables to Railway |
| "401 Unauthorized" | Token expired or invalid | Regenerate token in Zoho SalesIQ |
| "403 Forbidden" | Insufficient permissions | Check token has correct scopes |
| "Chat simulated" | API disabled | Check variables are set |
| "Request timeout" | Network issue | Check Railway can access Zoho |

---

**Summary:** Set these 4 variables on Railway, and your chatbot will transfer chats and create callbacks! 🎉
