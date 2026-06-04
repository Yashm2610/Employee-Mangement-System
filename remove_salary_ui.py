import re
file_path = r'c:\maxworth internship\templates\index.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern to remove the salary details section
# Starts with <!-- Section: Salary Breakdown -->
# Ends right before <button type="submit" ...>
pattern = re.compile(r'<!-- Section: Salary Breakdown -->.*?</div>\s*</div>\s*</div>\s*(<button type="submit")', re.DOTALL)

if pattern.search(content):
    content = pattern.sub(r'</div>\n                        </div>\n                    \1', content)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Salary details section removed from index.html successfully.")
else:
    print("Could not find the salary details section to remove.")
