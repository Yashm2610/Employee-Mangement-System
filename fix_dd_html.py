import re

with open('templates/data_dictionary.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the table header
new_thead = """<thead class="table-dark sticky-top">
                            <tr>
                                <th scope="col" class="col-id">id</th>
                                <th scope="col" class="col-emp_id">emp_id</th>
                                <th scope="col" class="col-emp_name">emp_name</th>
                                <th scope="col" class="col-email">email</th>
                                <th scope="col" class="col-date_of_birth">date_of_birth</th>
                                <th scope="col" class="col-joining_date">joining_date</th>
                                <th scope="col" class="col-basic_salary text-end">basic_salary</th>
                                <th scope="col" class="col-allowances text-end">allowances</th>
                                <th scope="col" class="col-deductions text-end">deductions</th>
                                <th scope="col" class="col-age text-center">age</th>
                                <th scope="col" class="col-gender">gender</th>
                                <th scope="col" class="col-education">education</th>
                                <th scope="col" class="col-title">title</th>
                                <th scope="col" class="col-department">department</th>
                                <th scope="col" class="col-posting_location">posting_location</th>
                                <th scope="col" class="col-payment_tier text-center">payment_tier</th>
                                <th scope="col" class="col-bank_name">bank_name</th>
                                <th scope="col" class="col-bank_account_num">bank_account_num</th>
                                <th scope="col" class="col-ifsc_code">ifsc_code</th>
                            </tr>
                        </thead>"""

content = re.sub(r'<thead class="table-dark sticky-top">.*?</thead>', new_thead, content, flags=re.DOTALL)

# Replace the table row loop
new_tbody_row = """<tr>
                                        <td class="col-id fw-semibold text-secondary">{{ row.id }}</td>
                                        <td class="col-emp_id font-monospace">{{ row.emp_id }}</td>
                                        <td class="col-emp_name fw-bold text-dark">{{ row.emp_name }}</td>
                                        <td class="col-email">{{ row.email }}</td>
                                        <td class="col-date_of_birth font-monospace">{{ row.date_of_birth }}</td>
                                        <td class="col-joining_date font-monospace">{{ row.joining_date }}</td>
                                        <td class="col-basic_salary text-end font-monospace">₹{{ "{:,.2f}".format(row.basic_salary) }}</td>
                                        <td class="col-allowances text-end font-monospace">₹{{ "{:,.2f}".format(row.allowances) }}</td>
                                        <td class="col-deductions text-end font-monospace">₹{{ "{:,.2f}".format(row.deductions) }}</td>
                                        <td class="col-age text-center font-monospace">{{ row.age }}</td>
                                        <td class="col-gender">{{ row.gender }}</td>
                                        <td class="col-education"><span class="badge bg-light text-dark border">{{ row.education }}</span></td>
                                        <td class="col-title"><span class="badge bg-light text-dark border">{{ row.title }}</span></td>
                                        <td class="col-department">{{ row.department }}</td>
                                        <td class="col-posting_location">{{ row.posting_location }}</td>
                                        <td class="col-payment_tier text-center font-monospace">{{ row.payment_tier }}</td>
                                        <td class="col-bank_name">{{ row.bank_name }}</td>
                                        <td class="col-bank_account_num font-monospace">{{ row.bank_account_num }}</td>
                                        <td class="col-ifsc_code">{{ row.ifsc_code }}</td>
                                    </tr>"""

content = re.sub(r'<tr>\s*<td class="col-id fw-semibold text-secondary">.*?</tr>', new_tbody_row, content, flags=re.DOTALL)

# Also fix the metadata colors for new tables
new_metadata_logic = """{% set tbl = field.get('table', 'employees') %}
                                {% if tbl == 'employees' %}
                                    {% set row_bg = '' %}
                                    {% set badge_class = 'bg-primary' %}
                                {% elif tbl == 'employee_bank_details' %}
                                    {% set row_bg = 'style="background-color: rgba(16,185,129,0.06);"' %}
                                    {% set badge_class = 'bg-success' %}
                                {% elif tbl == 'employee_financial_components' %}
                                    {% set row_bg = 'style="background-color: rgba(245,158,11,0.06);"' %}
                                    {% set badge_class = 'bg-warning text-dark' %}
                                {% elif tbl == 'payslip_master' %}
                                    {% set row_bg = 'style="background-color: rgba(99,102,241,0.06);"' %}
                                    {% set badge_class = 'bg-indigo text-white' %}
                                {% elif tbl == 'employee_holidays' %}
                                    {% set row_bg = 'style="background-color: rgba(239,68,68,0.06);"' %}
                                    {% set badge_class = 'bg-danger' %}
                                {% else %}
                                    {% set row_bg = '' %}
                                    {% set badge_class = 'bg-secondary' %}
                                {% endif %}"""

content = re.sub(r"{% set tbl = field\.get\('table', 'employees'\) %}.*?{% endif %}", new_metadata_logic, content, flags=re.DOTALL)

with open('templates/data_dictionary.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("Fixed data_dictionary.html!")
