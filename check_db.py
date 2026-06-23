import pymysql

DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = 'yabh'
DB_NAME = 'employee_db'

def get_db_connection():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )

def check_db():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Check Financial_component_master
            try:
                cursor.execute("SHOW COLUMNS FROM Financial_component_master")
                print("Financial_component_master columns:", [c['Field'] for c in cursor.fetchall()])
                cursor.execute("SELECT * FROM Financial_component_master")
                print("Financial_component_master data:", cursor.fetchall())
            except Exception as e:
                print("Error on Financial_component_master:", e)

            # Check Employee_Allowance
            try:
                cursor.execute("SHOW COLUMNS FROM Employee_Allowance")
                print("Employee_Allowance columns:", [c['Field'] for c in cursor.fetchall()])
                cursor.execute("SELECT COUNT(*) as c FROM Employee_Allowance")
                print("Employee_Allowance count:", cursor.fetchone()['c'])
                cursor.execute("SELECT COUNT(DISTINCT emp_id) as c FROM Employee_Allowance")
                print("Employee_Allowance distinct emp_id count:", cursor.fetchone()['c'])
            except Exception as e:
                print("Error on Employee_Allowance:", e)
                
            # Check Master_table if it has replaced Financial_component_master
            try:
                cursor.execute("SELECT * FROM Master_table WHERE MasterType LIKE '%financial%' OR MasterType LIKE '%allowance%'")
                print("Master_table financial entries:", cursor.fetchall())
            except Exception as e:
                print("Error on Master_table:", e)
                
            # Check Employee table
            try:
                cursor.execute("SELECT COUNT(*) as c FROM Employee")
                print("Employee count:", cursor.fetchone()['c'])
            except Exception as e:
                print("Error on Employee:", e)
                
    finally:
        conn.close()

if __name__ == '__main__':
    check_db()
