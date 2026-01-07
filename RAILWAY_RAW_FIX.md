# 🚨 The Error is Hidden in the UI

I understand it looks correct in the fields, but the error log is 100% certain: there is a hidden `=` sign at the start of the line that the UI is not showing you.

**You must use the "Raw Editor" to see and fix this.**

## 🛠️ Steps to Fix (Follow Exactly)

1. Go to **Railway Dashboard** → **Variables**.
2. Look for the **"Raw Editor"** button (usually a pencil icon ✏️ or a toggle switch) at the top of the variables list.
   - *This switches the view from boxes to a simple text file.*
3. Find the line that looks like this:
   ```properties
   = SALESIQ_APP_ID=2782000005628361
   ```
   *(You will likely see the extra `=` here)*
4. **DELETE** that line completely.
5. **PASTE** this clean version instead:
   ```properties
   SALESIQ_APP_ID=2782000005628361
   ```
6. Click **Update/Save**.

## 📋 Full Clean Config (Copy-Paste if needed)

If you want to be 100% sure, delete **everything** in the Raw Editor and paste this (fill in your masked values):

```properties
SALESIQ_ACCESS_TOKEN=1005.b70ba538762f45d76038cac936c45461.5a78ee2495a926e5cd841ba71220451c
SALESIQ_APP_ID=2782000005628361
SALESIQ_DEPARTMENT_ID=2782000000002013
SALESIQ_SCREEN_NAME=rtdsportal
DESK_ACCESS_TOKEN=1000.eb9de9ebc4a2925d05ffe038fb280a2e.6d5df6b2fc942385c9991de24699a1d7
DESK_ORGANIZATION_ID=YOUR_ORG_ID
OPENAI_API_KEY=YOUR_OPENAI_KEY
```

This will force Railway to re-read the variables correctly.
