import pymysql

conn = pymysql.connect(host='localhost', user='root', password='yabh', database='employee_db', autocommit=True)
cursor = conn.cursor()

# 1. Company Master
cursor.execute("""
CREATE TABLE IF NOT EXISTS company_master (
    company_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    gst_no VARCHAR(50),
    address TEXT,
    logo_url VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

# Ensure a default company exists
cursor.execute("SELECT COUNT(*) as count FROM company_master")
if cursor.fetchone()[0] == 0:
    cursor.execute("INSERT INTO company_master (name, gst_no) VALUES ('HRSM Inc.', '27AAAAA0000A1Z5')")

# 2. Payroll Snapshots
cursor.execute("""
CREATE TABLE IF NOT EXISTS payroll_snapshots (
    snapshot_id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT DEFAULT 1,
    emp_id VARCHAR(50),
    month VARCHAR(20),
    year INT,
    basic_salary DECIMAL(10,2) DEFAULT 0,
    hra DECIMAL(10,2) DEFAULT 0,
    bonus DECIMAL(10,2) DEFAULT 0,
    pf DECIMAL(10,2) DEFAULT 0,
    tax DECIMAL(10,2) DEFAULT 0,
    net_salary DECIMAL(10,2) DEFAULT 0,
    status VARCHAR(50) DEFAULT 'Locked',
    generated_on DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES company_master(company_id) ON DELETE CASCADE
)
""")

# 3. Alter existing tables if needed
try:
    cursor.execute("ALTER TABLE payslip_templates ADD COLUMN company_id INT DEFAULT 1")
    cursor.execute("ALTER TABLE payslip_templates ADD COLUMN formulas_json LONGTEXT")
except:
    pass

print("Phase 1 Database Schema initialized successfully.")
conn.close()
