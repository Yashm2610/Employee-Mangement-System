import json
import os
import tempfile
from playwright.sync_api import sync_playwright
import os
import string
import uuid
import random
import hashlib
import datetime
from functools import wraps
from flask import session
from werkzeug.security import check_password_hash, generate_password_hash

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

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def hr_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        if session.get('role') not in ['Admin', 'HR']:
            flash("Unauthorized access.", "danger")
            if session.get('role') == 'Employee':
                return redirect(url_for('employee_dashboard'))
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        if session.get('role') != 'Admin':
            flash("Admin privileges required.", "danger")
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

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
@hr_required
def index():
    """Displays the main interface with upload capabilities, manual entry, search, and sorting."""
    search_col = request.args.get('search_col', 'emp_name').strip()
    search_val = request.args.get('search_val', '').strip()
    sort_order = request.args.get('sort', 'id_asc')
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
            FROM v_employees e
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
                cursor.execute("SELECT COUNT(*) as cnt FROM v_employees")
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
                cursor.execute("SELECT COUNT(*) as cnt FROM v_employees")
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
@hr_required
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
            cursor.execute("SELECT COALESCE(MAX(id), 0) + 1 AS next_id FROM employees")
            next_emp_id = cursor.fetchone()['next_id']
            cursor.execute(
                """INSERT INTO employees (
                    id, emp_id, emp_name, email, date_of_birth, joining_date, basic_salary, allowances, deductions,
                    age, gender, education, title, department, posting_location, payment_tier
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (next_emp_id, emp_id, emp_name, email, date_of_birth, joining_date, basic_val, allowances_val, deductions_val,
                 age_val, gender_val, education_val, title_val, department_val, posting_location_val, payment_tier_val)
            )
            
            cursor.execute("SELECT COALESCE(MAX(id), 0) + 1 AS next_b_id FROM employee_bank_details")
            next_b_id = cursor.fetchone()['next_b_id']
            cursor.execute(
                "INSERT IGNORE INTO employee_bank_details (id, emp_id, bank_name, bank_account_num, ifsc_code, is_active) VALUES (%s,%s,%s,%s,%s,1)",
                (next_b_id, emp_id, bank_name_val, bank_account_num_val, ifsc_code_val)
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
@hr_required
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
@hr_required
def clear_records():
    """Helper route to clear all records from the database for easy testing."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE users SET employee_id = NULL")
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
@hr_required
def employee_profile(id):
    """Displays the comprehensive profile for an employee, including emails and payslip history."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM v_employees WHERE id = %s", (id,))
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
                           profile_chart_data=profile_chart_data, tenure_years=tenure_years, attendance=attendance_data, emails=email_logs[0] if email_logs else None)

@app.route('/send_email/<int:id>', methods=['POST'])
@hr_required
def send_email(id):
    """Simulates sending an email to the employee and logs it."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT emp_id, emp_name, email FROM v_employees WHERE id = %s", (id,))
    employee = cursor.fetchone()

    if not employee:
        conn.close()
        flash("Employee not found!", "danger")
        return redirect(url_for('index'))

    emp_id = employee['emp_id']
    receiver_email = employee['email']
    sender_email = request.form.get('sender_email', 'admin@hrsm.com').strip()
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
@hr_required
def view_payslip(id):
    """Generates and displays a detailed salary slip for an employee, fetching from normalized tables and logs the transaction."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM v_employees WHERE id = %s", (id,))
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
        company_name = "HRSM ENTERPRISE SOLUTIONS"

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
@hr_required
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
            FROM v_employees e
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
@hr_required
def download_report(filename):
    """Allows downloading the Word reports directly from the server."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return send_from_directory(base_dir, filename, as_attachment=True)


from flask import jsonify
from datetime import datetime

@app.route('/api/employee/<emp_id>')
@hr_required
def api_get_employee(emp_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Get employee basic + bank details
            cursor.execute('''
                SELECT e.*, b.bank_name, b.bank_account_num, b.ifsc_code 
                FROM v_employees e
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
                
            # Get company info
            cursor.execute('SELECT name, address FROM company_master LIMIT 1')
            company_info = cursor.fetchone()
            if company_info:
                emp['company_name'] = company_info.get('name', 'Maxworth')
                emp['company_address'] = company_info.get('address') or emp.get('posting_location', 'Head Office')
            else:
                emp['company_name'] = 'Maxworth'
                emp['company_address'] = emp.get('posting_location', 'Head Office')
                
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
            if 'basic_salary' in emp and emp['basic_salary'] is not None:
                emp['basic_salary'] = float(emp['basic_salary'])
                
            # Get financial components
            cursor.execute('SELECT * FROM employee_financial_components WHERE emp_id = %s', (emp_id,))
            components = cursor.fetchall()
            for c in components:
                if 'amount' in c and c['amount'] is not None:
                    c['amount'] = float(c['amount'])
            
            return jsonify({
                "employee": emp,
                "components": components
            })
    finally:
        conn.close()

@app.route('/payslip_builder_v1', methods=['GET', 'POST'])
@hr_required
def payslip_builder_legacy():
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
            cursor.execute("SELECT emp_id, emp_name, title FROM v_employees ORDER BY emp_name")
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

@app.route('/upload_verify', methods=['POST'])
@hr_required
def upload_verify():
    file = request.files.get('file') or request.files.get('csv_file')
    if not file:
        flash("No file part", "danger")
        return redirect(url_for('index'))
    if file.filename == '':
        flash("No selected file", "danger")
        return redirect(url_for('index'))
        
    ext = file.filename.split('.')[-1].lower()
    if ext not in ['csv', 'xlsx', 'xls']:
        flash("Invalid file type. Only CSV and Excel files are allowed.", "danger")
        return redirect(url_for('index'))
        
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    batch_id = str(uuid.uuid4())
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{batch_id}.{ext}")
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
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get max ID for auto-generation of EMP ID
        cursor.execute("SELECT COALESCE(MAX(id), 0) as max_id FROM employees")
        max_db_id = cursor.fetchone()
        current_max_id = max_db_id['max_id'] if isinstance(max_db_id, dict) else max_db_id[0]
        
        # Fetch existing to check duplicates
        cursor.execute("SELECT emp_id, email FROM employees")
        existing_data = cursor.fetchall()
        existing_emp_ids = {str(e['emp_id']).strip().lower() for e in existing_data}
        existing_emails = {str(e['email']).strip().lower() for e in existing_data if e['email']}
        
        # Get max id for upload_staging
        cursor.execute("SELECT COALESCE(MAX(id), 0) as max_s_id FROM upload_staging")
        max_s = cursor.fetchone()
        current_staging_id = max_s['max_s_id'] if isinstance(max_s, dict) else max_s[0]
        
        staging_records = []
        
        import json
        
        for idx, row in df.iterrows():
            current_max_id += 1
            current_staging_id += 1
            
            if id_col and id_col in row and not pd.isna(row[id_col]):
                emp_id = str(row[id_col]).strip()
            else:
                emp_id = f"EMP{current_max_id:05d}"
                
            if name_col and name_col in row and not pd.isna(row[name_col]):
                emp_name = str(row[name_col]).strip()
            else:
                emp_name = f"Employee {current_max_id}"
                
            if email_col and email_col in row and not pd.isna(row[email_col]):
                email = str(row[email_col]).strip()
            else:
                email = f"employee{current_max_id}@hrsm.com"
            
            # Determine status
            status = "NEW"
            if emp_id.lower() in existing_emp_ids or email.lower() in existing_emails:
                status = "EXISTING"
            
            # Simple invalid check (if name is completely missing)
            if not emp_name or emp_name == 'nan':
                status = "INVALID"
                
            # Convert row to dict for raw_json
            row_dict = {}
            for col in df.columns:
                val = row[col]
                row_dict[col] = str(val) if not pd.isna(val) else None
                
            raw_json = json.dumps(row_dict)
            
            staging_records.append((current_staging_id, batch_id, emp_id, emp_name, email, status, raw_json))
            
        # Insert into upload_staging
        if staging_records:
            cursor.executemany(
                "INSERT INTO upload_staging (id, upload_batch_id, employee_id, name, email, status, raw_json) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                staging_records
            )
            conn.commit()
            
    except Exception as e:
        flash(f"Error parsing file: {str(e)}", "danger")
        return redirect(url_for('index'))
    finally:
        if 'conn' in locals() and conn:
            conn.close()
    return jsonify({"success": True, "redirect": url_for('upload_verify_page', batch_id=batch_id)})

@app.route('/upload/verify/<batch_id>')
@hr_required
def upload_verify_page(batch_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM upload_staging WHERE upload_batch_id = %s ORDER BY id ASC", (batch_id,))
            staging_records = cursor.fetchall()
            
            if not staging_records:
                flash("Batch not found or already processed.", "warning")
                return redirect(url_for('index'))
                
            # For EXISTING records, fetch DB values for side-by-side
            existing_db = {}
            existing_ids = [r['employee_id'] for r in staging_records if r['status'] == 'EXISTING']
            
            if existing_ids:
                format_strings = ','.join(['%s'] * len(existing_ids))
                cursor.execute(f"SELECT * FROM v_employees WHERE emp_id IN ({format_strings})", tuple(existing_ids))
                db_recs = cursor.fetchall()
                for d in db_recs:
                    existing_db[d['emp_id']] = d
                    
    finally:
        conn.close()
        
    return render_template('verify_upload.html', records=staging_records, existing_db=existing_db, batch_id=batch_id)

@app.route('/upload_commit/<batch_id>', methods=['POST'])
@hr_required
def upload_commit(batch_id):
    data = request.json
    selected_ids = data.get('selected_ids', [])
    strategy = data.get('strategy', 'skip')
    
    if not selected_ids:
        return jsonify({"success": True, "message": "No records selected."})
        
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            format_strings = ','.join(['%s'] * len(selected_ids))
            cursor.execute(f"SELECT * FROM upload_staging WHERE id IN ({format_strings})", tuple(selected_ids))
            records_to_process = cursor.fetchall()
            
            # Implementation of insertions...
            # To keep it simple, we will insert / update.
            # (Actual full logic here)
            import json
            
            cursor.execute("SELECT COALESCE(MAX(id), 0) as max_id FROM employees")
            max_db_id = cursor.fetchone()
            current_max_id = max_db_id['max_id'] if isinstance(max_db_id, dict) else max_db_id[0]
            
            import random
            import datetime
            
            success_count = 0
            
            for r in records_to_process:
                status = r['status']
                emp_id = r['employee_id']
                raw = json.loads(r['raw_json'])
                
                # Dynamic fallback / parsing
                # Normalize keys for easier matching
                raw_lower = {k.lower().strip(): v for k, v in raw.items()}
                
                # Extraction helpers
                def get_val(keys, default):
                    for k in keys:
                        if k in raw_lower and raw_lower[k] is not None and str(raw_lower[k]).strip() != 'nan':
                            return raw_lower[k]
                    return default
                    
                # Parse or Generate Values
                age_val = int(float(get_val(['age', 'employee_age'], random.randint(22, 60))))
                
                # Generate a dynamic DOB based on age
                current_year = datetime.datetime.now().year
                dob_year = current_year - age_val
                dob_month = random.randint(1, 12)
                dob_day = random.randint(1, 28)
                date_of_birth = f"{dob_year}-{dob_month:02d}-{dob_day:02d}"
                
                join_year = get_val(['joiningyear', 'joining year', 'joining_year'], random.randint(2015, current_year))
                joining_date = f"{int(float(join_year))}-01-15"
                
                basic_salary = float(get_val(['basic_salary', 'salary', 'basicsalary'], random.randint(40000, 150000)))
                gender = get_val(['gender', 'sex'], random.choice(['Male', 'Female']))
                
                # Education: Randomly pick from BTech(1), MTech(2), PhD(3), BSc(4), MSc(5), BCA(6), MCA(7)
                edu_raw = str(get_val(['education', 'edu'], '')).lower()
                if edu_raw:
                    education_tier = 1
                    if 'master' in edu_raw or 'mtech' in edu_raw: education_tier = 2
                    elif 'phd' in edu_raw: education_tier = 3
                else:
                    education_tier = random.choice([1, 2, 3, 4, 5, 6, 7])
                
                title = get_val(['title', 'designation', 'role'], random.choice(['Software Engineer', 'Senior Developer', 'Data Analyst', 'HR Manager', 'Product Manager']))
                department = get_val(['department', 'dept', 'domain'], random.choice(['Software Development', 'Human Resources', 'Finance', 'Marketing', 'Sales']))
                posting_location = get_val(['posting_location', 'location', 'city'], random.choice(['Bangalore', 'Pune', 'Hyderabad', 'Mumbai', 'Delhi']))
                payment_tier = int(float(get_val(['payment_tier', 'paymenttier', 'tier'], random.randint(1, 3))))
                phone_number = get_val(['phone_number', 'phone', 'contact'], f"9{random.randint(100000000, 999999999)}")
                
                # FK Mappings (Optional mapping to Master Tables, if needed)
                # Ensure department_code, location_code, etc are populated if your system uses them.
                # Assuming simple insertion and we mapped them roughly or trigger handles it, or we insert into employees.
                
                # Check if exists
                cursor.execute("SELECT id FROM employees WHERE emp_id = %s", (emp_id,))
                exists = cursor.fetchone()
                
                if exists:
                    if strategy == 'skip' or strategy == 'insert_new':
                        continue
                    elif strategy == 'update':
                        cursor.execute("""
                            UPDATE employees SET 
                                emp_name=%s, email=%s, date_of_birth=%s, joining_date=%s, 
                                basic_salary=%s, age=%s, gender=%s, education=%s, 
                                title=%s, department=%s, posting_location=%s, payment_tier=%s, phone_number=%s
                            WHERE emp_id=%s
                        """, (r['name'], r['email'], date_of_birth, joining_date, basic_salary, age_val, gender, education_tier, title, department, posting_location, payment_tier, phone_number, emp_id))
                        success_count += 1
                else:
                    if strategy == 'update' or strategy == 'insert_new' or strategy == 'skip':
                        current_max_id += 1
                        cursor.execute("""
                            INSERT INTO employees (
                                id, emp_id, emp_name, email, date_of_birth, joining_date, 
                                basic_salary, age, gender, education, title, department, 
                                posting_location, payment_tier, phone_number
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (current_max_id, emp_id, r['name'], r['email'], date_of_birth, joining_date, basic_salary, age_val, gender, education_tier, title, department, posting_location, payment_tier, phone_number))
                        
                        # Generate Bank Details
                        bank_name = random.choice(['HDFC Bank', 'ICICI Bank', 'SBI', 'Axis Bank', 'Kotak Mahindra'])
                        acct_num = f"{random.randint(100000000000, 999999999999)}"
                        ifsc = f"{bank_name[:4].upper()}000{random.randint(1000, 9999)}"
                        pan = f"{''.join(random.choices(string.ascii_uppercase, k=5))}{random.randint(1000, 9999)}{random.choice(string.ascii_uppercase)}"
                        
                        cursor.execute("SELECT COALESCE(MAX(id), 0) FROM employee_bank_details")
                        b_max = cursor.fetchone()
                        next_b_id = (b_max[list(b_max.keys())[0]] if isinstance(b_max, dict) else b_max[0]) + 1
                        
                        cursor.execute("""
                            INSERT INTO employee_bank_details (
                                id, emp_id, bank_name, bank_account_num, ifsc_code, is_active
                            ) VALUES (%s, %s, %s, %s, %s, 1)
                        """, (next_b_id, emp_id, bank_name, acct_num, ifsc))
                        
                        # Generate Financial Components dynamically
                        components = [
                            ('Meal Allowance', 1, random.uniform(1000, 5000)),
                            ('Medical Allowance', 1, random.uniform(2000, 15000)),
                            ('Internet Allowance', 1, random.uniform(1000, 5000)),
                            ('House Rent Allowance', 1, random.uniform(5000, 25000)),
                            ('Transport Allowance', 1, random.uniform(2000, 10000)),
                            ('Special Allowance', 1, random.uniform(2000, 20000)),
                            ('Provident Fund', 2, random.uniform(1000, 10000)),
                            ('Insurance', 2, random.uniform(1000, 8000)),
                            ('Professional Tax', 2, random.uniform(500, 3000)),
                            ('Income Tax', 2, random.uniform(1000, 20000))
                        ]
                        
                        # Pick 6 to 9 random components for each employee
                        selected_components = random.sample(components, random.randint(6, 9))
                        
                        cursor.execute("SELECT COALESCE(MAX(id), 0) FROM employee_financial_components")
                        fc_max = cursor.fetchone()
                        next_fc_id = (fc_max[list(fc_max.keys())[0]] if isinstance(fc_max, dict) else fc_max[0]) + 1
                        
                        for comp_name, comp_code, base_amt in selected_components:
                            amt = round(base_amt * (basic_salary / 50000), 2)  # Scale roughly based on salary
                            if amt < 0: amt = 100.00
                            cursor.execute("""
                                INSERT INTO employee_financial_components (
                                    id, emp_id, component_name, component_code, amount, is_active
                                ) VALUES (%s, %s, %s, %s, %s, 1)
                            """, (next_fc_id, emp_id, comp_name, comp_code, amt))
                            next_fc_id += 1
                            
                        success_count += 1
                        
            # Clean up staging table
            cursor.execute("DELETE FROM upload_staging WHERE upload_batch_id = %s", (batch_id,))
            conn.commit()
            
            return jsonify({"success": True, "message": f"Successfully processed {success_count} records."})
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
    finally:
        conn.close()

@app.route('/export/employees')
@hr_required
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
@hr_required
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
@hr_required
def data_dictionary():
    return render_template('data_dictionary.html')

@app.route('/financial_master')
@hr_required
def financial_master():
    search_col = request.args.get('search_col', 'emp_name').strip()
    search_val = request.args.get('search_val', '').strip()
    tier = request.args.get('tier', 'all').strip()
    sort_order = request.args.get('sort', 'id_asc').strip()

    allowed_cols = {
        'emp_name': 'Employee Name',
        'emp_id': 'Employee ID',
        'bank_name': 'Bank Name',
        'bank_account_num': 'Bank Account',
        'ifsc_code': 'IFSC Code'
    }
    
    if search_col not in allowed_cols:
        search_col = 'emp_name'
        
    query = """
        SELECT e.emp_id, e.emp_name, e.basic_salary, e.joining_date, e.payment_tier,
               b.bank_name, b.bank_account_num, b.ifsc_code
        FROM v_employees e
        LEFT JOIN employee_bank_details b ON e.emp_id = b.emp_id
        WHERE 1=1
    """
    params = []
    
    if search_val:
        if search_col in ['emp_name', 'emp_id']:
            query += f" AND e.{search_col} LIKE %s"
        else:
            query += f" AND b.{search_col} LIKE %s"
        params.append(f"%{search_val}%")
        
    if tier != 'all':
        query += " AND e.payment_tier = %s"
        params.append(int(tier))
        
    if sort_order == 'date_asc':
        query += " ORDER BY e.joining_date ASC"
    elif sort_order == 'date_desc':
        query += " ORDER BY e.joining_date DESC"
    else:
        query += " ORDER BY e.emp_id ASC"
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
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
        
    return render_template('financial_master.html', 
                           employees=employees_data, 
                           emp_components=emp_components,
                           search_col=search_col,
                           search_val=search_val,
                           tier=tier,
                           sort=sort_order,
                           allowed_cols=allowed_cols)

@app.route('/update_employee_financials', methods=['POST'])
@hr_required
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



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identifier = request.form.get('identifier')
        password = request.form.get('password')
        
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE (username = %s OR email = %s) AND is_active = TRUE", (identifier, identifier))
                user = cursor.fetchone()
                
                if user and check_password_hash(user['password_hash'], password):
                    session['user_id'] = user['user_id']
                    session['username'] = user['username']
                    session['role'] = user['role']
                    session['employee_id'] = user['employee_id']
                    
                    # Log audit
                    ip_address = request.remote_addr
                    browser = request.user_agent.browser
                    device = request.user_agent.platform
                    cursor.execute("SELECT COALESCE(MAX(log_id), 0) + 1 AS next_id FROM user_login_logs")
                    new_log_id = cursor.fetchone()['next_id']
                    cursor.execute(
                        "INSERT INTO user_login_logs (log_id, user_id, ip_address, browser, device) VALUES (%s, %s, %s, %s, %s)",
                        (new_log_id, user['user_id'], ip_address, browser, device)
                    )
                    cursor.execute("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE user_id = %s", (user['user_id'],))
                    conn.commit()
                    
                    if user['role'] == 'Employee':
                        return redirect(url_for('employee_dashboard'))
                    return redirect(url_for('index'))
                else:
                    flash("Invalid credentials or account disabled.", "danger")
        finally:
            conn.close()
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Update logout time for the latest login log
            cursor.execute(
                "UPDATE user_login_logs SET logout_time = CURRENT_TIMESTAMP WHERE user_id = %s ORDER BY log_id DESC LIMIT 1",
                (session.get('user_id'),)
            )
            conn.commit()
    finally:
        conn.close()
    
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('login'))

@app.route('/users', methods=['GET', 'POST'])
@admin_required
def users():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            if request.method == 'POST':
                action = request.form.get('action')
                if action == 'create':
                    emp_id = request.form.get('employee_id')
                    username = request.form.get('username')
                    email = f"{username}@hrsm.com"
                    password = request.form.get('password')
                    role = request.form.get('role')
                    
                    pw_hash = generate_password_hash(password)
                    try:
                        cursor.execute("SELECT COALESCE(MAX(user_id), 0) + 1 AS next_id FROM users")
                        new_u_id = cursor.fetchone()['next_id']
                        cursor.execute(
                            "INSERT INTO users (user_id, employee_id, username, email, password_hash, role, is_active) VALUES (%s, %s, %s, %s, %s, %s, TRUE)",
                            (new_u_id, emp_id if emp_id else None, username, email, pw_hash, role)
                        )
                        conn.commit()
                        flash("User created successfully.", "success")
                    except Exception as e:
                        flash(f"Error creating user: {e}", "danger")
                
                elif action == 'toggle_status':
                    user_id = request.form.get('user_id')
                    cursor.execute("UPDATE users SET is_active = NOT is_active WHERE user_id = %s", (user_id,))
                    conn.commit()
                    flash("User status updated.", "success")
            
            cursor.execute("SELECT u.*, e.emp_name FROM users u LEFT JOIN employees e ON u.employee_id = e.emp_id")
            users_list = cursor.fetchall()
            
            import re
            for u in users_list:
                if not u['emp_name'] and u['email']:
                    # Extract from email
                    name_part = u['email'].split('@')[0]
                    name_part = re.sub(r'[0-9]', '', name_part).replace('.', ' ')
                    u['emp_name'] = name_part.title()
            
            
            cursor.execute("SELECT emp_id, emp_name FROM v_employees")
            employees_list = cursor.fetchall()
            
    finally:
        conn.close()
        
    return render_template('users.html', users=users_list, employees=employees_list)

@app.route('/employee/dashboard')
@login_required
def employee_dashboard():
    # Only employees or admins can view this (admins can view via the profile route, but if an admin goes here, it shows their linked profile if any)
    if session.get('role') not in ['Employee', 'Admin', 'HR']:
        return redirect(url_for('login'))
        
    emp_id = session.get('employee_id')
    if not emp_id:
        flash("No employee record linked to this account.", "danger")
        return redirect(url_for('login'))
        
    # We reuse the employee_profile logic but strict to emp_id
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM v_employees WHERE emp_id = %s", (emp_id,))
            employee = cursor.fetchone()
            
            if not employee:
                flash("Employee record not found.", "danger")
                return redirect(url_for('login'))
                
            cursor.execute("SELECT * FROM employee_bank_details WHERE emp_id = %s", (emp_id,))
            bank_details = cursor.fetchone()
            
            cursor.execute("SELECT * FROM employee_financial_components WHERE emp_id = %s", (emp_id,))
            financials = cursor.fetchall()
            allowances = [f for f in financials if f['component_code'] == 1]
            deductions = [f for f in financials if f['component_code'] == 2]
            
            cursor.execute("SELECT * FROM employee_emails WHERE emp_id = %s ORDER BY sent_at DESC", (emp_id,))
            emails = cursor.fetchall()
            
            cursor.execute("SELECT * FROM payslip_master WHERE emp_id = %s ORDER BY generated_on DESC", (emp_id,))
            payslips = cursor.fetchall()
            
            # Additional logic can be added if needed, matching employee_profile route
            basic_base = employee['basic_salary']
            _, _, _, _, calculated_allowances, calculated_taxes = get_dynamic_payroll_and_bank(
                basic_base, employee['title'], employee['department'], 
                int(employee['emp_id'].split('-')[1]) if '-' in employee['emp_id'] else 1
            )
            
            calculated_earn = sum(v for k, v in calculated_allowances)
            calculated_ded = sum(v for k, v in calculated_taxes)
            
            total_allowances_db = sum(float(a['amount']) for a in allowances) if allowances else calculated_earn
            total_deductions_db = sum(float(d['amount']) for d in deductions) if deductions else calculated_ded
            net_pay = float(basic_base) + total_allowances_db - total_deductions_db
            
            # Calculate tenure and attendance for template
            from datetime import datetime
            import random
            
            joining_date = employee['joining_date']
            if isinstance(joining_date, str):
                joining_date = datetime.strptime(joining_date, '%Y-%m-%d').date()
            
            today = datetime.now().date()
            tenure_days = (today - joining_date).days
            if tenure_days < 0: tenure_days = 0
            tenure_years = tenure_days / 365.25
            
            random.seed(emp_id + "attendance")
            total_working_days = int(tenure_days * 5 / 7)
            attendance_days = int(total_working_days * random.uniform(0.85, 0.98))
            attendance_score = (attendance_days / total_working_days * 100) if total_working_days > 0 else 100
            
            random.seed(emp_id + "performance")
            performance_score = random.uniform(3.5, 4.9)
            
            attendance_data = {
                'total': total_working_days,
                'present': attendance_days,
                'sick': 0,
                'casual': 0,
                'absent': total_working_days - attendance_days,
                'percentage': round(attendance_score, 1)
            }
            
            allowances_data = [(a['component_name'], a['amount']) for a in allowances]
            deductions_data = [(d['component_name'], d['amount']) for d in deductions]
            bank = bank_details or {}
            
            performance_labels = ['Q1', 'Q2', 'Q3', 'Q4']
            base_score = random.randint(70, 90)
            performance_scores = [
                min(100, max(0, base_score + random.randint(-5, 10))),
                min(100, max(0, base_score + random.randint(-5, 12))),
                min(100, max(0, base_score + random.randint(-3, 15))),
                min(100, max(0, base_score + random.randint(-2, 18)))
            ]
            
            profile_chart_data = {
                'holiday_labels': ['Present', 'Casual Leave', 'Sick Leave', 'Absent'],
                'holiday_counts': [attendance_days, 0, 0, total_working_days - attendance_days],
                'email_months': [],
                'email_counts': [],
                'performance_labels': performance_labels,
                'performance_scores': performance_scores
            }
            
            if not emails:
                emails_stats = {
                    'emails_sent': random.randint(20, 150),
                    'emails_received': random.randint(10, 80),
                    'avg_response_time': round(random.uniform(1.5, 4.2), 1),
                    'last_activity': today.strftime('%Y-%m-%d %H:%M')
                }
                # Generate some mock email logs for the history modal
                from datetime import datetime, timedelta
                now = datetime.now()
                mock_logs = []
                for i in range(5):
                    sent = now - timedelta(days=random.randint(1, 30), hours=random.randint(1, 23))
                    has_reply = random.choice([True, False])
                    if has_reply:
                        resp_hours = random.uniform(0.5, 48.0)
                        replied = sent + timedelta(hours=resp_hours)
                    else:
                        resp_hours = 0
                        replied = None
                        
                    mock_logs.append({
                        'subject': random.choice(['Project Update', 'Leave Request', 'Weekly Report', 'Client Feedback']),
                        'receiver_email': f"contact{i+1}@example.com",
                        'sent_at': sent,
                        'response_received_at': replied,
                        'avg_response': f"{round(resp_hours, 1)} hrs" if has_reply else "N/A"
                    })
                emails = mock_logs
            else:
                emails_stats = emails[0]

    finally:
        conn.close()
        
    return render_template('employee_profile.html', 
                          employee=employee, 
                          bank=bank,
                          allowances_data=allowances_data,
                          deductions_data=deductions_data,
                          total_allowances=total_allowances_db,
                          total_deductions=total_deductions_db,
                          payroll_transactions=payslips,
                          email_logs=emails,
                          profile_chart_data=profile_chart_data,
                          tenure_years=max(1.0, tenure_years),
                          attendance=attendance_data,
                          emails=emails_stats,
                          is_employee_dashboard=True)



# --- ENTERPRISE PAYSLIP DESIGNER ROUTES ---

@app.route('/payslip_builder')
@hr_required
def payslip_builder():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT emp_id, emp_name FROM employees")
    employees = cursor.fetchall()
    conn.close()
    return render_template('payslip_designer.html', employees=employees)

@app.route('/api/fields/discover', methods=['GET'])
@hr_required
def api_discover_fields():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    tables = [
        'employees', 'employee_bank_details', 'employee_financial_components',
        'department_master', 'designation_master'
    ]
    
    schema = {}
    for table in tables:
        try:
            cursor.execute(f"SHOW COLUMNS FROM {table}")
            columns = [row['Field'] for row in cursor.fetchall()]
            schema[table] = columns
        except Exception as e:
            pass
            
    conn.close()
    return jsonify(schema)

@app.route('/api/templates', methods=['GET', 'POST'])
@hr_required
def api_templates():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'GET':
        cursor.execute("SELECT * FROM payslip_templates ORDER BY updated_at DESC")
        templates = cursor.fetchall()
        for t in templates:
            t['created_at'] = t['created_at'].isoformat() if t['created_at'] else None
            t['updated_at'] = t['updated_at'].isoformat() if t['updated_at'] else None
        conn.close()
        return jsonify(templates)
        
    if request.method == 'POST':
        data = request.json
        template_name = data.get('template_name', 'Untitled')
        layout_json = json.dumps(data.get('layout_json', {}))
        status = data.get('status', 'Draft')
        
        cursor.execute(
            "INSERT INTO payslip_templates (template_name, layout_json, status) VALUES (%s, %s, %s)",
            (template_name, layout_json, status)
        )
        template_id = cursor.lastrowid
        
        cursor.execute(
            "INSERT INTO payslip_template_versions (template_id, version_number, published_by, layout_json) VALUES (%s, %s, %s, %s)",
            (template_id, 1, session.get('user_id'), layout_json)
        )
        cursor.execute(
            "INSERT INTO payslip_template_audit_log (template_id, version_number, action_type, user_id) VALUES (%s, %s, %s, %s)",
            (template_id, 1, 'Create', session.get('user_id'))
        )
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'template_id': template_id})

@app.route('/api/preview-data', methods=['GET'])
@hr_required
def api_preview_data():
    emp_id = request.args.get('emp_id')
    month = request.args.get('month')
    year = request.args.get('year')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM v_employees WHERE emp_id = %s", (emp_id,))
    employee = cursor.fetchone() or {}
    
    cursor.execute("SELECT * FROM employee_bank_details WHERE emp_id = %s", (emp_id,))
    bank = cursor.fetchone() or {}
    
    cursor.execute("SELECT * FROM employee_financial_components WHERE emp_id = %s", (emp_id,))
    financials = cursor.fetchall()
    
    allowances = [f for f in financials if f['component_code'] == 1]
    deductions = [f for f in financials if f['component_code'] == 2]
    
    conn.close()
    
    preview_data = {
        'employees': employee,
        'employee_bank_details': bank,
        'employee_financial_components': financials,
        'allowances': allowances,
        'deductions': deductions
    }
    
    def serialize_val(val):
        from datetime import date, datetime
        from decimal import Decimal
        if isinstance(val, (date, datetime)): return val.isoformat()
        if isinstance(val, Decimal): return float(val)
        return val
        
    def walk_dict(d):
        for k, v in d.items():
            if isinstance(v, dict): walk_dict(v)
            elif isinstance(v, list): 
                for item in v:
                    if isinstance(item, dict): walk_dict(item)
            else:
                d[k] = serialize_val(v)
                
    walk_dict(preview_data)
    return jsonify(preview_data)

@app.route('/api/generate-payslip-pdf', methods=['POST'])
@hr_required
def api_generate_payslip_pdf():
    data = request.json
    html_content = data.get('html_content')
    template_id = data.get('template_id')
    
    if not html_content:
        return jsonify({'success': False, 'error': 'No HTML content provided'})
        
    try:
        fd, temp_pdf_path = tempfile.mkstemp(suffix='.pdf')
        os.close(fd)
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_content(html_content, wait_until="networkidle")
            page.pdf(path=temp_pdf_path, format="A4", print_background=True)
            browser.close()
        
        if template_id:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO payslip_template_audit_log (template_id, action_type, user_id) VALUES (%s, %s, %s)",
                (template_id, 'Generate PDF', session.get('user_id'))
            )
            conn.commit()
            conn.close()
            
        return send_file(temp_pdf_path, as_attachment=True, download_name='Payslip.pdf')
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})



@app.route('/api/v1/templates/validate', methods=['POST'])
@hr_required
def api_template_validate():
    data = request.json
    html_content = data.get('layout_html', '')
    formulas = data.get('formulas', {})
    
    warnings = []
    errors = []
    
    if 'undefined' in html_content or 'null' in html_content:
        warnings.append('Template contains undefined data bindings.')
        
    for key, expr in formulas.items():
        if '/' in expr and '0' in expr:
            errors.append(f'Formula error in {key}: Potential division by zero.')
            
    if html_content.count('<tr') > 25:
        warnings.append('Table row count might exceed A4 page boundaries.')
        
    return jsonify({
        'valid': len(errors) == 0, 
        'errors': errors, 
        'warnings': warnings
    })

if __name__ == '__main__':
    # Only run database initialization in the main worker process when Flask's reloader is enabled
    # to avoid race conditions and deadlocks between parent and child processes.
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true' or not app.debug:
        init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
