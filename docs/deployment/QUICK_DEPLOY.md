# 🚀 QUICK DEPLOY CHECKLIST

## ✅ What Was Fixed

1. **Correct Visitor API endpoint** - Changed from `/api/v2/` to `/api/visitor/v1/rtdsportal/`
2. **Loaded app_id** - Now properly reads from environment
3. **Fixed payload structure** - Using official Visitor API format with visitor object
4. **Single correct endpoint** - Removed random endpoint attempts
5. **Better logging** - Can now debug API responses

---

## 📦 Deploy Commands

```bash
# 1. Add changes
git add zoho_api_integration.py SALESIQ_TRANSFER_FIXED.md

# 2. Commit
git commit -m "Fix: Implement correct SalesIQ Visitor API for chat transfers

- Use Visitor API endpoint (/api/visitor/v1/rtdsportal/conversations)
- Load app_id from environment (required for Visitor API)
- Fix payload structure to match official documentation
- Remove incorrect endpoint loop, use single correct endpoint
- Add detailed logging for API responses"

# 3. Push to Railway
git push origin main
```

---

## 🔍 Verify After Deploy

### 1. Check Railway Logs
Look for this line:
```
SalesIQ API configured - department: 2782000000002013, app_id: 2782000012893013
```

✅ **If you see this:** API is configured correctly
❌ **If you see "SalesIQ API not configured":** Check environment variables in Railway dashboard

### 2. Verify Environment Variables in Railway
Make sure these are set:
- `SALESIQ_ACCESS_TOKEN`
- `SALESIQ_DEPARTMENT_ID`
- `SALESIQ_SCREEN_NAME`
- `SALESIQ_APP_ID`

### 3. Test Live Transfer
1. Open SalesIQ widget
2. Type: "not working"
3. Click: "📞 Instant Chat"
4. Check logs for: `✅ SalesIQ chat transfer successful`

---

## 🆘 If It Doesn't Work

### Check API Response in Logs

**Status 200/201** → Success! ✅
**Status 401** → Token expired/invalid → Regenerate token
**Status 403** → Token lacks permissions → Check scopes
**Status 404** → Wrong department_id or app_id → Verify IDs
**Status 422** → Payload validation failed → Contact me

### Verify Token Scopes
Your token must have:
- `SalesIQ.conversations.ALL`
- `SalesIQ.visitors.ALL`

### Check Agent Availability
- At least one operator must be online in department 2782000000002013
- Check department working hours

---

## 📁 Files Changed

- ✅ `zoho_api_integration.py` - Fixed API implementation
- ✅ `SALESIQ_TRANSFER_FIXED.md` - Full documentation
- ✅ `QUICK_DEPLOY.md` - This file

---

## ⏱️ Timeline

1. **Now:** Git commit + push
2. **2-3 min:** Railway auto-deploys
3. **Immediately:** Test in SalesIQ widget
4. **Check logs:** Verify API response

---

## 🎯 What Happens When Transfer Works

1. User clicks "Instant Chat"
2. Bot calls: `POST https://salesiq.zoho.in/api/visitor/v1/rtdsportal/conversations`
3. SalesIQ creates conversation in department 2782000000002013
4. Agent gets notification
5. Agent sees full conversation history
6. Chat continues with agent

---

## 💡 Key Changes Summary

| Before | After |
|--------|-------|
| Wrong API type (Operator) | Correct API (Visitor) |
| Missing app_id | app_id loaded ✅ |
| Wrong payload format | Official format ✅ |
| 4 random endpoints | 1 correct endpoint ✅ |
| Generic errors | Detailed logging ✅ |

---

**The fix is complete and ready to deploy!** 🎉
