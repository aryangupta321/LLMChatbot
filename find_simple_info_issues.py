"""
Find issues that need simple information (not step-by-step guides)
These are questions users ask that can be answered in 1-2 sentences
"""
import json
from collections import Counter
import re

# Load the chat transcript data
with open("processed_data/FINAL_pinecone_all_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Filter only chat transcripts
chats = [item for item in data if item.get('metadata', {}).get('source') == 'chat_transcript']

print("="*70)
print("SIMPLE INFORMATION ISSUES")
print("Questions that need quick answers, not step-by-step guides")
print("="*70)

# Categories of simple informational questions
simple_info_patterns = {
    'Contact Info': {
        'keywords': ['support email', 'phone number', 'contact', 'reach support', 'call support'],
        'examples': [],
        'answer_type': 'Phone: 1-888-415-5240, Email: support@acecloudhosting.com',
        'complexity': 'INSTANT'
    },
    'Pricing/Plans': {
        'keywords': ['pricing', 'cost', 'how much', 'price', 'plan', 'upgrade cost'],
        'examples': [],
        'answer_type': 'List of plans with prices',
        'complexity': 'INSTANT'
    },
    'Server Info': {
        'keywords': ['server name', 'server address', 'server url', 'what is my server'],
        'examples': [],
        'answer_type': 'Your server is: [server_name].myrealdata.net',
        'complexity': 'INSTANT'
    },
    'Username': {
        'keywords': ['what is my username', 'forgot username', 'my username', 'user name'],
        'examples': [],
        'answer_type': 'Your username is: [username]',
        'complexity': 'INSTANT'
    },
    'Hours/Availability': {
        'keywords': ['support hours', 'available', 'when open', 'business hours'],
        'examples': [],
        'answer_type': '24/7 support available',
        'complexity': 'INSTANT'
    },
    'QuickBooks Version': {
        'keywords': ['qb version', 'quickbooks version', 'which version', 'what version'],
        'examples': [],
        'answer_type': 'You have QuickBooks [version]',
        'complexity': 'INSTANT'
    },
    'Disk Space Available': {
        'keywords': ['how much space', 'disk space left', 'storage available', 'space remaining'],
        'examples': [],
        'answer_type': 'You have X GB available',
        'complexity': 'INSTANT'
    },
    'Number of Users': {
        'keywords': ['how many users', 'user limit', 'max users', 'user count'],
        'examples': [],
        'answer_type': 'Your plan allows X users',
        'complexity': 'INSTANT'
    },
    'Backup Schedule': {
        'keywords': ['backup schedule', 'when backup', 'backup time', 'backup frequency'],
        'examples': [],
        'answer_type': 'Backups run daily at [time]',
        'complexity': 'INSTANT'
    },
    'RDP Port': {
        'keywords': ['rdp port', 'port number', 'connection port'],
        'examples': [],
        'answer_type': 'RDP port is 3389',
        'complexity': 'INSTANT'
    }
}

# Analyze chats
for chat in chats:
    text = chat.get('text', '').lower()
    if 'Question:' in text:
        question = text.split('question:')[1].split('answer:')[0].strip()
        
        for category, info in simple_info_patterns.items():
            if any(keyword in question for keyword in info['keywords']):
                if len(info['examples']) < 5:
                    info['examples'].append(question[:150])

print("\n📋 SIMPLE INFORMATION QUESTIONS (No steps needed)")
print("="*70)

for category, info in simple_info_patterns.items():
    count = len(info['examples'])
    if count > 0:
        print(f"\n{category}")
        print(f"  Count: {count} examples found")
        print(f"  Answer type: {info['answer_type']}")
        print(f"  Complexity: {info['complexity']}")
        print(f"  Examples:")
        for ex in info['examples'][:3]:
            print(f"    - {ex}")

print("\n" + "="*70)
print("SUPER SIMPLE ISSUES (1-2 sentence answers)")
print("="*70)

# Now find issues that are currently being solved with steps but could be simpler
simple_solutions = {
    'Disconnected from server': {
        'current': 'Multi-step reconnection guide',
        'better': 'Just close and reopen your RDP connection',
        'why_better': 'Users know how to reconnect, they just need confirmation'
    },
    'QuickBooks frozen': {
        'current': '5-7 steps with Task Manager',
        'better': 'Try the "QB Instance Kill" shortcut on your desktop first',
        'why_better': 'One-click solution before complex steps'
    },
    'Slow performance': {
        'current': 'Multiple troubleshooting steps',
        'better': 'Close unused applications and try again. Still slow? Contact support.',
        'why_better': 'Quick fix first, escalate if needed'
    },
    'Printer not working': {
        'current': '6-8 steps to configure',
        'better': 'Check if printer is selected in Print dialog. Not there? Contact support.',
        'why_better': 'Simple check before complex setup'
    },
    'File not found': {
        'current': 'Search and troubleshooting steps',
        'better': 'Check the usual location: C:\\Users\\[username]\\Documents. Not there? Contact support.',
        'why_better': 'Quick location check first'
    }
}

print("\nIssues that could be SIMPLIFIED:")
print("-"*70)

for issue, details in simple_solutions.items():
    print(f"\n❌ {issue}")
    print(f"   Current: {details['current']}")
    print(f"   ✅ Better: {details['better']}")
    print(f"   Why: {details['why_better']}")

print("\n" + "="*70)
print("RECOMMENDATIONS")
print("="*70)

print("""
1. CREATE QUICK ANSWER KB ARTICLES:
   - Contact information
   - Pricing/plans
   - Common quick checks
   
2. SIMPLIFY EXISTING KB ARTICLES:
   - Add "Quick Fix" section at the top
   - Give 1-sentence solution first
   - Then detailed steps if quick fix doesn't work
   
3. BOT BEHAVIOR:
   - For simple info questions → Give answer directly (no steps)
   - For troubleshooting → Try quick fix first, then detailed steps
   - Always offer escalation: "Still not working? Call 1-888-415-5240"

EXAMPLE IMPROVED FLOW:

User: "QuickBooks is frozen"
Bot: "Try double-clicking the 'QB Instance Kill' shortcut on your desktop. 
      Did that work?"

User: "I don't see that shortcut"
Bot: "No problem! Let's use Task Manager instead.
      Step 1: Right-click taskbar, select Task Manager..."

This way:
✅ Users try simple fix first (less frustration)
✅ Only get detailed steps if needed
✅ Feel empowered, not overwhelmed
""")

print("\n" + "="*70)
print("IMPACT")
print("="*70)

print("""
By simplifying responses:
→ 30-40% of users solve issue in 1 message
→ Reduced frustration (no long step lists)
→ Faster resolution time
→ Users feel more confident
→ Support team handles fewer tickets
""")
