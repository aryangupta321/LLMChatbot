# Deploy Buttons - Quick Guide

## What's Ready

✅ Buttons implemented for 3 escalation options
✅ Payload extraction added
✅ Option detection updated
✅ Backward compatible with text input
✅ No syntax errors

---

## Deploy in 3 Steps

### Step 1: Commit

```bash
git add fastapi_chatbot_hybrid.py BUTTONS_IMPLEMENTED.md
git commit -m "Feature: Add quick reply buttons for 3 escalation options"
```

### Step 2: Push to Railway

```bash
git push railway main
```

### Step 3: Monitor

```bash
railway logs --follow
```

---

## Test Immediately After Deploy

### Test 1: Trigger Escalation

```bash
curl -X POST http://localhost:8000/webhook/salesiq \
  -H "Content-Type: application/json" \
  -d '{"session_id": "t1", "message": {"text": "not working"}}'
```

**Expected**: Buttons appear in response

### Test 2: Click Button

```bash
curl -X POST http://localhost:8000/webhook/salesiq \
  -H "Content-Type: application/json" \
  -d '{"session_id": "t1", "payload": "option_1"}'
```

**Expected**: Transfer response

### Test 3: Text Still Works

```bash
curl -X POST http://localhost:8000/webhook/salesiq \
  -H "Content-Type: application/json" \
  -d '{"session_id": "t2", "message": {"text": "instant chat"}}'
```

**Expected**: Transfer response

---

## In SalesIQ Widget

1. Open widget
2. Send: "not working"
3. See: 3 buttons appear
4. Click: Any button
5. Verify: Correct action occurs

---

## Rollback (If Needed)

```bash
git revert HEAD
git push railway main
```

---

## Status

✅ **Ready to Deploy**

---

**Deploy now!** 🚀
