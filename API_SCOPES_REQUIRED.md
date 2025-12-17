# API Scopes Required for Chatbot

## 🔑 Exact Scopes Needed for Manager

### **SalesIQ API Scopes** (Chat Transfer & Closure)

#### **Required Scopes**
```
SalesIQ.chats.CREATE
SalesIQ.chats.UPDATE
SalesIQ.chats.READ
SalesIQ.departments.READ
```

#### **Scope Details**
| Scope | Purpose | Used For |
|-------|---------|----------|
| `SalesIQ.chats.CREATE` | Create new chat sessions | Transfer to human agent (Option 1) |
| `SalesIQ.chats.UPDATE` | Update chat status | Close chats (Options 2, 3, resolved) |
| `SalesIQ.chats.READ` | Read chat information | Verify chat exists before operations |
| `SalesIQ.departments.READ` | Read department info | Route chats to correct department |

#### **NOT Required** (Don't include these)
```
❌ SalesIQ.chats.DELETE
❌ SalesIQ.visitors.ALL
❌ SalesIQ.operators.ALL
❌ SalesIQ.reports.ALL
❌ SalesIQ.settings.ALL
```

---

### **Zoho Desk API Scopes** (Ticket Creation)

#### **Required Scopes**
```
Desk.tickets.CREATE
Desk.tickets.READ
Desk.contacts.CREATE
Desk.contacts.READ
```

#### **Scope Details**
| Scope | Purpose | Used For |
|-------|---------|----------|
| `Desk.tickets.CREATE` | Create support tickets | Callback requests (Option 2) & Support tickets (Option 3) |
| `Desk.tickets.READ` | Read ticket information | Verify ticket creation success |
| `Desk.contacts.CREATE` | Create customer contacts | Associate tickets with users |
| `Desk.contacts.READ` | Read contact information | Check if contact exists |

#### **NOT Required** (Don't include these)
```
❌ Desk.tickets.UPDATE
❌ Desk.tickets.DELETE
❌ Desk.settings.ALL
❌ Desk.reports.ALL
❌ Desk.agents.ALL
```

---

## 📋 Complete Scope List for Manager

### **Copy-Paste for Manager**

**SalesIQ API Scopes:**
```
SalesIQ.chats.CREATE
SalesIQ.chats.UPDATE
SalesIQ.chats.READ
SalesIQ.departments.READ
```

**Zoho Desk API Scopes:**
```
Desk.tickets.CREATE
Desk.tickets.READ
Desk.contacts.CREATE
Desk.contacts.READ
```

---

## 🔐 API Key Generation Steps for Manager

### **Step 1: SalesIQ API Key**

1. **Login to Zoho SalesIQ**
   - Go to: https://salesiq.zoho.com
   - Login with admin account

2. **Navigate to API Settings**
   - Settings → Developer Space → API
   - Or: https://salesiq.zoho.com/settings/developer-space/api

3. **Create New API Key**
   - Click "Generate API Key"
   - Name: "Chatbot Integration"
   - Select scopes: `SalesIQ.chats.CREATE`, `SalesIQ.chats.UPDATE`, `SalesIQ.chats.READ`, `SalesIQ.departments.READ`

4. **Get Department ID**
   - Settings → Departments
   - Copy the Department ID for support team

### **Step 2: Zoho Desk OAuth Token**

1. **Login to Zoho Desk**
   - Go to: https://desk.zoho.com
   - Login with admin account

2. **Navigate to API Settings**
   - Setup → Developer Space → API
   - Or: https://desk.zoho.com/support/[org]/ShowHomePage.do#Setup/developer-space/api

3. **Create OAuth Application**
   - Click "Add Client"
   - Client Type: "Self Client"
   - Name: "Chatbot Integration"
   - Select scopes: `Desk.tickets.CREATE`, `Desk.tickets.READ`, `Desk.contacts.CREATE`, `Desk.contacts.READ`

4. **Generate OAuth Token**
   - Click "Generate Token"
   - Copy the OAuth token

5. **Get Organization ID**
   - Setup → General → Organization Profile
   - Copy the Organization ID

---

## 🎯 What Each API Does

### **SalesIQ APIs Used**

#### **1. Create Chat Session** (Transfer to Agent)
```http
POST https://salesiq.zoho.com/api/v2/chats
```
**Requires**: `SalesIQ.chats.CREATE`
**Purpose**: Transfer bot conversation to human agent

#### **2. Close Chat Session** (End Conversation)
```http
PATCH https://salesiq.zoho.com/api/v2/chats/{session_id}
```
**Requires**: `SalesIQ.chats.UPDATE`
**Purpose**: Close chat after callback/ticket creation

### **Zoho Desk APIs Used**

#### **1. Create Support Ticket**
```http
POST https://desk.zoho.com/api/v1/tickets
```
**Requires**: `Desk.tickets.CREATE`
**Purpose**: Create callback requests and support tickets

#### **2. Create Contact** (if needed)
```http
POST https://desk.zoho.com/api/v1/contacts
```
**Requires**: `Desk.contacts.CREATE`
**Purpose**: Associate tickets with customer information

---

## 🔒 Security Best Practices

### **Principle of Least Privilege**
- ✅ Only request scopes actually used
- ✅ No admin or delete permissions
- ✅ No access to sensitive data
- ✅ Read-only where possible

### **Scope Justification**
| API Call | Scope | Justification |
|----------|-------|---------------|
| Transfer chat | `SalesIQ.chats.CREATE` | Create agent session |
| Close chat | `SalesIQ.chats.UPDATE` | Mark chat as closed |
| Create ticket | `Desk.tickets.CREATE` | Support requests |
| Link contact | `Desk.contacts.CREATE` | Associate user info |

---

## 📧 Email Template for Manager

### **Subject**: API Key Request - Chatbot Integration

**Dear [Manager Name],**

I need API keys for our customer support chatbot integration. The bot needs to:
1. Transfer chats to human agents
2. Create support tickets
3. Close completed chats

**Required API Scopes:**

**SalesIQ API:**
- SalesIQ.chats.CREATE (transfer to agents)
- SalesIQ.chats.UPDATE (close chats)
- SalesIQ.chats.READ (verify operations)
- SalesIQ.departments.READ (route correctly)

**Zoho Desk API:**
- Desk.tickets.CREATE (create tickets)
- Desk.tickets.READ (verify creation)
- Desk.contacts.CREATE (link customers)
- Desk.contacts.READ (check existing)

These are minimal scopes following security best practices. No admin or delete permissions requested.

**Deliverables Needed:**
1. SalesIQ API Key + Department ID
2. Desk OAuth Token + Organization ID

**Timeline:** [Your timeline]

Thank you!

---

## 🚀 After Getting API Keys

### **Environment Variables to Set**
```env
# SalesIQ
SALESIQ_API_KEY=your_salesiq_api_key_here
SALESIQ_DEPARTMENT_ID=your_department_id_here

# Zoho Desk  
DESK_OAUTH_TOKEN=your_desk_oauth_token_here
DESK_ORGANIZATION_ID=your_organization_id_here
```

### **Test API Access**
```bash
# Test SalesIQ API
curl -H "Authorization: Bearer YOUR_API_KEY" \
     https://salesiq.zoho.com/api/v2/departments

# Test Desk API  
curl -H "Authorization: Zoho-oauthtoken YOUR_OAUTH_TOKEN" \
     https://desk.zoho.com/api/v1/tickets?limit=1
```

---

## ✅ Verification Checklist

**Before requesting keys:**
- [ ] Confirmed exact scopes needed
- [ ] Prepared justification for each scope
- [ ] Ready to test integration

**After receiving keys:**
- [ ] Added to environment variables
- [ ] Tested API connectivity
- [ ] Verified bot functionality
- [ ] Monitored for errors

---

**These are the EXACT minimum scopes needed for your chatbot!** 🔐

**No additional permissions required.**