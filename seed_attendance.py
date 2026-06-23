import app
import datetime
import random
import calendar

def seed_attendance():
    conn = app.get_db_connection()
    cursor = conn.cursor()
    
    # 1. Create Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employee_attendance (
            id INT AUTO_INCREMENT PRIMARY KEY,
            emp_id VARCHAR(20),
            attendance_date DATE,
            status ENUM('Present', 'Absent', 'Half Day', 'Leave'),
            in_time TIME,
            out_time TIME,
            remarks VARCHAR(255),
            present_days INT DEFAULT 0,
            UNIQUE KEY unique_attendance (emp_id, attendance_date)
        )
    """)
    
    # 2. Check if data exists
    cursor.execute("SELECT COUNT(*) as count FROM employee_attendance")
    result = cursor.fetchone()
    if result and result['count'] > 0:
        print("Attendance data already exists. Skipping seed.")
        conn.close()
        return

    # 3. Fetch Employees
    cursor.execute("SELECT emp_id FROM employees")
    employees = cursor.fetchall()
    
    if not employees:
        print("No employees found to seed data.")
        conn.close()
        return

    # 4. Generate mock data for the current month (June 2026)
    year = 2026
    month = 6
    num_days = calendar.monthrange(year, month)[1]
    
    insert_query = """
        INSERT INTO employee_attendance (emp_id, attendance_date, status, in_time, out_time)
        VALUES (%s, %s, %s, %s, %s)
    """
    
    for emp in employees:
        emp_id = emp['emp_id']
        for day in range(1, num_days + 1):
            date_str = f"{year}-{month:02d}-{day:02d}"
            date_obj = datetime.date(year, month, day)
            
            # Skip weekends (Saturday=5, Sunday=6)
            if date_obj.weekday() >= 5:
                continue
                
            # Random status: 85% Present, 5% Absent, 5% Leave, 5% Half Day
            rand_val = random.random()
            if rand_val < 0.85:
                status = 'Present'
                # Randomize in-time around 9:00 AM to 9:30 AM
                in_hour = 9
                in_min = random.randint(0, 30)
                in_time = f"{in_hour:02d}:{in_min:02d}:00"
                # Randomize out-time around 5:30 PM to 6:30 PM
                out_hour = 17 + random.randint(0, 1)
                out_min = random.randint(0, 59)
                out_time = f"{out_hour:02d}:{out_min:02d}:00"
            elif rand_val < 0.90:
                status = 'Absent'
                in_time = None
                out_time = None
            elif rand_val < 0.95:
                status = 'Leave'
                in_time = None
                out_time = None
            else:
                status = 'Half Day'
                in_time = "09:00:00"
                out_time = "13:00:00"
                
            cursor.execute(insert_query, (emp_id, date_str, status, in_time, out_time))
            
    conn.commit()
    print("Mock attendance data seeded successfully!")
    conn.close()

if __name__ == '__main__':
    seed_attendance()
