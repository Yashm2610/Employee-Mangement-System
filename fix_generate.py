import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_generate_func = """def generate_employee_details(row, offset_index):
    \"\"\"
    Generates realistic employee details from a row of the Kaggle Employee dataset.
    Returns a dict with all fields for employees + satellite tables.
    \"\"\"
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
"""

content = re.sub(r"def generate_employee_details\(row, offset_index\):.*?return \{.*?\n    \}", new_generate_func, content, flags=re.DOTALL)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated generate_employee_details!")
