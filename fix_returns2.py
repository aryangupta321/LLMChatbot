#!/usr/bin/env python3
import re

# Read file
with open('llm_chatbot.py', 'r', encoding='utf-8') as f:
    content = f.read()

# List of patterns to replace
replacements = [
    # Pattern for returns with suggestions
    (
        r'return \{\s+\"action\": \"reply\",\s+\"replies\": (\[[^\]]+\]),\s+\"suggestions\": (\[[^\]]+\]),\s+\"session_id\": session_id\s+\}',
        r'return JSONResponse(status_code=200, content={"action": "reply", "replies": \1, "suggestions": \2, "session_id": session_id})'
    ),
    # Pattern for simple returns
    (
        r'return \{\s+\"action\": \"reply\",\s+\"replies\": (\[[^\]]+\]),\s+\"session_id\": session_id\s+\}',
        r'return JSONResponse(status_code=200, content={"action": "reply", "replies": \1, "session_id": session_id})'
    ),
]

# Apply replacements
for pattern, replacement in replacements:
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)

print(f"Applying {len(replacements)} regex patterns...")

# Write back
with open('llm_chatbot.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ Fixed return statements')
