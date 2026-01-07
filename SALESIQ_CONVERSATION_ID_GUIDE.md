# SalesIQ Conversation ID Extraction Guide

## Overview
The bot now extracts and logs all SalesIQ conversation IDs from incoming webhooks to help debug chat closure issues.

## What's Been Added

### 1. Comprehensive ID Logging
Every webhook now logs a detailed block showing:
```
================================================================================
SALESIQ WEBHOOK PAYLOAD - CONVERSATION ID MAPPING
================================================================================
Timestamp: 2026-01-06T10:30:45.123456
Visitor Info:
  - Name: John Doe
  - Email: john@example.com
  - Phone: 1234567890

ID Extraction:
  - salesiq_conversation_id: abc123xyz
  - salesiq_chat_id: chat_456
  - salesiq_visitor_id: visitor_789
  - salesiq_active_conversation: abc123xyz

Message Details:
  - Message Time: 1735654245000
  - Text: I need help with my account
  - Payload: (if button was clicked)

API CLOSE ENDPOINT:
  POST /api/v2/rtdsportal/conversations/abc123xyz/close

Full URL:
  https://salesiq.zohopublic.in/api/v2/rtdsportal/conversations/abc123xyz/close
================================================================================
```

### 2. ID Storage & Mapping
- Internal session IDs are mapped to SalesIQ conversation IDs
- Stored in memory: `conversation_id_map[session_id] = conversation_id`
- Logged: `[ID Mapping] Stored: session_id=xxx -> conversation_id=yyy`

### 3. Debug Endpoint
**GET** `/debug/conversation-ids`

Returns JSON with all active conversations:
```json
{
  "total_conversations": 3,
  "screen_name": "rtdsportal",
  "conversations": [
    {
      "internal_session_id": "session_abc",
      "salesiq_conversation_id": "conv_123",
      "close_api_url": "https://salesiq.zohopublic.in/api/v2/rtdsportal/conversations/conv_123/close",
      "has_messages": true,
      "message_count": 5
    }
  ],
  "note": "Use close_api_url with POST request and Bearer token to close chat"
}
```

## How to Use

### View Logs in Railway
1. Go to Railway dashboard → Your project → Deployments
2. Click "View Logs" on the latest deployment
3. Search for: `SALESIQ WEBHOOK PAYLOAD - CONVERSATION ID MAPPING`
4. Each webhook will show the complete ID mapping block

### Get the Conversation ID
Look for the line:
```
API CLOSE ENDPOINT:
  POST /api/v2/rtdsportal/conversations/{THIS_IS_THE_ID}/close
```

The ID between `/conversations/` and `/close` is what you need.

### Test the Close API
Use the full URL shown in logs:
```bash
curl -X POST \
  https://salesiq.zohopublic.in/api/v2/rtdsportal/conversations/YOUR_CONVERSATION_ID/close \
  -H "Authorization: Bearer YOUR_SALESIQ_ACCESS_TOKEN"
```

### Check All Active Conversations
Visit: `https://your-railway-app.up.railway.app/debug/conversation-ids`

This shows all conversations the bot is currently tracking.

## ID Types Explained

| ID Type | Source | Used For |
|---------|--------|----------|
| `salesiq_conversation_id` | `request.conversation.id` | **Primary - Use for close API** |
| `salesiq_chat_id` | `request.chat.id` | Fallback if conversation.id missing |
| `salesiq_visitor_id` | `request.visitor.id` | Visitor identification only |
| `salesiq_active_conversation` | `request.visitor.active_conversation_id` | Alternative conversation ID |
| `internal_session_id` | Bot's internal tracking | Maps to conversation_id |

## Priority Order for Close API
The bot selects the conversation ID in this order:
1. `conversation.id` (most reliable)
2. `visitor.active_conversation_id`
3. `chat.id`

The selected ID is shown in the `API CLOSE ENDPOINT` line.

## Troubleshooting

### "NO CONVERSATION ID FOUND"
If you see this warning, the webhook payload doesn't contain any conversation IDs. Possible causes:
- Webhook is a test message (not real visitor)
- SalesIQ API version mismatch
- Webhook configuration issue

Check the full payload: Search logs for `Full request payload`

### Conversation Not in Debug Endpoint
If `/debug/conversation-ids` doesn't show a conversation:
- Conversation might have already been deleted from memory
- No messages were exchanged (greeting only)
- Session ID extraction failed (check `session_id=unknown` in logs)

### Close API Returns 404
- The conversation ID might be expired/closed already
- Check if the ID format matches SalesIQ's expected format
- Verify screen_name is correct (currently: `rtdsportal`)

## Environment Variables Used
- `SALESIQ_SCREEN_NAME` - Your SalesIQ screen name (default: `rtdsportal`)
- `SALESIQ_ACCESS_TOKEN` - Bearer token for API calls

## Next Steps
1. Test a real chat conversation
2. Check Railway logs for the ID mapping block
3. Copy the full close API URL
4. Test closing the chat via curl or Postman
5. If 404 error, check if the ID format/screen name is correct
6. If 401 error, verify SALESIQ_ACCESS_TOKEN is valid

## Summary
✅ Every webhook logs complete ID information  
✅ Clear API endpoint URLs provided  
✅ Debug endpoint to view all active conversations  
✅ Correlation with visitor info and message text  
✅ Ready for testing chat closure via API
