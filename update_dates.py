import app
import random

conn = app.get_db_connection()
cursor = conn.cursor()
cursor.execute('SELECT id, joining_date FROM employees')
emps = cursor.fetchall()

for e in emps:
    old_date = e['joining_date']
    if old_date:
        year = old_date.year
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        new_date = f"{year}-{month:02d}-{day:02d}"
        cursor.execute('UPDATE employees SET joining_date = %s WHERE id = %s', (new_date, e['id']))

conn.commit()
print(f'Updated {len(emps)} employees')
conn.close()
