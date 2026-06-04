file_path = r'c:\maxworth internship\templates\index.html'

with open(file_path, 'r', encoding='utf-8') as f:
    html = f.read()

old_leave = '''                                                    {% set status_code = emp.get('leave_or_not', 0) %}
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

new_leave = '''                                                    {% set status_code = emp.get('leave_or_not', 0) %}
                                                    {% if status_code == 0 %}
                                                        <span class="badge bg-success-subtle text-success border border-success px-2 py-0.5 fs-8">Active</span>
                                                    {% elif status_code == 1 %}
                                                        <span class="badge bg-warning-subtle text-warning border border-warning px-2 py-0.5 fs-8">On Leave</span>
                                                    {% elif status_code == 2 %}
                                                        <span class="badge bg-danger-subtle text-danger border border-danger px-2 py-0.5 fs-8">Medical</span>
                                                    {% elif status_code == 3 %}
                                                        <span class="badge bg-info-subtle text-info border border-info px-2 py-0.5 fs-8">Parental</span>
                                                    {% elif status_code == 4 %}
                                                        <span class="badge bg-secondary-subtle text-secondary border border-secondary px-2 py-0.5 fs-8">Unpaid</span>
                                                    {% elif status_code == 5 %}
                                                        <span class="badge bg-dark-subtle text-dark border border-dark px-2 py-0.5 fs-8">Resigned</span>
                                                    {% else %}
                                                        <span class="badge bg-dark-subtle text-dark border border-dark px-2 py-0.5 fs-8">Retired</span>
                                                    {% endif %}'''

html = html.replace(old_leave, new_leave)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(html)
print("UI Updated Successfully.")
