file_path = r'c:\maxworth internship\app.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

import re

# We will use regex to find the whole export_employees route and replace it
pattern = re.compile(r"@app\.route\('/export/employees'\)\ndef export_employees\(\):.*?return send_file.*?mimetype='text/csv'\)", re.DOTALL)

new_route = '''@app.route('/export/employees')
def export_employees():
    fmt = request.args.get('format', 'csv')
    
    # Just return the empty template for importing
    columns = [
        'emp_id', 'emp_name', 'email', 'phone_number', 'date_of_birth', 
        'joining_date', 'basic_salary', 'age', 'gender', 'education', 
        'title', 'department', 'posting_location', 'payment_tier'
    ]
    import pandas as pd
    import io
    df = pd.DataFrame(columns=columns)
    
    if fmt == 'xlsx':
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Employees')
        output.seek(0)
        return send_file(output, as_attachment=True, download_name='employees_import_template.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    else:
        output = io.StringIO()
        df.to_csv(output, index=False)
        output.seek(0)
        return send_file(io.BytesIO(output.getvalue().encode()), as_attachment=True, download_name='employees_import_template.csv', mimetype='text/csv')'''

content = pattern.sub(new_route, content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("app.py export route updated successfully.")
