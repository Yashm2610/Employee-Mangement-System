import os
import random
import hashlib
import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
import pandas as pd
import pymysql

def amount_to_words_rupees(num):
    """Converts a numeric amount to English words in Indian Rupees format."""
    try:
        num = float(num)
    except (ValueError, TypeError):
        return ""
        
    if num == 0:
        return "Zero Rupees Only"
        
    units = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", 
             "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen"]
    tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]
    
    def helper(n):
        if n < 20:
            return units[n]
        elif n < 100:
            return tens[n // 10] + (" " + units[n % 10] if n % 10 != 0 else "")
        elif n < 1000:
            return units[n // 100] + " Hundred" + (" and " + helper(n % 100) if n % 100 != 0 else "")
        elif n < 100000: # up to 99,999 (Indian numbering)
            return helper(n // 1000) + " Thousand" + (" " + helper(n % 1000) if n % 1000 != 0 else "")
        elif n < 10000000: # up to 99,99,999 (Lakhs)
            return helper(n // 100000) + " Lakh" + (" " + helper(n % 100000) if n % 100000 != 0 else "")
        else: # Crores
            return helper(n // 10000000) + " Crore" + (" " + helper(n % 10000000) if n % 10000000 != 0 else "")
            
    integer_part = int(num)
    decimal_part = int(round((num - integer_part) * 100))
    
    words = helper(integer_part)
    words += " Rupees"
    if decimal_part > 0:
        words += " and " + helper(decimal_part) + " Paise"
    words += " Only"
        
    return words.strip()

def get_dynamic_payroll_and_bank(basic_base, title, department, emp_id_or_seed):
    """
    Computes payroll details and bank details.
    """
    import hashlib
    import random
    combo_str = f"{str(title).strip().lower()}|{str(department).strip().lower()}"
    role_seed = int(hashlib.md5(combo_str.encode('utf-8')).hexdigest(), 16) % 20000
    random.seed(role_seed)

    meal_pct = random.choice([0.05, 0.06, 0.07, 0.08, 0.09, 0.10])
    transport_pct = random.choice([0.04, 0.05, 0.06, 0.07, 0.08])
    medical_pct = random.choice([0.02, 0.03, 0.04, 0.05])
    retirement_pct = random.choice([0.10, 0.11, 0.12, 0.13])
    tax_pct = random.choice([0.015, 0.02, 0.025, 0.03])
    banks = ["Bank of America", "Chase Bank", "Wells Fargo", "Citibank", "HSBC", "HDFC Bank", "ICICI Bank"]
    bank_name = random.choice(banks)

    random.seed(emp_id_or_seed + 99999)
    variation_pct = random.uniform(-0.20, 0.20)
    basic_salary = round(float(basic_base) * (1 + variation_pct), 2)

    meal_allowance = round(basic_salary * meal_pct, 2)
    transportation_allowance = round(basic_salary * transport_pct, 2)
    medical_allowance = round(basic_salary * medical_pct, 2)
    retirement_insurance = round(basic_salary * retirement_pct, 2)
    tax_amount = round(basic_salary * tax_pct, 2)

    random.seed(emp_id_or_seed + 12345)
    bank_account_num = "".join([str(random.randint(0, 9)) for _ in range(10)])
    ifsc_code = bank_name[:4].upper() + "0" + "".join([str(random.randint(0, 9)) for _ in range(6)])

    allowances_list = [
        ('Meal Allowance', meal_allowance),
        ('Transportation Allowance', transportation_allowance),
        ('Medical Allowance', medical_allowance),
    ]
    taxes_list = [
        ('Retirement Insurance', retirement_insurance),
        ('Professional Tax', tax_amount),
    ]

    return (basic_salary, bank_name, bank_account_num, ifsc_code, allowances_list, taxes_list)

app = Flask(__name__)
app.secret_key = "employee_management_system_secret_key"
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')

DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = 'yabh'
DB_NAME = 'employee_db'

MALE_NAMES = ["Amit", "Rahul", "Rohit", "Abhishek", "Vivek", "Manish", "Sunil", "David", "John", "James", "Michael", "William", "Rajesh", "Sanjay", "Vikram", "Arjun", "Karan"]
FEMALE_NAMES = ["Pooja", "Priya", "Sneha", "Neha", "Anjali", "Ritu", "Divya", "Emily", "Sarah", "Jessica", "Kiran", "Shalini", "Sunita", "Deepika", "Preeti", "Kavita", "Swati"]
LAST_NAMES = ["Sharma", "Verma", "Gupta", "Patel", "Singh", "Kumar", "Smith", "Johnson", "Williams", "Brown", "Davis", "Miller", "Mehta", "Joshi", "Sen", "Reddy", "Nair"]

def get_db_connection():
    """Establishes a MySQL connection using PyMySQL."""
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )

def init_db():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 1. Read and execute schema.sql for base tables
            with open('schema.sql', 'r') as f:
                sql_script = f.read()
            for statement in sql_script.split(';'):
                if statement.strip():
                    cursor.execute(statement)
            
            # 2. Self-healing / Migrations
            # Rename city -> posting_location
            cursor.execute("SHOW COLUMNS FROM employees LIKE 'city'")
            if cursor.fetchone():
                try:
                    cursor.execute("ALTER TABLE employees CHANGE city posting_location VARCHAR(100) DEFAULT 'Bangalore'")
                except Exception as e:
                    pass
            
            # Rename date -> date_of_birth
            cursor.execute("SHOW COLUMNS FROM employees LIKE 'date'")
            if cursor.fetchone():
                try:
                    cursor.execute("ALTER TABLE employees CHANGE date date_of_birth DATE NOT NULL")
                except Exception as e:
                    pass
                    
            # Drop obsolete columns
            obsolete_cols = ['directorate', 'joining_year', 'ever_benched', 'experience_in_current_domain', 'leave_or_not', 'allowances', 'deductions']
            for col in obsolete_cols:
                cursor.execute("SHOW COLUMNS FROM employees LIKE %s", (col,))
                if cursor.fetchone():
                    try:
                        cursor.execute(f"ALTER TABLE employees DROP COLUMN {col}")
                    except Exception as e:
                        pass
                        
            # Ensure joining_date exists
            cursor.execute("SHOW COLUMNS FROM employees LIKE 'joining_date'")
            if not cursor.fetchone():
                try:
                    cursor.execute("ALTER TABLE employees ADD COLUMN joining_date DATE NOT NULL DEFAULT '2023-01-01'")
                except Exception as e:
                    pass
                    
            # Add ifsc_code to employee_bank_details
            cursor.execute("SHOW COLUMNS FROM employee_bank_details LIKE 'ifsc_code'")
            if not cursor.fetchone():
                try:
                    cursor.execute("ALTER TABLE employee_bank_details ADD COLUMN ifsc_code VARCHAR(20) DEFAULT 'BOFA0000001'")
                except Exception as e:
                    pass
                    
            # Fix employee_financial_components code -> component_code
            cursor.execute("SHOW COLUMNS FROM employee_financial_components LIKE 'code'")
            if cursor.fetchone():
                try:
                    cursor.execute("ALTER TABLE employee_financial_components CHANGE code component_code TINYINT NOT NULL COMMENT '1 for Allowance, 2 for Deduction'")
                except Exception as e:
                    pass
            
            # Fix employee_holidays holiday -> holiday_code
            cursor.execute("SHOW COLUMNS FROM employee_holidays LIKE 'holiday'")
            if cursor.fetchone():
                try:
                    cursor.execute("ALTER TABLE employee_holidays CHANGE holiday holiday_code TINYINT NOT NULL")
                except Exception as e:
                    pass
            
            # Fix payslip_master generated_at -> generated_on
            cursor.execute("SHOW COLUMNS FROM payslip_master LIKE 'generated_at'")
            if cursor.fetchone():
                try:
                    cursor.execute("ALTER TABLE payslip_master CHANGE generated_at generated_on DATETIME DEFAULT CURRENT_TIMESTAMP")
                except Exception as e:
                    pass

        conn.commit()
    except Exception as e:
        print(f"Error initializing DB: {e}")
    finally:
        conn.close()
def generate_employee_details(row, offset_index):
    """
    Generates realistic employee details from a row of the Kaggle Employee dataset.
    Returns a dict with all fields for employees + satellite tables.
    """
    import random
    import pandas as pd
    
    age_val = row.get('Age')
    if age_val is None or pd.isna(age_val):
        random.seed(offset_index + 42)
        age = random.randint(21, 58)
    else:
        age = int(age_val)
        
    joining_year = int(row.get('JoiningYear', 2020))
    gender = str(row.get('Gender', 'Male')).strip().capitalize()
    payment_tier = int(row.get('PaymentTier', 3))
    
    education_text = str(row.get('Education', 'B.Tech')).strip()
    if 'High School' in education_text or '10th' in education_text or '12th' in education_text:
        education_code = 0
    elif 'Diploma' in education_text:
        education_code = 1
    elif 'Bachelors' in education_text or 'B.Tech' in education_text:
        education_code = 2
    elif 'Masters' in education_text or 'M.Tech' in education_text:
        education_code = 3
    elif 'PhD' in education_text:
        education_code = 4
    else:
        education_code = 2

    choice_seed = offset_index + age
    random.seed(choice_seed)

    if gender == 'Female':
        first_name = random.choice(FEMALE_NAMES)
    else:
        first_name = random.choice(MALE_NAMES)
    last_name = random.choice(LAST_NAMES)
    emp_name = f"{first_name} {last_name}"

    emp_id = f"EMP-{joining_year}-{offset_index + 1001}"
    email = f"{first_name.lower()}.{last_name.lower()}{offset_index + 1}@company.com"

    month = random.randint(1, 12)
    day = random.randint(1, 28)
    date_of_birth = f"{1990 + (offset_index % 10)}-{month:02d}-{day:02d}"
    joining_date = f"{joining_year}-{month:02d}-{day:02d}"

    if payment_tier == 1:
        basic_base = 85000.00
    elif payment_tier == 2:
        basic_base = 50000.00
    else:
        basic_base = 32000.00

    designations = [
        "Software Engineer", "Senior Software Engineer", "Systems Analyst",
        "Data Engineer", "Product Manager", "Quality Analyst", "Security Engineer"
    ]
    title = designations[choice_seed % len(designations)]
    department_list = ["Core Development", "Data Platform", "QA & Testing", "Cloud Operations"]
    department = department_list[choice_seed % len(department_list)]

    (basic_salary, bank_name, bank_account_num, ifsc_code, allowances_list, taxes_list) = get_dynamic_payroll_and_bank(
        basic_base, title, department, offset_index
    )

    posting_location = str(row.get('City', 'Bangalore')).strip()
    
    holiday_code = random.randint(0, 4)

    return {
        'emp_id': emp_id, 'emp_name': emp_name, 'email': email, 'date_of_birth': date_of_birth, 'joining_date': joining_date,
        'basic_salary': basic_salary, 
        'age': age, 'gender': gender, 'education': education_code,
        'title': title, 'department': department,
        'bank_name': bank_name, 'bank_account_num': bank_account_num, 'ifsc_code': ifsc_code,
        'allowances_list': allowances_list, 'taxes_list': taxes_list,
        'posting_location': posting_location, 'payment_tier': payment_tier,
        'holiday_code': holiday_code
    }


@app.route('/')
def index():
    """Displays the main interface with upload capabilities, manual entry, search, and sorting."""
    search_col = request.args.get('search_col', 'emp_name').strip()
    search_val = request.args.get('search_val', '').strip()
    sort_order = request.args.get('sort', 'joining_date_desc')
    selected_tier = request.args.get('tier', 'all').strip()
    
    # Advanced Filters
    filter_dept = request.args.get('filter_dept', '').strip()
    filter_desig = request.args.get('filter_desig', '').strip()
    filter_loc = request.args.get('filter_loc', '').strip()
    filter_gender = request.args.get('filter_gender', '').strip()
    
    allowed_cols = {
        'emp_name': 'Employee Name',
        'emp_id': 'Employee ID',
        'email': 'Email Address',
        'age': 'Age',
        'gender': 'Gender',
        'education': 'Education',
        'basic_salary': 'Basic Salary',
        'allowances': 'Allowances Total',
        'deductions': 'Deductions Total',
        'title': 'Designation/Title',
        'department': 'Department',
        'posting_location': 'Posting Location',
        'bank_name': 'Bank Name',
        'bank_account_num': 'Bank Account #',
        'ifsc_code': 'IFSC Code',
        'payment_tier': 'Payment Tier',
        'joining_date': 'Joining Date'
    }
    
    if search_col not in allowed_cols:
        search_col = 'emp_name'
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT * FROM (
            SELECT 
                e.*,
                b.bank_name,
                b.bank_account_num,
                b.ifsc_code
            FROM employees e
            LEFT JOIN employee_bank_details b ON e.emp_id = b.emp_id
        ) AS emp_details WHERE 1=1
    """
    params = []
    
    if search_val:
        query += f" AND `{search_col}` LIKE %s"
        params.append(f"%{search_val}%")
        
    if filter_dept:
        query += " AND department = %s"
        params.append(filter_dept)
        
    if filter_desig:
        query += " AND title = %s"
        params.append(filter_desig)
        
    if filter_loc:
        query += " AND posting_location = %s"
        params.append(filter_loc)
        
    if filter_gender:
        query += " AND gender = %s"
        params.append(filter_gender)
        
    if selected_tier == '1':
        query += " AND basic_salary >= 80000"
    elif selected_tier == '2':
        query += " AND basic_salary >= 50000 AND basic_salary < 80000"
    elif selected_tier == '3':
        query += " AND basic_salary < 50000"
        
    if sort_order == 'date_asc':
        query += " ORDER BY joining_date ASC"
    elif sort_order == 'date_desc':
        query += " ORDER BY joining_date DESC"
    elif sort_order == 'name_asc':
        query += " ORDER BY emp_name ASC"
    elif sort_order == 'name_desc':
        query += " ORDER BY emp_name DESC"
    elif sort_order == 'id_asc':
        query += " ORDER BY emp_id ASC"
    elif sort_order == 'id_desc':
        query += " ORDER BY emp_id DESC"
    else:
        query += " ORDER BY joining_date DESC"
        
    cursor.execute(query, params)
    employees = cursor.fetchall()
    conn.close()
    # Analytics for Charts
    dept_dist = {}
    gender_dist = {}
    location_dist = {}
    
    for emp in employees:
        dept = emp.get('department') or 'Unknown'
        dept_dist[dept] = dept_dist.get(dept, 0) + 1
        
        gender = emp.get('gender') or 'Unknown'
        gender_dist[gender] = gender_dist.get(gender, 0) + 1
        
        loc = emp.get('posting_location') or 'Unknown'
        location_dist[loc] = location_dist.get(loc, 0) + 1
        
    chart_data = {
        'departments': list(dept_dist.keys()),
        'dept_counts': list(dept_dist.values()),
        'genders': list(gender_dist.keys()),
        'gender_counts': list(gender_dist.values()),
        'locations': list(location_dist.keys()),
        'location_counts': list(location_dist.values())
    }
    
    return render_template('index.html', 
                           employees=employees, 
                           search_col=search_col, 
                           search_val=search_val, 
                           allowed_cols=allowed_cols, 
                           sort=sort_order, 
                           tier=selected_tier, 
                           chart_data=chart_data,
                           filter_dept=filter_dept,
                           filter_desig=filter_desig,
                           filter_loc=filter_loc,
                           filter_gender=filter_gender)

def find_column(clean_cols, df_cols, synonyms):
    """Helper to find the actual case-sensitive column name from a list of synonyms."""
    for syn in synonyms:
        if syn in clean_cols:
            idx = clean_cols.index(syn)
            return df_cols[idx]
    return None

import io
from flask import send_file, jsonify

def find_column(columns_clean, df_cols, synonyms):
    for idx, col in enumerate(columns_clean):
        if col in synonyms:
            return df_cols[idx]
    return None

        
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
                            """INSERT INTO employees (
                                emp_id, emp_name, email, date_of_birth, joining_date, basic_salary,
                                age, gender, education, title, department,
                                posting_location, payment_tier
                            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                            (emp_id, emp_name, email, date_val, joining_val, basic_val,
                             age_val, gender_val, education_val, title_val, department_val,
                             posting_val, payment_tier_val)
                        )
                        cursor.execute(
                            """INSERT IGNORE INTO employee_bank_details (emp_id, bank_name, bank_account_num, ifsc_code) 
                            VALUES (%s,%s,%s,%s)""",
                            (emp_id, bank_name_val, bank_account_num_val, ifsc_val)
                        )
                        cursor.execute(
                            """INSERT IGNORE INTO employee_holidays (emp_id, holiday_code) VALUES (%s,%s)""",
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
                            """INSERT INTO employees (
                                emp_id, emp_name, email, date_of_birth, joining_date, basic_salary,
                                age, gender, education, title, department,
                                posting_location, payment_tier
                            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                            (details['emp_id'], details['emp_name'], details['email'], details['date_of_birth'], details['joining_date'],
                             details['basic_salary'], details['age'], details['gender'], details['education'],
                             details['title'], details['department'], details['posting_location'], details['payment_tier'])
                        )
                        cursor.execute(
                            """INSERT IGNORE INTO employee_bank_details (emp_id, bank_name, bank_account_num, ifsc_code) 
                            VALUES (%s,%s,%s,%s)""",
                            (details['emp_id'], details['bank_name'], details['bank_account_num'], details['ifsc_code'])
                        )
                        cursor.execute(
                            """INSERT IGNORE INTO employee_holidays (emp_id, holiday_code) VALUES (%s,%s)""",
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
            date_col = find_column(columns_clean, df_cols, ['date', 'joining date', 'joining_date', 'date of joining', 'doj', 'joiningyear', 'year'])
            basic_col = find_column(columns_clean, df_cols, ['basic_salary', 'basic salary', 'basic', 'salary'])
            allowances_col = find_column(columns_clean, df_cols, ['allowances', 'allowance', 'bonus'])
            deductions_col = find_column(columns_clean, df_cols, ['deductions', 'deduction', 'pf'])
            
            gender_col = find_column(columns_clean, df_cols, ['gender', 'sex'])
            age_col = find_column(columns_clean, df_cols, ['age'])
            education_col = find_column(columns_clean, df_cols, ['education', 'degree', 'qualification'])
            
            title_col = find_column(columns_clean, df_cols, ['title', 'designation', 'role', 'job_title'])
            directorate_col = find_column(columns_clean, df_cols, ['directorate', 'division'])
            department_col = find_column(columns_clean, df_cols, ['department', 'dept'])
            bank_name_col = find_column(columns_clean, df_cols, ['bank_name', 'bank name', 'bank'])
            bank_acc_col = find_column(columns_clean, df_cols, ['bank_account_num', 'bank account', 'account number', 'acc_num', 'bank_account'])
            meal_col = find_column(columns_clean, df_cols, ['meal_allowance', 'meal allowance', 'meal'])
            transport_col = find_column(columns_clean, df_cols, ['transportation_allowance', 'transportation allowance', 'transport', 'ta'])
            medical_col = find_column(columns_clean, df_cols, ['medical_allowance', 'medical allowance', 'medical'])
            retirement_col = find_column(columns_clean, df_cols, ['retirement_insurance', 'retirement insurance', 'retirement'])
            tax_col = find_column(columns_clean, df_cols, ['tax', 'professional tax', 'pt'])
            
            joining_year_col = find_column(columns_clean, df_cols, ['joining_year', 'joining year', 'joiningyear', 'year'])
            city_col = find_column(columns_clean, df_cols, ['city', 'location'])
            payment_tier_col = find_column(columns_clean, df_cols, ['payment_tier', 'payment tier', 'paymenttier', 'tier'])
            ever_benched_col = find_column(columns_clean, df_cols, ['ever_benched', 'ever benched', 'everbenched', 'benched'])
            experience_col = find_column(columns_clean, df_cols, ['experience_in_current_domain', 'experience in current domain', 'experienceincurrentdomain', 'experience'])
            leave_col = find_column(columns_clean, df_cols, ['leave_or_not', 'leave or not', 'leaveornot', 'leave'])

            conn = get_db_connection()
            cursor = conn.cursor()
            
            success_count = 0
            duplicate_count = 0
            
            # CASE 1: CSV contains all direct employee columns (or matched synonyms)
            if id_col and name_col and email_col and date_col:
                for _, row in df.iterrows():
                    emp_id = str(row[id_col]).strip()
                    emp_name = str(row[name_col]).strip()
                    email = str(row[email_col]).strip()
                    
                    try:
                        date_val = pd.to_datetime(row[date_col]).strftime('%Y-%m-%d')
                    except Exception:
                        date_val = str(row[date_col]).strip()
                        
                    basic_val = float(row[basic_col]) if basic_col else 45000.00
                    
                    meal_val = float(row[meal_col]) if meal_col else 300.00
                    transport_val = float(row[transport_col]) if transport_col else 300.00
                    medical_val = float(row[medical_col]) if medical_col else 300.00
                    retirement_val = float(row[retirement_col]) if retirement_col else 25.00
                    tax_val = float(row[tax_col]) if tax_col else 25.00
                    
                    allowances_val = float(row[allowances_col]) if allowances_col else (meal_val + transport_val + medical_val)
                    deductions_val = float(row[deductions_col]) if deductions_col else (retirement_val + tax_val)
                    
                    age_val = int(row[age_col]) if age_col and not pd.isna(row[age_col]) else 30
                    gender_val = str(row[gender_col]).strip().capitalize() if gender_col and not pd.isna(row[gender_col]) else 'Male'
                    education_val = str(row[education_col]).strip() if education_col and not pd.isna(row[education_col]) else 'B.Tech'
                    
                    title_val = str(row[title_col]).strip() if title_col and not pd.isna(row[title_col]) else 'Software Engineer'
                    directorate_val = str(row[directorate_col]).strip() if directorate_col and not pd.isna(row[directorate_col]) else 'Engineering'
                    department_val = str(row[department_col]).strip() if department_col and not pd.isna(row[department_col]) else 'IT Department'
                    bank_name_val = str(row[bank_name_col]).strip() if bank_name_col and not pd.isna(row[bank_name_col]) else 'Bank of America'
                    bank_account_num_val = str(row[bank_acc_col]).strip() if bank_acc_col and not pd.isna(row[bank_acc_col]) else '1234567890'
                        
                    joining_year_val = int(row[joining_year_col]) if joining_year_col and not pd.isna(row[joining_year_col]) else (pd.to_datetime(row[date_col]).year if date_col else 2026)
                    city_val = str(row[city_col]).strip() if city_col and not pd.isna(row[city_col]) else 'Bangalore'
                    payment_tier_val = int(row[payment_tier_col]) if payment_tier_col and not pd.isna(row[payment_tier_col]) else 3
                    ever_benched_val = str(row[ever_benched_col]).strip() if ever_benched_col and not pd.isna(row[ever_benched_col]) else 'No'
                    experience_val = int(row[experience_col]) if experience_col and not pd.isna(row[experience_col]) else 2
                    leave_val = int(row[leave_col]) if leave_col and not pd.isna(row[leave_col]) else 0
                        
                    try:
                        cursor.execute(
                            """INSERT INTO employees (
                                emp_id, emp_name, email, date, basic_salary, allowances, deductions,
                                age, gender, education, title, directorate, department,
                                joining_year, city, payment_tier, ever_benched, experience_in_current_domain, leave_or_not
                            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                            (emp_id, emp_name, email, date_val, basic_val, allowances_val, deductions_val,
                             age_val, gender_val, education_val, title_val, directorate_val, department_val,
                             joining_year_val, city_val, payment_tier_val, ever_benched_val, experience_val, leave_val)
                        )
                        # Bank details satellite table
                        cursor.execute(
                            "INSERT IGNORE INTO employee_bank_details (emp_id, bank_name, bank_account_num) VALUES (%s,%s,%s)",
                            (emp_id, bank_name_val, bank_account_num_val)
                        )
                        # Allowances satellite table
                        for atype, aamount in [('meal_allowance', meal_val), ('transportation_allowance', transport_val), ('medical_allowance', medical_val)]:
                            cursor.execute(
                                "INSERT INTO employee_allowances (emp_id, allowance_type, amount) VALUES (%s,%s,%s)",
                                (emp_id, atype, aamount)
                            )
                        # Taxes satellite table
                        for ttype, tamount in [('retirement_insurance', retirement_val), ('professional_tax', tax_val)]:
                            cursor.execute(
                                "INSERT INTO employee_taxes (emp_id, tax_type, amount) VALUES (%s,%s,%s)",
                                (emp_id, ttype, tamount)
                            )
                        success_count += 1
                    except pymysql.err.IntegrityError:
                        duplicate_count += 1
                        
            # CASE 2: CSV lacks Name/Email but contains year/gender (like Kaggle Employee.csv) or partial headers
            elif 'joiningyear' in columns_clean or date_col or id_col:
                # Fetch current record count to maintain unique indexing
                cursor.execute("SELECT COUNT(*) as cnt FROM employees")
                current_records_count = cursor.fetchone()['cnt']
                
                for idx, row in df.iterrows():
                    # 1. Resolve date
                    joining_year = 2026
                    if date_col:
                        val = str(row[date_col]).strip()
                        if len(val) == 4 and val.isdigit():  # e.g., "2017"
                            joining_year = int(val)
                            month = random.randint(1, 12)
                            day = random.randint(1, 28)
                            date_val = f"{joining_year}-{month:02d}-{day:02d}"
                        else:
                            try:
                                dt = pd.to_datetime(row[date_col])
                                date_val = dt.strftime('%Y-%m-%d')
                                joining_year = dt.year
                            except Exception:
                                date_val = val
                    else:
                        # fallback
                        joining_year = int(row.get('JoiningYear', 2026))
                        month = random.randint(1, 12)
                        day = random.randint(1, 28)
                        date_val = f"{joining_year}-{month:02d}-{day:02d}"
                    
                    # 2. Resolve emp_id
                    if id_col:
                        emp_id = str(row[id_col]).strip()
                    else:
                        emp_id = f"EMP-{joining_year}-{current_records_count + idx + 1001}"
                        
                    # 3. Resolve name
                    if name_col:
                        emp_name = str(row[name_col]).strip()
                    else:
                        gender = str(row[gender_col]).strip().capitalize() if gender_col else 'Male'
                        # Seed based on combinations for repeat reliability
                        random.seed(current_records_count + idx + joining_year)
                        if gender == 'Female':
                            first_name = random.choice(FEMALE_NAMES)
                        else:
                            first_name = random.choice(MALE_NAMES)
                        last_name = random.choice(LAST_NAMES)
                        emp_name = f"{first_name} {last_name}"
                        
                    # 4. Resolve email
                    if email_col:
                        email = str(row[email_col]).strip()
                    else:
                        first_part = emp_name.lower().replace(" ", ".")
                        email = f"{first_part}{current_records_count + idx + 1}@company.com"
                        
                    # 5. Resolve Salary (via details generator)
                    det = generate_employee_details(row, current_records_count + idx)
                    basic_val = det['basic_salary']
                    allowances_val = det['allowances']
                    deductions_val = det['deductions']
                    age_val = det['age']
                    gender_val = det['gender']
                    education_val = det['education']
                    title_val = det['title']
                    directorate_val = det['directorate']
                    department_val = det['department']
                    bank_name_val = det['bank_name']
                    bank_account_num_val = det['bank_account_num']
                    allowances_list = det['allowances_list']
                    taxes_list = det['taxes_list']
                    joining_year_val = det['joining_year']
                    city_val = det['city']
                    payment_tier_val = det['payment_tier']
                    ever_benched_val = det['ever_benched']
                    experience_val = det['experience']
                    leave_val = det['leave_or_not']
                    meal_val = next((a for t, a in allowances_list if t == 'meal_allowance'), 0)
                    transport_val = next((a for t, a in allowances_list if t == 'transportation_allowance'), 0)
                    medical_val = next((a for t, a in allowances_list if t == 'medical_allowance'), 0)
                    retirement_val = next((a for t, a in taxes_list if t == 'retirement_insurance'), 0)
                    tax_val = next((a for t, a in taxes_list if t == 'professional_tax'), 0)
                    allowances_val = meal_val + transport_val + medical_val
                    deductions_val = retirement_val + tax_val

                    try:
                        cursor.execute(
                            """INSERT INTO employees (
                                emp_id, emp_name, email, date, basic_salary, allowances, deductions,
                                age, gender, education, title, directorate, department,
                                joining_year, city, payment_tier, ever_benched, experience_in_current_domain, leave_or_not
                            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                            (emp_id, emp_name, email, date_val, basic_val, allowances_val, deductions_val,
                             age_val, gender_val, education_val, title_val, directorate_val, department_val,
                             joining_year_val, city_val, payment_tier_val, ever_benched_val, experience_val, leave_val)
                        )
                        cursor.execute(
                            "INSERT IGNORE INTO employee_bank_details (emp_id, bank_name, bank_account_num) VALUES (%s,%s,%s)",
                            (emp_id, bank_name_val, bank_account_num_val)
                        )
                        for atype, aamount in allowances_list:
                            cursor.execute(
                                "INSERT INTO employee_allowances (emp_id, allowance_type, amount) VALUES (%s,%s,%s)",
                                (emp_id, atype, aamount)
                            )
                        for ttype, tamount in taxes_list:
                            cursor.execute(
                                "INSERT INTO employee_taxes (emp_id, tax_type, amount) VALUES (%s,%s,%s)",
                                (emp_id, ttype, tamount)
                            )
                        success_count += 1
                    except pymysql.err.IntegrityError:
                        duplicate_count += 1
            else:
                flash("Unknown CSV Schema. CSV must contain at least ID/Date columns or match the Employee.csv dataset structure.", "warning")
                conn.close()
                return redirect(url_for('index'))
                
            conn.commit()
            conn.close()
            
            msg = f"Successfully imported {success_count} employee records."
            if duplicate_count > 0:
                msg += f" ({duplicate_count} duplicates skipped)."
            flash(msg, "success")
            
        except Exception as e:
            flash(f"Error parsing CSV file: {str(e)}", "danger")
        return redirect(url_for('index'))
    else:
        flash("Unsupported file format. Please upload a CSV file.", "danger")
        return redirect(url_for('index'))
 
@app.route('/add', methods=['POST'])
def add_employee():
    """Handles manual adding of employees from the front-end form."""
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
                """INSERT INTO employees (
                    emp_id, emp_name, email, date_of_birth, joining_date, basic_salary, allowances, deductions,
                    age, gender, education, title, department, posting_location, payment_tier
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
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

@app.route('/delete/<int:id>', methods=['POST'])
def delete_employee(id):
    """Optional helper route to delete a single employee record."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM employees WHERE id = %s", (id,))
        conn.commit()
        flash("Employee record deleted.", "info")
    except Exception as e:
        flash(f"Error deleting record: {str(e)}", "danger")
    finally:
        conn.close()
    return redirect(url_for('index'))

@app.route('/clear', methods=['POST'])
def clear_records():
    """Helper route to clear all records from the database for easy testing."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM employees")
            cursor.execute("DELETE FROM employee_bank_details")
            cursor.execute("DELETE FROM employee_financial_components")
            cursor.execute("DELETE FROM payslip_master")
            cursor.execute("DELETE FROM employee_holidays")
            cursor.execute("DELETE FROM employee_emails")
        conn.commit()
    except Exception as e:
        flash(f"Error clearing records: {str(e)}", "danger")
    finally:
        conn.close()
    return redirect(url_for('index'))

@app.route('/employee/<int:id>')
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

    # Fetch payslip transactions (payslip_master)
    cursor.execute("SELECT * FROM payslip_master WHERE emp_id = %s ORDER BY generated_on DESC", (emp_id,))
    payroll_transactions = cursor.fetchall()

    # Fetch email logs
    cursor.execute("SELECT * FROM employee_emails WHERE emp_id = %s ORDER BY sent_at DESC", (emp_id,))
    email_logs = cursor.fetchall()
    
    # Fetch holidays/attendance
    cursor.execute("SELECT holiday_code, COUNT(*) as count FROM employee_holidays WHERE emp_id = %s GROUP BY holiday_code", (emp_id,))
    holidays = cursor.fetchall()
    
    conn.close()

    total_allowances = sum(amt for _, amt in allowances_data)
    total_deductions = sum(amt for _, amt in deductions_data)
    
    # Process Holiday Data for Chart
    holiday_labels = {0: 'Present', 1: 'Casual Leave', 2: 'Sick Leave', 3: 'Paid Holiday', 4: 'Absent'}
    holiday_dist = [0]*5
    for row in holidays:
        code = row['holiday_code']
        if 0 <= code <= 4:
            holiday_dist[code] = row['count']
            
    # Process Email Data for Chart
    email_months = {}
    for email in email_logs:
        month = email['sent_at'].strftime('%Y-%m')
        email_months[month] = email_months.get(month, 0) + 1
        
    profile_chart_data = {
        'holiday_labels': list(holiday_labels.values()),
        'holiday_counts': holiday_dist,
        'email_months': list(reversed(list(email_months.keys())))[:6],
        'email_counts': list(reversed(list(email_months.values())))[:6]
    }

    return render_template('employee_profile.html', 
                           employee=employee, 
                           bank=bank, 
                           allowances_data=allowances_data, 
                           deductions_data=deductions_data,
                           total_allowances=total_allowances,
                           total_deductions=total_deductions,
                           payroll_transactions=payroll_transactions,
                           email_logs=email_logs,
                           profile_chart_data=profile_chart_data)

@app.route('/send_email/<int:id>', methods=['POST'])
def send_email(id):
    """Simulates sending an email to the employee and logs it."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT emp_id, emp_name, email FROM employees WHERE id = %s", (id,))
    employee = cursor.fetchone()

    if not employee:
        conn.close()
        flash("Employee not found!", "danger")
        return redirect(url_for('index'))

    emp_id = employee['emp_id']
    receiver_email = employee['email']
    sender_email = request.form.get('sender_email', 'admin@maxworth.com').strip()
    subject = request.form.get('subject', f"Update for {employee['emp_name']}")
    body = request.form.get('body', "Please review your latest documents.")

    try:
        cursor.execute(
            "INSERT INTO employee_emails (emp_id, sender_email, receiver_email, subject, body, status) VALUES (%s, %s, %s, %s, %s, %s)",
            (emp_id, sender_email, receiver_email, subject, body, 'Sent')
        )
        conn.commit()
        flash(f"Email sent to {employee['emp_name']} ({receiver_email}) and logged successfully.", "success")
    except Exception as e:
        flash(f"Error logging email: {str(e)}", "danger")
    finally:
        conn.close()

    return redirect(url_for('employee_profile', id=id))

@app.route('/payslip/<int:id>')
def view_payslip(id):
    """Generates and displays a detailed salary slip for an employee, fetching from normalized tables and logs the transaction."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM employees WHERE id = %s", (id,))
    employee = cursor.fetchone()

    if not employee:
        conn.close()
        flash("Employee not found!", "danger")
        return redirect(url_for('index'))

    emp_id = employee['emp_id']

    # Fetch bank details
    cursor.execute("SELECT * FROM employee_bank_details WHERE emp_id = %s", (emp_id,))
    bank_row = cursor.fetchone() or {}

    # Fetch financial components
    cursor.execute("SELECT component_name, component_code, amount FROM employee_financial_components WHERE emp_id = %s", (emp_id,))
    financials = cursor.fetchall()
    conn.close()

    basic = float(employee.get('basic_salary', 0))
    allowances_data = []
    taxes_data = []
    
    for f in financials:
        if f['component_code'] == 1:
            allowances_data.append((f['component_name'], float(f['amount'])))
        elif f['component_code'] == 2:
            taxes_data.append((f['component_name'], float(f['amount'])))

    gross_salary = basic + sum(a for _, a in allowances_data)
    total_deductions = sum(t for _, t in taxes_data)
    net_salary = gross_salary - total_deductions
    net_salary_words = amount_to_words_rupees(net_salary)

    month_param = request.args.get('month', '').strip()
    year_param = request.args.get('year', '').strip()
    if month_param:
        salary_month = month_param
    else:
        try:
            salary_month = pd.to_datetime(employee['date']).strftime('%B')
        except Exception:
            salary_month = 'January'
    if year_param:
        salary_year = year_param
    else:
        try:
            salary_year = str(pd.to_datetime(employee['date']).year)
        except Exception:
            salary_year = '2017'
    payment_date = f"{salary_month} 28, {salary_year}"

    email_val = employee.get('email', '')
    if '@' in email_val:
        domain_name = email_val.split('@')[1].split('.')[0]
        company_name = f"{domain_name.upper()} ENTERPRISE SOLUTIONS"
    else:
        company_name = "MAXWORTH ENTERPRISE SOLUTIONS"

    # Human-readable label map
    allowance_labels = {
        'meal_allowance': 'Meal Allowance',
        'transportation_allowance': 'Transportation Allowance',
        'medical_allowance': 'Medical Allowance',
        'wife_allowance': 'Wife Allowance',
        'housing_allowance': 'Housing Allowance',
    }
    tax_labels = {
        'retirement_insurance': 'Retirement Insurance',
        'professional_tax': 'Professional Tax',
        'income_tax': 'Income Tax',
    }

    return render_template(
        'payslip.html',
        employee=employee,
        bank=bank_row,
        company_name=company_name,
        basic=basic,
        allowances_data=allowances_data,
        taxes_data=taxes_data,
        allowance_labels=allowance_labels,
        tax_labels=tax_labels,
        gross_salary=gross_salary,
        total_deductions=total_deductions,
        net_salary=net_salary,
        net_salary_words=net_salary_words,
        salary_month=salary_month,
        payment_date=payment_date
    )

@app.route('/data-dictionary')
def data_dictionary_page():
    """Displays a side-by-side view of live database preview and the Data Dictionary metadata."""
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

    base_query = """
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
    """

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

@app.route('/download/<path:filename>')
def download_report(filename):
    """Allows downloading the Word reports directly from the server."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return send_from_directory(base_dir, filename, as_attachment=True)


from flask import jsonify
from datetime import datetime

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
            
            # Generate dummy phone number if missing
            import random
            if not emp.get('phone_number'):
                random.seed(emp_id)
                emp['phone_number'] = "+91-" + "".join([str(random.randint(0, 9)) for _ in range(10)])
                
            # Generate dummy bank details if missing
            if not emp.get('bank_name'):
                random.seed(emp_id + "bank")
                banks = ["HDFC Bank", "ICICI Bank", "State Bank of India", "Axis Bank", "Kotak Mahindra"]
                b_name = random.choice(banks)
                emp['bank_name'] = b_name
                emp['bank_account_num'] = "".join([str(random.randint(0, 9)) for _ in range(12)])
                emp['ifsc_code'] = b_name[:4].upper().replace(" ", "") + "0" + "".join([str(random.randint(0, 9)) for _ in range(6)])
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

@app.route('/payslip_builder', methods=['GET', 'POST'])
def payslip_builder():
    """Interactive UI for generating and customizing a Payslip in real-time."""
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
                        """INSERT INTO payslip_master 
                           (payslip_no, emp_id, salary_month, salary_year, basic_salary, total_allowance, total_deduction, final_in_hand_salary) 
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
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
                                """INSERT INTO employee_financial_components
                                (emp_id, component_name, component_code, amount)
                                VALUES (%s, %s, %s, %s)""",
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
        
    selected_emp_id = request.args.get('selected_emp_id', '')
        
    return render_template('payslip_builder.html', employees=employees, selected_emp_id=selected_emp_id)


import io
from flask import send_file, jsonify

def find_column(columns_clean, df_cols, synonyms):
    for idx, col in enumerate(columns_clean):
        if col in synonyms:
            return df_cols[idx]
    return None

@app.route('/upload', methods=['POST'])
def upload_file():
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
        
        dup_handling = request.form.get('duplicate_handling', 'skip')
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
            
            seed = idx + 1000
            dyn_basic, dyn_bank, dyn_acc, dyn_ifsc, dyn_allowances, dyn_taxes = get_dynamic_payroll_and_bank(
                basic_val if basic_val > 0 else 45000.0, title_val, department_val, seed
            )
            
            if basic_val <= 0: basic_val = dyn_basic
            
            b_name = str(row[bank_name_col]).strip() if bank_name_col and not pd.isna(row[bank_name_col]) else dyn_bank
            b_acc = str(row[bank_acc_col]).strip() if bank_acc_col and not pd.isna(row[bank_acc_col]) else dyn_acc
            ifsc = str(row[ifsc_col]).strip() if ifsc_col and not pd.isna(row[ifsc_col]) else dyn_ifsc
            
            try:
                # Check if exists
                cursor.execute('SELECT id FROM employees WHERE emp_id = %s', (emp_id,))
                exists = cursor.fetchone()
                
                if exists:
                    if dup_handling in ['skip', 'insert_new']:
                        error_rows.append({"Row": idx+2, "Error": f"Skipped Duplicate Employee ID: {emp_id}"})
                        continue
                    elif dup_handling == 'update':
                        cursor.execute(
                            """UPDATE employees SET emp_name=%s, email=%s, date_of_birth=%s, joining_date=%s, basic_salary=%s,
                            age=%s, gender=%s, education=%s, title=%s, department=%s, posting_location=%s, payment_tier=%s
                            WHERE emp_id=%s""",
                            (emp_name, email, date_val, joining_val, basic_val, age_val, gender_val, education_val, title_val, department_val, posting_val, payment_tier_val, emp_id)
                        )
                        cursor.execute("UPDATE employee_bank_details SET bank_name=%s, bank_account_num=%s, ifsc_code=%s WHERE emp_id=%s", (b_name, b_acc, ifsc, emp_id))
                        success_count += 1
                        continue
                
                # Insert New
                cursor.execute(
                    """INSERT INTO employees (
                        emp_id, emp_name, email, date_of_birth, joining_date, basic_salary,
                        age, gender, education, title, department, posting_location, payment_tier
                    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (emp_id, emp_name, email, date_val, joining_val, basic_val, age_val, gender_val, education_val, title_val, department_val, posting_val, payment_tier_val)
                )
                cursor.execute(
                    """INSERT IGNORE INTO employee_bank_details (emp_id, bank_name, bank_account_num, ifsc_code) 
                    VALUES (%s,%s,%s,%s)""", (emp_id, b_name, b_acc, ifsc)
                )
                cursor.execute("""INSERT IGNORE INTO employee_holidays (emp_id, holiday_code) VALUES (%s, 0)""", (emp_id,))
                
                # Insert dynamic allowances and deductions if the CSV didn't have them
                for atype, amt in dyn_allowances:
                    cursor.execute("INSERT INTO employee_financial_components (emp_id, component_name, component_code, amount) VALUES (%s,%s,1,%s)", (emp_id, atype, amt))
                for ttype, amt in dyn_taxes:
                    cursor.execute("INSERT INTO employee_financial_components (emp_id, component_name, component_code, amount) VALUES (%s,%s,2,%s)", (emp_id, ttype, amt))
                    
                success_count += 1
            except pymysql.err.IntegrityError:
                error_rows.append({"Row": idx+2, "Error": f"Duplicate Error: {emp_id}"})
            except Exception as ex:
                error_rows.append({"Row": idx+2, "Error": str(ex)})
                
        conn.commit()
        conn.close()
        
        error_file_url = ""
        if error_rows:
            error_df = pd.DataFrame(error_rows)
            from datetime import datetime
            err_filename = f"error_report_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
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
    
    # Just return the empty template for importing
    columns = [
        'emp_id', 'emp_name', 'email', 'phone_number', 'date_of_birth', 
        'joining_date', 'basic_salary', 'age', 'gender', 'education', 
        'title', 'department', 'posting_location', 'payment_tier'
    ]
    import pandas as pd
    import io
    df = pd.DataFrame(columns=columns)
    
    if fmt == 'xlsx':
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Employees')
        output.seek(0)
        return send_file(output, as_attachment=True, download_name='employees_import_template.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    else:
        output = io.StringIO()
        df.to_csv(output, index=False)
        output.seek(0)
        return send_file(io.BytesIO(output.getvalue().encode()), as_attachment=True, download_name='employees_import_template.csv', mimetype='text/csv')

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

@app.route('/data_dictionary')
def data_dictionary():
    return render_template('data_dictionary.html')

@app.route('/financial_master')
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
        
    return redirect(url_for('financial_master'))


if __name__ == '__main__':
    # Only run database initialization in the main worker process when Flask's reloader is enabled
    # to avoid race conditions and deadlocks between parent and child processes.
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true' or not app.debug:
        init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
