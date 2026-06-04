import re
import os

app_path = r'c:\maxworth internship\app.py'
html_path = r'c:\maxworth internship\templates\financial_master.html'

# --- UPDATE APP.PY ---
with open(app_path, 'r', encoding='utf-8') as f:
    app_content = f.read()

old_route = """@app.route('/financial_master')
def financial_master():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(\"\"\"
        SELECT e.emp_id, e.emp_name, e.basic_salary, 
               b.bank_name, b.bank_account_num, b.ifsc_code
        FROM employees e
        LEFT JOIN employee_bank_details b ON e.emp_id = b.emp_id
        ORDER BY e.emp_id
    \"\"\")
    employees_data = cursor.fetchall()
    
    cursor.execute('SELECT * FROM employee_financial_components')
    all_components = cursor.fetchall()
    conn.close()
    
    emp_components = {}
    for comp in all_components:
        eid = comp['emp_id']
        if eid not in emp_components:
            emp_components[eid] = []
        emp_components[eid].append(comp)
        
    return render_template('financial_master.html', employees=employees_data, emp_components=emp_components)"""

new_route = """@app.route('/financial_master')
def financial_master():
    search_col = request.args.get('search_col', 'emp_name').strip()
    search_val = request.args.get('search_val', '').strip()
    tier = request.args.get('tier', 'all').strip()
    sort_order = request.args.get('sort', 'date_desc').strip()

    allowed_cols = {
        'emp_name': 'Employee Name',
        'emp_id': 'Employee ID',
        'bank_name': 'Bank Name',
        'bank_account_num': 'Bank Account',
        'ifsc_code': 'IFSC Code'
    }
    
    if search_col not in allowed_cols:
        search_col = 'emp_name'
        
    query = \"\"\"
        SELECT e.emp_id, e.emp_name, e.basic_salary, e.joining_date, e.payment_tier,
               b.bank_name, b.bank_account_num, b.ifsc_code
        FROM employees e
        LEFT JOIN employee_bank_details b ON e.emp_id = b.emp_id
        WHERE 1=1
    \"\"\"
    params = []
    
    if search_val:
        if search_col in ['emp_name', 'emp_id']:
            query += f" AND e.{search_col} LIKE %s"
        else:
            query += f" AND b.{search_col} LIKE %s"
        params.append(f"%{search_val}%")
        
    if tier != 'all':
        query += " AND e.payment_tier = %s"
        params.append(int(tier))
        
    if sort_order == 'date_asc':
        query += " ORDER BY e.joining_date ASC"
    elif sort_order == 'date_desc':
        query += " ORDER BY e.joining_date DESC"
    else:
        query += " ORDER BY e.emp_id ASC"
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    employees_data = cursor.fetchall()
    
    cursor.execute('SELECT * FROM employee_financial_components')
    all_components = cursor.fetchall()
    conn.close()
    
    emp_components = {}
    for comp in all_components:
        eid = comp['emp_id']
        if eid not in emp_components:
            emp_components[eid] = []
        emp_components[eid].append(comp)
        
    return render_template('financial_master.html', 
                           employees=employees_data, 
                           emp_components=emp_components,
                           search_col=search_col,
                           search_val=search_val,
                           tier=tier,
                           sort=sort_order,
                           allowed_cols=allowed_cols)"""

app_content = app_content.replace(old_route, new_route)

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(app_content)

# --- UPDATE HTML ---
with open(html_path, 'r', encoding='utf-8') as f:
    html_content = f.read()

old_html_header = """<div class="row mb-4">
    <div class="col-12 d-flex justify-content-between align-items-center">
        <div>
            <h4 class="mb-1 text-primary d-flex align-items-center fw-bold">
                <i class="bi bi-cash-coin me-2"></i> Employee Financials
            </h4>
            <p class="text-secondary small mb-0">Manage individual Bank Details, Basic Salary, Allowances, and Deductions.</p>
        </div>
        <div class="w-25">
            <div class="input-group input-group-sm shadow-sm">
                <span class="input-group-text bg-white border-end-0"><i class="bi bi-search text-muted"></i></span>
                <input type="text" id="financialSearch" class="form-control border-start-0 ps-0" placeholder="Search by Name, Emp ID, A/c No..." onkeyup="filterFinancials()">
            </div>
        </div>
    </div>
</div>"""

new_html_header = """<div class="row mb-4 g-3 justify-content-between align-items-center">
    <div class="col-lg-4 col-12">
        <h4 class="mb-1 text-primary d-flex align-items-center fw-bold">
            <i class="bi bi-cash-coin me-2"></i> Employee Financials
            <span class="badge bg-secondary ms-2 fs-7 fw-normal">{{ employees|length }} Records</span>
        </h4>
        <p class="text-secondary small mb-0 mt-2">Manage individual Bank Details, Basic Salary, Allowances, and Deductions.</p>
    </div>
    
    <div class="col-lg-8 col-12">
        <form action="{{ url_for('financial_master') }}" method="GET" class="row g-2 justify-content-lg-end">
            <input type="hidden" name="sort" value="{{ sort }}">
            
            <div class="col-md-3 col-12">
                <select class="form-select border-secondary-subtle" name="search_col">
                    {% for col_key, col_label in allowed_cols.items() %}
                        <option value="{{ col_key }}" {% if search_col == col_key %}selected{% endif %}>{{ col_label }}</option>
                    {% endfor %}
                </select>
            </div>
            
            <div class="col-md-4 col-12">
                <div class="input-group">
                    <span class="input-group-text bg-white border-end-0 text-muted border-secondary-subtle"><i class="bi bi-search"></i></span>
                    <input type="text" class="form-control border-start-0 ps-0 border-secondary-subtle" name="search_val" placeholder="Enter filter value..." value="{{ search_val }}">
                    {% if search_val or tier != 'all' %}
                        <a href="{{ url_for('financial_master', sort=sort) }}" class="btn btn-outline-secondary d-flex align-items-center" title="Reset Filters">
                            <i class="bi bi-arrow-clockwise"></i>
                        </a>
                    {% endif %}
                </div>
            </div>
            
            <div class="col-md-3 col-12">
                <select class="form-select border-secondary-subtle" name="tier" onchange="this.form.submit()">
                    <option value="all" {% if tier == 'all' or not tier %}selected{% endif %}>All Slabs (Tiers)</option>
                    <option value="1" {% if tier == '1' %}selected{% endif %}>Executive (Tier 1)</option>
                    <option value="2" {% if tier == '2' %}selected{% endif %}>Professional (Tier 2)</option>
                    <option value="3" {% if tier == '3' %}selected{% endif %}>Associate (Tier 3)</option>
                </select>
            </div>
            
            <div class="col-md-2 col-12">
                <button class="btn btn-primary w-100" type="submit">
                    Apply
                </button>
            </div>
        </form>
    </div>
</div>

<div class="d-flex align-items-center justify-content-between p-3 bg-light rounded border border-light-subtle mb-4">
    <div class="d-flex align-items-center gap-2">
        <span class="text-secondary small fw-medium">Sort Order:</span>
        <div class="btn-group" role="group">
            <a href="{{ url_for('financial_master', search_col=search_col, search_val=search_val, tier=tier, sort='date_desc') }}" class="btn btn-sm {% if sort == 'date_desc' %}btn-secondary{% else %}btn-outline-secondary bg-white{% endif %}">Date (Newest)</a>
            <a href="{{ url_for('financial_master', search_col=search_col, search_val=search_val, tier=tier, sort='date_asc') }}" class="btn btn-sm {% if sort == 'date_asc' %}btn-secondary{% else %}btn-outline-secondary bg-white{% endif %}">Date (Oldest)</a>
        </div>
    </div>
</div>
"""

html_content = html_content.replace(old_html_header, new_html_header)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print("Financial master updated with advanced filter functionality.")
