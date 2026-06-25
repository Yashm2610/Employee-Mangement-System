import pymysql
import werkzeug.security

conn = pymysql.connect(host='localhost',user='root',password='yabh',database='employee_db',cursorclass=pymysql.cursors.DictCursor)
c = conn.cursor()
c.execute("SELECT * FROM users")
users = c.fetchall()
print("All users:")
for u in users:
    print(u['username'], u['role'])

# Now let's forcefully reset the 'admin' and 'hr' passwords if they exist to 'admin123' and 'hr123'
new_hr_pass = werkzeug.security.generate_password_hash('hr123')
new_admin_pass = werkzeug.security.generate_password_hash('admin123')

c.execute("UPDATE users SET password_hash = %s WHERE username = 'hr'", (new_hr_pass,))
c.execute("UPDATE users SET password_hash = %s WHERE username = 'admin'", (new_admin_pass,))
conn.commit()

print("Passwords reset successfully.")
conn.close()
