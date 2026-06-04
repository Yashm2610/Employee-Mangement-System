import re

file_path = r'c:\maxworth internship\templates\financial_master.html'
with open(file_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Replace table headers
old_thead = '''                <thead class="table-light text-secondary text-uppercase fs-8 tracking-wider">
                    <tr>
                        <th class="ps-4">Emp ID</th>
                        <th>Name</th>
                        <th>Bank Details</th>
                        <th>Basic Salary</th>
                        <th>Allowances (Count)</th>
                        <th>Deductions (Count)</th>
                        <th class="text-end pe-4">Actions</th>
                    </tr>
                </thead>'''

new_thead = '''                <thead class="table-light text-secondary text-uppercase fs-8 tracking-wider">
                    <tr>
                        <th class="ps-4">Emp ID</th>
                        <th>Name</th>
                        <th>Bank Details</th>
                        <th>Basic (₹)</th>
                        <th>Allowances (₹)</th>
                        <th>Deductions (₹)</th>
                        <th>Net Salary (₹)</th>
                        <th class="text-end pe-4">Actions</th>
                    </tr>
                </thead>'''

html = html.replace(old_thead, new_thead)

# Replace table body logic
old_tbody_full_regex = re.compile(r'                        <td class="fw-medium text-success">\s*₹\{\{ "\{:,\.2f\}".format\(emp\.basic_salary\|float\) \}\}\s*</td>.*?</td>\s*<td class="text-end pe-4">', re.DOTALL)

new_tbody_logic = '''                        <td class="fw-medium text-dark">
                            ₹{{ "{:,.2f}".format(emp.basic_salary|float) }}
                        </td>
                        {% set totals = namespace(allowance=0.0, deduction=0.0) %}
                        {% if emp.emp_id in emp_components %}
                            {% for comp in emp_components[emp.emp_id] %}
                                {% if comp.component_code == 1 %}
                                    {% set totals.allowance = totals.allowance + comp.amount|float %}
                                {% elif comp.component_code == 2 %}
                                    {% set totals.deduction = totals.deduction + comp.amount|float %}
                                {% endif %}
                            {% endfor %}
                        {% endif %}
                        <td class="text-success fw-medium">
                            + ₹{{ "{:,.2f}".format(totals.allowance) }}
                        </td>
                        <td class="text-danger fw-medium">
                            - ₹{{ "{:,.2f}".format(totals.deduction) }}
                        </td>
                        <td class="fw-bold text-primary">
                            ₹{{ "{:,.2f}".format((emp.basic_salary|float) + totals.allowance - totals.deduction) }}
                        </td>
                        <td class="text-end pe-4">'''

html = old_tbody_full_regex.sub(new_tbody_logic, html)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(html)
print("Table updated successfully.")
