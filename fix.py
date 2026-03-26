import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace both single and double quote variations of url_for
content = re.sub(
    r'\{\{\s*url_for\([\s\'"]+static[\s\'"]+,\s*filename=[\s\'"]+([^^\'"]+)[\s\'"]+\)\s*\}\}', 
    r'static/\1', 
    content
)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
