# SalesIQ API URLs - Simple Guide

## 🔗 API URLs Used in Your Bot

### **Base URL**
```
https://salesiq.zoho.com/api/v2
```

---

## 1. **Chat Transfer API** (Option 1: Instant Chat)

### **URL**
```
POST https://salesiq.zoho.com/api/v2/chats
```

### **When Used**
- User selects "1" or "instant chat"
- Bot transfers conversation to human agent

### **Code Location**
```python
# File: zoho_api_integration.py
def create_chat_session(self, visitor_id: str, conversation_history: str):
    response = requests.post(
        f"{self.base_url}/chats",  # https://salesiq.zoho.com/api/v2/chats
        json=payload,
        headers=headers
    )
```

### **What It Sends**
```json
{
  "visitor_id": "session_123",
  "department_id": "your_dept_id", 
  "conversation_history": "User: QuickBooks frozen\nBot: Are you on dedicated server?...",
  "transfer_to": "human_agent"
}
```

### **What Happens**
1. Creates new chat session in SalesIQ
2. Transfers conversation to available agent
3. Agent sees full conversation history
4. Agent takes over the chat

---

## 2. **Chat Closure API** (Options 2, 3, and Resolved Issues)

### **URL**
```
PATCH https://salesiq.zoho.com/api/v2/chats/{session_id}
```

### **When Used**
- User selects "2" (callback) → Bot closes chat
- User selects "3" (ticket) → Bot closes chat  
- User says "working now!" → Bot closes chat

### **Code Location**
```python
# File: zoho_api_integration.py
def close_chat(self, session_id: str, reason: str = "resolved"):
    response = requests.patch(
        f"{self.base_url}/chats/{session_id}",  # https://salesiq.zoho.com/api/v2/chats/session_123
        json=payload,
        headers=headers
    )
```

### **What It Sends**
```json
{
  "status": "closed",
  "reason": "callback_scheduled",  // or "ticket_created" or "resolved"
  "closed_by": "bot"
}
```

### **What Happens**
1. Marks chat as closed in SalesIQ
2. Records closure reason
3. Chat widget closes for user
4. Conversation saved in transcripts

---

## 🔄 How It Works in Your Bot

### **Scenario 1: User Needs Human Help**
```
User: "not working"
Bot: Shows 3 options
User: "1" (instant chat)

→ Bot calls: POST /chats
→ Creates agent session
→ Agent takes over chat
→ Agent closes when done
```

### **Scenario 2: User Wants Callback**
```
User: "not working" 
Bot: Shows 3 options
User: "2" (callback)

→ Bot creates Desk ticket
→ Bot calls: PATCH /chats/{session_id}
→ Chat closes automatically
→ User gets email confirmation
```

### **Scenario 3: User Wants Ticket**
```
User: "not working"
Bot: Shows 3 options  
User: "3" (ticket)

→ Bot creates Desk ticket
→ Bot calls: PATCH /chats/{session_id}
→ Chat closes automatically
→ User gets email confirmation
```

### **Scenario 4: Issue Resolved**
```
User: "working now!"
Bot: "Great! Glad it's resolved..."

→ Bot calls: PATCH /chats/{session_id}
→ Chat closes automatically
→ Issue marked as resolved
```

---

## 🔑 Authentication

### **Headers Sent**
```json
{
  "Authorization": "Bearer YOUR_SALESIQ_API_KEY",
  "Content-Type": "application/json"
}
```

### **Environment Variables Needed**
```env
SALESIQ_API_KEY=your_api_key_here
SALESIQ_DEPARTMENT_ID=your_department_id_here
```

---

## 🛡️ Graceful Degradation (Without API Keys)

### **What Happens Now (No API Keys)**
```python
if not self.enabled:
    return {
        "success": True,
        "simulated": True,
        "message": "Chat transfer initiated (simulated)"
    }
```

### **Bot Behavior**
- ✅ All features work
- ✅ Users see proper responses
- ✅ Conversation memory cleared
- ⚠️ No actual API calls made
- ⚠️ Chat widget may stay open

### **With API Keys (Optional)**
- ✅ Real chat transfers
- ✅ Real chat closures
- ✅ Chat widget closes properly
- ✅ SalesIQ dashboard shows activity

---

## 📊 API Response Examples

### **Successful Transfer**
```json
{
  "success": true,
  "data": {
    "chat_id": "chat_12345",
    "agent_id": "agent_67890",
    "status": "transferred"
  }
}
```

### **Successful Closure**
```json
{
  "success": true,
  "message": "Chat session_123 closed"
}
```

### **Simulated (No API Keys)**
```json
{
  "success": true,
  "simulated": true,
  "message": "Chat session_123 closed (simulated)"
}
```

---

## 🔍 How to Monitor API Calls

### **Railway Logs**
```bash
railway logs --follow | grep -i "salesiq"
```

### **Look For**
```
[SalesIQ] Creating chat session for visitor session_123
[SalesIQ] Chat session created successfully
[SalesIQ] Closing chat session session_123  
[SalesIQ] Chat session_123 closed successfully
```

### **Or Simulated**
```
[SalesIQ] API disabled - simulating transfer
[SalesIQ] API disabled - simulating chat closure
```

---

## 📝 Summary

### **2 Main API Endpoints**

1. **Transfer Chat**: `POST /chats` 
   - Creates agent session
   - Transfers conversation
   - Agent handles closure

2. **Close Chat**: `PATCH /chats/{id}`
   - Bot closes chat
   - Records closure reason
   - Saves transcript

### **Works With or Without API Keys**
- **Without**: Simulated (logs actions)
- **With**: Real API calls to SalesIQ

### **User Experience**
- Clean chat endings
- Proper completion messages  
- Automatic closures when appropriate
- Full conversation history preserved

---

**Your bot now properly manages chat lifecycle using SalesIQ APIs!** 🚀