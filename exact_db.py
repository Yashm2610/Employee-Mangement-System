import pymysql

conn = pymysql.connect(host='localhost',user='root',password='yabh',database='employee_db',cursorclass=pymysql.cursors.DictCursor)
c = conn.cursor()

# 1. Update financial_component_master
c.execute("TRUNCATE TABLE financial_component_master")

exact_comps = [
    ('HRA', 1),
    ('SA', 1),
    ('Meal Allow.', 1),
    ('Medical', 1),
    ('Conveyance', 1),
    ('PF', 2),
    ('ESIC', 2),
    ('TDS', 2),
    ('Advance', 2)
]

c.executemany("INSERT INTO financial_component_master (component_name, component_code, Cname, CreatedBy) VALUES (%s, %s, 'System', 'System')", exact_comps)

# 2. Get the new components to map their names
c.execute("SELECT * FROM financial_component_master")
comps = c.fetchall()

def calc_amt(comp_name, basic, gross):
    name = comp_name
    if name == 'HRA':
        return basic * 0.40
    elif name == 'SA':
        return basic * 0.20
    elif name == 'Meal Allow.':
        return 2000.0
    elif name == 'Medical':
        return 1500.0
    elif name == 'Conveyance':
        return 3000.0
    elif name == 'PF':
        return min(basic * 0.12, 1800.0)
    elif name == 'TDS':
        return (gross * 0.10 / 12) if (gross * 12 > 1200000) else 0.0 # prorated monthly TDS roughly
    elif name == 'ESIC':
        return gross * 0.0075 if gross <= 21000 else 0.0
    elif name == 'Advance':
        return 0.0
    return 0.0

c.execute("SELECT emp_id, basic_salary, payment_tier FROM v_employees")
employees = c.fetchall()

# 3. Clear and repopulate employee_allowance with EXACT names
c.execute("TRUNCATE TABLE employee_allowance")

batch = []
next_id = 1
for e in employees:
    basic = float(e['basic_salary'] or 0)
    if basic == 0:
        tier = e['payment_tier'] or 3
        basic = 50000.0 if tier == 1 else (30000.0 if tier == 2 else 15000.0)
    
    # Calculate gross first for TDS/ESI (Base gross for month)
    gross = basic + (basic * 0.40) + (basic * 0.20) + 2000 + 1500 + 3000
    
    for comp in comps:
        amt = calc_amt(comp['component_name'], basic, gross)
        if amt >= 0: # include all components even if 0, so it perfectly mirrors the columns
            batch.append((next_id, e['emp_id'], comp['component_name'], comp['component_code'], amt))
            next_id += 1

c.executemany("INSERT INTO employee_allowance (id, emp_id, component_name, component_code, amount) VALUES (%s, %s, %s, %s, %s)", batch)

conn.commit()
print(f"Master components replaced. Inserted {len(batch)} exact component records across {len(employees)} employees.")
conn.close()
