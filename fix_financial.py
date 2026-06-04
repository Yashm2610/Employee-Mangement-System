import re
file_path = r'c:\maxworth internship\app.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

pattern = re.compile(r"@app\.route\('/financial_master', methods=\['GET', 'POST'\]\)\ndef financial_master\(\):.*?return render_template\('financial_master\.html', components=components\)", re.DOTALL)

new_routes = '''@app.route('/financial_master')
def financial_master():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT e.emp_id, e.emp_name, e.basic_salary, 
               b.bank_name, b.bank_account_num, b.ifsc_code
        FROM employees e
        LEFT JOIN employee_bank_details b ON e.emp_id = b.emp_id
        ORDER BY e.emp_id
    """)
    employees_data = cursor.fetchall()
    
    cursor.execute('SELECT * FROM employee_financial_components')
    all_components = cursor.fetchall()
    conn.close()
    
    emp_components = {}
    for comp in all_components:
        eid = comp['emp_id']
        if eid not in emp_components:
            emp_components[eid] = []
        emp_components[eid].append(comp)
        
    return render_template('financial_master.html', employees=employees_data, emp_components=emp_components)

@app.route('/update_employee_financials', methods=['POST'])
def update_employee_financials():
    emp_id = request.form.get('emp_id')
    bank_name = request.form.get('bank_name')
    bank_account_num = request.form.get('bank_account_num')
    ifsc_code = request.form.get('ifsc_code')
    basic_salary = request.form.get('basic_salary', 0.0)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("UPDATE employees SET basic_salary=%s WHERE emp_id=%s", (basic_salary, emp_id))
        
        cursor.execute("SELECT id FROM employee_bank_details WHERE emp_id=%s", (emp_id,))
        if cursor.fetchone():
            cursor.execute("""
                UPDATE employee_bank_details 
                SET bank_name=%s, bank_account_num=%s, ifsc_code=%s 
                WHERE emp_id=%s
            """, (bank_name, bank_account_num, ifsc_code, emp_id))
        else:
            cursor.execute("""
                INSERT INTO employee_bank_details (emp_id, bank_name, bank_account_num, ifsc_code) 
                VALUES (%s, %s, %s, %s)
            """, (emp_id, bank_name, bank_account_num, ifsc_code))
            
        cursor.execute("DELETE FROM employee_financial_components WHERE emp_id=%s", (emp_id,))
        
        comp_names = request.form.getlist('component_name[]')
        comp_codes = request.form.getlist('component_code[]')
        comp_amounts = request.form.getlist('component_amount[]')
        
        for name, code, amt in zip(comp_names, comp_codes, comp_amounts):
            if name.strip() and amt.strip():
                cursor.execute("""
                    INSERT INTO employee_financial_components (emp_id, component_name, component_code, amount)
                    VALUES (%s, %s, %s, %s)
                """, (emp_id, name.strip(), int(code), float(amt)))
                
        conn.commit()
        flash(f"Financial details updated for {emp_id}.", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Error updating financials: {str(e)}", "danger")
    finally:
        conn.close()
        
    return redirect(url_for('financial_master'))'''

if pattern.search(content):
    content = pattern.sub(new_routes, content)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Routes replaced successfully.")
else:
    print("Regex failed to match.")
