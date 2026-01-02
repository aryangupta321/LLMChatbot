# Deployment Checklist - Chat Flow Fixes

## Pre-Deployment

- [x] Code changes reviewed
- [x] No syntax errors (verified with getDiagnostics)
- [x] Backward compatible (no breaking changes)
- [x] Logging added for debugging
- [x] Test cases documented
- [x] Documentation complete
- [x] Rollback plan ready

## Deployment Steps

### Step 1: Verify Changes
- [ ] Run `git status` to see all changes
- [ ] Review `fastapi_chatbot_hybrid.py` changes
- [ ] Verify no unintended changes

### Step 2: Commit Changes
- [ ] Run: `git add fastapi_chatbot_hybrid.py *.md`
- [ ] Run: `git commit -m "Fix: Improve password reset flow and step-by-step guidance"`
- [ ] Verify commit message is clear

### Step 3: Push to Railway
- [ ] Run: `git push railway main`
- [ ] Wait for build to complete (2-3 minutes)
- [ ] Check for any build errors

### Step 4: Monitor Deployment
- [ ] Run: `railway logs --follow`
- [ ] Look for "Starting Container"
- [ ] Look for "INFO: Uvicorn running on 0.0.0.0:8000"
- [ ] Verify no errors or exceptions

### Step 5: Verify Health
- [ ] Run: `curl https://your-railway-url.railway.app/health`
- [ ] Verify response: `{"status":"healthy",...}`
- [ ] Check active_sessions count

## Post-Deployment Testing

### Test 1: Password Reset (Registered)
- [ ] Send: "password reset"
- [ ] Verify: "Are you registered on the SelfCare portal?"
- [ ] Send: "yes"
- [ ] Verify: "Great! Visit https://selfcare.acecloudhosting.com..."

### Test 2: Password Reset (Not Registered)
- [ ] Send: "password reset"
- [ ] Verify: "Are you registered on the SelfCare portal?"
- [ ] Send: "no"
- [ ] Verify: "No problem! For server/user account password reset, please contact..."

### Test 3: QB Error Step-by-Step
- [ ] Send: "quickbooks error 6177"
- [ ] Verify: Step 1 provided
- [ ] Send: "okay then"
- [ ] Verify: Step 2 provided (NOT "Is there anything else?")
- [ ] Send: "okay then"
- [ ] Verify: Step 3 provided
- [ ] Send: "okay then"
- [ ] Verify: Step 4 provided
- [ ] Send: "ok"
- [ ] Verify: Step 5 provided

### Test 4: Acknowledgment Outside Troubleshooting
- [ ] Send: "what is your support number"
- [ ] Verify: Contact info provided
- [ ] Send: "thanks"
- [ ] Verify: "You're welcome! Is there anything else I can help you with?"

### Test 5: SalesIQ Widget
- [ ] Open SalesIQ chat widget
- [ ] Send: "password reset"
- [ ] Verify: Response appears correctly
- [ ] Send: "yes"
- [ ] Verify: Response appears correctly
- [ ] Check for any formatting issues

## Monitoring (First 24 Hours)

### Hourly Checks
- [ ] Check logs for errors: `railway logs --follow | grep -i error`
- [ ] Check response time: `railway logs --follow | grep -i "response generated"`
- [ ] Check for API errors: `railway logs --follow | grep -i "openai\|api"`

### Daily Checks
- [ ] Monitor escalation rate
- [ ] Monitor user feedback
- [ ] Check for any patterns of issues
- [ ] Verify metrics are improving

### Metrics to Track
- [ ] Escalation rate (target: <30%)
- [ ] First-contact resolution (target: >70%)
- [ ] User satisfaction (target: High)
- [ ] Response time (target: <2 seconds)
- [ ] Error rate (target: 0%)

## Success Criteria

- [x] Code changes implemented
- [x] Tests documented
- [x] Deployment guide ready
- [ ] Deployment successful
- [ ] All tests pass
- [ ] No errors in logs
- [ ] Response time <2 seconds
- [ ] SalesIQ widget displays correctly
- [ ] User feedback positive
- [ ] Metrics improving

## Rollback Criteria

If any of these occur, rollback immediately:
- [ ] High error rate (>5%)
- [ ] Response time >5 seconds
- [ ] Bot not responding
- [ ] Password reset not routing correctly
- [ ] Steps still being interrupted
- [ ] Multiple user complaints

## Rollback Steps

If rollback needed:
1. [ ] Run: `git revert HEAD`
2. [ ] Run: `git push railway main`
3. [ ] Run: `railway logs --follow`
4. [ ] Verify: Bot is responding normally
5. [ ] Document: What went wrong
6. [ ] Plan: How to fix

## Post-Deployment Documentation

- [ ] Document deployment date/time
- [ ] Document any issues encountered
- [ ] Document metrics before/after
- [ ] Document user feedback
- [ ] Update README with results
- [ ] Share results with team

## Sign-Off

- [ ] Deployment completed successfully
- [ ] All tests passed
- [ ] Monitoring plan in place
- [ ] Documentation updated
- [ ] Team notified

---

## Timeline

| Step | Time | Status |
|------|------|--------|
| Pre-deployment checks | 5 min | ⏳ |
| Commit & push | 2 min | ⏳ |
| Build & deploy | 3 min | ⏳ |
| Verify health | 1 min | ⏳ |
| Run tests | 10 min | ⏳ |
| Monitor (24 hours) | 24 hrs | ⏳ |

**Total time to deploy**: ~20 minutes
**Total time to verify**: ~24 hours

---

## Notes

- Keep this checklist handy during deployment
- Check off items as you complete them
- Document any issues or deviations
- Contact support if issues occur
- Refer to DEPLOY_FIXES.md for detailed instructions

---

## Contact

If issues occur:
1. Check logs: `railway logs --follow`
2. Review DEPLOY_FIXES.md for troubleshooting
3. Review CHAT_FLOW_FIXES.md for detailed explanation
4. Rollback if needed: `git revert HEAD && git push railway main`

---

**Deployment Date**: _______________
**Deployed By**: _______________
**Status**: _______________
**Notes**: _______________

---

Ready to deploy! ✅
