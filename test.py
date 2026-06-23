import pymysql
conn = pymysql.connect(host='localhost',user='root',password='yabh',database='employee_db',cursorclass=pymysql.cursors.DictCursor)
c=conn.cursor()
c.execute("SELECT * FROM Employee_Allowance WHERE emp_id LIKE '%136%' LIMIT 5")
print("Allowances for 136:", c.fetchall())

c.execute("SELECT * FROM Master_table WHERE MasterValue LIKE '%136%' OR MasterName LIKE '%136%'")
print("Master table:", c.fetchall())

conn.close()
