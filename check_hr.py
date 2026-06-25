import pymysql

conn = pymysql.connect(host='localhost',user='root',password='yabh',database='employee_db',cursorclass=pymysql.cursors.DictCursor)
c = conn.cursor()
c.execute("SELECT id, username, role FROM users WHERE role='HR' OR username LIKE '%hr%'")
print(c.fetchall())
conn.close()
