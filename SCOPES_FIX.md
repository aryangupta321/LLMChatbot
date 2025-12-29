# Zoho Desk API Scopes Fix

The error `HTTP 401 - INVALID_OAUTH` and the failure to fetch departments/contacts is happening because your current OAuth token is missing required permissions (Scopes).

You currently have:
- `Desk.tickets.CREATE`
- `Desk.activities.calls.CREATE`
- `Desk.activities.CREATE`

**You are missing permissions to READ departments and READ/CREATE contacts.** The API cannot create a "Call" without first finding or creating a "Contact" to attach it to.

## Required Scopes
Please regenerate your OAuth Access Token with the following **ALL** scopes:

```text
Desk.settings.READ
Desk.contacts.READ
Desk.contacts.CREATE
Desk.activities.calls.CREATE
Desk.tickets.CREATE
```

### Why each is needed:
1. **`Desk.settings.READ`**: To fetch the default Department ID (unless you set `DESK_DEPARTMENT_ID` in env vars).
2. **`Desk.contacts.READ`**: To search if the visitor (`aryan.gupta@...`) already exists in Desk.
3. **`Desk.contacts.CREATE`**: To create a new contact if they don't exist.
4. **`Desk.activities.calls.CREATE`**: To actually schedule the Callback.

## Action Plan
1. **Regenerate Token**: Go to Zoho Developer Console (or wherever you generate the token) and create a new Access Token including ALL the scopes above.
2. **Update Railway**: Update the `DESK_ACCESS_TOKEN` variable in Railway with the new token.
3. **Verify Base URL**: Ensure `DESK_BASE_URL` matches the data center where you generated the token (e.g., `https://desk.zoho.com/api/v1` or `https://desk.zoho.in/api/v1`).
4. **Restart**: Restart the Railway service.

Once this is done, the `401` errors for departments and contacts should disappear.
