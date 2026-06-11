import pymysql

conn = pymysql.connect(host='localhost', user='root', password='yabh', database='employee_db', autocommit=True)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS payslip_templates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    template_name VARCHAR(100) NOT NULL,
    version INT DEFAULT 1,
    is_default BOOLEAN DEFAULT FALSE,
    layout_json LONGTEXT,
    status VARCHAR(20) DEFAULT 'Draft',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS payslip_template_versions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    template_id INT,
    version_number INT,
    published_by INT,
    published_on DATETIME DEFAULT CURRENT_TIMESTAMP,
    change_notes TEXT,
    layout_json LONGTEXT,
    FOREIGN KEY (template_id) REFERENCES payslip_templates(id) ON DELETE CASCADE
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS payslip_template_audit_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    template_id INT,
    version_number INT,
    action_type VARCHAR(50),
    user_id INT,
    action_time DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

print("Successfully created Enterprise Payslip Designer tables.")
conn.close()
