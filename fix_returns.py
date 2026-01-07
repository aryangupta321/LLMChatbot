#!/usr/bin/env python3
import re

# Read file
with open('llm_chatbot.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Process lines
new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    
    # Check if this line starts a return dict
    if line.strip().startswith('return {'):
        # Found a return statement, collect until we find the closing brace
        return_block = [line]
        i += 1
        brace_count = 1
        
        while i < len(lines) and brace_count > 0:
            current_line = lines[i]
            return_block.append(current_line)
            brace_count += current_line.count('{') - current_line.count('}')
            i += 1
        
        # Now convert this block to JSONResponse
        # Join the block
        block_text = ''.join(return_block)
        
        # Extract indentation from first line
        indent_match = re.match(r'^(\s*)', line)
        indent = indent_match.group(1) if indent_match else '        '
        
        # Convert the block
        # Replace "return {" with "return JSONResponse(status_code=200, content={"
        new_block = block_text.replace('return {', f'return JSONResponse(\n{indent}    status_code=200,\n{indent}    content={{', 1)
        
        # Add closing ) for JSONResponse before the final }
        # The block ends with "            }" so we need to add ) after it
        new_block = new_block.rstrip()
        if new_block.endswith('}'):
            new_block = new_block[:-1] + '})'
        
        new_lines.append(new_block + '\n')
    else:
        new_lines.append(line)
        i += 1

# Write back
with open('llm_chatbot.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print('✅ Fixed all return statements to use JSONResponse')
