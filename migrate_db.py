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

def migrate():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 1. Master Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS Master_table (
                id INT AUTO_INCREMENT PRIMARY KEY,
                MasterType VARCHAR(50),
                Value VARCHAR(50),
                Name VARCHAR(255),
                orderby INT
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)
            
            master_tables = [
                ('education_master', 'education', 'education_code', 'education_name'),
                ('department_master', 'department', 'department_code', 'department_name'),
                ('designation_master', 'designation', 'designation_code', 'designation_name'),
                ('location_master', 'location', 'location_code', 'location_name'),
                ('holiday_master', 'holiday', 'holiday_code', 'holiday_name')
            ]
            
            for t_name, m_type, val_col, name_col in master_tables:
                try:
                    cursor.execute(f"SELECT {val_col}, {name_col} FROM {t_name}")
                    rows = cursor.fetchall()
                    for row in rows:
                        cursor.execute(
                            "INSERT INTO Master_table (MasterType, Value, Name, orderby) VALUES (%s, %s, %s, %s)",
                            (m_type, str(row[val_col]), row[name_col], 0)
                        )
                except Exception as e:
                    print(f"Skipping or error in {t_name}: {e}")

            # 2. Consolidated Salary_Payslip Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS Salary_Payslip (
                id INT AUTO_INCREMENT PRIMARY KEY,
                RecordType VARCHAR(50),
                emp_id VARCHAR(50),
                month_num TINYINT,
                month_str VARCHAR(20),
                year_num SMALLINT,
                basic_salary DECIMAL(12,2),
                total_allowance DECIMAL(12,2),
                total_deduction DECIMAL(12,2),
                net_salary DECIMAL(12,2),
                working_days INT,
                present_days FLOAT,
                hra DECIMAL(12,2),
                sa DECIMAL(12,2),
                meal DECIMAL(12,2),
                medical DECIMAL(12,2),
                conveyance DECIMAL(12,2),
                pf DECIMAL(12,2),
                esic DECIMAL(12,2),
                tds DECIMAL(12,2),
                advance DECIMAL(12,2),
                other_dedn DECIMAL(12,2),
                super_annuation DECIMAL(12,2),
                bonus DECIMAL(12,2),
                status VARCHAR(50),
                payslip_no VARCHAR(20),
                generated_on DATETIME,
                created_by VARCHAR(100),
                created_on DATETIME,
                modified_by VARCHAR(100),
                modified_on DATETIME
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)
            
            # Migrate salary_overrides
            try:
                cursor.execute("SELECT * FROM salary_overrides")
                for row in cursor.fetchall():
                    cursor.execute("""
                        INSERT INTO Salary_Payslip (
                            RecordType, emp_id, month_num, year_num, working_days, present_days,
                            basic_salary, hra, sa, meal, medical, conveyance, pf, esic, tds,
                            advance, other_dedn, super_annuation, modified_on
                        ) VALUES ('Override', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        row['emp_id'], row['month_num'], row['year_num'], row['working_days'], row['present_days'],
                        row['basic_override'], row['hra_override'], row['sa_override'], row['meal_override'],
                        row['medical_override'], row['conveyance_override'], row['pf_override'], row['esic_override'],
                        row['tds_override'], row['advance_override'], row['other_dedn_override'], row['super_annuation_override'],
                        row['updated_at']
                    ))
            except Exception as e:
                print("salary_overrides missing or error:", e)

            # Migrate payslip_master
            try:
                cursor.execute("SELECT * FROM payslip_master")
                for row in cursor.fetchall():
                    cursor.execute("""
                        INSERT INTO Salary_Payslip (
                            RecordType, emp_id, month_str, year_num, basic_salary, total_allowance, total_deduction, net_salary,
                            working_days, present_days, payslip_no, generated_on, created_by, created_on, modified_by, modified_on
                        ) VALUES ('Payslip', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        row['emp_id'], row['salary_month'], row['salary_year'], row['basic_salary'], row['total_allowance'],
                        row['total_deduction'], row['final_in_hand_salary'], row['working_days'], row['present_days'],
                        row['payslip_no'], row['generated_on'], row['created_by'], row['created_on'], row['modified_by'], row['modified_on']
                    ))
            except Exception as e:
                print("payslip_master missing or error:", e)

            # Migrate payroll_snapshots
            try:
                cursor.execute("SELECT * FROM payroll_snapshots")
                for row in cursor.fetchall():
                    cursor.execute("""
                        INSERT INTO Salary_Payslip (
                            RecordType, emp_id, month_str, year_num, basic_salary, hra, bonus, pf, tds, net_salary, status, generated_on
                        ) VALUES ('Snapshot', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        row['emp_id'], row['month'], row['year'], row['basic_salary'], row['hra'], row['bonus'],
                        row['pf'], row['tax'], row['net_salary'], row['status'], row['generated_on']
                    ))
            except Exception as e:
                print("payroll_snapshots missing or error:", e)

            # 3. Rename Tables
            renames = [
                ('company_master', 'Company'),
                ('employees', 'Employee'),
                ('financial_component_master', 'Allowance'),
                ('employee_financial_components', 'Employee_Allowance'),
                ('payslip_templates', 'Payslip_format'),
                ('payslip_template_versions', 'Payslip_format_setting')
            ]
            for old_t, new_t in renames:
                try:
                    # Drop new table if exists to allow rename
                    cursor.execute(f"DROP TABLE IF EXISTS {new_t}")
                    cursor.execute(f"RENAME TABLE {old_t} TO {new_t}")
                except Exception as e:
                    print(f"Rename failed for {old_t} to {new_t}: {e}")

            # 4. Drop old tables
            tables_to_drop = [
                'education_master', 'department_master', 'designation_master', 'location_master', 'holiday_master',
                'employee_emails', 'employee_holidays', 'payslip_template_audit_log',
                'salary_overrides', 'payslip_master', 'payroll_snapshots'
            ]
            for td in tables_to_drop:
                try:
                    # check foreign key constraints, we might need to disable them temporarily
                    cursor.execute(f"DROP TABLE IF EXISTS {td}")
                except Exception as e:
                    print(f"Drop failed for {td}: {e}")

        conn.commit()
        print("Migration Completed Successfully.")
    except Exception as e:
        conn.rollback()
        print(f"Migration aborted due to error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    # Disable foreign key checks for the session
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SET FOREIGN_KEY_CHECKS=0")
        conn.commit()
    except: pass
    conn.close()
    
    migrate()
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SET FOREIGN_KEY_CHECKS=1")
        conn.commit()
    except: pass
    conn.close()
