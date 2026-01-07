# 🚨 Fix Railway Build Error

The error `ERROR: invalid key-value pair "= SALESIQ_APP_ID=2782000005628361": empty key` means there is a **typo** in your Railway Environment Variables.

You likely have an extra `=` sign or space at the beginning of the `SALESIQ_APP_ID` variable.

## 🛠️ How to Fix It

1. Go to **Railway Dashboard** → Select your project.
2. Click on the **Variables** tab.
3. Look for `SALESIQ_APP_ID`.
4. **Check for typos:**
   - ❌ Incorrect: `= SALESIQ_APP_ID` (Leading equals sign)
   - ❌ Incorrect: ` SALESIQ_APP_ID` (Leading space)
   - ✅ Correct: `SALESIQ_APP_ID`

### If using "Raw Editor":
Check if you have a line that looks like this:
```
= SALESIQ_APP_ID=2782000005628361
```
**Delete the first `=` sign** so it looks like:
```
SALESIQ_APP_ID=2782000005628361
```

### After Fixing:
Railway will automatically restart the build. The error should disappear.
