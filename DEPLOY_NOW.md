# Deploy Now - Step by Step

## ✅ What Was Fixed

The Railway configuration files were pointing to the wrong filename:
- ❌ Was looking for: `fastapi_chatbot_server.py`
- ✅ Now looking for: `fastapi_chatbot_hybrid.py`

Both files have been fixed:
- `railway.json` ✅
- `Procfile` ✅

## 🚀 Deploy to Railway (3 Steps)

### Step 1: Commit Changes
```bash
git add railway.json Procfile
git commit -m "Fix: Update Railway config to use correct bot filename (fastapi_chatbot_hybrid.py)"
```

### Step 2: Push to Railway
```bash
git push railway main
```

### Step 3: Wait for Deployment
Railway will automatically:
1. Detect the changes
2. Rebuild the container
3. Start the bot with the correct filename
4. Begin receiving webhooks

**Deployment time**: 2-3 minutes

## 📊 Monitor Deployment

### Check Logs
```bash
railway logs --follow
```

**Expected output**:
```
======================================================================
ACE CLOUD HOSTING - SUPPORT BOT (HYBRID LLM)
======================================================================

🚀 Starting FastAPI server on port 8000...
📍 Endpoint: http://0.0.0.0:8000
📖 Docs: http://0.0.0.0:8000/docs

✅ Ready to receive webhooks from n8n!
======================================================================
```

### Test Health Endpoint
```bash
curl https://your-railway-url.railway.app/health
```

**Expected response**:
```json
{
  "status": "healthy",
  "openai": "connected",
  "active_sessions": 0
}
```

## 🧪 Test the Bot

### Test 1: Basic Message
```bash
curl -X POST https://your-railway-url.railway.app/webhook/salesiq \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_001",
    "message": {"text": "hello"},
    "visitor": {"id": "user-001"}
  }'
```

**Expected response**:
```json
{
  "action": "reply",
  "replies": ["Hello! How can I assist you today?"],
  "session_id": "test_001"
}
```

### Test 2: QuickBooks Issue
```bash
curl -X POST https://your-railway-url.railway.app/webhook/salesiq \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_002",
    "message": {"text": "QuickBooks is frozen"},
    "visitor": {"id": "user-002"}
  }'
```

**Expected response**:
```json
{
  "action": "reply",
  "replies": ["Are you using a dedicated server or a shared server?"],
  "session_id": "test_002"
}
```

### Test 3: Escalation
```bash
curl -X POST https://your-railway-url.railway.app/webhook/salesiq \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_003",
    "message": {"text": "option 1"},
    "visitor": {"id": "user-003"}
  }'
```

**Expected response**:
```json
{
  "action": "transfer",
  "transfer_to": "human_agent",
  "session_id": "test_003",
  "conversation_history": "...",
  "replies": ["Connecting you with a support agent..."]
}
```

## 🔧 Configure SalesIQ Webhook

1. Go to **SalesIQ** → **Settings** → **Webhooks**
2. Click **Add Webhook**
3. Enter:
   - **URL**: `https://your-railway-url.railway.app/webhook/salesiq`
   - **Event**: Message received
   - **Method**: POST
4. Click **Save**

## ✅ Verify Everything Works

### In SalesIQ Widget
1. Open your website with SalesIQ widget
2. Start a chat
3. Send: "hello"
4. Bot should respond: "Hello! How can I assist you today?"
5. Send: "QuickBooks is frozen"
6. Bot should ask: "Are you using a dedicated server or a shared server?"

### In Railway Logs
```bash
railway logs --follow
```

Should show:
```
[SalesIQ] Webhook received
[SalesIQ] Session ID: ...
[SalesIQ] Message: hello
[SalesIQ] Response generated: Hello! How can I assist you today?
```

## 🎯 Success Checklist

- [ ] Committed changes to git
- [ ] Pushed to Railway: `git push railway main`
- [ ] Railway logs show bot is running
- [ ] Health endpoint returns 200 OK
- [ ] Test webhook returns valid response
- [ ] SalesIQ webhook is configured
- [ ] Bot responds in SalesIQ widget
- [ ] No errors in Railway logs

## ⏱️ Timeline

| Step | Time |
|------|------|
| Commit changes | 1 min |
| Push to Railway | 1 min |
| Railway redeploys | 2-3 min |
| Bot starts | 1 min |
| Test webhook | 1 min |
| Configure SalesIQ | 2 min |
| Test in widget | 2 min |
| **Total** | **~10-12 min** |

## 🆘 If Something Goes Wrong

### Issue: Still getting "No such file or directory"
**Solution**: 
1. Check logs: `railway logs --follow`
2. Verify files were committed: `git log --oneline -5`
3. Force redeploy: `railway redeploy`

### Issue: Bot not responding
**Solution**:
1. Check health: `curl https://your-railway-url.railway.app/health`
2. Check logs: `railway logs --follow`
3. Verify OpenAI API key: `railway variables`

### Issue: SalesIQ webhook error
**Solution**:
1. Test webhook with curl (see above)
2. Check SalesIQ webhook URL is correct
3. Check SalesIQ webhook is enabled
4. Review Railway logs for errors

## 📚 Documentation

For more details, see:
- `RAILWAY_DEPLOYMENT_FIX.md` - Detailed fix explanation
- `TROUBLESHOOTING_MESSAGE_HANDLER.md` - Troubleshooting guide
- `SETUP_AND_DEPLOYMENT.md` - Complete setup guide

## 🚀 Ready to Deploy?

Run these commands:

```bash
# 1. Commit
git add railway.json Procfile
git commit -m "Fix: Update Railway config to use correct bot filename"

# 2. Push
git push railway main

# 3. Monitor
railway logs --follow
```

**Status**: ✅ Ready to deploy

