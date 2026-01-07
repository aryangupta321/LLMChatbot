#!/usr/bin/env python3
"""
Convert all plain dict returns in the SalesIQ webhook to JSONResponse
This is critical because SalesIQ cannot parse plain Python dicts
"""

# Read file
with open('llm_chatbot.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Lines to fix based on grep output above
# Focus on webhook returns (starting from line 566)
webhook_return_lines = [566, 761, 824, 903, 928, 961, 971, 982, 1001, 1058, 1090, 1165, 1215]

# Track which lines we've modified
modified_count = 0

# Process line by line
i = 0
while i < len(lines):
    line = lines[i]
    
    # Check if this is one of our target lines (with some tolerance for line number shifts)
    if 'return {' in line and i > 550:  # Only in webhook section
        # Look ahead to find the complete return statement
        if '"action"' in line or '"action"' in (lines[i+1] if i+1 < len(lines) else ''):
            # This looks like a webhook return statement
            # Find the closing brace
            return_lines = [line]
            i += 1
            brace_count = line.count('{') - line.count('}')
            
            while i < len(lines) and brace_count > 0:
                return_lines.append(lines[i])
                brace_count += lines[i].count('{') - lines[i].count('}')
                i += 1
            
            # Now transform the return statement
            block_text = ''.join(return_lines)
            
            # Extract indentation
            indent_match = return_lines[0][:len(return_lines[0]) - len(return_lines[0].lstrip())]
            
            # Replace return { with return JSONResponse(status_code=200, content={
            new_block = block_text.replace('return {', f'return JSONResponse(\n{indent_match}    status_code=200,\n{indent_match}    content={{', 1)
            
            # Replace final } with }})
            new_block = new_block.rstrip()
            if new_block.endswith('}'):
                new_block = new_block[:-1] + '})'
            
            # Replace the lines in the original list
            for j in range(len(return_lines)):
                if j == 0:
                    lines[i - len(return_lines)] = new_block + '\n'
                else:
                    del lines[i - len(return_lines) + 1]
            
            modified_count += 1
            i -= len(return_lines)  # Back up to process next line
            continue
    
    i += 1

# Write back
with open('llm_chatbot.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print(f'✅ Modified {modified_count} return statements')
