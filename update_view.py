import pymysql

DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = 'yabh'
DB_NAME = 'employee_db'

conn = pymysql.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME,
    cursorclass=pymysql.cursors.DictCursor
)

try:
    with conn.cursor() as cursor:
        cursor.execute("DROP VIEW IF EXISTS v_employees")
        cursor.execute("""
        CREATE VIEW v_employees AS 
        SELECT 
            e.id, e.emp_id, e.emp_name, e.email, e.date_of_birth, e.joining_date, 
            e.basic_salary, e.age, e.gender, e.education, e.payment_tier, e.phone_number, 
            e.location_code, e.department_code, e.designation_code, e.uan_number, e.employment_type,
            COALESCE(l.Name, e.posting_location) AS posting_location,
            COALESCE(d.Name, e.department) AS department,
            COALESCE(des.Name, e.title) AS title
        FROM Employee e
        LEFT JOIN Master_table l ON e.location_code = l.Value AND l.MasterType = 'location'
        LEFT JOIN Master_table d ON e.department_code = d.Value AND d.MasterType = 'department'
        LEFT JOIN Master_table des ON e.designation_code = des.Value AND des.MasterType = 'designation'
        """)
    conn.commit()
    print("v_employees view updated.")
finally:
    conn.close()
