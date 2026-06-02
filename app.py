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

def get_dynamic_payroll_and_bank(basic_base, title, directorate, department, emp_id_or_seed):
    """
    Computes payroll details and bank details.
    - Role-level metrics (allowance %, tax %, bank name) are stable per (title, directorate, department).
    - basic_salary has a per-employee ±20% variation using emp_id_or_seed.
    - bank_account_num is unique per employee.
    Returns structured dicts for allowances and taxes.
    """
    # 1. Role-stable seed
    combo_str = f"{str(title).strip().lower()}|{str(directorate).strip().lower()}|{str(department).strip().lower()}"
    role_seed = int(hashlib.md5(combo_str.encode('utf-8')).hexdigest(), 16) % 20000
    random.seed(role_seed)

    # Role-based percentages
    meal_pct = random.choice([0.05, 0.06, 0.07, 0.08, 0.09, 0.10])
    transport_pct = random.choice([0.04, 0.05, 0.06, 0.07, 0.08])
    medical_pct = random.choice([0.02, 0.03, 0.04, 0.05])
    retirement_pct = random.choice([0.10, 0.11, 0.12, 0.13])
    tax_pct = random.choice([0.015, 0.02, 0.025, 0.03])
    banks = ["Bank of America", "Chase Bank", "Wells Fargo", "Citibank", "HSBC", "HDFC Bank", "ICICI Bank"]
    bank_name = random.choice(banks)

    # 2. Per-employee salary variation (±20%) — makes same-role salaries different
    random.seed(emp_id_or_seed + 99999)
    variation_pct = random.uniform(-0.20, 0.20)
    basic_salary = round(float(basic_base) * (1 + variation_pct), 2)

    # 3. Calculate amounts
    meal_allowance = round(basic_salary * meal_pct, 2)
    transportation_allowance = round(basic_salary * transport_pct, 2)
    medical_allowance = round(basic_salary * medical_pct, 2)
    retirement_insurance = round(basic_salary * retirement_pct, 2)
    tax_amount = round(basic_salary * tax_pct, 2)

    allowances_total = meal_allowance + transportation_allowance + medical_allowance
    deductions_total = retirement_insurance + tax_amount

    # 4. Per-employee unique bank account
    random.seed(emp_id_or_seed + 12345)
    bank_account_num = "".join([str(random.randint(0, 9)) for _ in range(10)])

    allowances_list = [
        ('meal_allowance', meal_allowance),
        ('transportation_allowance', transportation_allowance),
        ('medical_allowance', medical_allowance),
    ]
    taxes_list = [
        ('retirement_insurance', retirement_insurance),
        ('professional_tax', tax_amount),
    ]

    return (basic_salary, allowances_total, deductions_total,
            bank_name, bank_account_num, allowances_list, taxes_list)

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
    """Initializes the MySQL database and normalized table structure at application startup."""

    conn = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD
    )
    try:
        with conn.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        conn.commit()
    finally:
        conn.close()

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # --- Main employees table ---
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS employees (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    emp_id VARCHAR(50) NOT NULL UNIQUE,
                    emp_name VARCHAR(100) NOT NULL,
                    email VARCHAR(100) NOT NULL,
                    date DATE NOT NULL,
                    basic_salary DECIMAL(10,2) DEFAULT 45000.00,
                    allowances DECIMAL(10,2) DEFAULT 0.00,
                    deductions DECIMAL(10,2) DEFAULT 0.00,
                    age INT DEFAULT 30,
                    gender VARCHAR(20) DEFAULT 'Male',
                    education VARCHAR(100) DEFAULT 'B.Tech'
                )
            """)
            
            # Database Self-Healing Migration: Add columns if they do not exist
            for col_name, col_def in [
                ("age", "INT DEFAULT 30"),
                ("gender", "VARCHAR(20) DEFAULT 'Male'"),
                ("education", "VARCHAR(100) DEFAULT 'B.Tech'")
            ]:
                try:
                    cursor.execute(f"ALTER TABLE employees ADD COLUMN {col_name} {col_def}")
                except pymysql.err.OperationalError as e:
                    if e.args[0] == 1060:
                        pass
                    else:
                        raise

            # Self-healing logic for expanded employee details
            cols_to_add = [
                ("title", "VARCHAR(100) DEFAULT 'Staff'"),
                ("directorate", "VARCHAR(100) DEFAULT 'Operation'"),
                ("department", "VARCHAR(100) DEFAULT 'General Affairs'"),
                ("bank_name", "VARCHAR(100) DEFAULT 'Bank of America'"),
                ("bank_account_num", "VARCHAR(50) DEFAULT '1234567890'"),
                ("meal_allowance", "DECIMAL(10,2) DEFAULT 300.00"),
                ("transportation_allowance", "DECIMAL(10,2) DEFAULT 300.00"),
                ("medical_allowance", "DECIMAL(10,2) DEFAULT 300.00"),
                ("retirement_insurance", "DECIMAL(10,2) DEFAULT 25.00"),
                ("tax", "DECIMAL(10,2) DEFAULT 25.00"),
                ("joining_year", "INT DEFAULT 2026"),
                ("city", "VARCHAR(100) DEFAULT 'Bangalore'"),
                ("payment_tier", "INT DEFAULT 3"),
                ("ever_benched", "VARCHAR(10) DEFAULT 'No'"),
                ("experience_in_current_domain", "INT DEFAULT 2"),
                ("leave_or_not", "INT DEFAULT 0")
            ]
            for col_name, col_def in cols_to_add:
                try:
                    cursor.execute(f"ALTER TABLE employees ADD COLUMN {col_name} {col_def}")
                except pymysql.err.OperationalError as e:
                    if e.args[0] == 1060:
                        pass
                    else:
                        raise

            # --- Normalized satellite tables ---

            # Bank details: one row per employee
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS employee_bank_details (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    emp_id VARCHAR(50) NOT NULL UNIQUE,
                    bank_name VARCHAR(100) DEFAULT 'Bank of America',
                    bank_account_num VARCHAR(50) DEFAULT '0000000000',
                    FOREIGN KEY (emp_id) REFERENCES employees(emp_id) ON DELETE CASCADE
                )
            """)

            # Allowances: multiple rows per employee (one per allowance type)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS employee_allowances (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    emp_id VARCHAR(50) NOT NULL,
                    allowance_type VARCHAR(100) NOT NULL,
                    amount DECIMAL(10,2) DEFAULT 0.00,
                    FOREIGN KEY (emp_id) REFERENCES employees(emp_id) ON DELETE CASCADE
                )
            """)

            # Taxes/deductions: multiple rows per employee
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS employee_taxes (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    emp_id VARCHAR(50) NOT NULL,
                    tax_type VARCHAR(100) NOT NULL,
                    amount DECIMAL(10,2) DEFAULT 0.00,
                    FOREIGN KEY (emp_id) REFERENCES employees(emp_id) ON DELETE CASCADE
                )
            """)

            # --- Migrate existing data from employees flat columns to new tables ---
            # Find employees that have flat columns but no satellite records yet
            cursor.execute("SHOW COLUMNS FROM employees LIKE 'bank_name'")
            has_bank_col = cursor.fetchone() is not None

            if has_bank_col:
                cursor.execute("""
                    SELECT e.emp_id, e.bank_name, e.bank_account_num,
                           e.meal_allowance, e.transportation_allowance, e.medical_allowance,
                           e.retirement_insurance, e.tax
                    FROM employees e
                    LEFT JOIN employee_bank_details b ON e.emp_id = b.emp_id
                    WHERE b.emp_id IS NULL
                """)
                migrate_rows = cursor.fetchall()
                for mr in migrate_rows:
                    eid = mr['emp_id']
                    # Bank details
                    cursor.execute(
                        "INSERT IGNORE INTO employee_bank_details (emp_id, bank_name, bank_account_num) VALUES (%s, %s, %s)",
                        (eid, mr.get('bank_name', 'Bank of America'), mr.get('bank_account_num', '0000000000'))
                    )
                    # Allowances — only insert if no records exist for this emp
                    cursor.execute("SELECT COUNT(*) as cnt FROM employee_allowances WHERE emp_id = %s", (eid,))
                    if cursor.fetchone()['cnt'] == 0:
                        meal = float(mr.get('meal_allowance') or 0)
                        transport = float(mr.get('transportation_allowance') or 0)
                        medical = float(mr.get('medical_allowance') or 0)
                        for atype, aamount in [('meal_allowance', meal), ('transportation_allowance', transport), ('medical_allowance', medical)]:
                            cursor.execute(
                                "INSERT INTO employee_allowances (emp_id, allowance_type, amount) VALUES (%s, %s, %s)",
                                (eid, atype, aamount)
                            )
                    # Taxes — only insert if no records exist
                    cursor.execute("SELECT COUNT(*) as cnt FROM employee_taxes WHERE emp_id = %s", (eid,))
                    if cursor.fetchone()['cnt'] == 0:
                        ret = float(mr.get('retirement_insurance') or 0)
                        tx = float(mr.get('tax') or 0)
                        for ttype, tamount in [('retirement_insurance', ret), ('professional_tax', tx)]:
                            cursor.execute(
                                "INSERT INTO employee_taxes (emp_id, tax_type, amount) VALUES (%s, %s, %s)",
                                (eid, ttype, tamount)
                            )

                # Recalculate allowances/deductions totals in main table from satellite tables
                cursor.execute("""
                    UPDATE employees e
                    SET allowances = COALESCE((SELECT SUM(amount) FROM employee_allowances WHERE emp_id = e.emp_id), 0),
                        deductions = COALESCE((SELECT SUM(amount) FROM employee_taxes WHERE emp_id = e.emp_id), 0)
                """)

            # --- New tables for transaction history and email log ---
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS payroll_transactions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    emp_id VARCHAR(50) NOT NULL,
                    salary_month VARCHAR(20) NOT NULL,
                    salary_year INT NOT NULL,
                    basic_salary DECIMAL(10,2) DEFAULT 0.00,
                    allowances DECIMAL(10,2) DEFAULT 0.00,
                    deductions DECIMAL(10,2) DEFAULT 0.00,
                    net_pay DECIMAL(10,2) DEFAULT 0.00,
                    generated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (emp_id) REFERENCES employees(emp_id) ON DELETE CASCADE
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS employee_emails (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    emp_id VARCHAR(50) NOT NULL,
                    sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    subject VARCHAR(255),
                    body TEXT,
                    response_received_at DATETIME,
                    response_notes TEXT,
                    status VARCHAR(20) DEFAULT 'Sent',
                    FOREIGN KEY (emp_id) REFERENCES employees(emp_id) ON DELETE CASCADE
                )
            """)

            # --- Drop old flat columns from employees after migration is done ---
            flat_cols_to_drop = [
                'bank_name', 'bank_account_num',
                'meal_allowance', 'transportation_allowance', 'medical_allowance',
                'retirement_insurance', 'tax'
            ]
            for col in flat_cols_to_drop:
                try:
                    cursor.execute(f"ALTER TABLE employees DROP COLUMN {col}")
                except pymysql.err.OperationalError as e:
                    if e.args[0] in (1091, 1060):
                        pass
                    else:
                        raise

            # One-time data correction: Randomize ages for existing records that default to 30
            cursor.execute("SELECT id FROM employees WHERE age = 30")
            existing_rows = cursor.fetchall()
            if existing_rows:
                for idx, r in enumerate(existing_rows):
                    # Seed to keep it deterministic for successive restarts but varied across records
                    random.seed(r['id'] + 100)
                    random_age = random.randint(21, 58)
                    cursor.execute("UPDATE employees SET age = %s WHERE id = %s", (random_age, r['id']))

            # One-time payroll correction: Recalculate dynamic values for old default records
            cursor.execute("SELECT id, basic_salary FROM employees WHERE title = 'Staff' OR title IS NULL")
            default_rows = cursor.fetchall()
            if default_rows:
                designations_1 = ["Director of Tech", "VP of Operations", "Research Fellow", "HR Director"]
                designations_2 = ["Senior Software Engineer", "Systems Architect", "Lead QA Engineer", "HR Manager"]
                designations_3 = ["Associate Engineer", "Operations Analyst", "Customer Support", "Marketing Associate"]
                directorate_list = ["Engineering", "Operations", "Information Technology", "Product & Design"]
                department_list = ["Core Development", "Data Platform", "QA & Testing", "Cloud Operations"]

                for r in default_rows:
                    emp_db_id = r['id']
                    basic_val = float(r['basic_salary'])
                    random.seed(emp_db_id + 200)
                    if basic_val >= 80000:
                        title_val = designations_1[emp_db_id % len(designations_1)]
                        dir_val = "Management"; dept_val = "Leadership"; basic_base = 85000.00
                    elif basic_val >= 50000:
                        title_val = designations_2[emp_db_id % len(designations_2)]
                        dir_val = directorate_list[emp_db_id % len(directorate_list)]
                        dept_val = department_list[emp_db_id % len(department_list)]; basic_base = 50000.00
                    else:
                        title_val = designations_3[emp_db_id % len(designations_3)]
                        dir_val = "Operations"; dept_val = "General Support"; basic_base = 32000.00

                    (basic_salary, allowances_total, deductions_total,
                     bank_name_val, bank_account_num_val, allowances_list, taxes_list) = get_dynamic_payroll_and_bank(
                        basic_base, title_val, dir_val, dept_val, emp_db_id
                    )
                    cursor.execute(
                        "UPDATE employees SET title=%s, directorate=%s, department=%s, basic_salary=%s, allowances=%s, deductions=%s WHERE id=%s",
                        (title_val, dir_val, dept_val, basic_salary, allowances_total, deductions_total, emp_db_id)
                    )
                    cursor.execute("INSERT IGNORE INTO employee_bank_details (emp_id, bank_name, bank_account_num) SELECT emp_id, %s, %s FROM employees WHERE id=%s",
                                   (bank_name_val, bank_account_num_val, emp_db_id))
                    cursor.execute("SELECT emp_id FROM employees WHERE id=%s", (emp_db_id,))
                    row = cursor.fetchone()
                    if row:
                        eid = row['emp_id']
                        cursor.execute("SELECT COUNT(*) as c FROM employee_allowances WHERE emp_id=%s", (eid,))
                        if cursor.fetchone()['c'] == 0:
                            for atype, amt in allowances_list:
                                cursor.execute("INSERT INTO employee_allowances (emp_id,allowance_type,amount) VALUES(%s,%s,%s)", (eid, atype, amt))
                        cursor.execute("SELECT COUNT(*) as c FROM employee_taxes WHERE emp_id=%s", (eid,))
                        if cursor.fetchone()['c'] == 0:
                            for ttype, amt in taxes_list:
                                cursor.execute("INSERT INTO employee_taxes (emp_id,tax_type,amount) VALUES(%s,%s,%s)", (eid, ttype, amt))
                
            # One-time correction for new Kaggle columns (making them dynamic/randomized)
            cursor.execute("SELECT id, date, age, basic_salary, title, directorate, department FROM employees WHERE joining_year = 2026 AND city = 'Bangalore'")
            new_col_rows = cursor.fetchall()
            if new_col_rows:
                cities = ["Bangalore", "New Delhi", "Pune", "Mumbai", "Hyderabad", "Chennai"]
                benched_opts = ["No", "Yes", "No", "No"]
                for r in new_col_rows:
                    emp_db_id = r['id']
                    age_val = r['age']
                    basic_val = float(r['basic_salary'])
                    title_val = r['title']
                    dir_val = r['directorate']
                    dept_val = r['department']
                    try:
                        date_val = pd.to_datetime(r['date'])
                        joining_year_val = date_val.year
                    except Exception:
                        joining_year_val = 2026
                    random.seed(emp_db_id + 500)
                    city_val = cities[random.randint(0, len(cities) - 1)]
                    ever_benched_val = benched_opts[random.randint(0, len(benched_opts) - 1)]
                    if basic_val >= 80000:
                        payment_tier_val = 1; basic_base = 85000.00
                    elif basic_val >= 50000:
                        payment_tier_val = 2; basic_base = 50000.00
                    else:
                        payment_tier_val = 3; basic_base = 32000.00
                    experience_val = random.randint(1, min(15, max(1, age_val - 20)))
                    leave_val = random.randint(0, 5)

                    (basic_salary, allowances_total, deductions_total,
                     bank_name_val, bank_account_num_val, allowances_list, taxes_list) = get_dynamic_payroll_and_bank(
                        basic_base, title_val, dir_val, dept_val, emp_db_id
                    )
                    cursor.execute(
                        """UPDATE employees SET joining_year=%s, city=%s, payment_tier=%s, ever_benched=%s,
                            experience_in_current_domain=%s, leave_or_not=%s,
                            basic_salary=%s, allowances=%s, deductions=%s WHERE id=%s""",
                        (joining_year_val, city_val, payment_tier_val, ever_benched_val,
                         experience_val, leave_val, basic_salary, allowances_total, deductions_total, emp_db_id)
                    )
                    cursor.execute("SELECT emp_id FROM employees WHERE id=%s", (emp_db_id,))
                    row = cursor.fetchone()
                    if row:
                        eid = row['emp_id']
                        cursor.execute("INSERT IGNORE INTO employee_bank_details (emp_id,bank_name,bank_account_num) VALUES(%s,%s,%s)",
                                       (eid, bank_name_val, bank_account_num_val))
                        cursor.execute("SELECT COUNT(*) as c FROM employee_allowances WHERE emp_id=%s", (eid,))
                        if cursor.fetchone()['c'] == 0:
                            for atype, amt in allowances_list:
                                cursor.execute("INSERT INTO employee_allowances(emp_id,allowance_type,amount) VALUES(%s,%s,%s)", (eid, atype, amt))
                        cursor.execute("SELECT COUNT(*) as c FROM employee_taxes WHERE emp_id=%s", (eid,))
                        if cursor.fetchone()['c'] == 0:
                            for ttype, amt in taxes_list:
                                cursor.execute("INSERT INTO employee_taxes(emp_id,tax_type,amount) VALUES(%s,%s,%s)", (eid, ttype, amt))

        conn.commit()
    finally:
        conn.close()

def generate_employee_details(row, offset_index):
    """
    Generates realistic employee details from a row of the Kaggle Employee dataset.
    Returns a dict with all fields for employees + satellite tables.
    """
    age_val = row.get('Age')
    if age_val is None or pd.isna(age_val):
        random.seed(offset_index + 42)
        age = random.randint(21, 58)
    else:
        age = int(age_val)
    experience = int(row.get('ExperienceInCurrentDomain', 2))
    joining_year = int(row.get('JoiningYear', 2020))
    gender = str(row.get('Gender', 'Male')).strip().capitalize()
    payment_tier = int(row.get('PaymentTier', 3))
    education = str(row.get('Education', 'B.Tech')).strip()

    choice_seed = offset_index + age + experience
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
    date_str = f"{joining_year}-{month:02d}-{day:02d}"

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
    directorate_list = ["Engineering", "Operations", "Information Technology", "Product & Design"]
    directorate = directorate_list[choice_seed % len(directorate_list)]
    department_list = ["Core Development", "Data Platform", "QA & Testing", "Cloud Operations"]
    department = department_list[choice_seed % len(department_list)]

    (basic_salary, allowances_total, deductions_total,
     bank_name, bank_account_num, allowances_list, taxes_list) = get_dynamic_payroll_and_bank(
        basic_base, title, directorate, department, offset_index
    )

    city = str(row.get('City', 'Bangalore')).strip()
    ever_benched = str(row.get('EverBenched', 'No')).strip()
    try:
        leave_or_not = int(row.get('LeaveOrNot', 0))
        if leave_or_not < 0 or leave_or_not > 5:
            leave_or_not = random.randint(0, 5)
    except (ValueError, TypeError):
        leave_or_not = random.randint(0, 5)

    return {
        'emp_id': emp_id, 'emp_name': emp_name, 'email': email, 'date_str': date_str,
        'basic_salary': basic_salary, 'allowances': allowances_total, 'deductions': deductions_total,
        'age': age, 'gender': gender, 'education': education,
        'title': title, 'directorate': directorate, 'department': department,
        'bank_name': bank_name, 'bank_account_num': bank_account_num,
        'allowances_list': allowances_list, 'taxes_list': taxes_list,
        'joining_year': joining_year, 'city': city, 'payment_tier': payment_tier,
        'ever_benched': ever_benched, 'experience': experience, 'leave_or_not': leave_or_not
    }

@app.route('/')
def index():
    """Displays the main interface with upload capabilities, manual entry, search, and sorting."""
    search_col = request.args.get('search_col', 'emp_name').strip()
    search_val = request.args.get('search_val', '').strip()
    sort_order = request.args.get('sort', 'date_desc')  # Default sort by date descending
    selected_tier = request.args.get('tier', 'all').strip()
    
    # Whitelist of allowed search columns
    allowed_cols = {
        'emp_name': 'Employee Name',
        'emp_id': 'Employee ID',
        'email': 'Email Address',
        'age': 'Age',
        'gender': 'Gender',
        'education': 'Education',
        'basic_salary': 'Basic Salary',
        'meal_allowance': 'Meal Allowance',
        'transportation_allowance': 'Transport Allowance',
        'medical_allowance': 'Medical Allowance',
        'allowances': 'Allowances Total',
        'retirement_insurance': 'Retirement Insurance',
        'tax': 'Professional Tax',
        'deductions': 'Deductions Total',
        'title': 'Designation/Title',
        'directorate': 'Directorate',
        'department': 'Department',
        'bank_name': 'Bank Name',
        'bank_account_num': 'Bank Account #',
        'joining_year': 'Joining Year',
        'city': 'City',
        'payment_tier': 'Payment Tier',
        'ever_benched': 'Ever Benched',
        'experience_in_current_domain': 'Experience (Years)',
        'leave_or_not': 'Leave or Not',
        'date': 'Joining Date'
    }
    
    if search_col not in allowed_cols:
        search_col = 'emp_name'
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Base query
    query = """
        SELECT * FROM (
            SELECT 
                e.*,
                b.bank_name,
                b.bank_account_num,
                COALESCE(a.meal_allowance, 0) AS meal_allowance,
                COALESCE(a.transportation_allowance, 0) AS transportation_allowance,
                COALESCE(a.medical_allowance, 0) AS medical_allowance,
                COALESCE(t.retirement_insurance, 0) AS retirement_insurance,
                COALESCE(t.tax, 0) AS tax
            FROM employees e
            LEFT JOIN employee_bank_details b ON e.emp_id = b.emp_id
            LEFT JOIN (
                SELECT 
                    emp_id,
                    SUM(CASE WHEN allowance_type = 'meal_allowance' THEN amount ELSE 0 END) AS meal_allowance,
                    SUM(CASE WHEN allowance_type = 'transportation_allowance' THEN amount ELSE 0 END) AS transportation_allowance,
                    SUM(CASE WHEN allowance_type = 'medical_allowance' THEN amount ELSE 0 END) AS medical_allowance
                FROM employee_allowances
                GROUP BY emp_id
            ) a ON e.emp_id = a.emp_id
            LEFT JOIN (
                SELECT 
                    emp_id,
                    SUM(CASE WHEN tax_type = 'retirement_insurance' THEN amount ELSE 0 END) AS retirement_insurance,
                    SUM(CASE WHEN tax_type = 'professional_tax' THEN amount ELSE 0 END) AS tax
                FROM employee_taxes
                GROUP BY emp_id
            ) t ON e.emp_id = t.emp_id
        ) AS emp_details WHERE 1=1
    """
    params = []
    
    # Search functionality
    if search_val:
        query += f" AND `{search_col}` LIKE %s"
        search_param = f"%{search_val}%"
        params.append(search_param)
        
    # Salary Tier/Slab label filter
    if selected_tier == '1':
        query += " AND basic_salary >= 80000"
    elif selected_tier == '2':
        query += " AND basic_salary >= 50000 AND basic_salary < 80000"
    elif selected_tier == '3':
        query += " AND basic_salary < 50000"
        
    # Sort functionality
    if sort_order == 'date_asc':
        query += " ORDER BY date ASC"
    elif sort_order == 'date_desc':
        query += " ORDER BY date DESC"
    elif sort_order == 'name_asc':
        query += " ORDER BY emp_name ASC"
    elif sort_order == 'name_desc':
        query += " ORDER BY emp_name DESC"
    elif sort_order == 'id_asc':
        query += " ORDER BY emp_id ASC"
    elif sort_order == 'id_desc':
        query += " ORDER BY emp_id DESC"
    else:
        query += " ORDER BY date DESC"
        
    cursor.execute(query, params)
    employees = cursor.fetchall()
    conn.close()
    
    return render_template('index.html', employees=employees, search_col=search_col, search_val=search_val, allowed_cols=allowed_cols, sort=sort_order, tier=selected_tier)

def find_column(clean_cols, df_cols, synonyms):
    """Helper to find the actual case-sensitive column name from a list of synonyms."""
    for syn in synonyms:
        if syn in clean_cols:
            idx = clean_cols.index(syn)
            return df_cols[idx]
    return None

@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Handles CSV uploads. Flexibly matches columns by common synonyms
    (e.g., 'Employee ID', 'Name', 'Email Address', 'Date') to import data directly.
    Falls back to generating details if fields are missing (like the Kaggle dataset).
    """
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
    date_val = request.form.get('date', '').strip()

    basic_val = float(request.form.get('basic_salary', '45000') or 45000)
    age_val = request.form.get('age', '').strip()
    age_val = int(age_val) if age_val else random.randint(21, 58)
    gender_val = request.form.get('gender', 'Male').strip()
    education_val = request.form.get('education', 'B.Tech').strip()

    title_val = request.form.get('title', 'Software Engineer').strip()
    directorate_val = request.form.get('directorate', 'Engineering').strip()
    department_val = request.form.get('department', 'IT Department').strip()
    bank_name_val = request.form.get('bank_name', 'Bank of America').strip()
    bank_account_num_val = request.form.get('bank_account_num', '0000000000').strip()

    meal_val = float(request.form.get('meal_allowance', '300') or 300)
    transport_val = float(request.form.get('transportation_allowance', '300') or 300)
    medical_val = float(request.form.get('medical_allowance', '300') or 300)
    retirement_val = float(request.form.get('retirement_insurance', '25') or 25)
    tax_val = float(request.form.get('tax', '25') or 25)

    try:
        joining_year_val = int(request.form.get('joining_year', '') or pd.to_datetime(date_val).year)
    except Exception:
        joining_year_val = 2026
    city_val = request.form.get('city', 'Bangalore').strip()
    payment_tier_val = int(request.form.get('payment_tier', '3') or 3)
    ever_benched_val = request.form.get('ever_benched', 'No').strip()
    experience_val = int(request.form.get('experience_in_current_domain', '2') or 2)
    leave_val = int(request.form.get('leave_or_not', '0') or 0)

    allowances_val = meal_val + transport_val + medical_val
    deductions_val = retirement_val + tax_val

    if not (emp_id and emp_name and email and date_val):
        flash("All fields are required for manual entry.", "danger")
        return redirect(url_for('index'))

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
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
            for atype, aamount in [('meal_allowance', meal_val), ('transportation_allowance', transport_val), ('medical_allowance', medical_val)]:
                cursor.execute(
                    "INSERT INTO employee_allowances (emp_id, allowance_type, amount) VALUES (%s,%s,%s)",
                    (emp_id, atype, aamount)
                )
            for ttype, tamount in [('retirement_insurance', retirement_val), ('professional_tax', tax_val)]:
                cursor.execute(
                    "INSERT INTO employee_taxes (emp_id, tax_type, amount) VALUES (%s,%s,%s)",
                    (emp_id, ttype, tamount)
                )
        conn.commit()
        flash(f"Employee '{emp_name}' added successfully!", "success")
    except pymysql.err.IntegrityError:
        flash(f"Conflict: Employee ID '{emp_id}' or Email '{email}' already exists.", "danger")
    except Exception as e:
        flash(f"Database error: {str(e)}", "danger")
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
            # Also clear related satellite tables
            cursor.execute("DELETE FROM employee_bank_details")
            cursor.execute("DELETE FROM employee_allowances")
            cursor.execute("DELETE FROM employee_taxes")
            cursor.execute("DELETE FROM payroll_transactions")
            cursor.execute("DELETE FROM employee_emails")
        conn.commit()
    except Exception as e:
        flash(f"Error clearing records: {str(e)}", "danger")
    finally:
        conn.close()
    return redirect(url_for('index'))

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

    # Fetch allowances
    cursor.execute("SELECT allowance_type, amount FROM employee_allowances WHERE emp_id = %s", (emp_id,))
    allowances_rows = cursor.fetchall()

    # Fetch taxes
    cursor.execute("SELECT tax_type, amount FROM employee_taxes WHERE emp_id = %s", (emp_id,))
    taxes_rows = cursor.fetchall()
    conn.close()

    basic = float(employee.get('basic_salary', 0))
    allowances_data = [(r['allowance_type'], float(r['amount'])) for r in allowances_rows]
    taxes_data = [(r['tax_type'], float(r['amount'])) for r in taxes_rows]

    # Fallback to old flat columns if satellite tables are empty
    if not allowances_data:
        allowances_data = [
            ('meal_allowance', float(employee.get('meal_allowance', 0))),
            ('transportation_allowance', float(employee.get('transportation_allowance', 0))),
            ('medical_allowance', float(employee.get('medical_allowance', 0))),
        ]
    if not taxes_data:
        taxes_data = [
            ('retirement_insurance', float(employee.get('retirement_insurance', 0))),
            ('professional_tax', float(employee.get('tax', 0))),
        ]

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

    # Whitelist of allowed search columns (same as index)
    allowed_cols = {
        'emp_name': 'Employee Name',
        'emp_id': 'Employee ID',
        'email': 'Email Address',
        'age': 'Age',
        'gender': 'Gender',
        'education': 'Education',
        'basic_salary': 'Basic Salary',
        'meal_allowance': 'Meal Allowance',
        'transportation_allowance': 'Transport Allowance',
        'medical_allowance': 'Medical Allowance',
        'allowances': 'Allowances Total',
        'retirement_insurance': 'Retirement Insurance',
        'tax': 'Professional Tax',
        'deductions': 'Deductions Total',
        'title': 'Designation/Title',
        'directorate': 'Directorate',
        'department': 'Department',
        'bank_name': 'Bank Name',
        'bank_account_num': 'Bank Account #',
        'joining_year': 'Joining Year',
        'city': 'City',
        'payment_tier': 'Payment Tier',
        'ever_benched': 'Ever Benched',
        'experience_in_current_domain': 'Experience (Years)',
        'leave_or_not': 'Leave or Not',
        'date': 'Joining Date'
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
                COALESCE(a.meal_allowance, 0) AS meal_allowance,
                COALESCE(a.transportation_allowance, 0) AS transportation_allowance,
                COALESCE(a.medical_allowance, 0) AS medical_allowance,
                COALESCE(t.retirement_insurance, 0) AS retirement_insurance,
                COALESCE(t.tax, 0) AS tax
            FROM employees e
            LEFT JOIN employee_bank_details b ON e.emp_id = b.emp_id
            LEFT JOIN (
                SELECT 
                    emp_id,
                    SUM(CASE WHEN allowance_type = 'meal_allowance' THEN amount ELSE 0 END) AS meal_allowance,
                    SUM(CASE WHEN allowance_type = 'transportation_allowance' THEN amount ELSE 0 END) AS transportation_allowance,
                    SUM(CASE WHEN allowance_type = 'medical_allowance' THEN amount ELSE 0 END) AS medical_allowance
                FROM employee_allowances
                GROUP BY emp_id
            ) a ON e.emp_id = a.emp_id
            LEFT JOIN (
                SELECT 
                    emp_id,
                    SUM(CASE WHEN tax_type = 'retirement_insurance' THEN amount ELSE 0 END) AS retirement_insurance,
                    SUM(CASE WHEN tax_type = 'professional_tax' THEN amount ELSE 0 END) AS tax
                FROM employee_taxes
                GROUP BY emp_id
            ) t ON e.emp_id = t.emp_id
        ) AS emp_details WHERE 1=1
    """

    if search_col and search_val:
        query = base_query + f" AND `{search_col}` LIKE %s ORDER BY date DESC"
        cursor.execute(query, (f"%{search_val}%",))
    else:
        query = base_query + " ORDER BY date DESC"
        cursor.execute(query)
    preview_data = cursor.fetchall()
    conn.close()

    # Metadata definitions — normalized 4-table schema
    metadata = [
        # TABLE: employees
        {"table": "employees", "column": "id",                          "type": "int AUTO_INCREMENT",   "description": "Internal unique identifier (Primary Key)"},
        {"table": "employees", "column": "emp_id",                      "type": "varchar(50) UNIQUE",   "description": "Unique business Employee ID (e.g. EMP-2024-1001)"},
        {"table": "employees", "column": "emp_name",                    "type": "varchar(100)",         "description": "Full legal name of the employee"},
        {"table": "employees", "column": "email",                       "type": "varchar(100)",         "description": "Corporate email address (unique)"},
        {"table": "employees", "column": "date",                        "type": "date",                 "description": "Date of joining the organization"},
        {"table": "employees", "column": "basic_salary",                "type": "decimal(10,2)",        "description": "Base monthly salary — varies per employee even for same role (±20%)"},
        {"table": "employees", "column": "allowances",                  "type": "decimal(10,2)",        "description": "Calculated total from employee_allowances table (auto-updated)"},
        {"table": "employees", "column": "deductions",                  "type": "decimal(10,2)",        "description": "Calculated total from employee_taxes table (auto-updated)"},
        {"table": "employees", "column": "age",                         "type": "int",                  "description": "Age of the employee in years"},
        {"table": "employees", "column": "gender",                      "type": "varchar(20)",          "description": "Gender identification (Male / Female / Other)"},
        {"table": "employees", "column": "education",                   "type": "varchar(100)",         "description": "Highest education qualification"},
        {"table": "employees", "column": "title",                       "type": "varchar(100)",         "description": "Job designation / position title"},
        {"table": "employees", "column": "directorate",                 "type": "varchar(100)",         "description": "Organizational division (e.g. Engineering, Operations)"},
        {"table": "employees", "column": "department",                  "type": "varchar(100)",         "description": "Specific department within the directorate"},
        {"table": "employees", "column": "joining_year",                "type": "int",                  "description": "Year of joining the organization"},
        {"table": "employees", "column": "city",                        "type": "varchar(100)",         "description": "City of residence / employment"},
        {"table": "employees", "column": "payment_tier",                "type": "int",                  "description": "Salary tier: 1=Executive (≥80K), 2=Professional (≥50K), 3=Associate (<50K)"},
        {"table": "employees", "column": "ever_benched",                "type": "varchar(10)",          "description": "Whether the employee was ever benched (Yes/No)"},
        {"table": "employees", "column": "experience_in_current_domain","type": "int",                  "description": "Years of experience in current technology domain"},
        {"table": "employees", "column": "leave_or_not",                "type": "int",                  "description": "Leave status: 0=Active, 1=On Leave, 2=Medical, 3=Parental, 4=Unpaid, 5=Resigned"},
        # TABLE: employee_bank_details (1-to-1)
        {"table": "employee_bank_details", "column": "emp_id",          "type": "varchar(50) FK",       "description": "References employees.emp_id — one bank record per employee"},
        {"table": "employee_bank_details", "column": "bank_name",       "type": "varchar(100)",         "description": "Name of the bank used for salary credit"},
        {"table": "employee_bank_details", "column": "bank_account_num","type": "varchar(50)",          "description": "Unique bank account number — generated per employee"},
        # TABLE: employee_allowances (many-to-1)
        {"table": "employee_allowances", "column": "emp_id",            "type": "varchar(50) FK",       "description": "References employees.emp_id — multiple rows per employee"},
        {"table": "employee_allowances", "column": "allowance_type",    "type": "varchar(100)",         "description": "Type of allowance (meal_allowance, transportation_allowance, wife_allowance, etc.)"},
        {"table": "employee_allowances", "column": "amount",            "type": "decimal(10,2)",        "description": "Monthly amount for this specific allowance type"},
        # TABLE: employee_taxes (many-to-1)
        {"table": "employee_taxes", "column": "emp_id",                 "type": "varchar(50) FK",       "description": "References employees.emp_id — multiple rows per employee"},
        {"table": "employee_taxes", "column": "tax_type",               "type": "varchar(100)",         "description": "Type of deduction (retirement_insurance, professional_tax, income_tax, etc.)"},
        {"table": "employee_taxes", "column": "amount",                 "type": "decimal(10,2)",        "description": "Monthly deduction amount for this specific tax type"},
    ]
    
    return render_template('data_dictionary.html', preview_data=preview_data, metadata=metadata,
                           search_col=search_col, search_val=search_val, allowed_cols=allowed_cols)

@app.route('/download/<path:filename>')
def download_report(filename):
    """Allows downloading the Word reports directly from the server."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return send_from_directory(base_dir, filename, as_attachment=True)

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
