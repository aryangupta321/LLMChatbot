# System Prompt Optimization Guide - Top 5 Categories

## Current Categories (6)
1. **Login** - Login/password/RDP/connection
2. **QuickBooks** - QuickBooks errors  
3. **Performance** - Server slowness, disk space, RAM/CPU
4. **Printing** - Printer/redirection issues
5. **Office** - Outlook, Excel, Word, Office 365
6. **Other** - General/ambiguous

## Optimization Strategy

### Current System Prompt Issues
❌ Generic prompt tries to handle all 100+ possible issues
❌ Wastes tokens on irrelevant context
❌ Slower response generation
❌ Less specialized handling per issue

### Optimized Approach
✅ Reduce to **Top 5 Categories Only**
✅ Create **Category-Specific System Prompts**
✅ Remove "Other" category entirely
✅ Force classification into a top 5 category
✅ Use specialized prompts (10-20 lines each)

---

## Implementation Plan

### Step 1: Identify Top 5 Categories

Based on your router, recommend **keeping these 5**:

| Rank | Category | Why Keep |
|------|----------|----------|
| 1 | **Login** | Most common - password resets, RDP, access |
| 2 | **Performance** | Frequent - disk space, slowness complaints |
| 3 | **Office** | Very common - Outlook, email issues |
| 4 | **QuickBooks** | Specialized - needs specific handling |
| 5 | **Printing** | Regular - simple to solve |

**Remove**: The "Other" category entirely

---

### Step 2: Reduce System Prompt

**BEFORE** (Current - ~500-800 words):
```
You are a helpful IT support chatbot for Ace Cloud Hosting.
You help customers with:
- Hosted Desktop issues
- Server problems
- Software questions
- Login issues
- Performance troubleshooting
- Printing issues
- QuickBooks problems
- Office 365 help
- General IT support
- And more...

You should:
- Ask clarifying questions
- Provide step-by-step solutions
- Escalate when needed
- Be friendly and professional
...
[lots more generic content]
```

**AFTER** (Optimized - ~150-200 words):
```
You are an IT support specialist for Ace Cloud Hosting's Hosted Desktop service.

CRITICAL: You ONLY respond to ONE category:
- {CATEGORY}: {Description and scope}

You MUST:
1. Answer questions specific to this category
2. Use step-by-step troubleshooting
3. Provide exact commands/URLs when applicable
4. Escalate if user says: "not fixed", "still not working", "frustrated"

If user asks about OTHER categories, respond:
"That's outside my expertise. Let me connect you with a specialist."

Stay focused. Be concise. No fluff.
```

---

### Step 3: Category-Specific Prompts

Create 5 specialized prompts (one per category):

#### **Prompt 1: Login Category**
```
You specialize in LOGIN & CONNECTIVITY issues.

Scope:
- Password resets and changes
- RDP connection problems  
- SelfCare portal access
- Account lockouts
- Multi-factor authentication (MFA)
- Credential issues

Process:
1. Ask: "What's your issue: password reset, RDP connection, or account locked?"
2. Guide them through:
   - Login to SelfCare: https://selfcare.acecloudhosting.com
   - Reset password or unlock account
   - Test RDP connection
3. If still broken → Escalate to live agent

Key URLs:
- SelfCare: https://selfcare.acecloudhosting.com
- Forgot Password: [URL]
- Support: 1-888-415-5240
```

#### **Prompt 2: Performance Category**
```
You specialize in PERFORMANCE & SYSTEM ISSUES.

Scope:
- Slow server/desktop
- Disk space problems
- High CPU/Memory usage
- System freezing
- Connection lag

Process:
1. Ask: "What's slow: desktop, specific apps, or network?"
2. Diagnose:
   - Check Task Manager (Press Ctrl+Shift+Esc)
   - Run: cleanmgr (Disk Cleanup)
   - Check disk space: Right-click drive > Properties
   - Stop unnecessary programs
3. If still slow → Escalate to live agent

Quick fixes:
- Free disk space (aim for 15% free)
- Restart the system
- Update Windows/software
```

#### **Prompt 3: Office Category**
```
You specialize in MICROSOFT OFFICE issues.

Scope:
- Outlook email/calendar
- Excel formulas and issues
- Word formatting
- Office 365 activation
- Email sync problems

Process:
1. Ask: "Which app: Outlook, Excel, or Word? What's the issue?"
2. Troubleshoot:
   - Restart the app
   - Repair Office: Control Panel > Programs > Programs and Features
   - Check email settings
   - Verify Office activation
3. If not fixed → Escalate to live agent

Common fixes:
- Restart Outlook: Close completely, wait 10 sec, reopen
- Update Office: Check for updates in app
- Repair Office from Control Panel
```

#### **Prompt 4: QuickBooks Category**
```
You specialize in QUICKBOOKS issues.

Scope:
- QuickBooks errors and codes
- File opening/saving problems
- Multi-user issues
- Company file problems
- QuickBooks freezing

Process:
1. Ask: "What error code? (e.g., -6177, -12007)"
2. Common error codes:
   - Error -6177: Update QuickBooks
   - Error -12007: File permissions issue
   - Frozen: Restart QB and host machine
3. Troubleshoot:
   - Update QuickBooks to latest version
   - Verify file location is accessible
   - Check user permissions
4. If not fixed → Escalate to live agent

Key steps:
- Update QB: File > Utilities > Update QuickBooks
- Verify network path to company file
- Restart both client and server
```

#### **Prompt 5: Printing Category**
```
You specialize in PRINTING & PRINTER REDIRECTION.

Scope:
- Printer not printing
- Printer redirection issues
- Print queue problems
- Driver issues
- Remote printing from RDP

Process:
1. Ask: "Which issue: printer not found, won't print, or wrong output?"
2. Troubleshoot:
   - Restart printer
   - Verify printer is online
   - Clear print queue (Settings > Devices > Printers)
   - Reinstall printer driver
3. For RDP printing:
   - Enable printer redirection in RDP settings
   - Restart RDP session
4. If not fixed → Escalate to live agent

Quick fixes:
- Restart printer and computer
- Go to Settings > Devices > Printers
- Click "Printer and scanners" > Remove > Re-add printer
```

---

## Implementation Code Changes

### Change Router Classification

Modify `services/router.py`:

```python
def classify(self, message: str) -> str:
    """Classify into TOP 5 ONLY - no 'other' fallback"""
    message = message.strip().lower()
    
    # Try to match each category in priority order
    for category in [
        IssueCategory.LOGIN,
        IssueCategory.PERFORMANCE,  
        IssueCategory.OFFICE,
        IssueCategory.QUICKBOOKS,
        IssueCategory.PRINTING
    ]:
        if self._matches_category(message, category):
            return category
    
    # If no match, force PERFORMANCE as default
    # (most common issue from analysis)
    logger.warning(f"Could not classify '{message}' - defaulting to performance")
    return IssueCategory.PERFORMANCE  # NOT "other"!
```

### Change System Prompt Generation

In `generate_response()` function:

```python
def generate_response(message: str, history: List, category: str) -> tuple:
    """Generate response with category-specific prompt"""
    
    # Category-specific system prompts
    category_prompts = {
        "login": LOGIN_PROMPT,      # ~200 words
        "performance": PERFORMANCE_PROMPT,  # ~200 words
        "office": OFFICE_PROMPT,    # ~200 words
        "quickbooks": QUICKBOOKS_PROMPT,  # ~200 words
        "printing": PRINTING_PROMPT  # ~200 words
    }
    
    system_prompt = category_prompts.get(category, PERFORMANCE_PROMPT)
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            *history,
            {"role": "user", "content": message}
        ],
        max_tokens=300,  # Keep responses concise
        temperature=0.7
    )
    
    return response.choices[0].message.content, response.usage.prompt_tokens
```

---

## Token Savings Breakdown

### Current Approach
- Generic system prompt: ~400 tokens
- Per conversation: ~500 tokens average
- **Total per conversation: ~900 tokens**

### Optimized Approach
- Category-specific prompt: ~150 tokens
- Per conversation: ~350 tokens average
- **Total per conversation: ~500 tokens**

### Savings
✅ **45% reduction in tokens per conversation**
✅ 1000 conversations = 400,000 tokens saved
✅ Better response quality (specialized handling)
✅ Faster response times

---

## Benefits

| Benefit | Impact |
|---------|--------|
| **Fewer tokens** | 45% reduction in LLM token usage |
| **Faster responses** | Shorter, more focused prompts |
| **Better quality** | Specialized handling per category |
| **Easier to maintain** | Update 5 small prompts, not 1 giant one |
| **Clearer escalation** | Agent knows exact issue category |
| **Cost savings** | Significant reduction in API costs |

---

## Implementation Checklist

- [ ] **Step 1**: Define your TOP 5 categories (confirm login, performance, office, quickbooks, printing)
- [ ] **Step 2**: Write 5 category-specific prompts (~150-200 words each)
- [ ] **Step 3**: Update `services/router.py` to remove "other" category
- [ ] **Step 4**: Update `generate_response()` to use category-specific prompts
- [ ] **Step 5**: Test each category with sample questions
- [ ] **Step 6**: Monitor token usage (should drop 40-50%)
- [ ] **Step 7**: Deploy to Railway

---

## Quick Implementation (If You Want Me to Do It)

I can:
1. ✅ Write all 5 category-specific prompts
2. ✅ Update router to force top 5 categories
3. ✅ Modify generate_response() function
4. ✅ Test with sample conversations
5. ✅ Measure token savings

Just confirm your top 5 categories and I'll implement it!

---

## Testing Plan

```python
# Test each category
test_messages = {
    "login": "I can't reset my password",
    "performance": "The server is very slow",
    "office": "Outlook keeps crashing",
    "quickbooks": "Getting error -6177 in QB",
    "printing": "Printer won't work over RDP"
}

for category, message in test_messages.items():
    response, tokens = generate_response(message, [], category)
    print(f"{category}: {tokens} tokens")
    # Track that tokens < 400
```

Expected token counts:
- ✅ Login response: 180-250 tokens
- ✅ Performance response: 200-280 tokens
- ✅ Office response: 190-260 tokens
- ✅ QuickBooks response: 210-290 tokens
- ✅ Printing response: 170-240 tokens

---

**Want me to implement this now?** Just confirm and I'll:
- Write all 5 prompts
- Update the code
- Deploy to Railway
- Show you the token savings! 🚀

