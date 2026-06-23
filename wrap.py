import re

with open('templates/payslip_designer.html', 'r', encoding='utf-8') as f:
    c = f.read()

def rep(m):
    return m.group(1) + '<span class="movable-label" style="display:inline-block; cursor:move;">' + m.group(2) + '</span>' + m.group(3)

labels = [
    'Employee ID:', 'Salary for Month', 'Employee Name:', 'Total Month Days',
    'Department/Designatio', 'Total Days Paid', 'Date of Joining', 'CL Balance',
    'UAN No.', 'EL Balance', 'Earnings', 'Deductions', 'Total Earnings',
    'Total Deduction', 'Net Pay'
]

pattern = r'(>)(' + '|'.join(re.escape(l) for l in labels) + r')(</div>)'
c = re.sub(pattern, rep, c)

with open('templates/payslip_designer.html', 'w', encoding='utf-8') as f:
    f.write(c)
