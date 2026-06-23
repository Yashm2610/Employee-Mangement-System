import app
import random
import datetime

conn = app.get_db_connection()
cursor = conn.cursor()

# 1. Fill employees UAN
cursor.execute("SELECT emp_id FROM employees WHERE uan_number IS NULL")
emps = cursor.fetchall()
for emp in emps:
    uan = "".join([str(random.randint(0, 9)) for _ in range(12)])
    cursor.execute("UPDATE employees SET uan_number = %s WHERE emp_id = %s", (uan, emp['emp_id']))

# 2. Fill holiday_master
cursor.execute("SELECT COUNT(*) as c FROM holiday_master")
if cursor.fetchone()['c'] == 0:
    holidays = [(1, 'New Year'), (2, 'Republic Day'), (3, 'Holi'), (4, 'Independence Day'), (5, 'Diwali'), (6, 'Christmas')]
    for h in holidays:
        cursor.execute("INSERT INTO holiday_master (holiday_code, holiday_name) VALUES (%s, %s)", h)

# 3. Fill employee_holidays
cursor.execute("SELECT COUNT(*) as c FROM employee_holidays")
if cursor.fetchone()['c'] == 0:
    cursor.execute("SELECT emp_id FROM employees")
    all_emps = cursor.fetchall()
    for emp in all_emps:
        # Give each employee 2 random holidays
        codes = random.sample([1, 2, 3, 4, 5, 6], 2)
        for code in codes:
            # get holiday name
            cursor.execute("SELECT holiday_name FROM holiday_master WHERE holiday_code = %s", (code,))
            name = cursor.fetchone()['holiday_name']
            cursor.execute("INSERT INTO employee_holidays (emp_id, holiday_code, holiday_name) VALUES (%s, %s, %s)", (emp['emp_id'], code, name))

# 4. Fill employee_emails
cursor.execute("SELECT COUNT(*) as c FROM employee_emails")
if cursor.fetchone()['c'] == 0:
    cursor.execute("SELECT emp_id, email, emp_name FROM employees")
    all_emps = cursor.fetchall()
    for emp in all_emps:
        if emp['email']:
            cursor.execute("""
                INSERT INTO employee_emails (emp_id, sender_email, receiver_email, subject, body, status, official_email) 
                VALUES (%s, 'hr@maxworth.com', %s, 'Welcome!', %s, 'Sent', %s)
            """, (emp['emp_id'], emp['email'], f"Welcome to Maxworth, {emp['emp_name']}!", emp['email']))

# 5. Fill financial_component_master
cursor.execute("SELECT COUNT(*) as c FROM financial_component_master")
if cursor.fetchone()['c'] == 0:
    comps = [(1, 'Basic Salary', 'Earning'), (2, 'HRA', 'Earning'), (3, 'Special Allowance', 'Earning'), (4, 'Income Tax', 'Deduction'), (5, 'PF', 'Deduction')]
    for c in comps:
        cursor.execute("INSERT INTO financial_component_master (component_code, component_name, type) VALUES (%s, %s, %s)", c)

# 6. Fill employee_financial_components
cursor.execute("SELECT COUNT(*) as c FROM employee_financial_components")
if cursor.fetchone()['c'] == 0:
    cursor.execute("SELECT emp_id, basic_salary FROM employees")
    all_emps = cursor.fetchall()
    cursor.execute("SELECT component_code, component_name, type FROM financial_component_master")
    comps = cursor.fetchall()
    for emp in all_emps:
        for c in comps:
            amt = 0
            if c['component_code'] == 1:
                amt = float(emp['basic_salary'] or 0)
            elif c['component_code'] == 2:
                amt = float(emp['basic_salary'] or 0) * 0.4
            elif c['component_code'] == 3:
                amt = random.randint(1000, 5000)
            elif c['component_code'] == 4:
                amt = float(emp['basic_salary'] or 0) * 0.1
            elif c['component_code'] == 5:
                amt = float(emp['basic_salary'] or 0) * 0.12
            cursor.execute("INSERT INTO employee_financial_components (emp_id, component_name, component_code, amount) VALUES (%s, %s, %s, %s)", (emp['emp_id'], c['component_name'], c['component_code'], amt))

# 7. Fill location_master, department_master, designation_master mapping
# Some employees might have null location_code etc.
cursor.execute("UPDATE employees SET location_code=1 WHERE location_code IS NULL")
cursor.execute("UPDATE employees SET department_code=1 WHERE department_code IS NULL")
cursor.execute("UPDATE employees SET designation_code=1 WHERE designation_code IS NULL")

conn.commit()
conn.close()
print("Successfully filled empty tables!")
