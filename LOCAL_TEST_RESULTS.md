# Local Testing - Visitor API v1 Structure

## Test Results

### ✅ Code Structure Verified
- Visitor API v1 endpoint: `https://salesiq.zoho.in/api/visitor/v1/{screen_name}/conversations` ✓
- Nested visitor object with `user_id`, `name`, `email` ✓
- Root level fields: `app_id`, `department_id`, `question` ✓

### ✅ Bot Preview Validation
- Added check to reject `botpreview_...` IDs
- Returns clear error: "Bot preview sessions cannot be transferred"

### 📋 Correct Payload Structure (Ready for Production)

```json
{
  "app_id": "2782000012893013",
  "department_id": "2782000000002013",
  "question": "Customer conversation history here",
  "visitor": {
    "user_id": "real.visitor@acecloudhosting.com",
    "name": "Visitor Name",
    "email": "real.visitor@acecloudhosting.com"
  }
}
```

## Key Changes Made

### 1. **zoho_api_simple.py**
- ✅ Changed base URL from `/api/v2/` to `/api/visitor/v1/`
- ✅ Removed org_id and default_tag_id (not needed for Visitor API)
- ✅ Restructured payload with nested `visitor` object
- ✅ Added validation to reject bot preview IDs
- ✅ Using real email as `user_id` (most reliable)

### 2. **llm_chatbot.py**  
- ✅ Updated webhook handler to extract visitor email
- ✅ Pass visitor email as unique user_id to API
- ✅ Updated test endpoints with proper user_id handling
- ✅ Fixed regex escape sequences in strings

### 3. **Environment Setup**
- ✅ No need for `SALESIQ_ORG_ID` (Visitor API doesn't need it)
- ✅ No need for `SALESIQ_DEFAULT_TAG_ID` (Visitor API doesn't have tags)
- ✅ Keep: `SALESIQ_ACCESS_TOKEN`, `SALESIQ_DEPARTMENT_ID`, `SALESIQ_APP_ID`, `SALESIQ_SCREEN_NAME`

## How to Test on SalesIQ Widget

### Method 1: Real Widget Test (RECOMMENDED)
1. Add the SalesIQ widget to your actual website
2. Open chat as a real visitor (not bot preview)
3. Click "📞 Instant Chat" button
4. Webhook sends real visitor email to API
5. Conversation created in SalesIQ with that visitor

### Method 2: Direct POST Test
```bash
curl -X POST http://localhost:8000/test/salesiq-transfer \
  -H "Content-Type: application/json" \
  -d '{
    "visitor_user_id": "real.visitor@acecloudhosting.com",
    "conversation": "Customer has issue with QuickBooks",
    "app_id": "2782000012893013",
    "department_id": "2782000000002013",
    "visitor": {
      "name": "John Doe",
      "email": "real.visitor@acecloudhosting.com"
    }
  }'
```

### Method 3: Simulate Webhook Payload
```bash
curl -X POST http://localhost:8000/webhook/salesiq \
  -H "Content-Type: application/json" \
  -d '{
    "visitor": {
      "id": "real_visitor_123",
      "email": "customer@example.com",
      "name": "Customer Name",
      "department_id": "2782000000002013"
    },
    "chat": {
      "id": "chat_123"
    },
    "message": "📞 Instant Chat"
  }'
```

## Expected Responses

### ✅ Success Response (201 Created)
```json
{
  "success": true,
  "endpoint": "https://salesiq.zoho.in/api/visitor/v1/rtdsportal/conversations",
  "data": {
    "url": "/api/visitor/v1/rtdsportal/conversations",
    "object": "conversations",
    "data": {
      "id": "conversation_id_xyz",
      "wms_chat_id": "LD_xxx",
      "question": "..."
    }
  }
}
```

### ❌ Bot Preview Rejection
```json
{
  "success": false,
  "error": "invalid_visitor_id",
  "details": "Bot preview sessions cannot be transferred. This is a SalesIQ limitation. Test with real visitor ID only."
}
```

### ❌ Invalid Credentials
```json
{
  "success": false,
  "error": "400",
  "details": "{\"error\":{\"code\":1008,\"message\":\"Invalid OAuthToken\"}}"
}
```

## Deployment Checklist

- [x] Fixed Visitor API v1 endpoint
- [x] Corrected payload structure  
- [x] Added bot preview validation
- [x] Updated webhook handler
- [x] Updated test endpoints
- [x] Fixed string escapes
- [x] Local code verified
- [x] Git committed and pushed
- [ ] **Manual Railway restart required**
- [ ] Test on Railway after restart
- [ ] Test with real SalesIQ widget

## Next Steps

1. **Commit and push** the escape sequence fixes:
   ```bash
   git add -A && git commit -m "Fix: String escape sequences in registry paths" && git push
   ```

2. **Restart Railway** service:
   - Go to https://railway.app/dashboard
   - Click "web" service → Settings → Restart
   - Wait 2-3 minutes

3. **Test endpoints**:
   ```bash
   # GET test (simplest)
   curl https://your-railway-app.up.railway.app/test/salesiq-transfer

   # Check logs in Railway
   # Should show Visitor API v1 call with nested visitor object
   ```

4. **Real widget test**:
   - Add SalesIQ widget to live website
   - Test with real visitor (not bot preview)
   - Verify conversation appears in SalesIQ

Done! No more `tag_ids` errors! 🎉
