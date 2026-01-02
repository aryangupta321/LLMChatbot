# Zoho Token Refresh Utility

Quick utility to refresh Zoho access tokens before testing.

## Two Configuration Modes

### Mode 1: Shared OAuth App (Recommended) ✅
**One OAuth app with both SalesIQ and Desk scopes**
- Same refresh token generates the same access token
- Use the same token for both `SALESIQ_ACCESS_TOKEN` and `DESK_ACCESS_TOKEN`
- Simpler setup, fewer credentials to manage

### Mode 2: Separate OAuth Apps
**Two separate OAuth apps (one for SalesIQ, one for Desk)**
- Different refresh tokens for each service
- Different access tokens for each service
- More complex but provides service isolation

## Setup

### For Shared OAuth App (Mode 1)

Add to your `.env` file:
```bash
ZOHO_REFRESH_TOKEN=your_long_lived_refresh_token
ZOHO_CLIENT_ID=your_oauth_client_id
ZOHO_CLIENT_SECRET=your_oauth_client_secret
ZOHO_ACCOUNTS_URL=https://accounts.zoho.in  # Optional, defaults to .in
```

The script will automatically use the same token for both services.

### For Separate OAuth Apps (Mode 2)

Add to your `.env` file:
```bash
# SalesIQ OAuth credentials
ZOHO_REFRESH_TOKEN=your_salesiq_refresh_token
ZOHO_CLIENT_ID=your_salesiq_client_id
ZOHO_CLIENT_SECRET=your_salesiq_client_secret

# Desk OAuth credentials (separate app)
ZOHO_DESK_REFRESH_TOKEN=your_desk_refresh_token
ZOHO_DESK_CLIENT_ID=your_desk_client_id
ZOHO_DESK_CLIENT_SECRET=your_desk_client_secret

ZOHO_ACCOUNTS_URL=https://accounts.zoho.in  # Optional
```

## Usage

```bash
# Refresh all tokens (SalesIQ + Desk)
python refresh_zoho_token.py --all

# Refresh specific token
python refresh_zoho_token.py --salesiq
python refresh_zoho_token.py --desk

# Refresh and auto-update .env file
python refresh_zoho_token.py --all --update-env
```

## Output

The script will:
- ✅ Refresh the access token(s)
- 📋 Display the new token (first 30 + last 10 chars)
- ⏰ Show expiration time (typically 1 hour)
- 📝 Optionally update your .env file

## For Railway Deployment

After refreshing tokens:
1. Copy the new token from the output
2. Go to Railway Dashboard → Your Service → Variables
3. Update the environment variable:
   - `SALESIQ_ACCESS_TOKEN=new_token`
   - `DESK_ACCESS_TOKEN=new_token`
4. Restart the service

## Token Expiration

- **Access tokens**: Expire after 1 hour
- **Refresh tokens**: Long-lived (months/years)
- **Recommendation**: Run this script before each testing session

## Troubleshooting

**"Missing required credentials"**
- Ensure all 3 variables are in .env: ZOHO_REFRESH_TOKEN, ZOHO_CLIENT_ID, ZOHO_CLIENT_SECRET

**"HTTP 400: invalid_code"**
- Your refresh token may have expired
- Generate a new refresh token from Zoho API Console

**"HTTP 401"**
- Check that client_id and client_secret are correct
- Ensure you're using the right Zoho domain (.in vs .com)

## Example Output

### Shared OAuth App (Mode 1)
```
======================================================================
🔐 Zoho Access Token Refresh Utility
======================================================================

ℹ️  Mode: Shared OAuth app (same token for SalesIQ + Desk)

🔄 Refreshing SalesIQ access token...
   Endpoint: https://accounts.zoho.in/oauth/v2/token
   Client ID: 1000.ABCDEF123456...
   Using shared OAuth credentials (same token for SalesIQ + Desk)
✅ SalesIQ token refreshed successfully!
   Token: 1000.a1b2c3d4e5f6g7h8i9j0...xyz789
   Length: 170 characters
   Valid for: 60 minutes

🔄 Desk token (using same token as SalesIQ)...
   ℹ️  Shared OAuth app - using same access token for both services
   
======================================================================
📊 Summary
======================================================================
SALESIQ: ✅ Success
  Token: 1000.a1b2c3d4e5f6g7h8i9j0...xyz789
DESK: ✅ Success
  Token: 1000.a1b2c3d4e5f6g7h8i9j0...xyz789  (same as SalesIQ)
```

### Separate OAuth Apps (Mode 2)
```
======================================================================
🔐 Zoho Access Token Refresh Utility
======================================================================

ℹ️  Mode: Separate OAuth apps (SalesIQ + Desk have different tokens)

🔄 Refreshing SalesIQ access token...
✅ SalesIQ token refreshed successfully!
   Token: 1000.salesiq_token_here...abc123

🔄 Refreshing Desk access token...
   Using separate Desk OAuth credentials
✅ Desk token refreshed successfully!
   Token: 1000.desk_token_here...xyz789
```
