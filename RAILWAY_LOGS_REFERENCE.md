# Railway Logs Quick Reference

## What to Look For in Logs

### Button Clicks / Escalations
```
[Action] ✅ BUTTON CLICKED: 
```
Look for these 3 options:
- `Instant Chat (Option 1)` → User wants live agent
- `Schedule Callback (Option 2)` → User wants callback
- `Create Support Ticket (Option 3)` → User wants support ticket

### Successful Actions
```
[Action] ✓ CALLBACK TICKET CREATED SUCCESSFULLY
[Action] ✓ SUPPORT TICKET CREATED SUCCESSFULLY  
[Action] ✓ TRANSFER CONFIRMATION SENT
[Action] ✓ CHAT CLOSED SUCCESSFULLY
```

### Failed Actions
```
[Action] ✗ CALLBACK TICKET CREATION FAILED
[Action] ✗ SUPPORT TICKET CREATION FAILED
Error: {error message}
```

### Conversation Start
```
[Session] 👋 INITIAL CONTACT
[Session] ✓ NEW CONVERSATION STARTED | Category: {category}
[Metrics] 📊 NEW CONVERSATION STARTED
```

### Conversation End
```
[Metrics] 📊 CONVERSATION ENDED - Reason: {reason}
Reasons include:
  - Agent Transfer
  - Callback Scheduled
  - Support Ticket Created
  - Resolved
```

### LLM Calls
```
[LLM] 🤖 CALLING GPT-4o-mini for category: {category}
[LLM] ✓ Response generated | Tokens used: {number} | Category: {category}
```

### Handler Matching
```
[Handler] ✅ HANDLER MATCHED - Processing response
[Handler] No handler matched, continuing with existing logic
```

### API Status
```
[SalesIQ] Chat closure result: {status}
[Desk] Support ticket result: {status}
[Desk] Callback call result: {status}
```

## Common Conversation Patterns

### Pattern 1: Quick Resolution (LLM-based)
```
[Session] 👋 INITIAL CONTACT
[Session] ✓ NEW CONVERSATION STARTED | Category: {type}
[Handler] ✅ HANDLER MATCHED
[Action] ✓ ISSUE RESOLVED
[Metrics] 📊 CONVERSATION ENDED - Reason: Resolved
```

### Pattern 2: User Requests Callback
```
[Escalation] 🆙 ESCALATION REQUESTED
[Escalation] Showing 3 options:
[Action] ✅ BUTTON CLICKED: Schedule Callback (Option 2)
[Action] 📞 CALLBACK SCHEDULED
[Action] ✓ CALLBACK TICKET CREATED SUCCESSFULLY
[Metrics] 📊 CONVERSATION ENDED - Reason: Callback Scheduled
```

### Pattern 3: Chat Transfer to Agent
```
[Escalation] 🆙 ESCALATION REQUESTED
[Action] ✅ BUTTON CLICKED: Instant Chat (Option 1)
[Action] 🔄 CHAT TRANSFER INITIATED
[Action] ✓ TRANSFER CONFIRMATION SENT
[Metrics] 📊 CONVERSATION ENDED - Reason: Agent Transfer
```

### Pattern 4: Create Support Ticket
```
[Escalation] 🆙 ESCALATION REQUESTED
[Action] ✅ BUTTON CLICKED: Create Support Ticket (Option 3)
[Action] 🎫 SUPPORT TICKET CREATION INITIATED
[Action] ✓ SUPPORT TICKET CREATED SUCCESSFULLY
[Action] 🎫 Ticket ID: {id}
[Metrics] 📊 CONVERSATION ENDED - Reason: Support Ticket Created
```

## Troubleshooting Checklist

### Escalation Options Not Showing?
Look for:
```
[Escalation] Showing 3 options:
```
If missing, check for:
- `[Handler] No handler matched` - Handler system issue
- `[LLM] CALLING GPT-4o-mini` - LLM response issue
- Check user message didn't have exact trigger words

### Callback Failed?
Look for:
```
[Action] ✗ CALLBACK TICKET CREATION FAILED
Error: {error message}
```
Check:
- Desk API credentials valid?
- API endpoint responding?
- Phone/email fields properly formatted?

### Transfer Failed?
Look for:
```
[Handler] Transfer API result: {status}
```
Check:
- SalesIQ API working?
- Session ID valid?
- Visitor still connected?

### Token Usage High?
Look for:
```
[LLM] Response generated | Tokens used: {number}
```
If > 500 tokens per response:
- Check message length
- Check history length
- Consider more specific category classification

### No Callback Created?
Should see:
```
[Action] 📞 CALLBACK SCHEDULED
[Action] ✓ CALLBACK TICKET CREATED SUCCESSFULLY
```
If only partial, check visitor details are being collected

## Emoji Legend

| Emoji | Meaning | Context |
|-------|---------|---------|
| 👋 | Initial greeting | Session start |
| 🆙 | Escalation needed | User wants help |
| ✅ | Action confirmed | Button clicked, action started |
| ✓ | Success | Operation completed successfully |
| ✗ | Failure | Operation failed |
| 🔄 | Transfer | Chat transfer initiated |
| 📞 | Callback | Callback scheduled/created |
| 🎫 | Ticket | Support ticket created |
| 🤖 | LLM/AI | Language model called |
| 📊 | Metrics | Tracking data recorded |

## Key Insights to Monitor

1. **Escalation Rate**: Count `[Escalation] 🆙` per day
2. **Callback Success**: Count `[Action] ✓ CALLBACK TICKET CREATED` vs `[Action] ✗ CALLBACK TICKET CREATION FAILED`
3. **Transfer Success**: Count `[Action] ✓ TRANSFER CONFIRMATION` vs failures
4. **Avg Tokens**: Monitor `[LLM] Tokens used: {number}` trend
5. **Conversation Duration**: Track time between `[Session] NEW` and `[Metrics] CONVERSATION ENDED`
6. **Handler Match Rate**: Count `[Handler] ✅ MATCHED` vs `[Handler] No handler matched`
7. **Category Distribution**: Count category values in `[Session] NEW | Category: {}`

## Example Full Conversation Log

```
[2024-01-15 10:30:45] [Session] 👋 INITIAL CONTACT - Sending greeting
[2024-01-15 10:30:46] [Session] ✓ NEW CONVERSATION STARTED | Category: connectivity
[2024-01-15 10:30:46] [Metrics] 📊 NEW CONVERSATION STARTED
[2024-01-15 10:30:46] [Metrics] Category: connectivity, Router Matched: True
[2024-01-15 10:30:47] [Handler] ✅ HANDLER MATCHED - Processing response
[2024-01-15 10:30:47] [Handler] Response text: To help with your connectivity issue, let me ask...
[2024-01-15 10:31:15] [SalesIQ] Message classified as: connectivity
[2024-01-15 10:31:15] [Handler] ✅ HANDLER MATCHED - Processing response
[2024-01-15 10:31:45] [Escalation] 🆙 ESCALATION REQUESTED - User wants human agent
[2024-01-15 10:31:45] [Escalation] Showing 3 options: ① Instant Chat | ② Schedule Callback | ③ Create Ticket
[2024-01-15 10:32:10] [Action] ✅ BUTTON CLICKED: Schedule Callback (Option 2)
[2024-01-15 10:32:10] [Action] 📞 CALLBACK SCHEDULED - Waiting for time & phone details
[2024-01-15 10:33:00] [Action] ✓ CALLBACK TICKET CREATED SUCCESSFULLY
[2024-01-15 10:33:00] [Action] 📞 Callback scheduled for visitor: John Smith
[2024-01-15 10:33:00] [Action] Email: john@example.com
[2024-01-15 10:33:01] [SalesIQ] Chat closure result: {'success': True}
[2024-01-15 10:33:01] [Metrics] 📊 CONVERSATION ENDED - Reason: Callback Scheduled
```

Total time: ~2.5 minutes from greeting to callback scheduled

