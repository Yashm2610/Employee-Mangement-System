import pymysql
conn = pymysql.connect(host='localhost',user='root',password='yabh',database='employee_db',cursorclass=pymysql.cursors.DictCursor)
c=conn.cursor()
c.execute("SELECT emp_id, COUNT(*) as c FROM Employee_Allowance GROUP BY emp_id ORDER BY c DESC LIMIT 10")
print("Top emp_ids by allowance count:", c.fetchall())

c.execute("SELECT emp_id, COUNT(*) as c FROM Employee_Allowance GROUP BY emp_id ORDER BY c ASC LIMIT 10")
print("Bottom emp_ids by allowance count:", c.fetchall())

c.execute("SELECT COUNT(*) as working FROM Employee WHERE employment_status != 'Terminated' or employment_status IS NULL")
print("Working employees:", c.fetchone())

conn.close()
