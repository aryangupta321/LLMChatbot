# Zoho Desk API Integration Guide

## Getting Desk API Credentials

### Step 1: Get Your Desk Organization ID
1. Go to https://desk.zoho.in
2. Login with your Zoho account
3. Click **Settings** → **General**
4. Look for **Organization ID** - copy it

Example: `567890123456`

### Step 2: Generate Desk OAuth Token
1. Go to https://accounts.zoho.in/developerconsole
2. Click **Add Client**
3. Select **Server-based Applications**
4. Fill in:
   - **Client Name:** Desk API Client
   - **Redirect URI:** `http://localhost:8000/callback` (or your Railway URL)
   - **Scope:** Add these scopes:
     - `Desk.contacts.READ`
     - `Desk.contacts.CREATE`
     - `Desk.tickets.READ`
     - `Desk.tickets.CREATE`
     - `Desk.tickets.UPDATE`
5. Click **Create**
6. Copy the **Client ID** and **Client Secret**

### Step 3: Generate Access Token

Run this PowerShell command (Windows):

```powershell
$clientId = "YOUR_CLIENT_ID"
$clientSecret = "YOUR_CLIENT_SECRET"
$redirectUri = "http://localhost:8000/callback"

# Step 1: Get authorization code
$authUrl = "https://accounts.zoho.in/oauth/v2/org/auth?scope=Desk.contacts.READ,Desk.contacts.CREATE,Desk.tickets.READ,Desk.tickets.CREATE,Desk.tickets.UPDATE&client_id=$clientId&state=desk&response_type=code&redirect_uri=$redirectUri&access_type=offline&prompt=consent"

Write-Host "Visit this URL in your browser:"
Write-Host $authUrl

# After authorization, you'll see the code in the URL - copy it
$code = Read-Host "Enter the authorization code from the callback URL"

# Step 2: Exchange code for token
$response = Invoke-RestMethod -Uri "https://accounts.zoho.in/oauth/v2/token" -Method POST -Body @{
    code = $code
    grant_type = "authorization_code"
    client_id = $clientId
    client_secret = $clientSecret
    redirect_uri = $redirectUri
}

Write-Host "Access Token:"
Write-Host $response.access_token
Write-Host "Refresh Token:"
Write-Host $response.refresh_token
```

### Step 4: Update .env File

Add these variables to your `.env`:

```dotenv
# Desk API Configuration
DESK_ACCESS_TOKEN=1005.xxxxxxxxxxxx.xxxxxxxxxxxx
DESK_ORGANIZATION_ID=567890123456
DESK_API_URL=https://desk.zoho.in/api/v1
```

### Step 5: Update Railway Environment Variables

Go to https://railway.app/dashboard:

1. Click your project → **web** service
2. Click **Variables** tab
3. Add these variables:
   - `DESK_ACCESS_TOKEN`
   - `DESK_ORGANIZATION_ID`
   - `DESK_API_URL` (set to: `https://desk.zoho.in/api/v1`)
4. Click **Deploy**

---

## Chatbot Features Using Desk API

### Feature 1: Create Support Ticket

**When User Selects "Create Ticket":**

1. Chatbot asks for:
   - Customer name
   - Email
   - Phone number
   - Issue description

2. System creates ticket in Desk with:
   - Auto-creates or finds existing contact
   - Subject: Customer issue title
   - Priority: Medium (adjustable)
   - Status: Open
   - Department: Support

3. Customer gets confirmation with ticket number

**Code in `llm_chatbot.py`:**
```python
api_result = desk_api.create_support_ticket(
    subject="Customer Issue - Chat Support Request",
    description=conversation_history,
    user_email="customer@example.com",
    phone="+1234567890",
    contact_name="John Doe",
    priority="Medium"
)
```

### Feature 2: Schedule Callback

**When User Selects "Schedule Callback":**

1. Chatbot asks for:
   - Preferred callback time
   - Phone number
   - Name

2. System creates callback ticket in Desk with:
   - Department: "Callbacks"
   - Priority: Medium
   - Status: Open
   - Notes: Callback time and customer info

3. Desk team can see all pending callbacks

**Code in `llm_chatbot.py`:**
```python
api_result = desk_api.create_callback_ticket(
    user_email="customer@example.com",
    phone="+1234567890",
    preferred_time="Tomorrow at 2 PM",
    contact_name="John Doe",
    description="Customer requested callback"
)
```

---

## Testing Desk API Locally

### Test 1: Create Support Ticket

Run in PowerShell:

```powershell
$response = Invoke-RestMethod -Uri "http://localhost:8000/test/desk-ticket" -Method POST -Body @{
    email = "test@example.com"
    name = "Test User"
    phone = "1234567890"
    subject = "Test Ticket"
    description = "This is a test ticket"
} | ConvertTo-Json

Write-Host $response
```

### Test 2: Create Callback

Run in PowerShell:

```powershell
$response = Invoke-RestMethod -Uri "http://localhost:8000/test/desk-callback" -Method POST -Body @{
    email = "test@example.com"
    phone = "1234567890"
    preferred_time = "Tomorrow at 3 PM"
    name = "Test User"
} | ConvertTo-Json

Write-Host $response
```

---

## Troubleshooting

### Error: "Invalid OAuthToken"
- Token may have expired
- Generate new token using steps above
- Update .env and .env

### Error: "Organization ID not found"
- Copy Organization ID from Desk settings exactly
- Make sure it's set in both .env and Railway Variables

### Error: "Contact creation failed"
- Check if email format is valid
- Verify Desk API scope includes `Desk.contacts.CREATE`

### Tickets not appearing in Desk
- Check if API call returned success
- Verify Department ID is correct
- Check Desk dashboard for any blocking rules

---

## API Endpoints Reference

### Create Support Ticket
```
POST https://desk.zoho.in/api/v1/tickets
Authorization: Zoho-oauthtoken {token}
X-Orgn-Id: {organization_id}

{
  "subject": "Issue Title",
  "description": "Detailed description",
  "contactId": "123456",
  "priority": "Medium",
  "departmentId": "Support",
  "status": "Open"
}
```

### Create Contact
```
POST https://desk.zoho.in/api/v1/contacts
Authorization: Zoho-oauthtoken {token}
X-Orgn-Id: {organization_id}

{
  "email": "customer@example.com",
  "firstName": "John",
  "lastName": "Doe",
  "phone": "+1234567890"
}
```

### Search Contacts
```
GET https://desk.zoho.in/api/v1/contacts?email=customer@example.com
Authorization: Zoho-oauthtoken {token}
X-Orgn-Id: {organization_id}
```

---

## Next Steps

1. ✅ Get Desk credentials
2. ✅ Add to .env file
3. ✅ Update Railway variables
4. ✅ Test locally with Postman
5. ✅ Deploy to Railway
6. ✅ Test on SalesIQ widget

For questions, check Zoho Desk API docs: https://www.zoho.com/desk/api/v1/
