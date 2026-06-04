import pymysql

def alter_payslip_master():
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='yabh',
        database='employee_db',
        cursorclass=pymysql.cursors.DictCursor
    )
    
    try:
        with conn.cursor() as cursor:
            # 1. Add payslip_no
            try:
                cursor.execute("ALTER TABLE payslip_master ADD COLUMN payslip_no VARCHAR(20) UNIQUE AFTER payslip_id;")
                print("Added payslip_no")
            except Exception as e:
                print(f"payslip_no error: {e}")
            
            # 2. Add salary_month
            try:
                cursor.execute("ALTER TABLE payslip_master ADD COLUMN salary_month VARCHAR(20) AFTER emp_id;")
                print("Added salary_month")
            except Exception as e:
                print(f"salary_month error: {e}")
                
            # 3. Add salary_year
            try:
                cursor.execute("ALTER TABLE payslip_master ADD COLUMN salary_year INT AFTER salary_month;")
                print("Added salary_year")
            except Exception as e:
                print(f"salary_year error: {e}")
                
        conn.commit()
        print("Database altered successfully!")
    finally:
        conn.close()

if __name__ == '__main__':
    alter_payslip_master()
