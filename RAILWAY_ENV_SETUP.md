# Railway Environment Variables Setup

## 🚨 Why Transfer is Not Working

The bot is **simulating** transfers because the **environment variables are not set in Railway**!

The `.env` file only works locally - Railway needs variables set in its dashboard.

---

## 🔧 Set Environment Variables in Railway

### **Step 1: Go to Railway Dashboard**
1. Open: https://railway.app/dashboard
2. Click on your project
3. Click on your service (the one running the bot)
4. Go to **Variables** tab

### **Step 2: Add These Variables**

Click "New Variable" and add each one:

| Variable Name | Value |
|--------------|-------|
| `SALESIQ_ACCESS_TOKEN` | `1000.21a18fe9ce30e588db59c39b4524a22a.87a0b3df50ec313a84b5e92479c659c3` |
| `SALESIQ_DEPARTMENT_ID` | `2782000000002013` |
| `SALESIQ_SCREEN_NAME` | `rtdsportal` |
| `SALESIQ_APP_ID` | `2782000012893013` |
| `OPENAI_API_KEY` | `your-openai-key` |

### **Step 3: Redeploy**
After adding variables, Railway will automatically redeploy.

---

## 🧪 Verify Variables Are Set

### **Check Health Endpoint:**
```
GET https://web-production-3032d.up.railway.app/health
```

**Should show:**
```json
{
  "status": "healthy",
  "salesiq_api": "enabled",  // ← Should be "enabled" not "disabled"
  ...
}
```

### **Check Railway Logs:**
```
Zoho API loaded - SalesIQ enabled: True, Desk enabled: False
SalesIQ API configured - department: 2782000000002013
```

**If you see:**
```
SalesIQ API not configured - missing token or department_id
```
Then the environment variables are NOT set correctly.

---

## 📊 Expected Behavior After Setup

### **Before (Current - Simulated):**
```
[API] Simulating chat transfer for botpreview_xxx
[SalesIQ] API result: {'success': True, 'simulated': True}
```

### **After (Real API):**
```
[SalesIQ] Creating SalesIQ conversation for visitor botpreview_xxx
[SalesIQ] Visitor API payload: user_id=botpreview_xxx, department_id=2782000000002013
[SalesIQ] SalesIQ conversation created successfully
```

---

## 🎯 Quick Steps

1. **Go to Railway Dashboard** → Your Project → Variables
2. **Add the 5 environment variables** listed above
3. **Wait for redeploy** (automatic)
4. **Test transfer** in SalesIQ widget
5. **Check logs** for "SalesIQ enabled: True"

---

## ⚠️ Important Notes

### **Token Expiry**
- Your access token expires in **1 hour** (3600 seconds)
- You'll need to refresh it periodically
- For production, set up automatic token refresh

### **If Transfer Still Fails**
1. Check Railway logs for specific errors
2. Verify token is not expired
3. Check department ID is correct
4. Test API endpoint directly

---

**Set the environment variables in Railway dashboard and the real transfer will work!** 🚀