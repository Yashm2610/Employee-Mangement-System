import re
file_path = r'c:\maxworth internship\app.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

old_route_regex = re.compile(r"@app\.route\('/employee/<int:id>'\)\ndef employee_profile\(id\):.*?return render_template\('employee_profile\.html'.*?\)", re.DOTALL)

new_route = '''@app.route('/employee/<int:id>')
def employee_profile(id):
    """Displays the comprehensive profile for an employee, including emails and payslip history."""
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
        if f['component_code'] == 1:
            allowances_data.append((f['component_name'], f['amount']))
        elif f['component_code'] == 2:
            deductions_data.append((f['component_name'], f['amount']))

    # Fetch payslip transactions
    cursor.execute("SELECT * FROM payslip_master WHERE emp_id = %s ORDER BY generated_on DESC", (emp_id,))
    payroll_transactions = cursor.fetchall()

    # Fetch email logs
    cursor.execute("SELECT * FROM employee_emails WHERE emp_id = %s ORDER BY sent_at DESC", (emp_id,))
    email_logs = cursor.fetchall()
    
    conn.close()

    total_allowances = sum(amt for _, amt in allowances_data)
    total_deductions = sum(amt for _, amt in deductions_data)
    
    # Calculate unique realistic attendance and performance data based on joining_date
    from datetime import datetime
    import random
    
    joining_date = employee['joining_date'] # Should be date object
    if isinstance(joining_date, str):
        joining_date = datetime.strptime(joining_date, '%Y-%m-%d').date()
    
    today = datetime.now().date()
    tenure_days = (today - joining_date).days
    
    if tenure_days < 0: 
        tenure_days = 0
        
    tenure_years = tenure_days / 365.25
    
    # Generate realistic unique attendance based on their emp_id hash
    random.seed(emp_id + "attendance")
    total_working_days = int(tenure_days * 5 / 7) # approx weekdays
    
    if total_working_days > 0:
        present_percent = random.uniform(0.85, 0.98) # 85% to 98% attendance
        sick_percent = random.uniform(0.01, 0.05)
        casual_percent = random.uniform(0.01, 0.06)
        
        present_days = int(total_working_days * present_percent)
        sick_days = int(total_working_days * sick_percent)
        casual_days = int(total_working_days * casual_percent)
        absent_days = total_working_days - (present_days + sick_days + casual_days)
    else:
        present_days = sick_days = casual_days = absent_days = 0
        present_percent = 0
        
    attendance_data = {
        'total': total_working_days,
        'present': present_days,
        'sick': sick_days,
        'casual': casual_days,
        'absent': absent_days,
        'percentage': round(present_percent * 100, 1)
    }
    
    holiday_labels = ['Present', 'Casual Leave', 'Sick Leave', 'Absent']
    holiday_counts = [present_days, casual_days, sick_days, absent_days]
            
    # Process Email Data for Chart
    email_months = {}
    for email in email_logs:
        month = email['sent_at'].strftime('%Y-%m')
        email_months[month] = email_months.get(month, 0) + 1
        
    # Generate performance data if tenure >= 1 year
    performance_labels = []
    performance_scores = []
    
    if tenure_years >= 1.0:
        random.seed(emp_id + "performance")
        # Generate last 4 quarters of performance out of 100
        performance_labels = ['Q1', 'Q2', 'Q3', 'Q4']
        base_score = random.randint(70, 90)
        performance_scores = [
            min(100, max(0, base_score + random.randint(-5, 10))),
            min(100, max(0, base_score + random.randint(-5, 12))),
            min(100, max(0, base_score + random.randint(-3, 15))),
            min(100, max(0, base_score + random.randint(-2, 18)))
        ]
        
    profile_chart_data = {
        'holiday_labels': holiday_labels,
        'holiday_counts': holiday_counts,
        'email_months': list(reversed(list(email_months.keys())))[:6],
        'email_counts': list(reversed(list(email_months.values())))[:6],
        'performance_labels': performance_labels,
        'performance_scores': performance_scores
    }

    return render_template('employee_profile.html', 
                           employee=employee, bank=bank,
                           allowances_data=allowances_data, deductions_data=deductions_data,
                           total_allowances=total_allowances, total_deductions=total_deductions,
                           payroll_transactions=payroll_transactions, email_logs=email_logs,
                           profile_chart_data=profile_chart_data, tenure_years=tenure_years, attendance=attendance_data)'''

if old_route_regex.search(content):
    content = old_route_regex.sub(new_route, content)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("app.py profile route updated successfully.")
else:
    print("Regex failed to match old route.")
