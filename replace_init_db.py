import re

new_init_db = """def init_db():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # --- Main employees table ---
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS employees (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    emp_id VARCHAR(50) NOT NULL UNIQUE,
                    emp_name VARCHAR(100) NOT NULL,
                    email VARCHAR(100) NOT NULL,
                    date_of_birth DATE NOT NULL,
                    joining_date DATE NOT NULL,
                    basic_salary DECIMAL(10,2) NOT NULL,
                    allowances DECIMAL(10,2) DEFAULT 0.00,
                    deductions DECIMAL(10,2) DEFAULT 0.00,
                    age INT NOT NULL,
                    gender VARCHAR(20) DEFAULT 'Male',
                    education INT DEFAULT 2,
                    title VARCHAR(100) DEFAULT 'Software Engineer',
                    department VARCHAR(100) DEFAULT 'General Affairs',
                    posting_location VARCHAR(100) DEFAULT 'Bangalore',
                    payment_tier INT NOT NULL
                )
            ''')
            
            # --- Normalized satellite tables ---
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS employee_bank_details (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    emp_id VARCHAR(50) NOT NULL UNIQUE,
                    bank_name VARCHAR(100) DEFAULT 'Bank of America',
                    bank_account_num VARCHAR(50) DEFAULT '0000000000',
                    ifsc_code VARCHAR(20) DEFAULT 'BOFA0000001',
                    FOREIGN KEY (emp_id) REFERENCES employees(emp_id) ON DELETE CASCADE
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS employee_financial_components (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    emp_id VARCHAR(50) NOT NULL,
                    component_name VARCHAR(100) NOT NULL,
                    code INT NOT NULL,
                    amount DECIMAL(10,2) DEFAULT 0.00,
                    FOREIGN KEY (emp_id) REFERENCES employees(emp_id) ON DELETE CASCADE
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS payslip_master (
                    payslip_id INT AUTO_INCREMENT PRIMARY KEY,
                    emp_id VARCHAR(50) NOT NULL,
                    salary_month VARCHAR(20) NOT NULL,
                    salary_year INT NOT NULL,
                    basic_salary DECIMAL(10,2) DEFAULT 0.00,
                    total_allowance DECIMAL(10,2) DEFAULT 0.00,
                    total_deduction DECIMAL(10,2) DEFAULT 0.00,
                    final_in_hand_salary DECIMAL(10,2) DEFAULT 0.00,
                    generated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (emp_id) REFERENCES employees(emp_id) ON DELETE CASCADE
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS employee_holidays (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    emp_id VARCHAR(50) NOT NULL,
                    holiday INT NOT NULL,
                    FOREIGN KEY (emp_id) REFERENCES employees(emp_id) ON DELETE CASCADE
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS employee_emails (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    emp_id VARCHAR(50) NOT NULL,
                    sender_email VARCHAR(100) DEFAULT 'admin@maxworth.com',
                    receiver_email VARCHAR(100),
                    sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    subject VARCHAR(255),
                    body TEXT,
                    response_received_at DATETIME,
                    response_notes TEXT,
                    status VARCHAR(20) DEFAULT 'Sent',
                    FOREIGN KEY (emp_id) REFERENCES employees(emp_id) ON DELETE CASCADE
                )
            ''')

        conn.commit()
    except Exception as e:
        print(f"Error initializing DB: {e}")
    finally:
        conn.close()
"""

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find init_db
pattern = r"def init_db\(\):.*?conn\.close\(\)"
content = re.sub(pattern, new_init_db, content, flags=re.DOTALL)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Replaced init_db!")
