import re

def update_app_routes():
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. New Upload Route
    new_upload_func = """import io
from flask import send_file, jsonify

def find_column(columns_clean, df_cols, synonyms):
    for idx, col in enumerate(columns_clean):
        if col in synonyms:
            return df_cols[idx]
    return None

@app.route('/upload', methods=['POST'])
def upload_file():
    \"\"\"
    AJAX endpoint for bulk import from CSV/XLSX/XLS.
    Returns JSON with success_count, error_count, and error_file URL.
    \"\"\"
    if 'csv_file' not in request.files:
        return jsonify({"error": "No file part"}), 400
        
    file = request.files['csv_file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    ext = file.filename.split('.')[-1].lower()
    if ext not in ['csv', 'xlsx', 'xls']:
        return jsonify({"error": "Invalid file type. Only CSV and Excel files are allowed."}), 400
        
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)
    
    try:
        if ext == 'csv':
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
            
        df_cols = list(df.columns)
        columns_clean = [str(c).strip().lower() for c in df_cols]
        
        id_col = find_column(columns_clean, df_cols, ['emp_id', 'employee id', 'employee_id', 'id', 'empid'])
        name_col = find_column(columns_clean, df_cols, ['emp_name', 'employee name', 'employee_name', 'name', 'full name'])
        email_col = find_column(columns_clean, df_cols, ['email', 'email address', 'email_address', 'mail'])
        date_col = find_column(columns_clean, df_cols, ['date_of_birth', 'dob'])
        joining_col = find_column(columns_clean, df_cols, ['joining_date', 'doj', 'joining date'])
        basic_col = find_column(columns_clean, df_cols, ['basic_salary', 'basic salary', 'basic', 'salary'])
        
        gender_col = find_column(columns_clean, df_cols, ['gender', 'sex'])
        age_col = find_column(columns_clean, df_cols, ['age'])
        education_col = find_column(columns_clean, df_cols, ['education', 'degree'])
        
        title_col = find_column(columns_clean, df_cols, ['title', 'designation', 'role'])
        department_col = find_column(columns_clean, df_cols, ['department', 'dept'])
        posting_col = find_column(columns_clean, df_cols, ['posting_location', 'location', 'city'])
        tier_col = find_column(columns_clean, df_cols, ['payment_tier', 'tier'])
        
        bank_name_col = find_column(columns_clean, df_cols, ['bank_name', 'bank'])
        bank_acc_col = find_column(columns_clean, df_cols, ['bank_account_num', 'account number', 'acc_num'])
        ifsc_col = find_column(columns_clean, df_cols, ['ifsc_code', 'ifsc'])
        
        if not (id_col and name_col and email_col):
            return jsonify({"error": f"Missing required columns (Employee ID, Name, Email). Found: {df_cols}"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        
        success_count = 0
        error_rows = []
        
        for idx, row in df.iterrows():
            emp_id = str(row[id_col]).strip()
            emp_name = str(row[name_col]).strip()
            email = str(row[email_col]).strip()
            
            if not emp_id or emp_id == 'nan':
                error_rows.append({"Row": idx+2, "Error": "Missing Employee ID"})
                continue
                
            if not email or '@' not in email:
                error_rows.append({"Row": idx+2, "Error": "Invalid Email"})
                continue
                
            try:
                date_val = pd.to_datetime(row[date_col]).strftime('%Y-%m-%d') if date_col else '1990-01-01'
            except:
                date_val = '1990-01-01'
            try:
                joining_val = pd.to_datetime(row[joining_col]).strftime('%Y-%m-%d') if joining_col else '2020-01-01'
            except:
                joining_val = '2020-01-01'
                
            basic_val = float(row[basic_col]) if basic_col and not pd.isna(row[basic_col]) else 0.0
            age_val = int(row[age_col]) if age_col and not pd.isna(row[age_col]) else 30
            gender_val = str(row[gender_col]).strip().capitalize() if gender_col and not pd.isna(row[gender_col]) else 'Male'
            
            education_val = 2
            if education_col and not pd.isna(row[education_col]):
                try: education_val = int(row[education_col])
                except: pass
                    
            title_val = str(row[title_col]).strip() if title_col and not pd.isna(row[title_col]) else 'Employee'
            department_val = str(row[department_col]).strip() if department_col and not pd.isna(row[department_col]) else 'General'
            posting_val = str(row[posting_col]).strip() if posting_col and not pd.isna(row[posting_col]) else 'Head Office'
            payment_tier_val = int(row[tier_col]) if tier_col and not pd.isna(row[tier_col]) else 3
            
            b_name = str(row[bank_name_col]).strip() if bank_name_col and not pd.isna(row[bank_name_col]) else 'Bank'
            b_acc = str(row[bank_acc_col]).strip() if bank_acc_col and not pd.isna(row[bank_acc_col]) else '0000'
            ifsc = str(row[ifsc_col]).strip() if ifsc_col and not pd.isna(row[ifsc_col]) else 'BANK0000'
            
            try:
                cursor.execute(
                    \"\"\"INSERT INTO employees (
                        emp_id, emp_name, email, date_of_birth, joining_date, basic_salary,
                        age, gender, education, title, department, posting_location, payment_tier
                    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)\"\"\",
                    (emp_id, emp_name, email, date_val, joining_val, basic_val, age_val, gender_val, education_val, title_val, department_val, posting_val, payment_tier_val)
                )
                cursor.execute(
                    \"\"\"INSERT IGNORE INTO employee_bank_details (emp_id, bank_name, bank_account_num, ifsc_code) 
                    VALUES (%s,%s,%s,%s)\"\"\", (emp_id, b_name, b_acc, ifsc)
                )
                cursor.execute(\"\"\"INSERT IGNORE INTO employee_holidays (emp_id, holiday_code) VALUES (%s, 0)\"\"\", (emp_id,))
                success_count += 1
            except pymysql.err.IntegrityError:
                error_rows.append({"Row": idx+2, "Error": f"Duplicate Employee ID: {emp_id}"})
            except Exception as ex:
                error_rows.append({"Row": idx+2, "Error": str(ex)})
                
        conn.commit()
        conn.close()
        
        error_file_url = ""
        if error_rows:
            error_df = pd.DataFrame(error_rows)
            err_filename = f"error_report_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
            error_df.to_csv(os.path.join(app.config['UPLOAD_FOLDER'], err_filename), index=False)
            error_file_url = url_for('download_report', filename=f"uploads/{err_filename}")
            
        return jsonify({
            "success": True,
            "success_count": success_count,
            "error_count": len(error_rows),
            "error_file": error_file_url
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/export/employees')
def export_employees():
    fmt = request.args.get('format', 'csv')
    conn = get_db_connection()
    df = pd.read_sql('''
        SELECT e.*, b.bank_name, b.bank_account_num, b.ifsc_code 
        FROM employees e 
        LEFT JOIN employee_bank_details b ON e.emp_id = b.emp_id
    ''', conn)
    conn.close()
    
    if fmt == 'xlsx':
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Employees')
        output.seek(0)
        return send_file(output, as_attachment=True, download_name='employees_export.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    else:
        output = io.StringIO()
        df.to_csv(output, index=False)
        output.seek(0)
        return send_file(io.BytesIO(output.getvalue().encode()), as_attachment=True, download_name='employees_export.csv', mimetype='text/csv')

@app.route('/export/payslips')
def export_payslips():
    fmt = request.args.get('format', 'csv')
    conn = get_db_connection()
    df = pd.read_sql('''
        SELECT p.payslip_no, p.emp_id, e.emp_name, p.salary_month, p.salary_year,
               p.basic_salary, p.total_allowance, p.total_deduction, p.final_in_hand_salary, p.generated_on
        FROM payslip_master p
        JOIN employees e ON p.emp_id = e.emp_id
        ORDER BY p.generated_on DESC
    ''', conn)
    conn.close()
    
    if fmt == 'xlsx':
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Payslips')
        output.seek(0)
        return send_file(output, as_attachment=True, download_name='payslips_export.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    else:
        output = io.StringIO()
        df.to_csv(output, index=False)
        output.seek(0)
        return send_file(io.BytesIO(output.getvalue().encode()), as_attachment=True, download_name='payslips_export.csv', mimetype='text/csv')
"""

    # We need to find the old upload_file function and replace it.
    old_upload_pattern = re.compile(r"@app\.route\('/upload', methods=\['POST'\]\)\s+def upload_file\(\):.*?return redirect\(url_for\('index'\)\)\n", re.DOTALL)
    if old_upload_pattern.search(content):
        content = old_upload_pattern.sub(new_upload_func, content)
    else:
        # If not found, just append to the end before if __name__ == '__main__':
        content = content.replace("if __name__ == '__main__':", new_upload_func + "\nif __name__ == '__main__':")

    # Add io to imports if missing
    if "import io" not in content:
        content = "import io\nfrom flask import send_file, jsonify\n" + content

    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)

    print("Successfully updated app.py with new upload/export routes.")

if __name__ == '__main__':
    update_app_routes()
