import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace init_db()
new_init_db = """def init_db():
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
"""

content = re.sub(r"def init_db\(\):.*?(?=def generate_employee_details)", new_init_db, content, flags=re.DOTALL)

# Modify get_dynamic_payroll_and_bank
new_get_dynamic = """def get_dynamic_payroll_and_bank(basic_base, title, department, emp_id_or_seed):
    \"\"\"
    Computes payroll details and bank details.
    \"\"\"
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
"""

content = re.sub(r"def get_dynamic_payroll_and_bank.*?return[^\n]+\n", new_get_dynamic, content, flags=re.DOTALL)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated app.py!")
