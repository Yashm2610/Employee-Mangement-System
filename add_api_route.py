import os
import shutil

src_logo = r'C:\Users\mathu\.gemini\antigravity-ide\brain\14f83aa3-2c83-489e-b487-c73ac310a318\starwell_inc_logo_1780561698280.png'
dest_logo = r'c:\maxworth internship\static\logo.png'

if os.path.exists(src_logo):
    if not os.path.exists(r'c:\maxworth internship\static'):
        os.makedirs(r'c:\maxworth internship\static')
    shutil.copy2(src_logo, dest_logo)

app_file = r'c:\maxworth internship\app.py'
with open(app_file, 'r', encoding='utf-8') as f:
    content = f.read()

api_route = '''
@app.route('/api/employee/<emp_id>')
def get_employee_data(emp_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Employee Details
            cursor.execute('SELECT * FROM employees WHERE emp_id = %s', (emp_id,))
            employee = cursor.fetchone()
            
            if not employee:
                return jsonify({'error': 'Employee not found'}), 404
                
            # Bank Details
            cursor.execute('SELECT * FROM employee_bank_details WHERE emp_id = %s', (emp_id,))
            bank = cursor.fetchone()
            
            # Financial Components
            cursor.execute('SELECT component_name, component_code, amount FROM employee_financial_components WHERE emp_id = %s', (emp_id,))
            financials = cursor.fetchall()
            
            return jsonify({
                'employee': employee,
                'bank': bank,
                'financials': financials
            })
    finally:
        conn.close()
'''

if '@app.route(\'/api/employee/<emp_id>\')' not in content:
    content = content.replace("if __name__ == '__main__':", api_route + "\nif __name__ == '__main__':")
    with open(app_file, 'w', encoding='utf-8') as f:
        f.write(content)
        
print('API route and logo added!')
