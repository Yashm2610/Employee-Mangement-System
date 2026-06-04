import pymysql
import random

conn = pymysql.connect(
    host='localhost',
    user='root',
    password='yabh',
    database='employee_db',
    cursorclass=pymysql.cursors.DictCursor
)

try:
    cursor = conn.cursor()
    
    # Try adding phone_number column if it doesn't exist
    try:
        cursor.execute('ALTER TABLE employees ADD COLUMN phone_number VARCHAR(20) DEFAULT NULL')
    except Exception as e:
        pass # Probably already exists
        
    # Get all employees
    cursor.execute('SELECT id, emp_id FROM employees')
    employees = cursor.fetchall()
    
    banks = ['HDFC Bank', 'ICICI Bank', 'State Bank of India', 'Axis Bank', 'Kotak Mahindra', 'Punjab National Bank']
    
    update_emp_query = 'UPDATE employees SET phone_number = %s WHERE emp_id = %s'
    insert_bank_query = '''
        INSERT INTO employee_bank_details (emp_id, bank_name, bank_account_num, ifsc_code)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE 
            bank_name = VALUES(bank_name),
            bank_account_num = VALUES(bank_account_num),
            ifsc_code = VALUES(ifsc_code)
    '''
    
    for emp in employees:
        eid = emp['emp_id']
        
        # Phone
        random.seed(eid)
        phone = '+91-' + ''.join([str(random.randint(0, 9)) for _ in range(10)])
        cursor.execute(update_emp_query, (phone, eid))
        
        # Bank
        random.seed(eid + 'bank')
        b_name = random.choice(banks)
        acct = ''.join([str(random.randint(0, 9)) for _ in range(12)])
        ifsc = b_name[:4].upper().replace(' ', '') + '0' + ''.join([str(random.randint(0, 9)) for _ in range(6)])
        
        cursor.execute(insert_bank_query, (eid, b_name, acct, ifsc))
        
    conn.commit()
    print(f'Successfully populated bank details and phone numbers for {len(employees)} employees.')
except Exception as e:
    print('Error:', e)
finally:
    conn.close()
