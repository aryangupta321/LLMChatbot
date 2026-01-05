# Real-World Log Examples

## Complete Conversation Examples

### Example 1: Quick Resolution with LLM

**Scenario**: Customer asks about connectivity issues, bot resolves it without escalation

```
[2024-01-15 10:30:45] [req:a1b2c3d4e5f6g7h8] [session:visitor_connectivity_001]
  [Session] 👋 INITIAL CONTACT - Sending greeting

[2024-01-15 10:30:46] [req:a1b2c3d4e5f6g7h8] [session:visitor_connectivity_001]
  [Session] ✓ NEW CONVERSATION STARTED | Category: connectivity
  [Metrics] 📊 NEW CONVERSATION STARTED
  [Metrics] Category: connectivity, Router Matched: True

[2024-01-15 10:30:50] [req:b2c3d4e5f6g7h8i9] [session:visitor_connectivity_001]
  [SalesIQ] Message classified as: connectivity
  [Handler] ✅ HANDLER MATCHED - Processing response
  [Handler] Response text: To help with your connectivity issue...

[2024-01-15 10:31:15] [req:c3d4e5f6g7h8i9j0] [session:visitor_connectivity_001]
  [Handler] ✅ HANDLER MATCHED - Processing response
  [Handler] Response text: Please try the following troubleshooting steps...

[2024-01-15 10:32:30] [req:d4e5f6g7h8i9j0k1] [session:visitor_connectivity_001]
  [Resolution] ✓ ISSUE RESOLVED
  [Resolution] Reason: User confirmed fix worked
  [Resolution] Action: Closing chat session
  [Action] ✓ CHAT CLOSED SUCCESSFULLY
  [SalesIQ] Chat closure result: {'success': True}
  [Metrics] 📊 CONVERSATION ENDED - Reason: Resolved

Time: 1 minute 45 seconds | Tokens used: 0 (Pattern handler) | Escalations: 0
```

**Insights**: 
- Pattern handler matched (100% automation)
- Quick resolution (1:45 average)
- No LLM tokens used
- Customer satisfied without escalation

---

### Example 2: Escalation to Callback

**Scenario**: Customer's issue not resolved by handler, requests callback

```
[2024-01-15 11:05:30] [req:e5f6g7h8i9j0k1l2] [session:visitor_billing_002]
  [Session] 👋 INITIAL CONTACT - Sending greeting

[2024-01-15 11:05:31] [req:e5f6g7h8i9j0k1l2] [session:visitor_billing_002]
  [Session] ✓ NEW CONVERSATION STARTED | Category: billing
  [Metrics] 📊 NEW CONVERSATION STARTED
  [Metrics] Category: billing, Router Matched: True

[2024-01-15 11:05:35] [req:f6g7h8i9j0k1l2m3] [session:visitor_billing_002]
  [SalesIQ] Message classified as: billing
  [Handler] ✅ HANDLER MATCHED - Processing response
  [Handler] Response text: I can help with billing issues...

[2024-01-15 11:06:20] [req:g7h8i9j0k1l2m3n4] [session:visitor_billing_002]
  [Handler] ✅ HANDLER MATCHED - Processing response
  [Handler] Response text: Here are common billing solutions...

[2024-01-15 11:07:00] [req:h8i9j0k1l2m3n4o5] [session:visitor_billing_002]
  [Escalation] 🆙 ESCALATION REQUESTED - User wants human agent
  [Escalation] Showing 3 options: ① Instant Chat | ② Schedule Callback | ③ Create Ticket

[2024-01-15 11:07:15] [req:i9j0k1l2m3n4o5p6] [session:visitor_billing_002]
  [Action] ✅ BUTTON CLICKED: Schedule Callback (Option 2)
  [Action] 📞 CALLBACK SCHEDULED - Waiting for time & phone details

[2024-01-15 11:08:00] [req:j0k1l2m3n4o5p6q7] [session:visitor_billing_002]
  [Action] ✓ CALLBACK TICKET CREATED SUCCESSFULLY
  [Action] 📞 Callback scheduled for visitor: Sarah Johnson
  [Action] Email: sarah.johnson@company.com
  [SalesIQ] Chat closure result: {'success': True}
  [Metrics] 📊 CONVERSATION ENDED - Reason: Callback Scheduled

Time: 2 minutes 30 seconds | Tokens used: 0 | Escalations: 1 (Callback) | Success: ✓
```

**Insights**:
- Handler attempted resolution (2 responses)
- Customer escalated to callback
- Callback created successfully
- Visitor details captured
- Complete audit trail available

---

### Example 3: Escalation with Chat Transfer to Agent

**Scenario**: Customer has complex issue, needs immediate agent

```
[2024-01-15 13:20:15] [req:k1l2m3n4o5p6q7r8] [session:visitor_support_003]
  [Session] 👋 INITIAL CONTACT - Sending greeting

[2024-01-15 13:20:16] [req:k1l2m3n4o5p6q7r8] [session:visitor_support_003]
  [Session] ✓ NEW CONVERSATION STARTED | Category: other
  [Metrics] 📊 NEW CONVERSATION STARTED
  [Metrics] Category: other, Router Matched: False

[2024-01-15 13:20:20] [req:l2m3n4o5p6q7r8s9] [session:visitor_support_003]
  [Handler] No handler matched, continuing with existing logic
  [LLM] 🤖 CALLING GPT-4o-mini for category: other
  [LLM] ✓ Response generated | Tokens used: 234 | Category: other
  [Metrics] 📊 Recording message: LLM=True, Tokens=234, Category=other

[2024-01-15 13:20:50] [req:m3n4o5p6q7r8s9t0] [session:visitor_support_003]
  [Handler] No handler matched, continuing with existing logic
  [LLM] 🤖 CALLING GPT-4o-mini for category: other
  [LLM] ✓ Response generated | Tokens used: 312 | Category: other
  [Metrics] 📊 Recording message: LLM=True, Tokens=312, Category=other

[2024-01-15 13:21:30] [req:n4o5p6q7r8s9t0u1] [session:visitor_support_003]
  [Escalation] 🆙 ESCALATION REQUESTED - User wants human agent
  [Escalation] Showing 3 options: ① Instant Chat | ② Schedule Callback | ③ Create Ticket

[2024-01-15 13:21:45] [req:o5p6q7r8s9t0u1v2] [session:visitor_support_003]
  [Action] ✅ BUTTON CLICKED: Instant Chat (Option 1)
  [Action] 🔄 CHAT TRANSFER INITIATED
  [Action] Status: Connecting visitor to live agent...
  [Handler] Transfer API result: {'success': True, 'agent_id': 'agent_sarah_001'}
  [Action] ✓ TRANSFER CONFIRMATION SENT

[2024-01-15 13:21:46] [req:p6q7r8s9t0u1v2w3] [session:visitor_support_003]
  [SalesIQ] Chat closure result: {'success': True}
  [Metrics] 📊 CONVERSATION ENDED - Reason: Agent Transfer

Time: 1 minute 31 seconds | Tokens used: 546 | Escalations: 1 (Live Agent) | Success: ✓
Assigned to: agent_sarah_001
```

**Insights**:
- Complex issue not matched by handlers
- LLM called twice (546 total tokens)
- Escalated to live agent
- Successfully transferred
- Agent assignment tracked

---

### Example 4: Support Ticket Creation

**Scenario**: Customer wants support ticket for documentation issue

```
[2024-01-15 14:45:00] [req:q7r8s9t0u1v2w3x4] [session:visitor_docs_004]
  [Session] 👋 INITIAL CONTACT - Sending greeting

[2024-01-15 14:45:01] [req:q7r8s9t0u1v2w3x4] [session:visitor_docs_004]
  [Session] ✓ NEW CONVERSATION STARTED | Category: documentation
  [Metrics] 📊 NEW CONVERSATION STARTED
  [Metrics] Category: documentation, Router Matched: True

[2024-01-15 14:45:05] [req:r8s9t0u1v2w3x4y5] [session:visitor_docs_004]
  [SalesIQ] Message classified as: documentation
  [Handler] ✅ HANDLER MATCHED - Processing response
  [Handler] Response text: For documentation issues, we recommend...

[2024-01-15 14:45:50] [req:s9t0u1v2w3x4y5z6] [session:visitor_docs_004]
  [Escalation] 🆙 ESCALATION REQUESTED - User wants human agent
  [Escalation] Showing 3 options: ① Instant Chat | ② Schedule Callback | ③ Create Ticket

[2024-01-15 14:46:10] [req:t0u1v2w3x4y5z6a7] [session:visitor_docs_004]
  [Action] ✅ BUTTON CLICKED: Create Support Ticket (Option 3)
  [Action] 🎫 SUPPORT TICKET CREATION INITIATED
  [Action] Status: Collecting user details for support ticket...

[2024-01-15 14:47:00] [req:u1v2w3x4y5z6a7b8] [session:visitor_docs_004]
  [Action] ✓ SUPPORT TICKET CREATED SUCCESSFULLY
  [Action] 🎫 Ticket ID: TICKET-2024-0156
  [Action] Status: Closing chat and transferring to support queue
  [Desk] Support ticket result: {'success': True, 'ticket_id': 'TICKET-2024-0156'}
  [SalesIQ] Chat closure result: {'success': True}
  [Metrics] 📊 CONVERSATION ENDED - Reason: Support Ticket Created

Time: 2 minutes 0 seconds | Tokens used: 0 | Escalations: 1 (Ticket) | Success: ✓
Ticket ID: TICKET-2024-0156
```

**Insights**:
- Pattern handler matched documentation category
- Escalated to support ticket
- Ticket created successfully
- Ticket ID generated
- Complete tracking for follow-up

---

### Example 5: Failed Callback Creation

**Scenario**: Customer requests callback but API call fails

```
[2024-01-15 15:30:20] [req:v2w3x4y5z6a7b8c9] [session:visitor_issue_005]
  [Session] 👋 INITIAL CONTACT - Sending greeting

[2024-01-15 15:30:21] [req:v2w3x4y5z6a7b8c9] [session:visitor_issue_005]
  [Session] ✓ NEW CONVERSATION STARTED | Category: general
  [Metrics] 📊 NEW CONVERSATION STARTED
  [Metrics] Category: general, Router Matched: False

[2024-01-15 15:30:25] [req:w3x4y5z6a7b8c9d0] [session:visitor_issue_005]
  [Handler] No handler matched, continuing with existing logic
  [LLM] 🤖 CALLING GPT-4o-mini for category: general
  [LLM] ✓ Response generated | Tokens used: 189 | Category: general
  [Metrics] 📊 Recording message: LLM=True, Tokens=189, Category=general

[2024-01-15 15:31:00] [req:x4y5z6a7b8c9d0e1] [session:visitor_issue_005]
  [Escalation] 🆙 ESCALATION REQUESTED - User wants human agent
  [Escalation] Showing 3 options: ① Instant Chat | ② Schedule Callback | ③ Create Ticket

[2024-01-15 15:31:20] [req:y5z6a7b8c9d0e1f2] [session:visitor_issue_005]
  [Action] ✅ BUTTON CLICKED: Schedule Callback (Option 2)
  [Action] 📞 CALLBACK SCHEDULED - Waiting for time & phone details

[2024-01-15 15:32:15] [req:z6a7b8c9d0e1f2g3] [session:visitor_issue_005]
  [Action] ✗ CALLBACK TICKET CREATION FAILED
  [Action] Error: Connection timeout to Desk API
  [Desk] Callback call error: Connection timeout

Time: 1 minute 55 seconds | Tokens used: 189 | Escalations: 1 (Callback - FAILED) | Success: ✗
Alert: Desk API Connection Issue Detected
```

**Insights**:
- Callback creation attempted
- API call failed (connection timeout)
- Clear error message logged
- Can trigger alerts for monitoring
- Support team notified of API issue

---

## Log Filtering Examples

### Find All Failed Actions
```bash
Search: [Action] ✗
Results: All failed escalation options, transfers, callbacks, tickets
```

### Find All Callbacks (Success + Failure)
```bash
Search: [Action] 📞
Results: All callback-related actions
  - [Action] 📞 CALLBACK SCHEDULED
  - [Action] ✓ CALLBACK CREATED SUCCESSFULLY
  - [Action] ✗ CALLBACK CREATION FAILED
```

### Find All Chat Transfers
```bash
Search: [Action] 🔄
Results: All chat transfer attempts
  - Shows agent assigned (if successful)
  - Shows transfer failure details
```

### Find All Support Tickets
```bash
Search: [Action] 🎫
Results: All support ticket creations
  - Shows ticket ID when created
  - Shows creation failures with errors
```

### Find High-Token LLM Calls
```bash
Search: [LLM].*Tokens used: [5-9][0-9]{2}
Results: LLM calls using 500+ tokens (potential optimizations needed)
```

### Find Escalation Rate
```bash
Search: [Escalation] 🆙
Results: Count total escalations
Divide by [Metrics] 📊 NEW CONVERSATION STARTED for escalation percentage
```

### Find Category Distribution
```bash
Search: [Session] NEW | Category: (.*)
Results: All categories seen
  - Count occurrences per category
  - Identify most common issues
  - See handler match rates per category
```

### Find Conversation Duration
```bash
1. Search: [Session] ✓ NEW | Category: billing
   Note timestamp: 10:30:45
2. Search: [Metrics] ENDED.*Callback Scheduled
   Note timestamp: 10:35:15
3. Duration: 4 minutes 30 seconds
```

---

## Performance Metrics You Can Extract

```
Metric                          Formula                              Example
─────────────────────────────────────────────────────────────────────────────
Escalation Rate                [🆙] / [NEW]                        45 / 200 = 22.5%
Callback Success Rate          [✓ CREATED] / [📞 SCHEDULED]        38 / 45 = 84%
Transfer Success Rate          [✓ TRANSFER] / [🔄 INITIATED]       35 / 40 = 87.5%
Handler Match Rate             [✅ MATCHED] / [classified]         120 / 200 = 60%
Avg Tokens per Response        SUM([Tokens]) / COUNT([LLM])        2345 / 15 = 156 tokens
LLM Call Rate                  COUNT([🤖]) / [NEW]                 80 / 200 = 40%
Avg Conversation Time          SUM(END - START) / COUNT([NEW])     500 min / 200 = 2.5 min
Ticket Success Rate            [✓ TICKET] / [🎫 INITIATED]        28 / 30 = 93%
Category Distribution          COUNT([Category: X]) / [NEW]        50 / 200 = 25% billing
Resolution Rate                [ENDED] with Reason / [NEW]         195 / 200 = 97.5%
```

---

## Alert Conditions to Monitor

```
⚠️ Alert When...
─────────────────────────────────────────────────────────────────────
1. [Action] ✗ FAILED appears → API failure detected
2. [LLM] Tokens > 800 → Token usage spike
3. [Metrics] ENDED - Reason: ? → Unexpected closure
4. Handler Match Rate < 40% → Pattern matching degraded
5. Avg Response Time > 3 seconds → Performance issue
6. Escalation Rate > 30% → Product issue indication
7. Callback Failure Rate > 20% → API integration issue
8. [SalesIQ] Chat closure result: failed → SalesIQ issue
9. No [NEW] for 5 minutes → Traffic issue
10. Transfer failures > 5 in 10 min → Agent system issue
```

These real examples show exactly what you'll see in Railway logs when chatbot operations occur!

