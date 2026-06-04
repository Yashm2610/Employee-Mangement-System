import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_upload_func = """def upload_file():
    \"\"\"
    Handles CSV uploads. Flexibly matches columns by common synonyms
    (e.g., 'Employee ID', 'Name', 'Email Address', 'Date') to import data directly.
    Falls back to generating details if fields are missing (like the Kaggle dataset).
    \"\"\"
    if 'csv_file' not in request.files:
        flash("No file selected", "danger")
        return redirect(url_for('index'))
        
    file = request.files['csv_file']
    if file.filename == '':
        flash("No selected file", "danger")
        return redirect(url_for('index'))
        
    if file and file.filename.endswith('.csv'):
        # Ensure uploads directory exists
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        
        try:
            # Read CSV using Pandas
            df = pd.read_csv(file_path)
            
            # Clean and lowercase columns for format check
            df_cols = list(df.columns)
            columns_clean = [str(c).strip().lower() for c in df_cols]
            
            # Map columns using common synonyms
            id_col = find_column(columns_clean, df_cols, ['emp_id', 'employee id', 'employee_id', 'id', 'empid', 'employee_code', 'emp_code'])
            name_col = find_column(columns_clean, df_cols, ['emp_name', 'employee name', 'employee_name', 'name', 'full name', 'fullname'])
            email_col = find_column(columns_clean, df_cols, ['email', 'email address', 'email_address', 'mail'])
            date_col = find_column(columns_clean, df_cols, ['date_of_birth', 'dob', 'date', 'birth'])
            joining_col = find_column(columns_clean, df_cols, ['joining_date', 'doj', 'joining date'])
            basic_col = find_column(columns_clean, df_cols, ['basic_salary', 'basic salary', 'basic', 'salary'])
            
            gender_col = find_column(columns_clean, df_cols, ['gender', 'sex'])
            age_col = find_column(columns_clean, df_cols, ['age'])
            education_col = find_column(columns_clean, df_cols, ['education', 'degree', 'qualification'])
            
            title_col = find_column(columns_clean, df_cols, ['title', 'designation', 'role', 'job_title'])
            department_col = find_column(columns_clean, df_cols, ['department', 'dept'])
            posting_col = find_column(columns_clean, df_cols, ['posting_location', 'location', 'city'])
            payment_tier_col = find_column(columns_clean, df_cols, ['payment_tier', 'payment tier', 'paymenttier', 'tier'])
            holiday_col = find_column(columns_clean, df_cols, ['holiday_code', 'holiday'])
            
            bank_name_col = find_column(columns_clean, df_cols, ['bank_name', 'bank name', 'bank'])
            bank_acc_col = find_column(columns_clean, df_cols, ['bank_account_num', 'bank account', 'account number', 'acc_num', 'bank_account'])
            ifsc_col = find_column(columns_clean, df_cols, ['ifsc_code', 'ifsc'])

            conn = get_db_connection()
            cursor = conn.cursor()
            
            success_count = 0
            duplicate_count = 0
            
            # CASE 1: CSV contains all direct employee columns (or matched synonyms)
            if id_col and name_col and email_col:
                for _, row in df.iterrows():
                    emp_id = str(row[id_col]).strip()
                    emp_name = str(row[name_col]).strip()
                    email = str(row[email_col]).strip()
                    
                    try:
                        date_val = pd.to_datetime(row[date_col]).strftime('%Y-%m-%d') if date_col else '1990-01-01'
                    except Exception:
                        date_val = '1990-01-01'
                    try:
                        joining_val = pd.to_datetime(row[joining_col]).strftime('%Y-%m-%d') if joining_col else '2020-01-01'
                    except Exception:
                        joining_val = '2020-01-01'
                        
                    basic_val = float(row[basic_col]) if basic_col else 45000.00
                    
                    age_val = int(row[age_col]) if age_col and not pd.isna(row[age_col]) else 30
                    gender_val = str(row[gender_col]).strip().capitalize() if gender_col and not pd.isna(row[gender_col]) else 'Male'
                    
                    education_val = 2
                    if education_col and not pd.isna(row[education_col]):
                        try:
                            education_val = int(row[education_col])
                        except:
                            education_val = 2
                            
                    title_val = str(row[title_col]).strip() if title_col and not pd.isna(row[title_col]) else 'Software Engineer'
                    department_val = str(row[department_col]).strip() if department_col and not pd.isna(row[department_col]) else 'IT Department'
                    posting_val = str(row[posting_col]).strip() if posting_col and not pd.isna(row[posting_col]) else 'Bangalore'
                    payment_tier_val = int(row[payment_tier_col]) if payment_tier_col and not pd.isna(row[payment_tier_col]) else 3
                    
                    bank_name_val = str(row[bank_name_col]).strip() if bank_name_col and not pd.isna(row[bank_name_col]) else 'Bank of America'
                    bank_account_num_val = str(row[bank_acc_col]).strip() if bank_acc_col and not pd.isna(row[bank_acc_col]) else '1234567890'
                    ifsc_val = str(row[ifsc_col]).strip() if ifsc_col and not pd.isna(row[ifsc_col]) else 'BOFA0000001'
                        
                    holiday_val = 0
                    if holiday_col and not pd.isna(row[holiday_col]):
                        try:
                            holiday_val = int(row[holiday_col])
                        except:
                            pass
                        
                    try:
                        cursor.execute(
                            \"\"\"INSERT INTO employees (
                                emp_id, emp_name, email, date_of_birth, joining_date, basic_salary,
                                age, gender, education, title, department,
                                posting_location, payment_tier
                            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)\"\"\",
                            (emp_id, emp_name, email, date_val, joining_val, basic_val,
                             age_val, gender_val, education_val, title_val, department_val,
                             posting_val, payment_tier_val)
                        )
                        cursor.execute(
                            \"\"\"INSERT IGNORE INTO employee_bank_details (emp_id, bank_name, bank_account_num, ifsc_code) 
                            VALUES (%s,%s,%s,%s)\"\"\",
                            (emp_id, bank_name_val, bank_account_num_val, ifsc_val)
                        )
                        cursor.execute(
                            \"\"\"INSERT IGNORE INTO employee_holidays (emp_id, holiday_code) VALUES (%s,%s)\"\"\",
                            (emp_id, holiday_val)
                        )
                        success_count += 1
                    except pymysql.err.IntegrityError:
                        duplicate_count += 1
                        
            # CASE 2: Generate details dynamically
            else:
                cursor.execute("SELECT COUNT(*) as cnt FROM employees")
                current_records_count = cursor.fetchone()['cnt']
                
                for idx, row in df.iterrows():
                    details = generate_employee_details(row, current_records_count + idx)
                    try:
                        cursor.execute(
                            \"\"\"INSERT INTO employees (
                                emp_id, emp_name, email, date_of_birth, joining_date, basic_salary,
                                age, gender, education, title, department,
                                posting_location, payment_tier
                            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)\"\"\",
                            (details['emp_id'], details['emp_name'], details['email'], details['date_of_birth'], details['joining_date'],
                             details['basic_salary'], details['age'], details['gender'], details['education'],
                             details['title'], details['department'], details['posting_location'], details['payment_tier'])
                        )
                        cursor.execute(
                            \"\"\"INSERT IGNORE INTO employee_bank_details (emp_id, bank_name, bank_account_num, ifsc_code) 
                            VALUES (%s,%s,%s,%s)\"\"\",
                            (details['emp_id'], details['bank_name'], details['bank_account_num'], details['ifsc_code'])
                        )
                        cursor.execute(
                            \"\"\"INSERT IGNORE INTO employee_holidays (emp_id, holiday_code) VALUES (%s,%s)\"\"\",
                            (details['emp_id'], details['holiday_code'])
                        )
                        for atype, amt in details['allowances_list']:
                            cursor.execute("INSERT INTO employee_financial_components (emp_id, component_name, component_code, amount) VALUES (%s,%s,1,%s)", (details['emp_id'], atype, amt))
                        for ttype, amt in details['taxes_list']:
                            cursor.execute("INSERT INTO employee_financial_components (emp_id, component_name, component_code, amount) VALUES (%s,%s,2,%s)", (details['emp_id'], ttype, amt))
                        
                        success_count += 1
                    except pymysql.err.IntegrityError:
                        duplicate_count += 1
            
            conn.commit()
            conn.close()
            
            msg = f"Successfully imported {success_count} records."
            if duplicate_count > 0:
                msg += f" Skipped {duplicate_count} duplicates."
            flash(msg, "success")
            
        except Exception as e:
            flash(f"Error processing CSV: {str(e)}", "danger")
            
    return redirect(url_for('index'))
"""

content = re.sub(r"def upload_file\(\):.*?return redirect\(url_for\('index'\)\)\n", new_upload_func, content, flags=re.DOTALL)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated upload_file!")
