import json
from app import get_db_connection
conn = get_db_connection()
cursor = conn.cursor()
cursor.execute('SHOW TABLES')
tables = [list(t.values())[0] for t in cursor.fetchall()]
empty_tables = []
table_info = {}
for t in tables:
    if t.startswith('v_'): continue
    cursor.execute(f'SELECT COUNT(*) as c FROM {t}')
    count = cursor.fetchone()['c']
    if count == 0: empty_tables.append(t)
    cursor.execute(f'DESCRIBE {t}')
    schema = cursor.fetchall()
    table_info[t] = {'count': count, 'columns': [col['Field'] for col in schema]}
with open('C:\\\\Users\\\\mathu\\\\.gemini\\\\antigravity-ide\\\\brain\\\\db_analysis.json', 'w') as f:
    json.dump({'empty_tables': empty_tables, 'table_info': table_info}, f, indent=2)
print('Done')
