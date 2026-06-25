import pymysql
import werkzeug.security

conn = pymysql.connect(host='localhost',user='root',password='yabh',database='employee_db',cursorclass=pymysql.cursors.DictCursor)
c = conn.cursor()

pass_hash = werkzeug.security.generate_password_hash('hr123')

c.execute("SELECT * FROM users WHERE username='hr'")
hr_user = c.fetchone()

if hr_user:
    c.execute("UPDATE users SET password_hash = %s WHERE username='hr'", (pass_hash,))
    print("Updated HR user password to: hr123")
else:
    c.execute("SELECT MAX(user_id) as max_id FROM users")
    row = c.fetchone()
    next_id = (row['max_id'] or 0) + 1
    
    c.execute("INSERT INTO users (user_id, username, email, password_hash, role) VALUES (%s, 'hr', 'hr@maxworth.com', %s, 'HR')", (next_id, pass_hash,))
    print("Created new HR user: hr / hr123")

conn.commit()
conn.close()
