import sys

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

import_statement = "import json\nimport os\nimport tempfile\nfrom playwright.sync_api import sync_playwright\n"

if "from playwright.sync_api import sync_playwright" not in content:
    content = import_statement + content

new_routes = """
# --- ENTERPRISE PAYSLIP DESIGNER ROUTES ---

@app.route('/payslip_designer')
@hr_required
def payslip_designer():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT emp_id, emp_name FROM employees")
    employees = cursor.fetchall()
    conn.close()
    return render_template('payslip_designer.html', employees=employees)

@app.route('/api/fields/discover', methods=['GET'])
@hr_required
def api_discover_fields():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    tables = [
        'employees', 'employee_bank_details', 'employee_financial_components',
        'department_master', 'designation_master'
    ]
    
    schema = {}
    for table in tables:
        try:
            cursor.execute(f"SHOW COLUMNS FROM {table}")
            columns = [row['Field'] for row in cursor.fetchall()]
            schema[table] = columns
        except Exception as e:
            pass
            
    conn.close()
    return jsonify(schema)

@app.route('/api/templates', methods=['GET', 'POST'])
@hr_required
def api_templates():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'GET':
        cursor.execute("SELECT * FROM payslip_templates ORDER BY updated_at DESC")
        templates = cursor.fetchall()
        for t in templates:
            t['created_at'] = t['created_at'].isoformat() if t['created_at'] else None
            t['updated_at'] = t['updated_at'].isoformat() if t['updated_at'] else None
        conn.close()
        return jsonify(templates)
        
    if request.method == 'POST':
        data = request.json
        template_name = data.get('template_name', 'Untitled')
        layout_json = json.dumps(data.get('layout_json', {}))
        status = data.get('status', 'Draft')
        
        cursor.execute(
            "INSERT INTO payslip_templates (template_name, layout_json, status) VALUES (%s, %s, %s)",
            (template_name, layout_json, status)
        )
        template_id = cursor.lastrowid
        
        cursor.execute(
            "INSERT INTO payslip_template_versions (template_id, version_number, published_by, layout_json) VALUES (%s, %s, %s, %s)",
            (template_id, 1, session.get('user_id'), layout_json)
        )
        cursor.execute(
            "INSERT INTO payslip_template_audit_log (template_id, version_number, action_type, user_id) VALUES (%s, %s, %s, %s)",
            (template_id, 1, 'Create', session.get('user_id'))
        )
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'template_id': template_id})

@app.route('/api/preview-data', methods=['GET'])
@hr_required
def api_preview_data():
    emp_id = request.args.get('emp_id')
    month = request.args.get('month')
    year = request.args.get('year')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM v_employees WHERE emp_id = %s", (emp_id,))
    employee = cursor.fetchone() or {}
    
    cursor.execute("SELECT * FROM employee_bank_details WHERE emp_id = %s", (emp_id,))
    bank = cursor.fetchone() or {}
    
    cursor.execute("SELECT * FROM employee_financial_components WHERE emp_id = %s", (emp_id,))
    financials = cursor.fetchall()
    
    allowances = [f for f in financials if f['component_code'] == 1]
    deductions = [f for f in financials if f['component_code'] == 2]
    
    conn.close()
    
    preview_data = {
        'employees': employee,
        'employee_bank_details': bank,
        'employee_financial_components': financials,
        'allowances': allowances,
        'deductions': deductions
    }
    
    def serialize_val(val):
        from datetime import date, datetime
        from decimal import Decimal
        if isinstance(val, (date, datetime)): return val.isoformat()
        if isinstance(val, Decimal): return float(val)
        return val
        
    def walk_dict(d):
        for k, v in d.items():
            if isinstance(v, dict): walk_dict(v)
            elif isinstance(v, list): 
                for item in v:
                    if isinstance(item, dict): walk_dict(item)
            else:
                d[k] = serialize_val(v)
                
    walk_dict(preview_data)
    return jsonify(preview_data)

@app.route('/api/generate-payslip-pdf', methods=['POST'])
@hr_required
def api_generate_payslip_pdf():
    data = request.json
    html_content = data.get('html_content')
    template_id = data.get('template_id')
    
    if not html_content:
        return jsonify({'success': False, 'error': 'No HTML content provided'})
        
    try:
        fd, temp_pdf_path = tempfile.mkstemp(suffix='.pdf')
        os.close(fd)
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_content(html_content, wait_until="networkidle")
            page.pdf(path=temp_pdf_path, format="A4", print_background=True)
            browser.close()
        
        if template_id:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO payslip_template_audit_log (template_id, action_type, user_id) VALUES (%s, %s, %s)",
                (template_id, 'Generate PDF', session.get('user_id'))
            )
            conn.commit()
            conn.close()
            
        return send_file(temp_pdf_path, as_attachment=True, download_name='Payslip.pdf')
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

"""

content = content.replace("if __name__ == '__main__':", new_routes + "\nif __name__ == '__main__':")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Successfully injected APIs.")
