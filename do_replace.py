import io
import re

# Read current financial_master.html
with io.open('templates/financial_master.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Read new_table.html
with io.open('new_table.html', 'r', encoding='utf-8') as f:
    new_table = f.read()

# Read extracted modal
with io.open('extracted_actions.txt', 'r', encoding='utf-8') as f:
    extracted = f.read()
    
modal_code = extracted.split('--- MODAL ---\n')[1].split('\n--- TH ---')[0]

# Replace the table-responsive div
# We find the <div class="table-responsive"> and the matching closing </div>
# Since regex for nested divs is hard, we can just replace everything between <div class="table-responsive"> and </div>\n        </div>\n    </div>
pattern = re.compile(r'<div class="table-responsive">.*?</table>\s*</div>', re.DOTALL)
new_content = pattern.sub(new_table, content)

# Append modal code right before {% endblock %}
if '<!-- Edit Financials Modal -->' not in new_content:
    new_content = new_content.replace('{% endblock %}', modal_code + '\n\n{% endblock %}')

with io.open('templates/financial_master.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

