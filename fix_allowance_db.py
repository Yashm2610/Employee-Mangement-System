import pymysql

conn = pymysql.connect(host='localhost',user='root',password='yabh',database='employee_db',cursorclass=pymysql.cursors.DictCursor)
c = conn.cursor()

# Get components
c.execute("SELECT * FROM financial_component_master")
comps = c.fetchall()

# Map component names to default calculation logic
def calc_amt(comp_name, basic, gross):
    name = comp_name.lower()
    if 'house rent' in name or 'hra' in name:
        return basic * 0.40
    elif 'special' in name or 'sa' in name:
        return basic * 0.20
    elif 'meal' in name:
        return 2000.0
    elif 'medical' in name:
        return 1500.0
    elif 'conveyance' in name or 'transport' in name:
        return 3000.0
    elif 'provident fund' in name or 'pf' in name:
        return min(basic * 0.12, 1800.0)
    elif 'income tax' in name or 'tds' in name:
        return (gross * 0.10) if (gross * 12 > 1200000) else 0.0
    elif 'professional tax' in name:
        return 200.0 if gross > 15000 else 0.0
    elif 'insurance' in name or 'esi' in name:
        return gross * 0.0075 if gross <= 21000 else 0.0
    elif 'internet' in name:
        return 1000.0
    return 0.0

c.execute("SELECT emp_id, basic_salary, payment_tier FROM v_employees")
employees = c.fetchall()

# Clear existing allowances to replace them with full breakdown
c.execute("TRUNCATE TABLE employee_allowance")

batch = []
next_id = 1
for e in employees:
    basic = float(e['basic_salary'] or 0)
    if basic == 0:
        tier = e['payment_tier'] or 3
        basic = 50000.0 if tier == 1 else (30000.0 if tier == 2 else 15000.0)
    
    # Calculate gross first for TDS/ESI
    gross = basic + (basic * 0.40) + (basic * 0.20) + 2000 + 1500 + 3000 + 1000
    
    for comp in comps:
        amt = calc_amt(comp['component_name'], basic, gross)
        if amt > 0:
            batch.append((next_id, e['emp_id'], comp['component_name'], comp['component_code'], amt))
            next_id += 1

c.executemany("INSERT INTO employee_allowance (id, emp_id, component_name, component_code, amount) VALUES (%s, %s, %s, %s, %s)", batch)

conn.commit()
print(f"Inserted {len(batch)} component records across {len(employees)} employees.")
conn.close()
