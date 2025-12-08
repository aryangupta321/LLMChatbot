"""
Extract top common issues from 9 months of chat transcripts
Focus on issues that can be solved with simple steps
"""
import json
from collections import Counter, defaultdict
import re

# Load the chat transcript data
with open("processed_data/FINAL_pinecone_all_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Filter only chat transcripts
chats = [item for item in data if item.get('metadata', {}).get('source') == 'chat_transcript']

print("="*80)
print("TOP COMMON ISSUES FROM 9 MONTHS OF CHAT TRANSCRIPTS")
print("="*80)
print(f"Total chat transcripts analyzed: {len(chats)}")
print()

# Define issue categories with keywords
issue_categories = {
    'QuickBooks Frozen/Not Responding': ['frozen', 'freeze', 'not responding', 'stuck', 'hang', 'qb frozen'],
    'Password Reset': ['password', 'reset password', 'forgot password', 'change password'],
    'Login Issues': ['login', 'log in', 'sign in', 'cant login', "can't login", 'login failed'],
    'Email/Outlook Issues': ['email', 'outlook', 'send email', 'cant send email', 'email not working'],
    'Printer Issues': ['printer', 'print', 'printing', 'cant print', 'printer not working'],
    'Slow Performance': ['slow', 'slowness', 'running slow', 'performance', 'lagging'],
    'Disconnection Issues': ['disconnect', 'disconnected', 'connection lost', 'keeps disconnecting'],
    'Screen/Display Issues': ['screen', 'resolution', 'display', 'monitor', 'screen size'],
    'QuickBooks Error Codes': ['error -6', 'error 6', 'error code', 'qb error', 'error -80'],
    'File Not Found': ['file not found', 'cant find', "can't find", 'missing file', 'where is'],
    'Multi-User Issues': ['multi-user', 'multiple users', 'user limit', 'switch to multi'],
    'Backup/Restore': ['backup', 'restore', 'backup failed', 'restore file'],
    'Disk Space': ['disk space', 'storage', 'space full', 'low space', 'out of space'],
    'QuickBooks Update': ['qb update', 'quickbooks update', 'update quickbooks', 'payroll update'],
    'Remote Desktop Issues': ['rdp', 'remote desktop', 'cant connect', 'connection failed'],
    'License/Activation': ['license', 'activation', 'activate', 'license expired'],
    'Company File Issues': ['company file', 'cant open file', 'file damaged', 'file corrupt'],
    'User Access/Permissions': ['user access', 'permission', 'cant access', 'access denied'],
    'QuickBooks Crash': ['crash', 'crashed', 'qb crashed', 'closes unexpectedly'],
    'Bank Feed Issues': ['bank feed', 'bank connection', 'bank sync', 'banking']
}

# Count issues
issue_counts = Counter()
issue_examples = defaultdict(list)

for chat in chats:
    text = chat.get('text', '').lower()
    if 'question:' in text:
        question = text.split('question:')[1].split('answer:')[0].strip()
        
        # Categorize the question
        for category, keywords in issue_categories.items():
            if any(keyword in question for keyword in keywords):
                issue_counts[category] += 1
                if len(issue_examples[category]) < 5:
                    issue_examples[category].append(question[:120])
                break  # Only count once per category

# Sort by frequency
sorted_issues = issue_counts.most_common(20)

print("\n" + "="*80)
print("TOP 20 MOST COMMON ISSUES")
print("="*80)
print(f"\n{'#':<4} {'ISSUE':<40} {'COUNT':<10} {'%':<8}")
print("-"*80)

total_categorized = sum(issue_counts.values())
for i, (issue, count) in enumerate(sorted_issues, 1):
    percentage = (count / len(chats)) * 100
    print(f"{i:<4} {issue:<40} {count:<10} {percentage:.1f}%")

print("\n" + "="*80)
print("DETAILED BREAKDOWN WITH EXAMPLES")
print("="*80)

for i, (issue, count) in enumerate(sorted_issues[:15], 1):
    percentage = (count / len(chats)) * 100
    print(f"\n{i}. {issue}")
    print(f"   Frequency: {count} tickets ({percentage:.1f}%)")
    print(f"   Real examples:")
    for example in issue_examples[issue][:3]:
        print(f"   • {example}...")

print("\n" + "="*80)
print("ISSUES THAT NEED SIMPLE KB ARTICLES")
print("="*80)

# Identify which issues can be solved with simple steps
simple_solvable = {
    'QuickBooks Frozen/Not Responding': {
        'count': issue_counts.get('QuickBooks Frozen/Not Responding', 0),
        'priority': 'HIGH',
        'steps_needed': '2-3 simple steps',
        'solution': 'Use QB Instance Kill shortcut or Task Manager',
        'user_friendly': 'YES - Very simple'
    },
    'Password Reset': {
        'count': issue_counts.get('Password Reset', 0),
        'priority': 'HIGH',
        'steps_needed': '3-5 simple steps',
        'solution': 'Self-Care portal password reset',
        'user_friendly': 'YES - Already have KB'
    },
    'Disconnection Issues': {
        'count': issue_counts.get('Disconnection Issues', 0),
        'priority': 'MEDIUM',
        'steps_needed': '1-2 simple steps',
        'solution': 'Close and reconnect RDP',
        'user_friendly': 'YES - Very simple'
    },
    'Screen/Display Issues': {
        'count': issue_counts.get('Screen/Display Issues', 0),
        'priority': 'MEDIUM',
        'steps_needed': '2-3 simple steps',
        'solution': 'Adjust RDP display settings',
        'user_friendly': 'YES - Already have KB'
    },
    'Disk Space': {
        'count': issue_counts.get('Disk Space', 0),
        'priority': 'MEDIUM',
        'steps_needed': '3-4 simple steps',
        'solution': 'Clear temp files and recycle bin',
        'user_friendly': 'YES - Already have KB'
    },
    'Printer Issues': {
        'count': issue_counts.get('Printer Issues', 0),
        'priority': 'MEDIUM',
        'steps_needed': '3-4 steps',
        'solution': 'Enable printer redirection',
        'user_friendly': 'MEDIUM - Needs simplification'
    },
    'Slow Performance': {
        'count': issue_counts.get('Slow Performance', 0),
        'priority': 'LOW',
        'steps_needed': '2-3 simple steps',
        'solution': 'Close unused apps, check resources',
        'user_friendly': 'YES - Can be simple'
    }
}

print("\n{:<35} {:<10} {:<12} {:<20}".format("ISSUE", "COUNT", "PRIORITY", "USER-FRIENDLY"))
print("-"*80)

for issue, details in sorted(simple_solvable.items(), key=lambda x: x[1]['count'], reverse=True):
    if details['count'] > 0:
        print("{:<35} {:<10} {:<12} {:<20}".format(
            issue[:34],
            details['count'],
            details['priority'],
            details['user_friendly']
        ))

print("\n" + "="*80)
print("RECOMMENDED NEW KB ARTICLES TO CREATE")
print("="*80)

recommendations = [
    {
        'title': 'Quick Fix: QuickBooks Frozen',
        'issue': 'QuickBooks Frozen/Not Responding',
        'count': issue_counts.get('QuickBooks Frozen/Not Responding', 0),
        'steps': [
            'Look for "QB Instance Kill" shortcut on desktop',
            'Double-click it',
            'Wait 10 seconds, then reopen QuickBooks',
            'If no shortcut: Right-click taskbar → Task Manager → End QuickBooks'
        ],
        'why_needed': 'Most common issue, needs quick 1-click solution first'
    },
    {
        'title': 'Quick Fix: Disconnected from Server',
        'issue': 'Disconnection Issues',
        'count': issue_counts.get('Disconnection Issues', 0),
        'steps': [
            'Close the RDP window completely',
            'Wait 5 seconds',
            'Double-click your server shortcut to reconnect',
            'Still disconnecting? Contact support at 1-888-415-5240'
        ],
        'why_needed': 'Very common, users just need confirmation to reconnect'
    },
    {
        'title': 'Quick Fix: QuickBooks Running Slow',
        'issue': 'Slow Performance',
        'count': issue_counts.get('Slow Performance', 0),
        'steps': [
            'Close any unused applications',
            'Close extra browser tabs',
            'Log out and log back in',
            'Still slow? Contact support at 1-888-415-5240'
        ],
        'why_needed': 'Simple checks before escalating to support'
    },
    {
        'title': 'Quick Fix: Printer Not Showing',
        'issue': 'Printer Issues',
        'count': issue_counts.get('Printer Issues', 0),
        'steps': [
            'In QuickBooks, go to File → Print',
            'Check if your printer appears in the list',
            'Not there? Log out and log back in',
            'Still missing? Contact support at 1-888-415-5240'
        ],
        'why_needed': 'Simple check before complex printer setup'
    }
]

for i, rec in enumerate(recommendations, 1):
    print(f"\n{i}. {rec['title']}")
    print(f"   Issue: {rec['issue']}")
    print(f"   Frequency: {rec['count']} tickets")
    print(f"   Why needed: {rec['why_needed']}")
    print(f"   Simple steps:")
    for j, step in enumerate(rec['steps'], 1):
        print(f"      {j}. {step}")

print("\n" + "="*80)
print("SUMMARY & IMPACT")
print("="*80)

total_simple = sum(details['count'] for details in simple_solvable.values() if details['count'] > 0)
total_percentage = (total_simple / len(chats)) * 100

print(f"""
Total issues that can be solved with simple steps: {total_simple}
Percentage of all tickets: {total_percentage:.1f}%

If we create these simple KB articles:
→ {total_simple} tickets could be self-served
→ {total_percentage:.1f}% reduction in support workload
→ Users get instant solutions (no waiting)
→ Less frustration (simple steps, not complex guides)
→ Support team focuses on complex issues

NEXT STEPS:
1. Create the 4 "Quick Fix" KB articles above
2. Add them to Pinecone
3. Update bot to prioritize quick fixes
4. Monitor reduction in support tickets
""")

print("="*80)
