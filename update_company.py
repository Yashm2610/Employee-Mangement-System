import app

conn = app.get_db_connection()
cursor = conn.cursor()
cursor.execute("UPDATE company_master SET name = 'Maxworth'")
conn.commit()
conn.close()
print('Updated company_master successfully')
