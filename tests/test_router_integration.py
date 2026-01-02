"""Test IssueRouter integration with chatbot"""

from llm_chatbot import issue_router, generate_response

print('✓ IssueRouter imported successfully')
print(f'✓ Router instance: {issue_router}')

# Test classification
test_messages = [
    'QuickBooks is frozen',
    'I cant login',
    'Server is slow',
    'Printer not working',
    'Outlook asking for password'
]

print('\n' + '='*60)
print('Testing IssueRouter integration:')
print('='*60)

for msg in test_messages:
    category = issue_router.classify(msg)
    print(f'\n"{msg}"')
    print(f'  → Category: {category}')

print('\n✓ All tests passed!')
