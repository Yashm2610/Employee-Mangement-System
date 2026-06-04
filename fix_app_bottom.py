import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace payslip_builder
new_payslip_builder = """@app.route('/payslip_builder', methods=['GET', 'POST'])
def payslip_builder():
    \"\"\"Interactive UI for generating and customizing a Payslip in real-time.\"\"\"
    if request.method == 'POST':
        # Save the generated payslip to payslip_master
        emp_id = request.form.get('emp_id')
        basic_salary = float(request.form.get('basic_salary') or 0)
        total_allowance = float(request.form.get('total_allowance') or 0)
        total_deduction = float(request.form.get('total_deduction') or 0)
        final_in_hand_salary = float(request.form.get('final_in_hand_salary') or 0)
        
        # Dynamic components
        comp_names = request.form.getlist('component_name[]')
        comp_codes = request.form.getlist('component_code[]')
        comp_amounts = request.form.getlist('component_amount[]')
        
        if emp_id:
            conn = get_db_connection()
            try:
                with conn.cursor() as cursor:
                    # Insert into payslip_master
                    cursor.execute(
                        \"\"\"INSERT INTO payslip_master 
                           (emp_id, basic_salary, total_allowance, total_deduction, final_in_hand_salary) 
                           VALUES (%s, %s, %s, %s, %s)\"\"\",
                        (emp_id, basic_salary, total_allowance, total_deduction, final_in_hand_salary)
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
                flash("Payslip and components saved successfully!", "success")
            except Exception as e:
                flash(f"Error saving payslip: {str(e)}", "danger")
            finally:
                conn.close()
        
        return redirect(url_for('payslip_builder'))
        
    return render_template('payslip_builder.html')
"""
content = re.sub(r"@app\.route\('/payslip_builder'.*?return render_template\('payslip_builder\.html'\)\n", new_payslip_builder, content, flags=re.DOTALL)


# Replace data_dictionary_page query and metadata
new_data_dict = """@app.route('/data-dictionary')
def data_dictionary_page():
    \"\"\"Displays a side-by-side view of live database preview and the Data Dictionary metadata.\"\"\"
    search_col = request.args.get('search_col', '').strip()
    search_val = request.args.get('search_val', '').strip()

    allowed_cols = {
        'emp_name': 'Employee Name',
        'emp_id': 'Employee ID',
        'email': 'Email Address',
        'age': 'Age',
        'gender': 'Gender',
        'education': 'Education',
        'basic_salary': 'Basic Salary',
        'title': 'Designation/Title',
        'department': 'Department',
        'bank_name': 'Bank Name',
        'bank_account_num': 'Bank Account #',
        'ifsc_code': 'IFSC Code',
        'posting_location': 'Location',
        'payment_tier': 'Payment Tier',
        'date_of_birth': 'Date of Birth',
        'joining_date': 'Joining Date'
    }

    if search_col not in allowed_cols:
        search_col = ''

    conn = get_db_connection()
    cursor = conn.cursor()

    base_query = \"\"\"
        SELECT * FROM (
            SELECT 
                e.*,
                b.bank_name,
                b.bank_account_num,
                b.ifsc_code,
                COALESCE(a.total_allowances, 0) AS allowances,
                COALESCE(d.total_deductions, 0) AS deductions
            FROM employees e
            LEFT JOIN employee_bank_details b ON e.emp_id = b.emp_id
            LEFT JOIN (
                SELECT emp_id, SUM(amount) AS total_allowances 
                FROM employee_financial_components 
                WHERE component_code = 1 
                GROUP BY emp_id
            ) a ON e.emp_id = a.emp_id
            LEFT JOIN (
                SELECT emp_id, SUM(amount) AS total_deductions 
                FROM employee_financial_components 
                WHERE component_code = 2 
                GROUP BY emp_id
            ) d ON e.emp_id = d.emp_id
        ) AS emp_details WHERE 1=1
    \"\"\"

    if search_col and search_val:
        query = base_query + f" AND `{search_col}` LIKE %s ORDER BY joining_date DESC"
        cursor.execute(query, (f"%{search_val}%",))
    else:
        query = base_query + " ORDER BY joining_date DESC"
        cursor.execute(query)
    preview_data = cursor.fetchall()
    conn.close()

    # Metadata definitions — normalized
    metadata = [
        {"table": "employees", "column": "id", "type": "int AUTO_INCREMENT", "description": "Internal unique identifier (Primary Key)"},
        {"table": "employees", "column": "emp_id", "type": "varchar(50) UNIQUE", "description": "Unique business Employee ID (e.g. EMP-2024-1001)"},
        {"table": "employees", "column": "emp_name", "type": "varchar(100)", "description": "Full legal name of the employee"},
        {"table": "employees", "column": "email", "type": "varchar(100)", "description": "Corporate email address (unique)"},
        {"table": "employees", "column": "date_of_birth", "type": "date", "description": "Date of birth of the employee"},
        {"table": "employees", "column": "joining_date", "type": "date", "description": "Date of joining the organization"},
        {"table": "employees", "column": "basic_salary", "type": "decimal(12,2)", "description": "Base monthly salary"},
        {"table": "employees", "column": "age", "type": "int", "description": "Age of the employee in years"},
        {"table": "employees", "column": "gender", "type": "varchar(20)", "description": "Gender identification (Male / Female / Other)"},
        {"table": "employees", "column": "education", "type": "int", "description": "0=High School, 1=Diploma, 2=Bachelor's, 3=Master's, 4=PhD"},
        {"table": "employees", "column": "title", "type": "varchar(100)", "description": "Job designation / position title"},
        {"table": "employees", "column": "department", "type": "varchar(100)", "description": "Specific department within the company"},
        {"table": "employees", "column": "posting_location", "type": "varchar(100)", "description": "City of employment"},
        {"table": "employees", "column": "payment_tier", "type": "int", "description": "Salary tier: 1=Executive, 2=Professional, 3=Associate"},
        
        {"table": "employee_bank_details", "column": "emp_id", "type": "varchar(50) FK", "description": "References employees.emp_id"},
        {"table": "employee_bank_details", "column": "bank_name", "type": "varchar(100)", "description": "Name of the bank used for salary credit"},
        {"table": "employee_bank_details", "column": "bank_account_num", "type": "varchar(50)", "description": "Unique bank account number"},
        {"table": "employee_bank_details", "column": "ifsc_code", "type": "varchar(20)", "description": "Bank IFSC Code"},
        
        {"table": "employee_financial_components", "column": "emp_id", "type": "varchar(50) FK", "description": "References employees.emp_id"},
        {"table": "employee_financial_components", "column": "component_name", "type": "varchar(100)", "description": "Name of the component (e.g., Meal Allowance)"},
        {"table": "employee_financial_components", "column": "component_code", "type": "tinyint", "description": "1 for Allowance, 2 for Deduction"},
        {"table": "employee_financial_components", "column": "amount", "type": "decimal(12,2)", "description": "Monetary value"},

        {"table": "payslip_master", "column": "payslip_id", "type": "int PK", "description": "Primary key for payslips"},
        {"table": "payslip_master", "column": "emp_id", "type": "varchar(50) FK", "description": "References employees.emp_id"},
        {"table": "payslip_master", "column": "basic_salary", "type": "decimal(12,2)", "description": "Basic Salary amount"},
        {"table": "payslip_master", "column": "total_allowance", "type": "decimal(12,2)", "description": "Total allowance sum"},
        {"table": "payslip_master", "column": "total_deduction", "type": "decimal(12,2)", "description": "Total deduction sum"},
        {"table": "payslip_master", "column": "final_in_hand_salary", "type": "decimal(12,2)", "description": "Net pay"},
        {"table": "payslip_master", "column": "generated_on", "type": "datetime", "description": "When the payslip was generated"},
        
        {"table": "employee_holidays", "column": "emp_id", "type": "varchar(50) FK", "description": "References employees.emp_id"},
        {"table": "employee_holidays", "column": "holiday_code", "type": "tinyint", "description": "0=Present, 1=Casual Leave, 2=Sick Leave, 3=Paid Holiday, 4=Absent"},
    ]
    
    return render_template('data_dictionary.html', preview_data=preview_data, metadata=metadata,
                           search_col=search_col, search_val=search_val, allowed_cols=allowed_cols)
"""
content = re.sub(r"@app\.route\('/data-dictionary'\).*?return render_template\('data_dictionary\.html', preview_data=preview_data, metadata=metadata,\n                           search_col=search_col, search_val=search_val, allowed_cols=allowed_cols\)\n", new_data_dict, content, flags=re.DOTALL)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated data_dictionary_page and payslip_builder!")
