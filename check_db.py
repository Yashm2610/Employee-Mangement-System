import pymysql

conn = pymysql.connect(host='localhost',user='root',password='yabh',database='employee_db',cursorclass=pymysql.cursors.DictCursor)
c = conn.cursor()

c.execute("SHOW TABLES")
tables = [row['Tables_in_employee_db'] for row in c.fetchall()]
print("Tables:", tables)

if 'Allowance' in tables:
    c.execute("DESCRIBE Allowance")
    print("Allowance Schema:", c.fetchall())
elif 'employee_allowance' in tables:
    c.execute("DESCRIBE employee_allowance")
    print("employee_allowance Schema:", c.fetchall())

if 'financial_component_master' in tables:
    c.execute("SELECT * FROM financial_component_master LIMIT 5")
    print("Financial components:", c.fetchall())

conn.close()
