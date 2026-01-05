# 🚨 QUICK FIX: Railway Environment Variables Setup

## ❌ Current Issue
Your logs show:
```
[WARNING] SalesIQ Visitor API not fully configured - token: False, dept: False, app_id: False
[WARNING] Desk API not configured - simulated. token=False orgId=False
```

This means **environment variables are NOT set on Railway**.

---

## ✅ STEP-BY-STEP FIX

### 1️⃣ Go to Railway Dashboard
1. Open: https://railway.app
2. Click on your project: **"AGChatBot"** or similar
3. Click on your service/deployment
4. Click **"Variables"** tab on the left

---

### 2️⃣ Add These 4 Variables (Copy-Paste Each One)

Click **"+ New Variable"** for each:

#### Variable 1: OPENAI_API_KEY
```
Key: OPENAI_API_KEY
Value: sk-proj-YOUR_ACTUAL_OPENAI_KEY
```

#### Variable 2: SALESIQ_ACCESS_TOKEN
```
Key: SALESIQ_ACCESS_TOKEN
Value: 1000.YOUR_ACTUAL_SALESIQ_TOKEN
```

#### Variable 3: SALESIQ_DEPARTMENT_ID
```
Key: SALESIQ_DEPARTMENT_ID
Value: YOUR_DEPARTMENT_ID_NUMBER
```

#### Variable 4: SALESIQ_APP_ID
```
Key: SALESIQ_APP_ID
Value: YOUR_APP_ID_NUMBER
```

---

### 3️⃣ Optional (But Recommended) Variables

#### Variable 5: SALESIQ_SCREEN_NAME
```
Key: SALESIQ_SCREEN_NAME
Value: rtdsportal
```
*Note: Only add if different from "rtdsportal"*

#### Variable 6: DESK_ACCESS_TOKEN (for callback tickets)
```
Key: DESK_ACCESS_TOKEN
Value: 1000.YOUR_DESK_TOKEN
```

#### Variable 7: DESK_ORG_ID (for callback tickets)
```
Key: DESK_ORG_ID
Value: YOUR_DESK_ORG_ID
```

---

## 🔍 How to Get Each Value

### OPENAI_API_KEY
1. Go to: https://platform.openai.com/account/api-keys
2. Click "Create new secret key"
3. Copy the key (starts with `sk-proj-`)

### SALESIQ_ACCESS_TOKEN
1. Log into: https://salesiq.zoho.in
2. Go to: **Settings → Developers → API**
3. Click **"Generate Token"**
4. Select scopes:
   - ✅ `SalesIQ.conversations.CREATE`
   - ✅ `SalesIQ.conversations.READ`
   - ✅ `SalesIQ.conversations.UPDATE`
5. Copy the token (starts with `1000.`)

### SALESIQ_DEPARTMENT_ID
1. In SalesIQ, go to: **Settings → Departments**
2. Click on your department (e.g., "Support")
3. Look at the URL or department info
4. Copy the **numeric ID** (e.g., `1234567890`)

### SALESIQ_APP_ID
1. In SalesIQ, go to: **Settings → Brands/Widgets**
2. Click on your chat widget
3. Look for **App ID** or **Widget ID**
4. Copy the **numeric ID** (e.g., `9876543210`)

### DESK_ACCESS_TOKEN (Optional - for tickets)
1. Log into: https://desk.zoho.in
2. Go to: **Setup → API → OAuth**
3. Generate token with `Desk.tickets.CREATE` scope
4. Copy the token

### DESK_ORG_ID (Optional - for tickets)
1. In Zoho Desk, check your organization settings
2. Look for **Organization ID**
3. Copy the numeric ID

---

## 📋 Complete Railway Variables List

After adding all variables, you should see this in Railway:

```
✅ OPENAI_API_KEY = sk-proj-...
✅ SALESIQ_ACCESS_TOKEN = 1000...
✅ SALESIQ_DEPARTMENT_ID = 1234567890
✅ SALESIQ_APP_ID = 9876543210
⚠️ SALESIQ_SCREEN_NAME = rtdsportal (optional)
⚠️ DESK_ACCESS_TOKEN = 1000... (optional)
⚠️ DESK_ORG_ID = 123456 (optional)
```

---

## 🚀 After Adding Variables

### Railway will automatically:
1. ✅ Detect changes
2. ✅ Redeploy your app
3. ✅ Load new environment variables

### Check Logs After Redeploy

✅ **Success - You should see:**
```
[INFO] SalesIQ Visitor API v1 configured - department: 1234567890, app_id: 9876543210
[INFO] Desk API configured - org: 123456
[INFO] Zoho API loaded successfully - SalesIQ enabled: True
```

❌ **Still failing - You'll see:**
```
[WARNING] SalesIQ Visitor API not fully configured - token: False
```
→ Go back and check the variable names are EXACT (case-sensitive!)

---

## 🧪 Test After Setup

### 1. Check Railway Logs
Go to **Deployments → Latest → View Logs**

Look for:
```
✅ SalesIQ Visitor API v1 configured
✅ Zoho API loaded successfully - SalesIQ enabled: True
```

### 2. Test Chat Transfer
1. Open your chat widget
2. Say: "I need help with login"
3. Click: "📞 Instant Chat"
4. Check logs for:
   ```
   [INFO] [SalesIQ] Transferring 3 messages to agent
   [INFO] ✅ SalesIQ chat transfer successful
   ```

### 3. Test Callback
1. Open your chat widget
2. Say: "I need help"
3. Click: "📅 Schedule Callback"
4. Provide time and phone
5. Check logs for:
   ```
   [INFO] [Desk] Callback ticket created: CALL-001
   ```

---

## 🐛 Common Issues

### Issue 1: Variables Not Loading
**Symptom:**
```
[WARNING] token: False, dept: False
```

**Fix:**
1. Check Railway Variables tab
2. Verify all 4 variables are there
3. Check for typos in variable names
4. Click "Redeploy" if needed

---

### Issue 2: Token Invalid
**Symptom:**
```
[ERROR] 401 Unauthorized
```

**Fix:**
1. Token expired → Generate new token
2. Update `SALESIQ_ACCESS_TOKEN` on Railway
3. Wait for auto-redeploy

---

### Issue 3: Wrong Department ID
**Symptom:**
```
[ERROR] 403 Forbidden - department not found
```

**Fix:**
1. Verify department ID in SalesIQ
2. Update `SALESIQ_DEPARTMENT_ID` on Railway
3. Must be numeric only (no quotes)

---

## 📝 Exact Variable Names (Copy These!)

```bash
# Required for bot to work:
OPENAI_API_KEY

# Required for chat transfer:
SALESIQ_ACCESS_TOKEN
SALESIQ_DEPARTMENT_ID
SALESIQ_APP_ID

# Optional:
SALESIQ_SCREEN_NAME

# Optional for tickets:
DESK_ACCESS_TOKEN
DESK_ORG_ID
```

---

## ⚡ Quick Test Command

After setting variables, check if they're loaded:

1. Go to Railway dashboard
2. Click on your service
3. Click **"Deploy Logs"**
4. Look for these lines at startup:

✅ **Working:**
```
[INFO] SalesIQ Visitor API v1 configured - department: 1234567890, app_id: 9876543210
[INFO] Zoho API loaded successfully - SalesIQ enabled: True
```

❌ **Not working:**
```
[WARNING] SalesIQ Visitor API not fully configured - token: False, dept: False, app_id: False
```

---

## 🎯 Summary Checklist

Before testing, verify:

- [ ] OPENAI_API_KEY added to Railway
- [ ] SALESIQ_ACCESS_TOKEN added to Railway
- [ ] SALESIQ_DEPARTMENT_ID added to Railway
- [ ] SALESIQ_APP_ID added to Railway
- [ ] Railway redeployed automatically
- [ ] Check logs show "SalesIQ enabled: True"
- [ ] Test chat transfer works
- [ ] Test callback scheduling works

---

## 💡 Pro Tips

1. **Copy-paste carefully** - Variable names are case-sensitive!
2. **No spaces** - Trim any spaces before/after values
3. **No quotes** - Railway adds quotes automatically
4. **Wait for redeploy** - Takes 1-2 minutes
5. **Check logs first** - Always verify startup logs

---

**Once you add these 4 variables to Railway, your chatbot will work perfectly!** 🚀

Need help getting the actual token values? See: [RAILWAY_ENV_VARIABLES.md](RAILWAY_ENV_VARIABLES.md)
