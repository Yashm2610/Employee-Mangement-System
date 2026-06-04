import re

def update_app_py():
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Add /api/employee route
    api_route = """
@app.route('/api/employee/<emp_id>')
def api_get_employee(emp_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Get employee basic + bank details
            cursor.execute('''
                SELECT e.*, b.bank_name, b.bank_account_num, b.ifsc_code 
                FROM employees e
                LEFT JOIN employee_bank_details b ON e.emp_id = b.emp_id
                WHERE e.emp_id = %s
            ''', (emp_id,))
            emp = cursor.fetchone()
            
            if not emp:
                return jsonify({"error": "Not found"}), 404
            
            # Convert date objects to string for JSON serialization
            if emp.get('date_of_birth'):
                emp['date_of_birth'] = str(emp['date_of_birth'])
            if emp.get('joining_date'):
                emp['joining_date'] = str(emp['joining_date'])
                
            # Get financial components
            cursor.execute('SELECT * FROM employee_financial_components WHERE emp_id = %s', (emp_id,))
            components = cursor.fetchall()
            
            return jsonify({
                "employee": emp,
                "components": components
            })
    finally:
        conn.close()
"""
    
    # Find the right place to inject (before payslip_builder)
    if "api_get_employee" not in content:
        content = content.replace("@app.route('/payslip_builder', methods=['GET', 'POST'])", 
                                  "from flask import jsonify\nfrom datetime import datetime\n" + api_route + "\n@app.route('/payslip_builder', methods=['GET', 'POST'])")

    # 2. Update payslip_builder route
    new_builder_route = """@app.route('/payslip_builder', methods=['GET', 'POST'])
def payslip_builder():
    \"\"\"Interactive UI for generating and customizing a Payslip in real-time.\"\"\"
    if request.method == 'POST':
        # Save the generated payslip to payslip_master
        emp_id = request.form.get('emp_id')
        basic_salary = float(request.form.get('basic_salary') or 0)
        total_allowance = float(request.form.get('total_allowance') or 0)
        total_deduction = float(request.form.get('total_deduction') or 0)
        final_in_hand_salary = float(request.form.get('final_in_hand_salary') or 0)
        
        # Auto-generate month and year from current time
        now = datetime.now()
        salary_month = now.strftime('%B')
        salary_year = now.year
        
        # Dynamic components
        comp_names = request.form.getlist('component_name[]')
        comp_codes = request.form.getlist('component_code[]')
        comp_amounts = request.form.getlist('component_amount[]')
        
        if emp_id:
            conn = get_db_connection()
            try:
                with conn.cursor() as cursor:
                    # Auto-generate payslip number
                    cursor.execute("SELECT COUNT(*) as count FROM payslip_master")
                    count = cursor.fetchone()['count'] + 1
                    payslip_no = f"PSL-{salary_year}-{str(count).zfill(5)}"
                    
                    # Insert into payslip_master
                    cursor.execute(
                        \"\"\"INSERT INTO payslip_master 
                           (payslip_no, emp_id, salary_month, salary_year, basic_salary, total_allowance, total_deduction, final_in_hand_salary) 
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s)\"\"\",
                        (payslip_no, emp_id, salary_month, salary_year, basic_salary, total_allowance, total_deduction, final_in_hand_salary)
                    )
                    
                    # Delete existing components to replace them with the new generated ones
                    cursor.execute("DELETE FROM employee_financial_components WHERE emp_id = %s", (emp_id,))
                    
                    # Insert dynamic components into employee_financial_components
                    for i in range(len(comp_names)):
                        name = comp_names[i].strip()
                        code = int(comp_codes[i]) if i < len(comp_codes) else 1
                        amt = float(comp_amounts[i]) if i < len(comp_amounts) else 0.0
                        if name:
                            cursor.execute(
                                \"\"\"INSERT INTO employee_financial_components
                                (emp_id, component_name, component_code, amount)
                                VALUES (%s, %s, %s, %s)\"\"\",
                                (emp_id, name, code, amt)
                            )
                conn.commit()
                flash(f"Payslip {payslip_no} saved successfully!", "success")
            except Exception as e:
                flash(f"Error saving payslip: {str(e)}", "danger")
            finally:
                conn.close()
        
        return redirect(url_for('payslip_builder'))
        
    # GET request: fetch all employees for the dropdown
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT emp_id, emp_name, title FROM employees ORDER BY emp_name")
            employees = cursor.fetchall()
    finally:
        conn.close()
        
    return render_template('payslip_builder.html', employees=employees)"""

    # Replace the old payslip_builder function
    content = re.sub(
        r"@app.route\('/payslip_builder', methods=\['GET', 'POST'\]\).*?return render_template\('payslip_builder\.html'\)", 
        new_builder_route, 
        content, 
        flags=re.DOTALL
    )

    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
        
    print("app.py updated successfully.")

if __name__ == '__main__':
    update_app_py()
