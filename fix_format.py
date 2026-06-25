import re

html_path = 'templates/financial_master.html'
with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace {{ "{:,.2f}".format(emp.month_gross) }} with {{ emp.month_gross | inr_format }}
pattern = r'\{\{\s*"{:,\.2f}"\.format\((.*?)\)\s*\}\}'
new_content = re.sub(pattern, r'{{ \1 | inr_format }}', content)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Formatting applied.")
