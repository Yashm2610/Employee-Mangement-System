import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

employee_new = """@app.route('/employee/<int:id>')
def employee_profile(id):
    \"\"\"Displays the comprehensive profile for an employee, including emails and payslip history.\"\"\"
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM employees WHERE id = %s", (id,))
    employee = cursor.fetchone()
    if not employee:
        conn.close()
        flash("Employee not found.", "danger")
        return redirect(url_for('index'))

    emp_id = employee['emp_id']

    # Fetch bank details
    cursor.execute("SELECT * FROM employee_bank_details WHERE emp_id = %s", (emp_id,))
    bank = cursor.fetchone() or {}

    # Fetch financial components (allowances and deductions)
    cursor.execute("SELECT * FROM employee_financial_components WHERE emp_id = %s", (emp_id,))
    financials = cursor.fetchall()
    
    allowances_data = []
    deductions_data = []
    for f in financials:
        if f['code'] == 1:
            allowances_data.append((f['component_name'], f['amount']))
        elif f['code'] == 2:
            deductions_data.append((f['component_name'], f['amount']))

    # Fetch payslip transactions (payslip_master)
    cursor.execute("SELECT * FROM payslip_master WHERE emp_id = %s ORDER BY generated_at DESC", (emp_id,))
    payroll_transactions = cursor.fetchall()

    # Fetch email logs
    cursor.execute("SELECT * FROM employee_emails WHERE emp_id = %s ORDER BY sent_at DESC", (emp_id,))
    email_logs = cursor.fetchall()

    conn.close()

    total_allowances = sum(amt for _, amt in allowances_data)
    total_deductions = sum(amt for _, amt in deductions_data)

    return render_template('employee_profile.html', 
                           employee=employee, 
                           bank=bank, 
                           allowances_data=allowances_data, 
                           deductions_data=deductions_data,
                           total_allowances=total_allowances,
                           total_deductions=total_deductions,
                           payroll_transactions=payroll_transactions,
                           email_logs=email_logs)
"""

content = re.sub(r"@app\.route\('/employee/<int:id>'\).*?def send_email\(id\):", employee_new + "\n@app.route('/send_email/<int:id>', methods=['POST'])\ndef send_email(id):", content, flags=re.DOTALL)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated employee_profile!")
