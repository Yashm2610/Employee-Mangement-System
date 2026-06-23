import io
import re

content = io.open('old_financial_master.html', encoding='utf-16').read()
modal_start = content.find('<!-- Edit Financials Modal -->')
modal_code = content[modal_start:]

th_match = re.search(r'<th[^>]*>ACTIONS</th>', content, re.IGNORECASE)
td_match = re.search(r'<td[^>]*>\s*<div class="d-flex[^>]*>.*?</div>\s*</td>', content, re.IGNORECASE | re.DOTALL)

with io.open('extracted_actions.txt', 'w', encoding='utf-8') as f:
    f.write('--- MODAL ---\n')
    f.write(modal_code)
    f.write('\n--- TH ---\n')
    if th_match: f.write(th_match.group(0))
    f.write('\n--- TD ---\n')
    if td_match: f.write(td_match.group(0))
