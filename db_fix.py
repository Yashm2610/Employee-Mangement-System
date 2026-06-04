import pymysql

def fix_db():
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='yabh',
        database='employee_db',
        cursorclass=pymysql.cursors.DictCursor
    )
    try:
        with conn.cursor() as cursor:
            # Add ifsc_code
            try:
                cursor.execute("ALTER TABLE employee_bank_details ADD COLUMN ifsc_code VARCHAR(20) DEFAULT 'BOFA0000001'")
                print("Added ifsc_code")
            except Exception as e:
                print(f"ifsc_code error: {e}")

            # Add columns to employees
            cols = [
                ("date_of_birth", "DATE DEFAULT '1990-01-01'"),
                ("joining_date", "DATE DEFAULT '2026-01-01'"),
                ("posting_location", "VARCHAR(100) DEFAULT 'Bangalore'"),
                ("education", "INT DEFAULT 2")
            ]
            for c, t in cols:
                try:
                    cursor.execute(f"ALTER TABLE employees ADD COLUMN {c} {t}")
                    print(f"Added {c}")
                except Exception as e:
                    print(f"{c} error: {e}")
                    
            # Try to drop old columns from employees just in case
            to_drop = ['date', 'city', 'directorate', 'joining_year', 'ever_benched', 'experience_in_current_domain', 'leave_or_not']
            for d in to_drop:
                try:
                    cursor.execute(f"ALTER TABLE employees DROP COLUMN {d}")
                    print(f"Dropped {d}")
                except Exception as e:
                    print(f"{d} drop error: {e}")
                    
        conn.commit()
    finally:
        conn.close()

if __name__ == '__main__':
    fix_db()
