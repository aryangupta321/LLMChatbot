# Deploy Transfer Fix - Quick Guide

## Problem Fixed

Error: **"action type transfer is invalid"**

When user clicked "Instant Chat", SalesIQ showed this error because the webhook response format was wrong.

---

## Solution

Changed from invalid format:
```json
{"action": "transfer", "transfer_to": "human_agent"}
```

To valid format:
```json
{"action": "reply", "replies": ["Connecting you with a support agent..."]}
```

The actual transfer happens through the SalesIQ API call, not the webhook response.

---

## Deploy in 3 Steps

### Step 1: Commit

```bash
git add fastapi_chatbot_hybrid.py SALESIQ_TRANSFER_FIX.md
git commit -m "Fix: Use correct SalesIQ webhook response format for transfers"
```

### Step 2: Push

```bash
git push railway main
```

### Step 3: Monitor

```bash
railway logs --follow
```

---

## Test After Deploy

### In SalesIQ Widget

1. Send: "not working"
2. See: 3 buttons appear
3. Click: [📞 Instant Chat]
4. Expected: "Connecting you with a support agent. Please wait..."
5. Verify: No error message
6. Chat transfers to agent

---

## Expected Result

✅ No more "action type transfer is invalid" error
✅ Chat transfers to agent successfully
✅ Agent sees conversation history
✅ User sees confirmation message

---

## Status

✅ **Fixed**
✅ **Ready to Deploy**

---

**Deploy now!** 🚀
