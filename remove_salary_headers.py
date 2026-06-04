import re
file_path = r'c:\maxworth internship\templates\index.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Use regex to remove headers from "Basic (₹)" to "Net Pay (₹)"
pattern = re.compile(r'<th[^>]*>Basic \(₹\)</th>\s*<th[^>]*>Meal Allowance \(₹\)</th>\s*<th[^>]*>Transport Allowance \(₹\)</th>\s*<th[^>]*>Medical Allowance \(₹\)</th>\s*<th[^>]*>Allowances Total \(₹\)</th>\s*<th[^>]*>Retirement Ins\. \(₹\)</th>\s*<th[^>]*>Professional Tax \(₹\)</th>\s*<th[^>]*>Deductions Total \(₹\)</th>\s*<th[^>]*>Net Pay \(₹\)</th>', re.DOTALL)

if pattern.search(content):
    content = pattern.sub('', content)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Headers removed using regex.")
else:
    print("Headers STILL not found. Let's do it individually.")
    
    headers = [
        r'<th[^>]*>Basic \(₹\)</th>\s*',
        r'<th[^>]*>Meal Allowance \(₹\)</th>\s*',
        r'<th[^>]*>Transport Allowance \(₹\)</th>\s*',
        r'<th[^>]*>Medical Allowance \(₹\)</th>\s*',
        r'<th[^>]*>Allowances Total \(₹\)</th>\s*',
        r'<th[^>]*>Retirement Ins\. \(₹\)</th>\s*',
        r'<th[^>]*>Professional Tax \(₹\)</th>\s*',
        r'<th[^>]*>Deductions Total \(₹\)</th>\s*',
        r'<th[^>]*>Net Pay \(₹\)</th>\s*'
    ]
    for h in headers:
        content = re.sub(h, '', content, flags=re.DOTALL)
        
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Headers removed individually.")
