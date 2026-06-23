import pymysql
from datetime import datetime

DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = 'yabh'
DB_NAME = 'employee_db'

conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME, cursorclass=pymysql.cursors.DictCursor)

try:
    with conn.cursor() as cursor:
        # Get unique components from Employee_Allowance
        cursor.execute("SELECT DISTINCT component_name, component_code FROM Employee_Allowance")
        components = cursor.fetchall()
        
        # Insert into Financial_component_master
        for comp in components:
            cursor.execute("SELECT COUNT(*) as c FROM Financial_component_master WHERE component_name = %s", (comp['component_name'],))
            if cursor.fetchone()['c'] == 0:
                cursor.execute("""
                    INSERT INTO Financial_component_master 
                    (component_name, component_code, Cname, CreatedBy, CreatedOn, IActive) 
                    VALUES (%s, %s, 'System', 'System', %s, 1)
                """, (comp['component_name'], comp['component_code'], datetime.now()))
        
        conn.commit()
        print("Financial_component_master populated successfully!")
        
        # Also print some stats about Employee_Allowance to confirm
        cursor.execute("SELECT COUNT(*) as c FROM Employee_Allowance")
        print("Employee_Allowance total rows:", cursor.fetchone()['c'])
        
        cursor.execute("SELECT COUNT(DISTINCT emp_id) as c FROM Employee_Allowance")
        print("Employee_Allowance unique employees:", cursor.fetchone()['c'])
        
        cursor.execute("SELECT COUNT(*) as c FROM Employee WHERE employment_status != 'Terminated' or employment_status IS NULL")
        
finally:
    conn.close()
