import pymysql
conn = pymysql.connect(host='localhost',user='root',password='yabh',database='employee_db')
c=conn.cursor()
c.execute('SHOW TABLES')
tables=[t[0] for t in c.fetchall()]
for t in tables:
    try:
        c.execute('SELECT COUNT(*) FROM '+t)
        print(f"{t}: {c.fetchone()[0]}")
    except:
        pass
conn.close()
