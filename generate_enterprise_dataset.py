import os
import random
import csv
from datetime import datetime, timedelta
from faker import Faker
import uuid

fake = Faker('en_IN')

# Configuration
NUM_EMPLOYEES = 5000
OUTPUT_DIR = "enterprise_dataset"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# --------------------------
# Definitions & Rules
# --------------------------
EDUCATION_CODES = {0: "High School", 1: "Diploma", 2: "Bachelor's Degree", 3: "Master's Degree", 4: "PhD"}
DEPARTMENTS = ["Software Development", "Data Science", "AI/ML", "Human Resources", "Finance", "Sales", "Marketing", "Operations", "Cyber Security", "DevOps", "Product Management", "Customer Support"]
LOCATIONS = ["Chennai", "Bangalore", "Hyderabad", "Pune", "Mumbai", "Delhi", "Noida", "Gurugram", "Kolkata", "Ahmedabad"]
BANKS = ["State Bank of India", "HDFC Bank", "ICICI Bank", "Axis Bank", "Kotak Mahindra Bank", "Canara Bank", "Punjab National Bank"]
HOLIDAY_DIST = [0]*80 + [1]*8 + [2]*6 + [3]*4 + [4]*2
EMAIL_TYPES = ["Payslip Delivery", "HR Communication", "Leave Request", "Policy Update", "Performance Review", "Manager Communication", "Payroll Query"]
EMAIL_STATUSES = ["Sent", "Delivered", "Replied", "Closed"]

ALLOWANCE_NAMES = ["House Rent Allowance", "Transport Allowance", "Medical Allowance", "Internet Allowance", "Special Allowance", "Travel Allowance", "Meal Allowance", "Performance Allowance", "Shift Allowance", "Remote Work Allowance"]
DEDUCTION_NAMES = ["Provident Fund", "Professional Tax", "Income Tax", "Insurance", "Gratuity Contribution"]

# Designation Rules
DESIGNATIONS = [
    {"title": "Intern", "tier": 3, "min_sal": 10000, "max_sal": 25000, "min_age": 21, "max_age": 24, "min_exp": 0, "max_exp": 1, "edu": [2]},
    {"title": "Trainee", "tier": 3, "min_sal": 20000, "max_sal": 40000, "min_age": 22, "max_age": 26, "min_exp": 0, "max_exp": 2, "edu": [2, 3]},
    {"title": "Associate Engineer", "tier": 3, "min_sal": 35000, "max_sal": 60000, "min_age": 23, "max_age": 30, "min_exp": 1, "max_exp": 4, "edu": [2, 3]},
    {"title": "Software Engineer", "tier": 2, "min_sal": 50000, "max_sal": 90000, "min_age": 25, "max_age": 35, "min_exp": 3, "max_exp": 7, "edu": [2, 3]},
    {"title": "Senior Software Engineer", "tier": 2, "min_sal": 80000, "max_sal": 150000, "min_age": 28, "max_age": 45, "min_exp": 5, "max_exp": 12, "edu": [2, 3, 4]},
    {"title": "Lead Engineer", "tier": 2, "min_sal": 120000, "max_sal": 250000, "min_age": 30, "max_age": 50, "min_exp": 8, "max_exp": 15, "edu": [2, 3, 4]},
    {"title": "Principal Engineer", "tier": 1, "min_sal": 200000, "max_sal": 400000, "min_age": 35, "max_age": 60, "min_exp": 12, "max_exp": 25, "edu": [3, 4]},
    {"title": "Manager", "tier": 2, "min_sal": 150000, "max_sal": 300000, "min_age": 32, "max_age": 50, "min_exp": 10, "max_exp": 20, "edu": [2, 3, 4]},
    {"title": "Senior Manager", "tier": 1, "min_sal": 250000, "max_sal": 500000, "min_age": 38, "max_age": 55, "min_exp": 15, "max_exp": 25, "edu": [3, 4]},
    {"title": "Director", "tier": 1, "min_sal": 400000, "max_sal": 1000000, "min_age": 45, "max_age": 65, "min_exp": 20, "max_exp": 35, "edu": [3, 4]},
]
# Weighted choice for designations (more juniors than seniors)
DESIG_WEIGHTS = [10, 15, 20, 25, 12, 8, 3, 4, 2, 1]

# Caches for uniqueness
email_cache = set()
phone_cache = set()
acc_cache = set()

employees = []
banks = []
components = []
holidays = []
payslips = []
emails = []

print(f"Generating {NUM_EMPLOYEES} employee records...")

# Generate Schema
with open(os.path.join(OUTPUT_DIR, 'schema.sql'), 'w') as f:
    f.write('''-- Enterprise Database Schema
CREATE TABLE IF NOT EXISTS employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    emp_id VARCHAR(50) UNIQUE NOT NULL,
    emp_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    date_of_birth DATE NOT NULL,
    joining_date DATE NOT NULL,
    basic_salary DECIMAL(12,2) NOT NULL,
    age INT NOT NULL,
    gender VARCHAR(20),
    education INT,
    title VARCHAR(100),
    department VARCHAR(100),
    posting_location VARCHAR(100),
    payment_tier INT
);
CREATE TABLE IF NOT EXISTS employee_bank_details (
    id INT AUTO_INCREMENT PRIMARY KEY,
    emp_id VARCHAR(50) UNIQUE NOT NULL,
    bank_name VARCHAR(100),
    bank_account_num VARCHAR(50) UNIQUE NOT NULL,
    ifsc_code VARCHAR(20)
);
CREATE TABLE IF NOT EXISTS employee_financial_components (
    id INT AUTO_INCREMENT PRIMARY KEY,
    emp_id VARCHAR(50) NOT NULL,
    component_name VARCHAR(100) NOT NULL,
    component_code TINYINT NOT NULL,
    amount DECIMAL(12,2)
);
CREATE TABLE IF NOT EXISTS payslip_master (
    payslip_id INT AUTO_INCREMENT PRIMARY KEY,
    payslip_no VARCHAR(50) UNIQUE,
    emp_id VARCHAR(50) NOT NULL,
    salary_month VARCHAR(20),
    salary_year INT,
    basic_salary DECIMAL(12,2),
    total_allowance DECIMAL(12,2),
    total_deduction DECIMAL(12,2),
    final_in_hand_salary DECIMAL(12,2),
    generated_on DATETIME
);
CREATE TABLE IF NOT EXISTS employee_holidays (
    id INT AUTO_INCREMENT PRIMARY KEY,
    emp_id VARCHAR(50) NOT NULL,
    holiday_code TINYINT
);
CREATE TABLE IF NOT EXISTS employee_emails (
    id INT AUTO_INCREMENT PRIMARY KEY,
    emp_id VARCHAR(50) NOT NULL,
    sender_email VARCHAR(100),
    receiver_email VARCHAR(100),
    subject VARCHAR(255),
    email_type VARCHAR(100),
    sent_timestamp DATETIME,
    response_timestamp DATETIME,
    response_time_hours DECIMAL(6,2),
    status VARCHAR(20)
);
''')

# --------------------------
# Generation Loop
# --------------------------
payslip_counter = 1
for i in range(1, NUM_EMPLOYEES + 1):
    emp_id = f"EMP-{str(i).zfill(5)}"
    gender = random.choice(["Male", "Female"])
    if gender == "Male":
        emp_name = fake.name_male()
    else:
        emp_name = fake.name_female()
        
    # Unique Email
    email = f"{emp_name.replace(' ', '.').lower()}{random.randint(1,999)}@hrsm.com"
    while email in email_cache:
        email = f"{emp_name.replace(' ', '.').lower()}{random.randint(1000,9999)}@hrsm.com"
    email_cache.add(email)
    
    # Unique Phone
    phone = fake.phone_number()
    while phone in phone_cache or len(phone) > 20:
        phone = fake.phone_number()
    phone_cache.add(phone)
    
    # Designation mapping
    desig = random.choices(DESIGNATIONS, weights=DESIG_WEIGHTS, k=1)[0]
    
    # Age & Dates
    age = random.randint(desig["min_age"], desig["max_age"])
    dob = datetime.now() - timedelta(days=age*365.25 + random.randint(0,364))
    
    exp_years = random.randint(desig["min_exp"], desig["max_exp"])
    joining = datetime.now() - timedelta(days=exp_years*365.25 + random.randint(0,364))
    
    # Must join after age 20
    min_joining_date = dob + timedelta(days=20*365.25)
    if joining < min_joining_date:
        joining = min_joining_date + timedelta(days=random.randint(10, 365))
        
    education = random.choice(desig["edu"])
    basic_salary = round(random.uniform(desig["min_sal"], desig["max_sal"]), 2)
    dept = random.choice(DEPARTMENTS)
    loc = random.choice(LOCATIONS)
    
    employees.append([emp_id, emp_name, email, phone, dob.strftime('%Y-%m-%d'), joining.strftime('%Y-%m-%d'), basic_salary, age, gender, education, desig["title"], dept, loc, desig["tier"]])
    
    # Bank Details
    bank_name = random.choice(BANKS)
    acc_num = f"{random.randint(1000000000, 9999999999)}"
    while acc_num in acc_cache:
        acc_num = f"{random.randint(1000000000, 9999999999)}"
    acc_cache.add(acc_num)
    
    ifsc = bank_name[:4].upper().replace(" ", "")[:4].ljust(4, 'X') + "0" + str(random.randint(100000, 999999))
    banks.append([emp_id, bank_name, acc_num, ifsc])
    
    # Holidays
    h_code = random.choice(HOLIDAY_DIST)
    holidays.append([emp_id, h_code])
    
    # Financial Components
    # Randomly pick 3-6 allowances and 2-4 deductions
    num_allow = random.randint(3, 6)
    num_deduct = random.randint(2, 4)
    emp_allow = random.sample(ALLOWANCE_NAMES, num_allow)
    emp_deduct = random.sample(DEDUCTION_NAMES, num_deduct)
    
    total_allow = 0
    total_deduct = 0
    
    for a in emp_allow:
        amt = round(basic_salary * random.uniform(0.02, 0.15), 2)
        total_allow += amt
        components.append([emp_id, a, 1, amt])
        
    for d in emp_deduct:
        amt = round(basic_salary * random.uniform(0.01, 0.10), 2)
        total_deduct += amt
        components.append([emp_id, d, 2, amt])
        
    final_salary = round(basic_salary + total_allow - total_deduct, 2)
    
    # 12 Months Payslips
    current_date = datetime.now()
    for m in range(12):
        month_date = current_date - timedelta(days=30*m)
        s_month = month_date.strftime('%B')
        s_year = month_date.year
        psl_num = f"PSL-{s_year}-{str(payslip_counter).zfill(6)}"
        payslip_counter += 1
        
        # Slight variation for older months (salary progression)
        if m > 0:
            hist_basic = round(basic_salary * (1 - 0.05*(m//12)), 2) # Simulate 5% raise per year
            h_allow = round(total_allow * (1 - 0.05*(m//12)), 2)
            h_deduct = round(total_deduct * (1 - 0.05*(m//12)), 2)
            h_final = round(hist_basic + h_allow - h_deduct, 2)
        else:
            hist_basic = basic_salary
            h_allow = total_allow
            h_deduct = total_deduct
            h_final = final_salary
            
        payslips.append([psl_num, emp_id, s_month, s_year, hist_basic, h_allow, h_deduct, h_final, month_date.strftime('%Y-%m-%d %H:%M:%S')])
        
    # Emails
    num_emails = random.randint(1, 10)
    for _ in range(num_emails):
        etype = random.choice(EMAIL_TYPES)
        subj = f"[{etype}] Notice for {emp_name}"
        sent = current_date - timedelta(days=random.randint(1, 365))
        status = random.choice(EMAIL_STATUSES)
        resp = ""
        resp_hrs = ""
        if status in ["Replied", "Closed"]:
            resp_hrs = round(random.uniform(0.1, 48.0), 2)
            resp = (sent + timedelta(hours=resp_hrs)).strftime('%Y-%m-%d %H:%M:%S')
            
        emails.append([emp_id, "admin@hrsm.com", email, subj, etype, sent.strftime('%Y-%m-%d %H:%M:%S'), resp, resp_hrs, status])

# --------------------------
# Write Outputs
# --------------------------
print("Writing CSVs...")
def write_csv(filename, headers, data):
    with open(os.path.join(OUTPUT_DIR, filename), 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(data)

write_csv('employees.csv', ['emp_id', 'emp_name', 'email', 'phone_number', 'date_of_birth', 'joining_date', 'basic_salary', 'age', 'gender', 'education', 'title', 'department', 'posting_location', 'payment_tier'], employees)
write_csv('employee_bank_details.csv', ['emp_id', 'bank_name', 'account_number', 'ifsc_code'], banks)
write_csv('employee_financial_components.csv', ['emp_id', 'component_name', 'component_code', 'amount'], components)
write_csv('employee_holidays.csv', ['emp_id', 'holiday_code'], holidays)
write_csv('payslip_master.csv', ['payslip_number', 'emp_id', 'salary_month', 'salary_year', 'basic_salary', 'total_allowance', 'total_deduction', 'final_in_hand_salary', 'generated_date'], payslips)
write_csv('employee_emails.csv', ['emp_id', 'sender_email', 'receiver_email', 'subject', 'email_type', 'sent_timestamp', 'response_timestamp', 'response_time_hours', 'status'], emails)

print("Writing SQL files...")
def chunk_list(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def write_sql(filename, table, cols, data, format_str):
    with open(os.path.join(OUTPUT_DIR, filename), 'w', encoding='utf-8') as f:
        for chunk in chunk_list(data, 1000):
            values = []
            for row in chunk:
                # Escape single quotes in strings
                clean_row = [str(x).replace("'", "''") if isinstance(x, str) else x for x in row]
                # Format NULLs
                clean_row = ['NULL' if x == '' else (f"'{x}'" if isinstance(x, str) else str(x)) for x in clean_row]
                values.append(f"({','.join(clean_row)})")
            f.write(f"INSERT IGNORE INTO {table} ({cols}) VALUES {','.join(values)};\n")

write_sql('insert_employees.sql', 'employees', 'emp_id, emp_name, email, phone_number, date_of_birth, joining_date, basic_salary, age, gender, education, title, department, posting_location, payment_tier', employees, "")
write_sql('insert_bank_details.sql', 'employee_bank_details', 'emp_id, bank_name, bank_account_num, ifsc_code', banks, "")
write_sql('insert_financial_components.sql', 'employee_financial_components', 'emp_id, component_name, component_code, amount', components, "")
write_sql('insert_holidays.sql', 'employee_holidays', 'emp_id, holiday_code', holidays, "")
write_sql('insert_payslips.sql', 'payslip_master', 'payslip_no, emp_id, salary_month, salary_year, basic_salary, total_allowance, total_deduction, final_in_hand_salary, generated_on', payslips, "")
write_sql('insert_employee_emails.sql', 'employee_emails', 'emp_id, sender_email, receiver_email, subject, email_type, sent_timestamp, response_timestamp, response_time_hours, status', emails, "")

print("Dataset generation complete!")
