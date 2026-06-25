import json
import os
import tempfile
from playwright.sync_api import sync_playwright
import os
import string
import os
import json
from datetime import datetime, date
import calendar
import pymysql.cursors
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

@app.template_filter('inr_format')
def inr_format(value):
    try:
        value = float(value)
        is_negative = value < 0
        value = abs(value)
        s, *d = str(f"{value:.2f}").partition(".")
        if len(s) > 3:
            s_head = s[:-3]
            s_tail = s[-3:]
            r = ""
            while len(s_head) > 2:
                r = "," + s_head[-2:] + r
                s_head = s_head[:-2]
            r = s_head + r + "," + s_tail
        else:
            r = s
        res = "".join([r] + d)
        return "-" + res if is_negative else res
    except (ValueError, TypeError):
        return value

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
            cursor.execute("SHOW COLUMNS FROM Employee LIKE 'city'")
            if cursor.fetchone():
                try:
                    cursor.execute("ALTER TABLE Employee CHANGE city posting_location VARCHAR(100) DEFAULT 'Bangalore'")
                except Exception as e:
                    pass
            
            # Rename date -> date_of_birth
            cursor.execute("SHOW COLUMNS FROM Employee LIKE 'date'")
            if cursor.fetchone():
                try:
                    cursor.execute("ALTER TABLE Employee CHANGE date date_of_birth DATE NOT NULL")
                except Exception as e:
                    pass
                    
            # Drop obsolete columns
            obsolete_cols = ['directorate', 'joining_year', 'ever_benched', 'experience_in_current_domain', 'leave_or_not', 'allowances', 'deductions']
            for col in obsolete_cols:
                cursor.execute("SHOW COLUMNS FROM Employee LIKE %s", (col,))
                if cursor.fetchone():
                    try:
                        cursor.execute(f"ALTER TABLE Employee DROP COLUMN {col}")
                    except Exception as e:
                        pass
                        
            # Ensure joining_date exists
            cursor.execute("SHOW COLUMNS FROM Employee LIKE 'joining_date'")
            if not cursor.fetchone():
                try:
                    cursor.execute("ALTER TABLE Employee ADD COLUMN joining_date DATE NOT NULL DEFAULT '2023-01-01'")
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
            cursor.execute("SHOW COLUMNS FROM Employee_Allowance LIKE 'code'")
            if cursor.fetchone():
                try:
                    cursor.execute("ALTER TABLE Employee_Allowance CHANGE code component_code TINYINT NOT NULL COMMENT '1 for Allowance, 2 for Deduction'")
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
            cursor.execute("SHOW COLUMNS FROM Salary_Payslip LIKE 'generated_at'")
            if cursor.fetchone():
                try:
                    cursor.execute("ALTER TABLE Salary_Payslip CHANGE generated_at generated_on DATETIME DEFAULT CURRENT_TIMESTAMP")
                except Exception as e:
                    pass

            # Create salary_overrides table for Salary Master per-month edits
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS salary_overrides (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    emp_id VARCHAR(50) NOT NULL,
                    month_num TINYINT NOT NULL,
                    year_num SMALLINT NOT NULL,
                    working_days INT DEFAULT NULL,
                    present_days FLOAT DEFAULT NULL,
                    basic_override FLOAT DEFAULT NULL,
                    hra_override FLOAT DEFAULT NULL,
                    sa_override FLOAT DEFAULT NULL,
                    meal_override FLOAT DEFAULT NULL,
                    medical_override FLOAT DEFAULT NULL,
                    conveyance_override FLOAT DEFAULT NULL,
                    pf_override FLOAT DEFAULT NULL,
                    esic_override FLOAT DEFAULT NULL,
                    tds_override FLOAT DEFAULT NULL,
                    advance_override FLOAT DEFAULT NULL,
                    other_dedn_override FLOAT DEFAULT NULL,
                    super_annuation_override FLOAT DEFAULT NULL,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    UNIQUE KEY uq_emp_month_year (emp_id, month_num, year_num)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)

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
                            """INSERT INTO Employee (
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
                            """INSERT INTO Employee (
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
                            cursor.execute("INSERT INTO Employee_Allowance (emp_id, component_name, component_code, amount) VALUES (%s,%s,1,%s)", (details['emp_id'], atype, amt))
                        for ttype, amt in details['taxes_list']:
                            cursor.execute("INSERT INTO Employee_Allowance (emp_id, component_name, component_code, amount) VALUES (%s,%s,2,%s)", (details['emp_id'], ttype, amt))
                        
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
                            """INSERT INTO Employee (
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
                            """INSERT INTO Employee (
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
            cursor.execute("SELECT COALESCE(MAX(id), 0) + 1 AS next_id FROM Employee")
            next_emp_id = cursor.fetchone()['next_id']
            cursor.execute(
                """INSERT INTO Employee (
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
                    "INSERT INTO Employee_Allowance (emp_id, component_name, code, amount) VALUES (%s,%s,%s,%s)",
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
            cursor.execute("DELETE FROM Employee WHERE id = %s", (id,))
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
            cursor.execute("DELETE FROM Employee")
            cursor.execute("DELETE FROM employee_bank_details")
            cursor.execute("DELETE FROM Employee_Allowance")
            cursor.execute("DELETE FROM Salary_Payslip")
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
    cursor.execute("SELECT * FROM Employee_Allowance WHERE emp_id = %s", (emp_id,))
    financials = cursor.fetchall()
    
    allowances_data = []
    deductions_data = []
    for f in financials:
        if f['component_code'] == 1:
            allowances_data.append((f['component_name'], f['amount']))
        elif f['component_code'] == 2:
            deductions_data.append((f['component_name'], f['amount']))

    # Fetch payslip transactions
    cursor.execute("SELECT * FROM Salary_Payslip WHERE emp_id = %s ORDER BY generated_on DESC", (emp_id,))
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
    
    if not email_logs:
        emails_stats = {
            'emails_sent': random.randint(20, 150),
            'emails_received': random.randint(10, 80),
            'avg_response_time': round(random.uniform(1.5, 4.2), 1),
            'last_activity': today.strftime('%Y-%m-%d %H:%M')
        }
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
        email_logs = mock_logs
        emails_to_pass = emails_stats
    else:
        emails_to_pass = email_logs[0]

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
                           profile_chart_data=profile_chart_data, tenure_years=max(1.0, tenure_years), attendance=attendance_data, emails=emails_to_pass)

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
    """Generates and displays a detailed salary slip for an employee.
    If a salary_override exists for the requested month/year, those values are used.
    Otherwise falls back to the employee's base financial components.
    """
    import calendar as cal_mod
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM v_employees WHERE id = %s", (id,))
    employee = cursor.fetchone()

    if not employee:
        conn.close()
        flash("Employee not found!", "danger")
        return redirect(url_for('index'))

    emp_id = employee['emp_id']

    # Resolve month/year params
    now = datetime.now()
    try:
        month_num = int(request.args.get('month_num', now.month))
    except (ValueError, TypeError):
        month_num = now.month
    try:
        year_num = int(request.args.get('year_num', now.year))
    except (ValueError, TypeError):
        year_num = now.year

    month_name_param = request.args.get('month', '').strip()
    year_param = request.args.get('year', '').strip()

    salary_month = month_name_param if month_name_param else datetime(year_num, month_num, 1).strftime('%B')
    salary_year = year_param if year_param else str(year_num)
    payment_date = f"{salary_month} 28, {salary_year}"

    # Fetch bank details
    cursor.execute("SELECT * FROM employee_bank_details WHERE emp_id = %s", (emp_id,))
    bank_row = cursor.fetchone() or {}

    # Fetch leave balances
    cursor.execute("SELECT cl_balance, el_balance, sl_balance FROM employee_leave_balances WHERE emp_id = %s", (emp_id,))
    leave_row = cursor.fetchone() or {}

    # Check for Salary Master override for this month/year
    cursor.execute(
        "SELECT * FROM Salary_Payslip WHERE emp_id = %s AND month_num = %s AND year_num = %s",
        (emp_id, month_num, year_num)
    )
    override = cursor.fetchone()

    # Fetch base financial components
    cursor.execute("SELECT component_name, component_code, amount FROM Employee_Allowance WHERE emp_id = %s", (emp_id,))
    financials = cursor.fetchall()

    # Fetch attendance
    cursor.execute(
        "SELECT total_days, present_days FROM employee_monthly_attendance WHERE emp_id = %s AND month_num = %s AND year_num = %s LIMIT 1",
        (emp_id, month_num, year_num)
    )
    attendance = cursor.fetchone()
    conn.close()

    base_basic = float(employee.get('basic_salary', 0) or 0)

    # Build component dicts from DB
    comp_dict = {}
    for f in financials:
        comp_dict[f['component_name'].lower()] = (f['component_code'], float(f['amount'] or 0))

    # Helper to get base component value
    def get_comp(keys, default=0.0):
        for k in keys:
            if k in comp_dict:
                return comp_dict[k][1]
        return default

    # Use overrides if they exist, else compute from base components
    if override:
        basic = override['basic_override'] if override['basic_override'] is not None else base_basic
        hra   = override['hra_override']   if override['hra_override']   is not None else get_comp(['house rent allowance', 'hra'], base_basic * 0.40)
        sa    = override['sa_override']    if override['sa_override']    is not None else get_comp(['special allowance', 'sa'], base_basic * 0.20)
        meal  = override['meal_override']  if override['meal_override']  is not None else get_comp(['meal allowance', 'meal_allowance'], 0.0)
        med   = override['medical_override'] if override['medical_override'] is not None else get_comp(['medical allowance', 'medical_allowance'], 0.0)
        conv  = override['conveyance_override'] if override['conveyance_override'] is not None else get_comp(['conveyance', 'transport allowance'], 0.0)
        pf    = override['pf_override']    if override['pf_override']    is not None else get_comp(['provident fund', 'pf'], min(basic * 0.12, 1800.0))
        esic  = override['esic_override']  if override['esic_override']  is not None else get_comp(['esi', 'insurance'], 0.0)
        tds   = override['tds_override']   if override['tds_override']   is not None else get_comp(['income tax', 'tds'], 0.0)
        advance = override['advance_override'] if override['advance_override'] is not None else get_comp(['advance', 'loan'], 0.0)
        other_dedn = override['other_dedn_override'] if override['other_dedn_override'] is not None else get_comp(['other deduction'], 0.0)
        super_ann = override['super_annuation_override'] if override['super_annuation_override'] is not None else get_comp(['super annuation'], 0.0)

        w_days = override['working_days'] or 26
        p_days = override['present_days'] or w_days
        factor = (p_days / w_days) if w_days > 0 else 1.0

        # Prorate all values
        basic = round(basic * factor, 2)
        hra   = round(hra * factor, 2)
        sa    = round(sa * factor, 2)
        meal  = round(meal * factor, 2)
        med   = round(med * factor, 2)
        conv  = round(conv * factor, 2)
        pf    = round(pf * factor, 2)
        esic  = round(esic * factor, 2)
        tds   = round(tds * factor, 2)
        advance = round(advance * factor, 2)
        other_dedn = round(other_dedn * factor, 2)
        super_ann = round(super_ann * factor, 2)
    else:
        _, days_in_month = cal_mod.monthrange(year_num, month_num)
        w_off = sum(1 for d in range(1, days_in_month + 1) if datetime(year_num, month_num, d).weekday() >= 5)
        w_days = days_in_month - w_off

        if attendance:
            p_days = attendance['present_days']
        else:
            p_days = w_days

        basic = base_basic
        hra   = get_comp(['house rent allowance', 'hra'], base_basic * 0.40)
        sa    = get_comp(['special allowance', 'sa'], base_basic * 0.20)
        meal  = get_comp(['meal allowance', 'meal_allowance'], 0.0)
        med   = get_comp(['medical allowance', 'medical_allowance'], 0.0)
        conv  = get_comp(['conveyance', 'transport allowance'], 0.0)
        pf    = get_comp(['provident fund', 'pf'], min(base_basic * 0.12, 1800.0))
        esic  = get_comp(['esi', 'insurance'], 0.0)
        tds   = get_comp(['income tax', 'tds'], 0.0)
        advance = get_comp(['advance', 'loan'], 0.0)
        other_dedn = get_comp(['other deduction'], 0.0)
        super_ann  = get_comp(['super annuation'], 0.0)

    allowances_data = [
        ('Basic', basic),
        ('House Rent Allowance', hra),
        ('Special Allowance', sa),
    ]
    if meal:  allowances_data.append(('Meal Allowance', meal))
    if med:   allowances_data.append(('Medical Allowance', med))
    if conv:  allowances_data.append(('Conveyance', conv))

    taxes_data = []
    # Always include PF, ESIC, TDS, and Advance, even if 0
    taxes_data.append(('Provident Fund', pf))
    taxes_data.append(('ESIC', esic))
    taxes_data.append(('TDS / Income Tax', tds))
    taxes_data.append(('Advance / Loan', advance))
    if other_dedn: taxes_data.append(('Other Deduction', other_dedn))
    if super_ann:  taxes_data.append(('Super Annuation', super_ann))

    gross_salary = sum(a for _, a in allowances_data)
    total_deductions = sum(t for _, t in taxes_data)
    net_salary = gross_salary - total_deductions
    net_salary_words = amount_to_words_rupees(net_salary)

    email_val = employee.get('email', '')
    if '@' in email_val:
        domain_name = email_val.split('@')[1].split('.')[0]
        company_name = f"{domain_name.upper()} ENTERPRISE SOLUTIONS"
    else:
        company_name = "HRSM ENTERPRISE SOLUTIONS"

    allowance_labels = {}
    tax_labels = {}

    return render_template(
        'payslip.html',
        employee=employee,
        bank=bank_row,
        company_name=company_name,
        basic=basic,
        allowances_data=[(lbl, amt) for lbl, amt in allowances_data if lbl != 'Basic'],
        taxes_data=taxes_data,
        allowance_labels=allowance_labels,
        tax_labels=tax_labels,
        gross_salary=gross_salary,
        total_deductions=total_deductions,
        net_salary=net_salary,
        net_salary_words=net_salary_words,
        salary_month=salary_month,
        payment_date=payment_date,
        w_days=w_days,
        p_days=p_days,
        cl_balance=leave_row.get('cl_balance', 0),
        el_balance=leave_row.get('el_balance', 0),
        sl_balance=leave_row.get('sl_balance', 0)
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
                FROM Employee_Allowance 
                WHERE component_code = 1 
                GROUP BY emp_id
            ) a ON e.emp_id = a.emp_id
            LEFT JOIN (
                SELECT emp_id, SUM(amount) AS total_deductions 
                FROM Employee_Allowance 
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


from flask import jsonify, request
from datetime import datetime

@app.route('/api/templates/save', methods=['POST'])
@hr_required
def api_save_template():
    data = request.json
    t_name = data.get('template_name')
    t_json = data.get('layout_json')
    
    if not t_name or not t_json:
        return jsonify({'success': False, 'error': 'Missing data'}), 400
        
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                INSERT INTO Payslip_format (template_name, layout_json, Cname, CreatedBy)
                VALUES (%s, %s, %s, %s)
            ''', (t_name, t_json, current_user.username, current_user.username))
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/templates/load', methods=['GET'])
@hr_required
def api_load_templates():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT template_id, template_name, layout_json FROM Payslip_format WHERE IActive=1')
            templates = cursor.fetchall()
            return jsonify({'success': True, 'templates': templates})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/employee/<emp_id>')
@hr_required
def api_get_employee(emp_id):
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Get employee basic + bank details + leave balances
            cursor.execute('''
                SELECT e.*, b.bank_name, b.bank_account_num, b.ifsc_code,
                       l.cl_balance, l.el_balance, l.sl_balance, l.coff_balance
                FROM v_employees e
                LEFT JOIN employee_bank_details b ON e.emp_id = b.emp_id
                LEFT JOIN employee_leave_balances l ON e.emp_id = l.emp_id
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
            
            # Fetch attendance
            if month and year:
                cursor.execute('''
                    SELECT total_days, present_days FROM employee_monthly_attendance 
                    WHERE emp_id = %s AND month_num = %s AND year_num = %s LIMIT 1
                ''', (emp_id, month, year))
            else:
                cursor.execute('''
                    SELECT total_days, present_days FROM employee_monthly_attendance 
                    WHERE emp_id = %s ORDER BY year_num DESC, month_num DESC LIMIT 1
                ''', (emp_id,))
            attendance = cursor.fetchone()
            if attendance:
                emp['month_days'] = attendance['total_days']
                emp['paid_days'] = float(attendance['present_days'])
            else:
                emp['month_days'] = 31 if not month else calendar.monthrange(year, month)[1]
                emp['paid_days'] = 0.0


            # Get company info
            cursor.execute('SELECT name, address FROM Company LIMIT 1')
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
            cursor.execute('SELECT * FROM Employee_Allowance WHERE emp_id = %s', (emp_id,))
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
                    cursor.execute("SELECT COUNT(*) as count FROM Salary_Payslip")
                    count = cursor.fetchone()['count'] + 1
                    payslip_no = f"PSL-{salary_year}-{str(count).zfill(5)}"
                    
                    # Insert into payslip_master
                    cursor.execute(
                        """INSERT INTO Salary_Payslip 
                           (payslip_no, emp_id, salary_month, salary_year, basic_salary, total_allowance, total_deduction, final_in_hand_salary) 
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                        (payslip_no, emp_id, salary_month, salary_year, basic_salary, total_allowance, total_deduction, final_in_hand_salary)
                    )
                    
                    # Delete existing components to replace them with the new generated ones
                    cursor.execute("DELETE FROM Employee_Allowance WHERE emp_id = %s", (emp_id,))
                    
                    # Insert dynamic components into employee_financial_components
                    for i in range(len(comp_names)):
                        name = comp_names[i].strip()
                        code = int(comp_codes[i]) if i < len(comp_codes) else 1
                        amt = float(comp_amounts[i]) if i < len(comp_amounts) else 0.0
                        if name:
                            cursor.execute(
                                """INSERT INTO Employee_Allowance
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
        cursor.execute("SELECT COALESCE(MAX(id), 0) as max_id FROM Employee")
        max_db_id = cursor.fetchone()
        current_max_id = max_db_id['max_id'] if isinstance(max_db_id, dict) else max_db_id[0]
        
        # Fetch existing to check duplicates
        cursor.execute("SELECT emp_id, email FROM Employee")
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
            
            cursor.execute("SELECT COALESCE(MAX(id), 0) as max_id FROM Employee")
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
                join_month = random.randint(1, 12)
                join_day = random.randint(1, 28)
                joining_date = f"{int(float(join_year))}-{join_month:02d}-{join_day:02d}"
                
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
                cursor.execute("SELECT id FROM Employee WHERE emp_id = %s", (emp_id,))
                exists = cursor.fetchone()
                
                if exists:
                    if strategy == 'skip' or strategy == 'insert_new':
                        continue
                    elif strategy == 'update':
                        cursor.execute("""
                            UPDATE Employee SET 
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
                            INSERT INTO Employee (
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
                        
                        cursor.execute("SELECT COALESCE(MAX(id), 0) FROM Employee_Allowance")
                        fc_max = cursor.fetchone()
                        next_fc_id = (fc_max[list(fc_max.keys())[0]] if isinstance(fc_max, dict) else fc_max[0]) + 1
                        
                        for comp_name, comp_code, base_amt in selected_components:
                            amt = round(base_amt * (basic_salary / 50000), 2)  # Scale roughly based on salary
                            if amt < 0: amt = 100.00
                            cursor.execute("""
                                INSERT INTO Employee_Allowance (
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
        FROM Salary_Payslip p
        JOIN Employee e ON p.emp_id = e.emp_id
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
    from datetime import datetime
    import random, calendar
    
    search_col = request.args.get('search_col', 'emp_name').strip()
    search_val = request.args.get('search_val', '').strip()
    tier = request.args.get('tier', 'all').strip()
    sort_order = request.args.get('sort', 'id_asc').strip()
    
    now = datetime.now()
    try:
        month = int(request.args.get('month', now.month))
        year = int(request.args.get('year', now.year))
    except ValueError:
        month = now.month
        year = now.year

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
        SELECT e.emp_id, e.emp_name, e.basic_salary, e.joining_date, e.payment_tier, e.uan_number,
               b.bank_name, b.bank_account_num, b.ifsc_code,
               e.department, e.title,
               l.cl_balance, l.el_balance, l.sl_balance, l.coff_balance,
               a.total_days as db_total_days, a.present_days as db_present_days
        FROM v_employees e
        LEFT JOIN employee_bank_details b ON e.emp_id = b.emp_id
        LEFT JOIN employee_leave_balances l ON e.emp_id = l.emp_id
        LEFT JOIN employee_monthly_attendance a ON e.emp_id = a.emp_id AND a.month_num = %s AND a.year_num = %s
        WHERE 1=1
    """
    params = [month, year]
    
    if search_val:
        if search_col in ['emp_name', 'emp_id']:
            query += f" AND e.{search_col} LIKE %s"
        else:
            query += f" AND b.{search_col} LIKE %s"
        params.append(f"%{search_val}%")
        
    if tier != 'all':
        query += f" AND e.payment_tier = %s"
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
    
    # Calculate days in month
    _, days_in_month = calendar.monthrange(year, month)
    
    # Simple word converter
    def num2words(num):
        units = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen"]
        tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]
        if num < 20: return units[num]
        if num < 100: return tens[num // 10] + (" " + units[num % 10] if num % 10 != 0 else "")
        if num < 1000: return units[num // 100] + " Hundred" + (" and " + num2words(num % 100) if num % 100 != 0 else "")
        if num < 100000: return num2words(num // 1000) + " Thousand" + (" " + num2words(num % 1000) if num % 1000 != 0 else "")
        if num < 10000000: return num2words(num // 100000) + " Lakh" + (" " + num2words(num % 100000) if num % 100000 != 0 else "")
        return str(num)
    
    # Preload financial components for all fetched employees to avoid N+1 query problem
    emp_ids = [e['emp_id'] for e in employees_data]
    components_by_emp = {}
    if emp_ids:
        # Batch size for IN clause
        batch_size = 1000
        for i in range(0, len(emp_ids), batch_size):
            batch = emp_ids[i:i+batch_size]
            format_strings = ','.join(['%s'] * len(batch))
            cursor.execute(f"SELECT emp_id, component_name, amount FROM Employee_Allowance WHERE emp_id IN ({format_strings})", tuple(batch))
            for comp in cursor.fetchall():
                eid = comp['emp_id']
                if eid not in components_by_emp:
                    components_by_emp[eid] = {}
                components_by_emp[eid][comp['component_name'].lower()] = float(comp['amount'] or 0)
                
    enhanced_employees = []
    for emp in employees_data:
        emp_dict = dict(emp)
        emp_id_str = emp['emp_id']
        
        # Calculate joined condition
        join_date = emp['joining_date']
        if join_date and (join_date.year > year or (join_date.year == year and join_date.month > month)):
            total_days = 0
            payable_days = 0
        else:
            total_days = int(emp['db_total_days']) if emp['db_total_days'] is not None else days_in_month
            payable_days = float(emp['db_present_days']) if emp['db_present_days'] is not None else 0.0
            
        # Use exact DB Leave Balances
        emp_dict['sl_bal'] = float(emp['sl_balance'] or 0)
        emp_dict['cl_bal'] = float(emp['cl_balance'] or 0)
        emp_dict['el_bal'] = float(emp['el_balance'] or 0)
        emp_dict['coff_bal'] = float(emp['coff_balance'] or 0)
        
        # Base Components
        base_basic = float(emp['basic_salary']) if emp['basic_salary'] else 0.0
        
        # If base_basic is 0, let's mock it for demo based on tier
        if base_basic == 0.0:
            if emp['payment_tier'] == 1: base_basic = 50000.0
            elif emp['payment_tier'] == 2: base_basic = 30000.0
            else: base_basic = 15000.0
            
        comp_dict = components_by_emp.get(emp_id_str, {})
        base_hra = comp_dict.get('house rent allowance', comp_dict.get('hra', base_basic * 0.40))
        base_sa = comp_dict.get('special allowance', comp_dict.get('sa', base_basic * 0.20))
        base_gross = base_basic + base_hra + base_sa
        
        emp_dict['month_gross'] = base_gross
        emp_dict['month_basic'] = base_basic
        emp_dict['month_hra'] = base_hra
        emp_dict['month_sa'] = base_sa
        emp_dict['total_dys'] = payable_days
        
        # Prorated Components
        factor = 1.0
        
        final_basic = base_basic * factor
        final_hra = base_hra * factor
        final_sa = base_sa * factor
        final_gross = final_basic + final_hra + final_sa
        
        emp_dict['final_basic'] = final_basic
        emp_dict['final_hra'] = final_hra
        emp_dict['final_sa'] = final_sa
        emp_dict['final_gross'] = final_gross
        
        # Other Earnings
        emp_dict['arrier'] = comp_dict.get('arrear', comp_dict.get('arrears', 0.0)) * factor
        emp_dict['bonus'] = comp_dict.get('bonus', 0.0) * factor
        emp_dict['telephone'] = comp_dict.get('telephone', 0.0) * factor
        emp_dict['special_incentive'] = comp_dict.get('special incentive', 0.0) * factor
        emp_dict['meal_allowance'] = comp_dict.get('meal allowance', 0.0) * factor
        emp_dict['medical_allowance'] = comp_dict.get('medical allowance', 0.0) * factor
        emp_dict['conveyance'] = comp_dict.get('conveyance', comp_dict.get('transport allowance', 0.0)) * factor
        
        total_earning = final_gross + emp_dict['arrier'] + emp_dict['bonus'] + emp_dict['telephone'] + emp_dict['special_incentive'] + emp_dict['meal_allowance'] + emp_dict['medical_allowance'] + emp_dict['conveyance']
        emp_dict['total_earning'] = total_earning
        
        # Deductions
        base_pf = comp_dict.get('provident fund', comp_dict.get('pf', min(base_basic * 0.12, 1800.0) if base_basic > 0 else 0.0))
        pf = base_pf * factor
        
        base_esic = comp_dict.get('esi', comp_dict.get('insurance', base_gross * 0.0075 if base_gross <= 21000 and base_gross > 0 else 0.0))
        esic = base_esic * factor
        
        base_advance = comp_dict.get('advance', comp_dict.get('loan', 0.0))
        advance = base_advance * factor
        
        base_tds = comp_dict.get('income tax', comp_dict.get('tds', (base_gross * 0.05) if base_gross > 40000 else 0.0))
        tds = base_tds * factor
        
        base_other = comp_dict.get('other deduction', 0.0)
        other_dedn = base_other * factor
        
        base_super = comp_dict.get('super annuation', 0.0)
        super_annuation = base_super * factor
        
        total_dedn = pf + esic + advance + tds + other_dedn + super_annuation
        emp_dict['pf'] = pf
        emp_dict['esic'] = esic
        emp_dict['advance'] = advance
        emp_dict['tds'] = tds
        emp_dict['other_dedn'] = other_dedn
        emp_dict['super_annuation'] = super_annuation
        emp_dict['total_dedn'] = total_dedn
        
        # Net Salary
        net_salary = total_earning - total_dedn
        emp_dict['net_salary'] = net_salary
        
        # Employer Contributions (for CTC)
        pf_employer = pf
        esic_employer = total_earning * 0.0325 if total_earning <= 21000 and total_earning > 0 else 0.0
        basic_da_pf = final_basic # Using final basic
        ctc = total_earning + pf_employer + esic_employer
        
        emp_dict['pf_employer'] = pf_employer
        emp_dict['esic_employer'] = esic_employer
        emp_dict['basic_da_pf'] = basic_da_pf
        emp_dict['ctc'] = ctc
        
        # In words
        if net_salary > 0:
            emp_dict['net_salary_word'] = f"Rupees {num2words(int(net_salary))} Only"
        else:
            emp_dict['net_salary_word'] = "Zero"
            
        enhanced_employees.append(emp_dict)
        
    cursor.execute('SELECT * FROM Employee_Allowance')
    all_components = cursor.fetchall()
    
    emp_components = {}
    for comp in all_components:
        eid = comp['emp_id']
        if eid not in emp_components:
            emp_components[eid] = []
        emp_components[eid].append(dict(comp))
        
    conn.close()
    
    return render_template('financial_master.html', 
                           employees=enhanced_employees,
                           emp_components=emp_components,
                           search_col=search_col,
                           search_val=search_val,
                           tier=tier,
                           sort=sort_order,
                           allowed_cols=allowed_cols,
                           month=month,
                           year=year,
                           now=now)

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
        cursor.execute("UPDATE Employee SET basic_salary=%s WHERE emp_id=%s", (basic_salary, emp_id))
        
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
            
        cursor.execute("DELETE FROM Employee_Allowance WHERE emp_id=%s", (emp_id,))
        
        comp_names = request.form.getlist('component_name[]')
        comp_codes = request.form.getlist('component_code[]')
        comp_amounts = request.form.getlist('component_amount[]')
        
        for name, code, amt in zip(comp_names, comp_codes, comp_amounts):
            if name.strip() and amt.strip():
                cursor.execute("""
                    INSERT INTO Employee_Allowance (emp_id, component_name, component_code, amount)
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
                    cursor.execute(
                        "INSERT INTO user_login_logs (user_id, ip_address, browser, device) VALUES (%s, %s, %s, %s)",
                        (user['user_id'], ip_address, browser, device)
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
            
            cursor.execute("""
                SELECT u.*, e.emp_name FROM users u 
                LEFT JOIN Employee e ON u.employee_id = e.emp_id
                ORDER BY 
                    CASE 
                        WHEN u.role = 'Admin' THEN 1 
                        WHEN u.role = 'HR' THEN 2 
                        ELSE 3 
                    END, 
                    u.user_id ASC
            """)
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
            
            cursor.execute("SELECT * FROM Employee_Allowance WHERE emp_id = %s", (emp_id,))
            financials = cursor.fetchall()
            allowances = [f for f in financials if f['component_code'] == 1]
            deductions = [f for f in financials if f['component_code'] == 2]
            
            cursor.execute("SELECT * FROM employee_emails WHERE emp_id = %s ORDER BY sent_at DESC", (emp_id,))
            emails = cursor.fetchall()
            
            cursor.execute("SELECT * FROM Salary_Payslip WHERE emp_id = %s ORDER BY generated_on DESC", (emp_id,))
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
    cursor.execute("SELECT emp_id, emp_name FROM Employee")
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
        cursor.execute("SELECT * FROM Payslip_format ORDER BY updated_at DESC")
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
            "INSERT INTO Payslip_format (template_name, layout_json, status) VALUES (%s, %s, %s)",
            (template_name, layout_json, status)
        )
        template_id = cursor.lastrowid
        
        cursor.execute(
            "INSERT INTO Payslip_format_setting (template_id, version_number, published_by, layout_json) VALUES (%s, %s, %s, %s)",
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
    
    cursor.execute("SELECT * FROM Employee_Allowance WHERE emp_id = %s", (emp_id,))
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

@app.route('/attendance_master')
@hr_required
def attendance_master():
    from datetime import datetime
    import random, calendar
    
    search_col = request.args.get('search_col', 'emp_name').strip()
    search_val = request.args.get('search_val', '').strip()
    year = request.args.get('year', str(datetime.now().year))
    month = request.args.get('month', str(datetime.now().month))
    
    allowed_cols = {
        'emp_name': 'Employee Name',
        'emp_id': 'Employee ID'
    }
    
    if search_col not in allowed_cols:
        search_col = 'emp_name'
        
    query = """
        SELECT e.emp_id, e.emp_name, e.department, e.title, e.employment_type, e.joining_date,
               SUM(CASE WHEN a.status IN ('Present', '1') THEN 1 ELSE 0 END) as present_days,
               SUM(CASE WHEN a.status IN ('Absent', '2') THEN 1 ELSE 0 END) as absent_days,
               SUM(CASE WHEN a.status IN ('Leave', '3') THEN 1 ELSE 0 END) as leave_days,
               SUM(CASE WHEN a.status IN ('Half Day', '4') THEN 1 ELSE 0 END) as half_days
        FROM v_employees e
        LEFT JOIN employee_attendance a ON e.emp_id = a.emp_id 
             AND YEAR(a.attendance_date) = %s AND MONTH(a.attendance_date) = %s
        WHERE 1=1
    """
    params = [year, month]
    
    if search_val:
        query += f" AND e.{search_col} LIKE %s"
        params.append(f"%{search_val}%")
        
    query += " GROUP BY e.emp_id, e.emp_name, e.department, e.title, e.employment_type, e.joining_date ORDER BY e.emp_id ASC"
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    employees_data = cursor.fetchall()
    conn.close()
    
    enhanced_employees = []
    
    y, m = int(year), int(month)
    _, days_in_month = calendar.monthrange(y, m)
    
    # Calculate weekends in the month
    w_off = sum(1 for d in range(1, days_in_month + 1) if datetime(y, m, d).weekday() >= 5)
    working_days = days_in_month - w_off
    
    # Mocking standard holidays (1 per month max for simple mock)
    base_holiday = 1 if m in [1, 8, 10, 11, 12] else 0
    
    for emp in employees_data:
        emp_dict = dict(emp)
        emp_id_str = emp['emp_id']
        joining_date = emp['joining_date']
        
        if isinstance(joining_date, str):
            joining_date = datetime.strptime(joining_date, '%Y-%m-%d').date()
            
        emp_dict['joining_date_obj'] = joining_date
        
        # Check if joined after this month
        if joining_date and (joining_date.year > y or (joining_date.year == y and joining_date.month > m)):
            # Employee not yet joined
            emp_dict.update({
                'working_days': working_days,
                'present_days': 0,
                'w_off': w_off,
                'holiday': base_holiday,
                'sl_taken': 0, 'coff_taken': 0, 'cl_taken': 0, 'el_taken': 0, 'lwp': 0,
                'final_processed': 0,
                'late_cl': 'NA', 'late_el': 'NA', 'final_coff_month': 'NA',
                'last_sl': 'NA', 'sl_wo_dedn': 'NA',
                'last_cl': 'NA', 'cl_wo_dedn': 'NA',
                'last_el': 'NA', 'el_wo_dedn': 'NA',
                'coff_bal': '#VALUE!', 'sl_bal': '#VALUE!', 'cl_bal': '#VALUE!', 'el_bal': '#VALUE!'
            })
            enhanced_employees.append(emp_dict)
            continue
            
        random.seed(f"{emp_id_str}_{m}_{y}")
        
        holiday = base_holiday
        
        total_tracked = int(emp['present_days'] or 0) + int(emp['absent_days'] or 0) + int(emp['leave_days'] or 0) + int(emp['half_days'] or 0)
        
        # If no real data, mock total leaves/absents
        if total_tracked == 0:
            # Random mock between 0 and 5 total absence days
            total_unattended = random.randint(0, 5)
            present_days = working_days - total_unattended
        else:
            total_unattended = int(emp['absent_days'] or 0) + int(emp['leave_days'] or 0)
            present_days = int(emp['present_days'] or 0)
            
        # Split unattended into categories
        sl_taken = 0
        cl_taken = 0
        el_taken = 0
        coff_taken = 0
        lwp = 0
        
        # Distribute unattended
        rem = total_unattended
        if rem > 0:
            sl_taken = random.randint(0, min(2, rem))
            rem -= sl_taken
        if rem > 0:
            cl_taken = random.randint(0, min(2, rem))
            rem -= cl_taken
        if rem > 0:
            el_taken = random.randint(0, min(1, rem))
            rem -= el_taken
        if rem > 0:
            coff_taken = random.randint(0, min(1, rem))
            rem -= coff_taken
        lwp = rem
        
        late_cl = 0
        late_el = 0
        
        # Mock last month balances
        last_sl = random.randint(1, 10)
        last_cl = random.randint(1, 10)
        last_el = random.randint(5, 30)
        last_coff = round(random.uniform(0, 3), 2)
        
        sl_wo_dedn = max(0, last_sl - sl_taken)
        cl_wo_dedn = max(0, last_cl - cl_taken)
        el_wo_dedn = max(0, last_el - el_taken)
        
        final_sl = sl_wo_dedn
        final_cl = max(0, cl_wo_dedn - late_cl)
        final_el = max(0, el_wo_dedn - late_el)
        final_coff = max(0, last_coff - coff_taken)
        
        final_processed = working_days + w_off + holiday - lwp
        
        emp_dict.update({
            'working_days': working_days,
            'present_days': present_days,
            'w_off': w_off,
            'holiday': holiday,
            'sl_taken': sl_taken, 'coff_taken': coff_taken, 'cl_taken': cl_taken, 'el_taken': el_taken, 'lwp': lwp,
            'final_processed': final_processed,
            'late_cl': late_cl, 'late_el': late_el, 'final_coff_month': final_coff,
            'last_sl': last_sl, 'sl_wo_dedn': sl_wo_dedn,
            'last_cl': last_cl, 'cl_wo_dedn': cl_wo_dedn,
            'last_el': last_el, 'el_wo_dedn': el_wo_dedn,
            'coff_bal': final_coff, 'sl_bal': final_sl, 'cl_bal': final_cl, 'el_bal': final_el
        })
        enhanced_employees.append(emp_dict)
        
    return render_template('attendance_master.html', 
                           employees=enhanced_employees, 
                           search_col=search_col,
                           search_val=search_val,
                           year=year,
                           month=month,
                           allowed_cols=allowed_cols)

@app.route('/api/attendance/<emp_id>/<year>/<month>')
@hr_required
def api_get_attendance(emp_id, year, month):
    from datetime import datetime
    import random, calendar
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT attendance_date, status, in_time, out_time, remarks
        FROM employee_attendance
        WHERE emp_id = %s AND YEAR(attendance_date) = %s AND MONTH(attendance_date) = %s
        ORDER BY attendance_date ASC
    """, (emp_id, year, month))
    records = list(cursor.fetchall())
    
    cursor.execute("SELECT emp_name, joining_date FROM Employee WHERE emp_id = %s", (emp_id,))
    emp = cursor.fetchone()
    conn.close()
    
    if not records and emp:
        joining_date = emp['joining_date']
        if isinstance(joining_date, str):
            joining_date = datetime.strptime(joining_date, '%Y-%m-%d').date()
            
        y, m = int(year), int(month)
        last_day_of_month = datetime(y, m, calendar.monthrange(y, m)[1]).date()
        
        if joining_date <= last_day_of_month:
            random.seed(emp_id + str(year) + str(month))
            num_days = calendar.monthrange(y, m)[1]
            
            today = datetime.now().date()
            if datetime(y, m, 1).date() <= today:
                end_day = num_days if datetime(y, m, num_days).date() <= today else today.day
                for day in range(1, end_day + 1):
                    date_obj = datetime(y, m, day)
                    if date_obj.date() < joining_date: continue
                    
                    if date_obj.weekday() >= 5:
                        status = 'Leave'
                        in_time = None
                        out_time = None
                        remarks = 'Weekend'
                    else:
                        rand_val = random.random()
                        if rand_val < 0.85:
                            status = 'Present'
                            in_time = f"09:{random.randint(0,30):02d}:00"
                            out_time = f"17:{random.randint(30,59):02d}:00"
                        elif rand_val < 0.90:
                            status = 'Absent'
                            in_time = None
                            out_time = None
                        elif rand_val < 0.95:
                            status = 'Leave'
                            in_time = None
                            out_time = None
                        else:
                            status = 'Half Day'
                            in_time = "09:00:00"
                            out_time = "13:00:00"
                        remarks = None
                    
                records.append({
                    'attendance_date': date_obj.date(),
                    'status': status,
                    'in_time': in_time,
                    'out_time': out_time,
                    'remarks': remarks
                })
                
    for r in records:
        if r['attendance_date']: r['attendance_date'] = r['attendance_date'].strftime('%Y-%m-%d')
        if r['in_time']: r['in_time'] = str(r['in_time'])
        if r['out_time']: r['out_time'] = str(r['out_time'])
        
    return jsonify({"records": records, "emp_name": emp['emp_name'] if emp else emp_id})

# ─────────────────────────────────────────────────────────────────────────────
# SALARY MASTER ROUTES
# ─────────────────────────────────────────────────────────────────────────────

@app.route('/salary_master')
@hr_required
def salary_master():
    """Salary Master — shows all employee salary details prorated by working/present days.
    Supports per-month overrides stored in salary_overrides table.
    """
    from datetime import datetime as _dt
    import calendar as cal_mod

    now = _dt.now()
    try:
        month = int(request.args.get('month', now.month))
        year  = int(request.args.get('year',  now.year))
    except (ValueError, TypeError):
        month, year = now.month, now.year

    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1
    per_page = 5

    search_val = request.args.get('search_val', '').strip()
    search_col = request.args.get('search_col', 'emp_name').strip()
    allowed_cols = {'emp_name': 'Employee Name', 'emp_id': 'Employee ID'}
    if search_col not in allowed_cols:
        search_col = 'emp_name'

    _, days_in_month = cal_mod.monthrange(year, month)
    # Default working days = calendar days in the month (e.g. 30, 31, 28)
    default_working_days = days_in_month
    is_future = (year > now.year) or (year == now.year and month > now.month)

    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch oldest joining year for dialog year range
    cursor.execute("SELECT MIN(YEAR(joining_date)) as min_year FROM v_employees")
    row = cursor.fetchone()
    min_year = int(row['min_year']) if row and row['min_year'] else 2018

    query = """
        SELECT e.id, e.emp_id, e.emp_name, e.joining_date, e.basic_salary, e.payment_tier,
               e.department, e.title,
               b.bank_name, b.bank_account_num, b.ifsc_code,
               ma.total_days as db_total_days, ma.present_days as db_present_days
        FROM v_employees e
        LEFT JOIN employee_bank_details b ON e.emp_id = b.emp_id
        LEFT JOIN employee_monthly_attendance ma
            ON e.emp_id = ma.emp_id AND ma.month_num = %s AND ma.year_num = %s
        WHERE 1=1
    """
    params = [month, year]
    
    # Exclude employees who haven't joined yet
    query += " AND (e.joining_date IS NULL OR YEAR(e.joining_date) < %s OR (YEAR(e.joining_date) = %s AND MONTH(e.joining_date) <= %s))"
    params.extend([year, year, month])

    if search_val:
        if search_col == 'emp_id':
            query += " AND e.emp_id LIKE %s"
        else:
            query += " AND e.emp_name LIKE %s"
        params.append(f"%{search_val}%")
    query += " ORDER BY e.emp_id ASC"

    cursor.execute(query, params)
    employees_data = cursor.fetchall()
    
    total_employees = len(employees_data)
    total_pages = (total_employees + per_page - 1) // per_page
    if page < 1: page = 1
    if page > total_pages and total_pages > 0: page = total_pages
    offset = (page - 1) * per_page
    employees_data = employees_data[offset:offset + per_page]

    # Fetch financial components for all employees (batch)
    emp_ids = [e['emp_id'] for e in employees_data]
    components_by_emp = {}
    if emp_ids:
        fmt = ','.join(['%s'] * len(emp_ids))
        cursor.execute(
            f"SELECT emp_id, component_name, component_code, amount FROM Employee_Allowance WHERE emp_id IN ({fmt})",
            tuple(emp_ids)
        )
        for comp in cursor.fetchall():
            eid = comp['emp_id']
            if eid not in components_by_emp:
                components_by_emp[eid] = {}
            components_by_emp[eid][comp['component_name'].lower()] = float(comp['amount'] or 0)

    # Fetch salary overrides for this month/year
    overrides_by_emp = {}
    if emp_ids:
        fmt = ','.join(['%s'] * len(emp_ids))
        cursor.execute(
            f"SELECT * FROM Salary_Payslip WHERE month_num=%s AND year_num=%s AND emp_id IN ({fmt})",
            tuple([month, year] + emp_ids)
        )
        for ov in cursor.fetchall():
            overrides_by_emp[ov['emp_id']] = dict(ov)

    conn.close()

    month_name = _dt(year, month, 1).strftime('%B')
    enhanced = []

    for emp in employees_data:
        ed = dict(emp)
        emp_id_str = emp['emp_id']
        joining_date = emp['joining_date']

        if isinstance(joining_date, str):
            try:
                joining_date = _dt.strptime(joining_date, '%Y-%m-%d').date()
            except Exception:
                joining_date = None

        ed['joining_date_obj'] = joining_date
        ed['joining_date_fmt'] = joining_date.strftime('%d-%b-%y') if joining_date else 'N/A'

        # Determine if employee was active in this month
        not_working = joining_date and (
            joining_date.year > year or
            (joining_date.year == year and joining_date.month > month)
        )
        ed['not_working'] = not_working

        if not_working:
            ed.update({
                'working_days': default_working_days,
                'present_days': 0,
                'basic': 0, 'hra': 0, 'sa': 0,
                'meal': 0, 'medical': 0, 'conveyance': 0,
                'pf': 0, 'esic': 0, 'tds': 0, 'advance': 0,
                'other_dedn': 0, 'super_annuation': 0,
                'total_earning': 0, 'total_dedn': 0, 'net_salary': 0,
                'has_override': False
            })
            enhanced.append(ed)
            continue

        comp = components_by_emp.get(emp_id_str, {})
        ov  = overrides_by_emp.get(emp_id_str)

        base_basic = float(emp['basic_salary'] or 0)
        if base_basic == 0:
            tier = emp['payment_tier'] or 3
            base_basic = 50000.0 if tier == 1 else (30000.0 if tier == 2 else 15000.0)

        # Base component values
        def gc(keys, default=0.0):
            for k in keys:
                if k in comp: return comp[k]
            return default

        base_hra  = gc(['house rent allowance', 'hra'], 0.0)
        base_sa   = gc(['special allowance', 'sa'], 0.0)
        base_meal = gc(['meal allowance', 'meal_allowance'], 0.0)
        base_med  = gc(['medical allowance', 'medical_allowance'], 0.0)
        base_conv = gc(['conveyance', 'transport allowance'], 0.0)
        base_pf   = gc(['provident fund', 'pf'], 0.0)
        base_esic = gc(['esi', 'insurance'], 0.0)
        base_tds  = gc(['income tax', 'tds'], 0.0)
        base_adv  = gc(['advance', 'loan'], 0.0)
        base_other = gc(['other deduction'], 0.0)
        base_super = gc(['super annuation'], 0.0)

        # Apply TDS rule: Only if Gross Salary > 1,200,000 per year
        base_gross = base_basic + base_hra + base_sa + base_meal + base_med + base_conv
        if (base_gross * 12) <= 1200000:
            base_tds = 0.0

        # Working days: override > calculated weekday count for this month
        # NOTE: attendance.total_days stores CALENDAR days (31), NOT working days — so we ignore it here
        if ov and ov.get('working_days') is not None:
            working_days = int(ov['working_days'])
        else:
            working_days = default_working_days  # weekdays in month, e.g. 21 for May 2026

        # Present days: override > attendance record > assume full attendance
        if ov and ov.get('present_days') is not None:
            present_days = float(ov['present_days'])
        elif emp['db_present_days'] is not None:
            present_days = float(emp['db_present_days'])
        else:
            present_days = 0.0

        factor = (present_days / working_days) if working_days > 0 else 1.0

        def ov_val(key, base, prorate=True):
            """Return override value if set, else prorate base."""
            if ov and ov.get(key) is not None:
                val = float(ov[key])
                return round(val * factor, 2) if prorate else round(val, 2)
            return round(base * factor, 2) if prorate else round(base, 2)

        basic = ov_val('basic_override', base_basic, True)
        hra   = ov_val('hra_override',   base_hra, True)
        sa    = ov_val('sa_override',    base_sa, True)
        meal  = ov_val('meal_override',  base_meal, True)
        med   = ov_val('medical_override', base_med, True)
        conv  = ov_val('conveyance_override', base_conv, True)
        pf    = ov_val('pf_override',    base_pf, True)
        esic  = ov_val('esic_override',  base_esic, True)
        tds   = ov_val('tds_override',   base_tds, True)
        advance = ov_val('advance_override', base_adv, False)
        other_dedn = ov_val('other_dedn_override', base_other, False)
        super_ann  = ov_val('super_annuation_override', base_super, False)

        total_earning = basic + hra + sa + meal + med + conv
        total_dedn    = pf + esic + tds + advance + other_dedn + super_ann
        net_salary    = total_earning - total_dedn

        ed.update({
            'working_days': working_days,
            'present_days': present_days,
            'basic': basic, 'hra': hra, 'sa': sa,
            'meal': meal, 'medical': med, 'conveyance': conv,
            'pf': pf, 'esic': esic, 'tds': tds, 'advance': advance,
            'other_dedn': other_dedn, 'super_annuation': super_ann,
            'total_earning': total_earning,
            'total_dedn': total_dedn,
            'net_salary': net_salary,
            # Base (unprorated) values for Edit modal defaults
            'base_basic': base_basic, 'base_hra': base_hra, 'base_sa': base_sa,
            'base_meal': base_meal, 'base_med': base_med, 'base_conv': base_conv,
            'base_pf': base_pf, 'base_esic': base_esic, 'base_tds': base_tds,
            'base_adv': base_adv, 'base_other': base_other, 'base_super': base_super,
            'has_override': ov is not None
        })
        enhanced.append(ed)

    return render_template(
        'salary_master.html',
        employees=enhanced,
        month=month,
        year=year,
        month_name=month_name,
        min_year=min_year,
        now_year=_dt.now().year,
        search_col=search_col,
        search_val=search_val,
        allowed_cols=allowed_cols,
        default_working_days=default_working_days,
        page=page,
        total_pages=total_pages
    )


@app.route('/api/salary/update', methods=['POST'])
@hr_required
def api_salary_update():
    """Bulk update working/present days and overrides for selected employees.
    Returns recalculated salary figures for live JS update.
    """
    data = request.get_json(force=True)
    updates      = data.get('updates', [])
    month        = int(data.get('month', 1))
    year         = int(data.get('year', 2026))

    if not updates:
        return jsonify({'success': False, 'error': 'No employees selected'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    results = []
    for update in updates:
        emp_id = update.get('emp_id')
        if not emp_id: continue
        
        working_days = update.get('working_days')
        present_days = update.get('present_days')
        meal_ov = update.get('meal_override')
        med_ov = update.get('medical_override')
        conv_ov = update.get('conveyance_override')

        try:
            update_fields = []
            update_vals   = []
            if working_days is not None:
                update_fields.append('working_days=%s')
                update_vals.append(int(working_days))
            if present_days is not None:
                update_fields.append('present_days=%s')
                update_vals.append(float(present_days))
            if meal_ov is not None:
                update_fields.append('meal_override=%s')
                update_vals.append(float(meal_ov))
            if med_ov is not None:
                update_fields.append('medical_override=%s')
                update_vals.append(float(med_ov))
            if conv_ov is not None:
                update_fields.append('conveyance_override=%s')
                update_vals.append(float(conv_ov))

            if update_fields:
                cursor.execute(
                    f"""
                    INSERT INTO Salary_Payslip (emp_id, month_num, year_num, {', '.join(f.split('=')[0] for f in update_fields)})
                    VALUES (%s, %s, %s, {', '.join(['%s']*len(update_fields))})
                    ON DUPLICATE KEY UPDATE {', '.join(update_fields)}
                    """,
                    tuple([emp_id, month, year] + update_vals + update_vals)
                )

            # Fetch updated override + base to return recalculated values
            cursor.execute("SELECT basic_salary, payment_tier FROM v_employees WHERE emp_id=%s", (emp_id,))
            emp_row = cursor.fetchone()
            cursor.execute("SELECT * FROM Salary_Payslip WHERE emp_id=%s AND month_num=%s AND year_num=%s", (emp_id, month, year))
            ov = cursor.fetchone()
            cursor.execute("SELECT component_name, amount FROM Employee_Allowance WHERE emp_id=%s", (emp_id,))
            comps_raw = cursor.fetchall()
            comp = {r['component_name'].lower(): float(r['amount'] or 0) for r in comps_raw}

            base_basic = float(emp_row['basic_salary'] or 0) if emp_row else 0
            if base_basic == 0:
                tier = (emp_row or {}).get('payment_tier', 3)
                base_basic = 50000.0 if tier == 1 else (30000.0 if tier == 2 else 15000.0)

            def gc2(keys, default=0.0):
                for k in keys:
                    if k in comp: return comp[k]
                return default

            wd = int(ov['working_days']) if ov and ov.get('working_days') is not None else (int(working_days) if working_days else 26)
            pd_ = float(ov['present_days']) if ov and ov.get('present_days') is not None else (float(present_days) if present_days else float(wd))
            factor = (pd_ / wd) if wd > 0 else 1.0

            def ov_val_local(key, base, prorate=True):
                if ov and ov.get(key) is not None:
                    return round(float(ov[key]) * factor, 2) if prorate else round(float(ov[key]), 2)
                return round(base * factor, 2) if prorate else round(base, 2)

            b = round(base_basic * factor, 2)
            h_base = gc2(['house rent allowance','hra'], base_basic*0.40)
            s_base = gc2(['special allowance','sa'], base_basic*0.20)
            ml_base = gc2(['meal allowance','meal_allowance'], 2000)
            md_base = gc2(['medical allowance','medical_allowance'], 1500)
            cv_base = gc2(['conveyance','transport allowance'], 3000)
            
            h = round(h_base * factor, 2)
            s = round(s_base * factor, 2)
            ml = ov_val_local('meal_override', ml_base, False)
            md = ov_val_local('medical_override', md_base, False)
            cv = ov_val_local('conveyance_override', cv_base, False)
            
            base_gross = base_basic + h_base + s_base + ml_base + md_base + cv_base
            base_tds_val = gc2(['income tax','tds'])
            if (base_gross * 12) <= 1200000:
                base_tds_val = 0.0

            pf = round(gc2(['provident fund','pf'], min(base_basic*0.12,1800.0)) * factor, 2)
            esic = round(gc2(['esi','insurance']) * factor, 2)
            tds  = round(base_tds_val * factor, 2)
            adv  = round(gc2(['advance','loan']) * factor, 2)

            te = b + h + s + ml + md + cv
            td = pf + esic + tds + adv
            ns = te - td

            results.append({
                'emp_id': emp_id, 'working_days': wd, 'present_days': pd_,
                'basic': b, 'hra': h, 'sa': s, 'meal': ml, 'medical': md, 'conveyance': cv,
                'pf': pf, 'esic': esic, 'tds': tds, 'advance': adv,
                'total_earning': te, 'total_dedn': td, 'net_salary': ns
            })
        except Exception as e:
            results.append({'emp_id': emp_id, 'error': str(e)})

    conn.commit()
    conn.close()
    return jsonify({'success': True, 'results': results})


@app.route('/api/salary/edit_month', methods=['POST'])
@hr_required
def api_salary_edit_month():
    """Save a full per-month salary override for one employee (from Edit Salary modal)."""
    data = request.get_json(force=True)
    emp_id = data.get('emp_id')
    month  = int(data.get('month', 1))
    year   = int(data.get('year', 2026))

    if not emp_id:
        return jsonify({'success': False, 'error': 'emp_id required'}), 400

    fields = [
        'working_days', 'present_days',
        'basic_override', 'hra_override', 'sa_override',
        'meal_override', 'medical_override', 'conveyance_override',
        'pf_override', 'esic_override', 'tds_override',
        'advance_override', 'other_dedn_override', 'super_annuation_override'
    ]

    insert_cols = ['emp_id', 'month_num', 'year_num']
    insert_vals = [emp_id, month, year]
    update_parts = []

    for f in fields:
        val = data.get(f)
        if val is not None and val != '':
            try:
                val = float(val)
            except (ValueError, TypeError):
                continue
            insert_cols.append(f)
            insert_vals.append(val)
            update_parts.append(f"{f}=%s")

    if not update_parts:
        return jsonify({'success': False, 'error': 'No data to save'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cols_str = ', '.join(insert_cols)
        placeholders = ', '.join(['%s'] * len(insert_cols))
        update_str = ', '.join(update_parts)
        update_vals = [v for v in insert_vals[3:]]

        cursor.execute(
            f"""
            INSERT INTO Salary_Payslip ({cols_str})
            VALUES ({placeholders})
            ON DUPLICATE KEY UPDATE {update_str}
            """,
            tuple(insert_vals + update_vals)
        )
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()


# ─────────────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    # Only run database initialization in the main worker process when Flask's reloader is enabled
    # to avoid race conditions and deadlocks between parent and child processes.
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true' or not app.debug:
        init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
