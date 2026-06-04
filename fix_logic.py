file_path = r'c:\maxworth internship\templates\index.html'
with open(file_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Fix Joining Date
html = html.replace('{{ emp.date }}', '{{ emp.joining_date }}')

# Fix Salary Slab logic to use payment_tier instead of basic_salary
old_slab = '''                                                    {% if emp.basic_salary >= 80000 %}
                                                        <span class="badge bg-success-subtle text-success border border-success px-2 py-1.5 fs-7">Executive (Tier 1)</span>
                                                    {% elif emp.basic_salary >= 50000 %}
                                                        <span class="badge bg-info-subtle text-info border border-info px-2 py-1.5 fs-7">Professional (Tier 2)</span>
                                                    {% else %}
                                                        <span class="badge bg-warning-subtle text-warning border border-warning px-2 py-1.5 fs-7">Associate (Tier 3)</span>
                                                    {% endif %}'''

new_slab = '''                                                    {% if emp.payment_tier == 1 %}
                                                        <span class="badge bg-success-subtle text-success border border-success px-2 py-1.5 fs-7">Executive (Tier 1)</span>
                                                    {% elif emp.payment_tier == 2 %}
                                                        <span class="badge bg-info-subtle text-info border border-info px-2 py-1.5 fs-7">Professional (Tier 2)</span>
                                                    {% else %}
                                                        <span class="badge bg-warning-subtle text-warning border border-warning px-2 py-1.5 fs-7">Associate (Tier 3)</span>
                                                    {% endif %}'''
html = html.replace(old_slab, new_slab)

# Fix Leave or Not logic
old_leave = '''                                                    {% if emp.leave_or_not == 0 %}
                                                        <span class="badge bg-success-subtle text-success border border-success px-2 py-0.5 fs-8">Active (0)</span>
                                                    {% elif emp.leave_or_not == 1 %}
                                                        <span class="badge bg-warning-subtle text-warning border border-warning px-2 py-0.5 fs-8">On Leave (1)</span>
                                                    {% elif emp.leave_or_not == 2 %}
                                                        <span class="badge bg-danger-subtle text-danger border border-danger px-2 py-0.5 fs-8">Medical (2)</span>
                                                    {% elif emp.leave_or_not == 3 %}
                                                        <span class="badge bg-info-subtle text-info border border-info px-2 py-0.5 fs-8">Parental (3)</span>
                                                    {% elif emp.leave_or_not == 4 %}
                                                        <span class="badge bg-secondary-subtle text-secondary border border-secondary px-2 py-0.5 fs-8">Unpaid (4)</span>
                                                    {% else %}
                                                        <span class="badge bg-dark-subtle text-dark border border-dark px-2 py-0.5 fs-8">Resigned ({{ emp.leave_or_not }})</span>
                                                    {% endif %}'''

new_leave = '''                                                    {% set status_code = emp.leave_or_not if emp.leave_or_not is not none else 0 %}
                                                    {% if status_code == 0 %}
                                                        <span class="badge bg-success-subtle text-success border border-success px-2 py-0.5 fs-8">Active (0)</span>
                                                    {% elif status_code == 1 %}
                                                        <span class="badge bg-warning-subtle text-warning border border-warning px-2 py-0.5 fs-8">On Leave (1)</span>
                                                    {% elif status_code == 2 %}
                                                        <span class="badge bg-danger-subtle text-danger border border-danger px-2 py-0.5 fs-8">Medical (2)</span>
                                                    {% elif status_code == 3 %}
                                                        <span class="badge bg-info-subtle text-info border border-info px-2 py-0.5 fs-8">Parental (3)</span>
                                                    {% elif status_code == 4 %}
                                                        <span class="badge bg-secondary-subtle text-secondary border border-secondary px-2 py-0.5 fs-8">Unpaid (4)</span>
                                                    {% else %}
                                                        <span class="badge bg-dark-subtle text-dark border border-dark px-2 py-0.5 fs-8">Resigned ({{ status_code }})</span>
                                                    {% endif %}'''
html = html.replace(old_leave, new_leave)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(html)
print("index.html updated successfully.")
