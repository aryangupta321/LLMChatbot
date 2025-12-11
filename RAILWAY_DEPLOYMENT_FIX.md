# Railway Deployment Fix

## Problem

Railway was looking for `fastapi_chatbot_server.py` but the actual file is `fastapi_chatbot_hybrid.py`.

**Error**:
```
python: can't open file '/app/fastapi_chatbot_server.py': [Errno 2] No such file or directory
```

## Solution Applied

Fixed both configuration files:

### 1. railway.json
**Before**:
```json
"startCommand": "python fastapi_chatbot_server.py"
```

**After**:
```json
"startCommand": "python fastapi_chatbot_hybrid.py"
```

### 2. Procfile
**Before**:
```
web: python fastapi_chatbot_server.py
```

**After**:
```
web: python fastapi_chatbot_hybrid.py
```

## Next Steps

1. **Commit the changes**:
   ```bash
   git add railway.json Procfile
   git commit -m "Fix: Update Railway config to use correct bot filename"
   ```

2. **Push to Railway**:
   ```bash
   git push railway main
   ```

3. **Railway will automatically redeploy** with the correct filename

4. **Check logs**:
   ```bash
   railway logs --follow
   ```

   Expected output:
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

5. **Test the webhook**:
   ```bash
   curl -X POST https://your-railway-url.railway.app/webhook/salesiq \
     -H "Content-Type: application/json" \
     -d '{"session_id": "test", "message": {"text": "hello"}, "visitor": {"id": "user"}}'
   ```

   Expected response:
   ```json
   {
     "action": "reply",
     "replies": ["Hello! How can I assist you today?"],
     "session_id": "test"
   }
   ```

6. **Configure SalesIQ webhook** (if not done yet):
   - Go to SalesIQ → Settings → Webhooks
   - Add webhook URL: `https://your-railway-url.railway.app/webhook/salesiq`
   - Event: Message received
   - Method: POST

## Verification

### Check 1: Railway Logs
```bash
railway logs --follow
```

Should show:
```
✅ Ready to receive webhooks from n8n!
```

### Check 2: Health Endpoint
```bash
curl https://your-railway-url.railway.app/health
```

Expected:
```json
{
  "status": "healthy",
  "openai": "connected",
  "active_sessions": 0
}
```

### Check 3: Test Webhook
```bash
curl -X POST https://your-railway-url.railway.app/webhook/salesiq \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test", "message": {"text": "hello"}, "visitor": {"id": "user"}}'
```

Expected:
```json
{
  "action": "reply",
  "replies": ["Hello! How can I assist you today?"],
  "session_id": "test"
}
```

### Check 4: SalesIQ Widget
1. Open your website with SalesIQ widget
2. Start a chat
3. Send: "hello"
4. Bot should respond: "Hello! How can I assist you today?"

## Files Fixed

- ✅ `railway.json` - Updated startCommand
- ✅ `Procfile` - Updated web command

## Timeline

1. **Commit changes** (1 min)
2. **Push to Railway** (1 min)
3. **Railway redeploys** (2-3 min)
4. **Bot starts** (1 min)
5. **Test webhook** (1 min)

**Total**: ~5-10 minutes

## If Still Having Issues

1. Check Railway logs: `railway logs --follow`
2. Look for `[SalesIQ] Webhook received` messages
3. Verify environment variables are set: `railway variables`
4. Check OpenAI API key is valid
5. Review `TROUBLESHOOTING_MESSAGE_HANDLER.md`

## Summary

The bot is now configured correctly to run on Railway. After pushing the changes, Railway will automatically:
1. Detect the new configuration
2. Rebuild the container
3. Start the bot with the correct filename
4. Begin receiving webhooks from SalesIQ

**Status**: ✅ Ready to deploy

