# 🧹 Deep Clean: Delete and Re-Add

Since the Raw Editor looks clean but the error persists, there is likely a **hidden character** or a **corrupted entry** that is stuck in Railway's database.

We need to **delete the variable completely** and re-create it.

## 1. Remove the Variable
1. Go to **Railway Dashboard** → **Variables**.
2. Switch to the **List View** (Exit Raw Editor).
3. Find `SALESIQ_APP_ID`.
4. Click the **Trash Icon 🗑️** next to it to delete it.
5. **Click "Deploy" or "Update"** (if prompted) to save the state without the variable.

## 2. Re-Add the Variable
1. Click **"New Variable"**.
2. **VARIABLE_NAME**: `SALESIQ_APP_ID`
   *(Type this manually, do not copy-paste to avoid hidden chars)*
3. **VALUE**: `2782000005628361`
4. Click **Add**.

## 3. Remove Quotes (Recommended)
In your Raw Editor, you have quotes around the values. While usually okay, it's safer to remove them to avoid parsing issues.

**Change this:**
```properties
SALESIQ_APP_ID="2782000005628361"
```
**To this:**
```properties
SALESIQ_APP_ID=2782000005628361
```

(Do this for all variables if possible)

## 4. Trigger a Redeploy
Once fixed, if it doesn't auto-deploy:
1. Go to **Deployments**.
2. Click **Redeploy**.
