import pymysql
import werkzeug.security

conn = pymysql.connect(host='localhost',user='root',password='yabh',database='employee_db',cursorclass=pymysql.cursors.DictCursor)
c = conn.cursor()

accounts = [
    ('admin1', 'Admin', None),
    ('admin2', 'Admin', None),
    ('hr1', 'HR', None),
    ('hr2', 'HR', None),
    ('emp1', 'Employee', 'EMP-00001'),
    ('emp2', 'Employee', 'EMP-00002')
]

for username, role, emp_id in accounts:
    pass_hash = werkzeug.security.generate_password_hash(username) # password = username
    email = f"{username}@maxworth.com"
    
    # Check if exists
    c.execute("SELECT user_id FROM users WHERE username=%s", (username,))
    row = c.fetchone()
    if row:
        c.execute("UPDATE users SET password_hash=%s, role=%s, employee_id=%s, email=%s WHERE username=%s",
                  (pass_hash, role, emp_id, email, username))
    else:
        c.execute("SELECT MAX(user_id) as max_id FROM users")
        max_id_row = c.fetchone()
        next_id = (max_id_row['max_id'] or 0) + 1
        c.execute("INSERT INTO users (user_id, username, email, password_hash, role, employee_id) VALUES (%s, %s, %s, %s, %s, %s)",
                  (next_id, username, email, pass_hash, role, emp_id))

conn.commit()
conn.close()
print("Setup complete")
