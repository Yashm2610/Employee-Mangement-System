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
        for t in ['salary_overrides', 'payslip_master', 'payroll_snapshots']:
            try:
                cursor.execute(f"DESCRIBE {t}")
                cols = cursor.fetchall()
                print(f"--- {t} ---")
                for c in cols:
                    print(f"{c['Field']}: {c['Type']}")
            except Exception as e:
                print(f"Table {t} error: {e}")
finally:
    conn.close()
