import pymysql

conn = pymysql.connect(host='localhost', user='root', password='yabh', database='employee_db', cursorclass=pymysql.cursors.DictCursor)
c = conn.cursor()

# 1. Find all foreign keys referencing `employees`
c.execute("""
    SELECT TABLE_NAME, CONSTRAINT_NAME, COLUMN_NAME 
    FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
    WHERE REFERENCED_TABLE_NAME = 'employees' AND TABLE_SCHEMA = 'employee_db'
""")
fks = c.fetchall()

for fk in fks:
    table = fk['TABLE_NAME']
    constraint = fk['CONSTRAINT_NAME']
    column = fk['COLUMN_NAME']
    print(f"Dropping FK {constraint} on table {table}")
    
    # Drop the old FK
    c.execute(f"ALTER TABLE `{table}` DROP FOREIGN KEY `{constraint}`")
    
    # Re-add the FK pointing to the new `Employee` table
    # Assuming `Employee` has `emp_id` as the referenced column
    c.execute(f"ALTER TABLE `{table}` ADD CONSTRAINT `{constraint}` FOREIGN KEY (`{column}`) REFERENCES `Employee` (`emp_id`) ON DELETE CASCADE")

# Now drop the unused master tables
tables_to_drop = [
    'employees', 
    'company_master', 
    'department_master', 
    'designation_master', 
    'education_master', 
    'location_master'
]

for t in tables_to_drop:
    try:
        c.execute(f"DROP TABLE IF EXISTS `{t}`")
        print(f"Dropped {t}")
    except Exception as e:
        print(f"Failed to drop {t}: {e}")

conn.commit()
conn.close()
print("Cleanup complete.")
