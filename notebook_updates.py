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

def notebook_updates():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SET FOREIGN_KEY_CHECKS=0")
            
            # 1. Employee Table: employment_type to Master_table
            cursor.execute("SELECT DISTINCT employment_type FROM Employee WHERE employment_type IS NOT NULL AND employment_type NOT IN ('1', '2', '3', '4', '5')")
            types = cursor.fetchall()
            
            type_mapping = {}
            cursor.execute("SELECT Value, Name FROM Master_table WHERE MasterType = 'employment_type'")
            existing_types = cursor.fetchall()
            existing_max = 0
            for row in existing_types:
                type_mapping[row['Name']] = str(row['Value'])
                if row['Value'].isdigit() and int(row['Value']) > existing_max:
                    existing_max = int(row['Value'])

            for t in types:
                emp_type = t['employment_type']
                if emp_type not in type_mapping:
                    existing_max += 1
                    val_str = str(existing_max)
                    cursor.execute("INSERT INTO Master_table (MasterType, Value, Name, orderby) VALUES ('employment_type', %s, %s, %s)",
                                   (val_str, emp_type, 0))
                    type_mapping[emp_type] = val_str
            
            for name, val in type_mapping.items():
                cursor.execute("UPDATE Employee SET employment_type = %s WHERE employment_type = %s", (val, name))

            # 2. employee_attendance Table: status to Master_table & remarks
            cursor.execute("ALTER TABLE employee_attendance MODIFY status VARCHAR(50)")
            
            cursor.execute("SELECT DISTINCT status FROM employee_attendance WHERE status IS NOT NULL AND status NOT IN ('1', '2', '3', '4', '5', '6')")
            statuses = cursor.fetchall()
            
            status_mapping = {}
            cursor.execute("SELECT Value, Name FROM Master_table WHERE MasterType = 'attendance_status'")
            existing_statuses = cursor.fetchall()
            existing_status_max = 0
            for row in existing_statuses:
                status_mapping[row['Name']] = str(row['Value'])
                if row['Value'].isdigit() and int(row['Value']) > existing_status_max:
                    existing_status_max = int(row['Value'])

            for s in statuses:
                st = s['status']
                if st not in status_mapping:
                    existing_status_max += 1
                    val_str = str(existing_status_max)
                    cursor.execute("INSERT INTO Master_table (MasterType, Value, Name, orderby) VALUES ('attendance_status', %s, %s, %s)",
                                   (val_str, st, 0))
                    status_mapping[st] = val_str
            
            for name, val in status_mapping.items():
                cursor.execute("UPDATE employee_attendance SET status = %s WHERE status = %s", (val, name))

            absent_val = status_mapping.get('Absent', '2')
            half_day_val = status_mapping.get('Half Day', '3')
            cursor.execute("UPDATE employee_attendance SET remarks = 'Sick Leave' WHERE status = %s AND (remarks IS NULL OR remarks = '')", (absent_val,))
            cursor.execute("UPDATE employee_attendance SET remarks = 'Casual Leave' WHERE status = %s AND (remarks IS NULL OR remarks = '')", (half_day_val,))

            # 3. user_login_logs & users
            cursor.execute("UPDATE user_login_logs SET browser = 'Chrome', device = 'Windows Desktop' WHERE browser IS NULL")
            
            # Fix NULL employee_ids using unused employee IDs
            cursor.execute("SELECT user_id FROM users WHERE employee_id IS NULL")
            null_users = cursor.fetchall()
            
            if null_users:
                cursor.execute("SELECT emp_id FROM Employee WHERE emp_id NOT IN (SELECT employee_id FROM users WHERE employee_id IS NOT NULL)")
                available_emps = cursor.fetchall()
                
                for i, u in enumerate(null_users):
                    if i < len(available_emps):
                        cursor.execute("UPDATE users SET employee_id = %s WHERE user_id = %s", (available_emps[i]['emp_id'], u['user_id']))

            # 4. Payslip_format_setting
            cursor.execute("SELECT COUNT(*) as c FROM Payslip_format_setting")
            if cursor.fetchone()['c'] == 0:
                # Insert a Payslip_format first
                cursor.execute("INSERT IGNORE INTO Payslip_format (id, template_name, status) VALUES (1, 'Standard Format', 'Published')")
                cursor.execute("""
                INSERT INTO Payslip_format_setting (template_id, version_number, published_by, change_notes, layout_json)
                VALUES (1, 1, 1, 'Initial Published Format', '{}')
                """)

            cursor.execute("SET FOREIGN_KEY_CHECKS=1")

        conn.commit()
        print("Notebook Updates Completed Successfully.")
    except Exception as e:
        conn.rollback()
        print(f"Update aborted due to error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    notebook_updates()
