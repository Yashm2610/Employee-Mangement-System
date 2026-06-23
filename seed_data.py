import app
import datetime
import random

conn = app.get_db_connection()
cursor = conn.cursor()

# Get all employee IDs
cursor.execute('SELECT emp_id, email, emp_name FROM employees')
employees = cursor.fetchall()
if not employees:
    print("No employees found to seed data for.")
else:
    # 1. Seed employee_emails
    cursor.execute('SELECT COUNT(*) as count FROM employee_emails')
    if cursor.fetchone()['count'] == 0:
        for emp in employees:
            if emp['email']:
                cursor.execute('''
                    INSERT INTO employee_emails (emp_id, sender_email, receiver_email, subject, body, status, created_by)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                ''', (emp['emp_id'], 'hr@maxworth.com', emp['email'], 'Welcome to Maxworth', f'Hello {emp["emp_name"]}, welcome to the company!', 'Sent', 'System'))
        print("Seeded employee_emails.")

    # 2. Seed employee_holidays
    cursor.execute('SELECT COUNT(*) as count FROM employee_holidays')
    if cursor.fetchone()['count'] == 0:
        for emp in employees:
            cursor.execute('''
                INSERT INTO employee_holidays (emp_id, holiday_date, description, holiday_type, status, created_by)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (emp['emp_id'], '2026-08-15', 'Independence Day', 'Public Holiday', 'Approved', 'System'))
        print("Seeded employee_holidays.")

    # 3. Seed financial_component_master
    cursor.execute('SELECT COUNT(*) as count FROM financial_component_master')
    if cursor.fetchone()['count'] == 0:
        components = [
            ('Basic Salary', 'Earning', 1, 'System'),
            ('HRA', 'Earning', 1, 'System'),
            ('Transport Allowance', 'Earning', 1, 'System'),
            ('Income Tax', 'Deduction', 1, 'System'),
            ('PF', 'Deduction', 1, 'System')
        ]
        for c in components:
            cursor.execute('INSERT INTO financial_component_master (component_name, type, is_active, CreatedBy) VALUES (%s, %s, %s, %s)', c)
        print("Seeded financial_component_master.")

    # 4. Seed employee_financial_components
    cursor.execute('SELECT COUNT(*) as count FROM employee_financial_components')
    if cursor.fetchone()['count'] == 0:
        cursor.execute('SELECT id, component_name, type FROM financial_component_master')
        comps = cursor.fetchall()
        for emp in employees:
            for c in comps:
                amount = random.randint(1000, 20000) if c['type'] == 'Earning' else random.randint(500, 2000)
                cursor.execute('''
                    INSERT INTO employee_financial_components (emp_id, component_id, amount, effective_date, CreatedBy)
                    VALUES (%s, %s, %s, %s, %s)
                ''', (emp['emp_id'], c['id'], amount, '2026-01-01', 'System'))
        print("Seeded employee_financial_components.")

conn.commit()
conn.close()
print("Data seeding complete.")
