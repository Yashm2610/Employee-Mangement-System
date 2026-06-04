import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# The old upload_file was added by fix_upload.py
# It starts with 'def upload_file():' and ends just before '@app.route('/dashboard')' or similar.
# Wait, old one doesn't have @app.route('/upload') above it? Ah! I missed that in fix_upload.py!
# In fix_upload.py: content = re.sub(r"def upload_file\(\):.*?return redirect\(url_for\('index'\)\)\n", new_upload_func, content, flags=re.DOTALL)
# So it replaced the old one.

# Let's just find the first def upload_file() and remove it, along with its decorator if any.
match = re.search(r"(@app\.route\('/upload', methods=\['POST'\]\)\s+)?def upload_file\(\):.*?return redirect\(url_for\('index'\)\)\n", content, flags=re.DOTALL)
if match:
    content = content[:match.start()] + content[match.end():]
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Removed duplicate upload_file")
else:
    print("Could not find the old upload_file")
