# Quick Test Guide - Chat Flow Fixes

## Test Locally Before Deploying

### Setup

```bash
# 1. Make sure bot is running locally
python fastapi_chatbot_hybrid.py

# 2. In another terminal, run tests
```

---

## Test 1: Password Reset - Registered on SelfCare

**Flow**: User is registered on SelfCare → Bot provides reset steps

```bash
# Message 1: User asks for password reset
curl -X POST http://localhost:8000/webhook/salesiq \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_pw_registered",
    "message": {"text": "can u help me reset password"},
    "visitor": {"id": "user-1"}
  }'
```

**Expected Response**:
```json
{
  "action": "reply",
  "replies": ["I can help! Are you registered on the SelfCare portal?"],
  "session_id": "test_pw_registered"
}
```

```bash
# Message 2: User says yes
curl -X POST http://localhost:8000/webhook/salesiq \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_pw_registered",
    "message": {"text": "yes i am registered"},
    "visitor": {"id": "user-1"}
  }'
```

**Expected Response**:
```json
{
  "action": "reply",
  "replies": ["Great! Visit https://selfcare.acecloudhosting.com and click 'Forgot your password'. Let me know when you're there!"],
  "session_id": "test_pw_registered"
}
```

✅ **PASS**: Bot asks first, then provides SelfCare steps

---

## Test 2: Password Reset - NOT Registered on SelfCare

**Flow**: User is NOT registered → Bot escalates to support

```bash
# Message 1: User asks for password reset
curl -X POST http://localhost:8000/webhook/salesiq \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_pw_not_registered",
    "message": {"text": "password reset please"},
    "visitor": {"id": "user-2"}
  }'
```

**Expected Response**:
```json
{
  "action": "reply",
  "replies": ["I can help! Are you registered on the SelfCare portal?"],
  "session_id": "test_pw_not_registered"
}
```

```bash
# Message 2: User says no
curl -X POST http://localhost:8000/webhook/salesiq \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_pw_not_registered",
    "message": {"text": "no i m not registered on self care"},
    "visitor": {"id": "user-2"}
  }'
```

**Expected Response**:
```json
{
  "action": "reply",
  "replies": ["No problem! For server/user account password reset, please contact our support team at 1-888-415-5240. They'll help you right away!"],
  "session_id": "test_pw_not_registered"
}
```

✅ **PASS**: Bot escalates to support instead of confusing user

---

## Test 3: QB Error -6177 - Step-by-Step Guidance

**Flow**: User gets QB error → Bot provides 5 steps one at a time → User says "okay then" → Bot continues (NOT interrupts)

```bash
# Message 1: User reports QB error
curl -X POST http://localhost:8000/webhook/salesiq \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_qb_error",
    "message": {"text": "quickbooks error 6177"},
    "visitor": {"id": "user-3"}
  }'
```

**Expected Response**:
```json
{
  "action": "reply",
  "replies": ["I can help! First, select 'Computer' from the Start menu. Let me know when you're ready!"],
  "session_id": "test_qb_error"
}
```

```bash
# Message 2: User says "okay then"
curl -X POST http://localhost:8000/webhook/salesiq \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_qb_error",
    "message": {"text": "okay then"},
    "visitor": {"id": "user-3"}
  }'
```

**Expected Response** (IMPORTANT - should continue, NOT ask "Is there anything else?"):
```json
{
  "action": "reply",
  "replies": ["Great! Now, navigate to the Client data drive (usually the D drive) where your company files are located. Let me know when you get there!"],
  "session_id": "test_qb_error"
}
```

❌ **FAIL** if response is: "Is there anything else I can help you with?"

```bash
# Message 3: User says "okay then" again
curl -X POST http://localhost:8000/webhook/salesiq \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_qb_error",
    "message": {"text": "okay then"},
    "visitor": {"id": "user-3"}
  }'
```

**Expected Response** (should continue with step 3):
```json
{
  "action": "reply",
  "replies": ["Perfect! Now, click once on the .QBW file, and select 'Rename' from the File menu. Can you do that?"],
  "session_id": "test_qb_error"
}
```

```bash
# Message 4: User says "okay then" again
curl -X POST http://localhost:8000/webhook/salesiq \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_qb_error",
    "message": {"text": "okay then"},
    "visitor": {"id": "user-3"}
  }'
```

**Expected Response** (should continue with step 4):
```json
{
  "action": "reply",
  "replies": ["Awesome! Now, click off the file to save the modified name. Let me know when you've done that!"],
  "session_id": "test_qb_error"
}
```

```bash
# Message 5: User says "ok"
curl -X POST http://localhost:8000/webhook/salesiq \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_qb_error",
    "message": {"text": "ok"},
    "visitor": {"id": "user-3"}
  }'
```

**Expected Response** (should continue with final step):
```json
{
  "action": "reply",
  "replies": ["Great! Now, rename the file back to its original name. Let me know when you're finished!"],
  "session_id": "test_qb_error"
}
```

✅ **PASS**: All 5 steps provided in sequence without interruption

---

## Test 4: QB Error - User Says "Is There Any Step Left"

**Flow**: Simulates the exact scenario from the chat transcript

```bash
# Message 1: User reports QB error
curl -X POST http://localhost:8000/webhook/salesiq \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_qb_steps",
    "message": {"text": "quickbooks error 6177"},
    "visitor": {"id": "user-4"}
  }'
```

**Expected**: Step 1

```bash
# Message 2-5: User says "okay then" for steps 2-4
curl -X POST http://localhost:8000/webhook/salesiq \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_qb_steps",
    "message": {"text": "okay then"},
    "visitor": {"id": "user-4"}
  }'
```

**Expected**: Step 2

```bash
curl -X POST http://localhost:8000/webhook/salesiq \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_qb_steps",
    "message": {"text": "okay then"},
    "visitor": {"id": "user-4"}
  }'
```

**Expected**: Step 3

```bash
curl -X POST http://localhost:8000/webhook/salesiq \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_qb_steps",
    "message": {"text": "okay then"},
    "visitor": {"id": "user-4"}
  }'
```

**Expected**: Step 4

```bash
curl -X POST http://localhost:8000/webhook/salesiq \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_qb_steps",
    "message": {"text": "ok"},
    "visitor": {"id": "user-4"}
  }'
```

**Expected**: Step 5 (NOT "Is there anything else?")

```bash
# Message 6: User asks "is there any step left"
curl -X POST http://localhost:8000/webhook/salesiq \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_qb_steps",
    "message": {"text": "is there any step left"},
    "visitor": {"id": "user-4"}
  }'
```

**Expected Response** (should say no, all steps done):
```json
{
  "action": "reply",
  "replies": ["No, that was the last step! The error should be resolved now. Is there anything else I can help you with?"],
  "session_id": "test_qb_steps"
}
```

✅ **PASS**: All steps provided, user doesn't need to ask "is there any step left"

---

## Test 5: Acknowledgment Outside Troubleshooting

**Flow**: User says "thanks" when NOT in troubleshooting → Bot should ask "Is there anything else?"

```bash
# Message 1: User asks simple question
curl -X POST http://localhost:8000/webhook/salesiq \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_ack",
    "message": {"text": "what is your support number"},
    "visitor": {"id": "user-5"}
  }'
```

**Expected**: Contact info

```bash
# Message 2: User says "thanks"
curl -X POST http://localhost:8000/webhook/salesiq \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_ack",
    "message": {"text": "thanks"},
    "visitor": {"id": "user-5"}
  }'
```

**Expected Response**:
```json
{
  "action": "reply",
  "replies": ["You're welcome! Is there anything else I can help you with?"],
  "session_id": "test_ack"
}
```

✅ **PASS**: Acknowledgment handled correctly outside troubleshooting

---

## Summary of Tests

| Test | Scenario | Expected | Status |
|------|----------|----------|--------|
| 1 | Password reset (registered) | Ask first, then provide steps | ✅ |
| 2 | Password reset (not registered) | Ask first, then escalate | ✅ |
| 3 | QB error step-by-step | All 5 steps without interruption | ✅ |
| 4 | QB error with "is there any step left" | All steps provided automatically | ✅ |
| 5 | Acknowledgment outside troubleshooting | Ask "Is there anything else?" | ✅ |

---

## Deployment Checklist

- [ ] Run all 5 tests locally
- [ ] All tests pass
- [ ] Commit changes: `git add . && git commit -m "Fix chat flows"`
- [ ] Push to Railway: `git push railway main`
- [ ] Monitor logs: `railway logs --follow`
- [ ] Test in SalesIQ widget
- [ ] Verify responses appear correctly
- [ ] Collect user feedback

---

## If Tests Fail

**If Test 3 fails** (QB error continues with "Is there anything else?"):
- Check that troubleshooting_patterns includes all keywords
- Verify acknowledgment detection logic
- Check conversation history is being stored correctly

**If Test 1 or 2 fails** (Password reset not routing correctly):
- Check password_keywords includes all variations
- Verify history is being checked correctly
- Check SelfCare registration detection

**Debug Command**:
```bash
# Check logs for detailed info
railway logs --follow | grep -i "password\|acknowledgment\|troubleshooting"
```
