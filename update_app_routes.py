import re

add_new = """@app.route('/add', methods=['POST'])
def add_employee():
    \"\"\"Handles manual adding of employees from the front-end form.\"\"\"
    emp_id = request.form.get('emp_id', '').strip()
    emp_name = request.form.get('emp_name', '').strip()
    email = request.form.get('email', '').strip()
    date_of_birth = request.form.get('date_of_birth', '').strip()
    joining_date = request.form.get('joining_date', '').strip()

    basic_val = float(request.form.get('basic_salary', '0') or 0)
    age_val = request.form.get('age', '').strip()
    age_val = int(age_val) if age_val else 30
    gender_val = request.form.get('gender', 'Male').strip()
    education_val = int(request.form.get('education', '2') or 2)

    title_val = request.form.get('title', 'Software Engineer').strip()
    department_val = request.form.get('department', 'IT Department').strip()
    bank_name_val = request.form.get('bank_name', 'Bank of America').strip()
    bank_account_num_val = request.form.get('bank_account_num', '0000000000').strip()
    ifsc_code_val = request.form.get('ifsc_code', 'BOFA0000001').strip()

    posting_location_val = request.form.get('posting_location', 'Bangalore').strip()
    payment_tier_val = int(request.form.get('payment_tier', '3') or 3)
    holiday_val = int(request.form.get('holiday', '0') or 0)

    # Unified Financial Components (Allowances & Deductions)
    comp_names = request.form.getlist('component_name[]')
    comp_amounts = request.form.getlist('component_amount[]')
    comp_codes = request.form.getlist('component_code[]')
    
    allowances_val = 0
    deductions_val = 0
    comps_to_insert = []
    
    for name, amt, code in zip(comp_names, comp_amounts, comp_codes):
        name = name.strip()
        try:
            amt = float(amt)
            code = int(code)
        except ValueError:
            amt = 0.0
            code = 1
        if name and amt >= 0:
            comps_to_insert.append((name, code, amt))
            if code == 1:
                allowances_val += amt
            elif code == 2:
                deductions_val += amt

    if not (emp_id and emp_name and email and date_of_birth and joining_date):
        flash("All mandatory fields are required.", "danger")
        return redirect(url_for('index'))

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                \"\"\"INSERT INTO employees (
                    emp_id, emp_name, email, date_of_birth, joining_date, basic_salary, allowances, deductions,
                    age, gender, education, title, department, posting_location, payment_tier
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)\"\"\",
                (emp_id, emp_name, email, date_of_birth, joining_date, basic_val, allowances_val, deductions_val,
                 age_val, gender_val, education_val, title_val, department_val, posting_location_val, payment_tier_val)
            )
            cursor.execute(
                "INSERT IGNORE INTO employee_bank_details (emp_id, bank_name, bank_account_num, ifsc_code) VALUES (%s,%s,%s,%s)",
                (emp_id, bank_name_val, bank_account_num_val, ifsc_code_val)
            )
            cursor.execute(
                "INSERT INTO employee_holidays (emp_id, holiday) VALUES (%s,%s)",
                (emp_id, holiday_val)
            )
            for cname, ccode, camount in comps_to_insert:
                cursor.execute(
                    "INSERT INTO employee_financial_components (emp_id, component_name, code, amount) VALUES (%s,%s,%s,%s)",
                    (emp_id, cname, ccode, camount)
                )
        conn.commit()
        flash(f"Employee {emp_name} added successfully!", "success")
    except Exception as e:
        flash(f"Error adding employee: {str(e)}", "danger")
    finally:
        conn.close()
    return redirect(url_for('index'))
"""

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = re.sub(r"@app\.route\('/add', methods=\['POST'\]\).*?return redirect\(url_for\('index'\)\)", add_new, content, flags=re.DOTALL)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated add_employee!")
