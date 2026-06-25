import pymysql

conn = pymysql.connect(host='localhost', user='root', password='yabh', database='employee_db', cursorclass=pymysql.cursors.DictCursor)
c = conn.cursor()

query = """
CREATE OR REPLACE VIEW v_employees AS
SELECT 
    e.id AS id,
    e.emp_id AS emp_id,
    e.emp_name AS emp_name,
    e.email AS email,
    e.date_of_birth AS date_of_birth,
    e.joining_date AS joining_date,
    e.basic_salary AS basic_salary,
    e.age AS age,
    e.gender AS gender,
    e.education AS education,
    e.payment_tier AS payment_tier,
    e.phone_number AS phone_number,
    e.location_code AS location_code,
    e.department_code AS department_code,
    e.designation_code AS designation_code,
    e.uan_number AS uan_number,
    e.employment_type AS employment_type,
    COALESCE(l.Name, e.posting_location) AS posting_location,
    COALESCE(d.Name, e.department) AS department,
    COALESCE(des.Name, e.title) AS title
FROM Employee e
LEFT JOIN Master_table l ON CAST(e.location_code AS CHAR) = CAST(l.Value AS CHAR) AND l.MasterType='location'
LEFT JOIN Master_table d ON CAST(e.department_code AS CHAR) = CAST(d.Value AS CHAR) AND d.MasterType='department'
LEFT JOIN Master_table des ON CAST(e.designation_code AS CHAR) = CAST(des.Value AS CHAR) AND des.MasterType='designation'
"""

c.execute(query)
conn.commit()
conn.close()

print("View updated successfully.")
