import os

filepath = r'c:\maxworth internship\templates\employee_profile.html'
with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find where the mangled part starts:
# We know line 115 is '        </div>\n'
# Line 116 is '                        <h5 class="modal-title" id="emailLogModalLabel">Email Interaction Log</h5>\n'

start_idx = -1
for i, line in enumerate(lines):
    if 'id="emailLogModalLabel"' in line:
        start_idx = i
        break

if start_idx != -1:
    missing_block = """        {% endif %}
        
        <!-- Payslip History -->
        <div class="mt-5">
            <h4 class="mb-3">Payslip History</h4>
            {% if payroll_transactions %}
            <div class="table-responsive">
                <table class="table table-hover table-sm">
                    <thead class="thead-dark">
                        <tr>
                            <th>#</th>
                            <th>Date</th>
                            <th>Month</th>
                            <th>Net Salary</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for txn in payroll_transactions %}
                        <tr>
                            <td>{{ loop.index }}</td>
                            <td>{{ txn.generated_on.strftime('%Y-%m-%d') if txn.generated_on else '' }}</td>
                            <td>{{ txn.salary_month }}</td>
                            <td>{{ "₹{:,.2f}".format(txn.final_in_hand_salary) }}</td>
                            <td><a href="{{ url_for('view_payslip', id=employee.id) }}?month={{ txn.salary_month|lower }}" class="btn btn-sm btn-outline-primary">View Slip</a></td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            {% else %}
            <p class="text-muted">No payslip transactions recorded for this employee.</p>
            {% endif %}
        </div>
        
        <!-- Email Log Modal Trigger -->
        <div class="mt-4 text-end">
            <button class="btn btn-outline-info" data-bs-toggle="modal" data-bs-target="#emailLogModal">
                <i class="bi bi-envelope me-1"></i> Email Log
            </button>
        </div>
        
        <!-- Email Log Modal -->
        <div class="modal fade" id="emailLogModal" tabindex="-1" aria-labelledby="emailLogModalLabel" aria-hidden="true">
            <div class="modal-dialog modal-lg modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header bg-primary text-white">
"""
    # We remove the line `{% endif %}` if it was before the error
    if '{% endif %}' in lines[start_idx-1]:
        lines.pop(start_idx-1)
        start_idx -= 1
        
    lines.insert(start_idx, missing_block)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print('Successfully restored the missing Payslip History table!')
else:
    print('Could not find the insertion point!')
