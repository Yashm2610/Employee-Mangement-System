import pymysql
import sys

def test():
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        db='employee_db',
        cursorclass=pymysql.cursors.DictCursor
    )
    cursor = conn.cursor()
    query = """
        SELECT * FROM (
            SELECT 
                e.*,
                b.bank_name,
                b.bank_account_num,
                COALESCE(a.meal_allowance, 0) AS meal_allowance
            FROM employees e
            LEFT JOIN employee_bank_details b ON e.emp_id = b.emp_id
            LEFT JOIN (
                SELECT 
                    emp_id,
                    SUM(CASE WHEN allowance_type = 'meal_allowance' THEN amount ELSE 0 END) AS meal_allowance
                FROM employee_allowances
                GROUP BY emp_id
            ) a ON e.emp_id = a.emp_id
        ) AS emp_details LIMIT 1
    """
    cursor.execute(query)
    res = cursor.fetchall()
    print(res)
    
if __name__ == '__main__':
    test()
