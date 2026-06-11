import app
from werkzeug.security import generate_password_hash

def setup_logins():
    conn = app.get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT emp_id, email FROM employees WHERE emp_id != 'EMP-00001'")
    employees = cursor.fetchall()
    
    default_hash = generate_password_hash('emp123')
    count = 0
    
    for emp in employees:
        emp_id = emp['emp_id']
        num = int(emp_id.split('-')[1])
        username = f"emp{num}"
        email = emp['email']
        
        # Check if already exists
        cursor.execute("SELECT user_id FROM users WHERE employee_id = %s", (emp_id,))
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute("UPDATE users SET username = %s, password_hash = %s WHERE user_id = %s", (username, default_hash, existing['user_id']))
        else:
            # Check if username exists
            cursor.execute("SELECT user_id FROM users WHERE username = %s", (username,))
            ex_u = cursor.fetchone()
            if ex_u:
                cursor.execute("UPDATE users SET employee_id = %s, password_hash = %s WHERE user_id = %s", (emp_id, default_hash, ex_u['user_id']))
            else:
                # Find an unassigned user
                cursor.execute("SELECT user_id FROM users WHERE employee_id IS NULL AND role = 'Employee' LIMIT 1")
                unassigned = cursor.fetchone()
                if unassigned:
                    cursor.execute("UPDATE users SET employee_id = %s, username = %s, email = %s, password_hash = %s WHERE user_id = %s", (emp_id, username, email, default_hash, unassigned['user_id']))
                else:
                    print(f"No unassigned user slots left for {emp_id}")
                    
        count += 1
        if count % 1000 == 0:
            print(f"Processed {count} employees...")
            
    conn.commit()
    conn.close()
    print("Done setting up logins!")

if __name__ == '__main__':
    setup_logins()
