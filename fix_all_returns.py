import re

with open('llm_chatbot.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Count before
before = content.count('return {')
print(f'Found {before} plain dict returns')

# Pattern 1: return with suggestions
pattern1 = r'return\s+\{\s+"action":\s"reply",\s+"replies":\s(\[[^\]]+\]),\s+"suggestions":\s(\[[^\]]*?\]),\s+"session_id":\s+session_id\s+\}'
replacement1 = r'return JSONResponse(status_code=200, content={"action": "reply", "replies": \1, "suggestions": \2, "session_id": session_id})'
content = re.sub(pattern1, replacement1, content, flags=re.DOTALL)

# Pattern 2: return without suggestions (simple)
pattern2 = r'return\s+\{\s+"action":\s"reply",\s+"replies":\s(\[[^\]]+\]),\s+"session_id":\s+session_id\s+\}'
replacement2 = r'return JSONResponse(status_code=200, content={"action": "reply", "replies": \1, "session_id": session_id})'
content = re.sub(pattern2, replacement2, content, flags=re.DOTALL)

# Count after
after = content.count('return {')
print(f'After regex: {after} plain dict returns remaining')
print(f'Replaced: {before - after} returns')

with open('llm_chatbot.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ Fixed returns')
