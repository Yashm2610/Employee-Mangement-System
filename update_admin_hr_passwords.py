import app
from werkzeug.security import generate_password_hash

def update_passwords():
    conn = app.get_db_connection()
    cursor = conn.cursor()
    
    admin_hash = generate_password_hash('admin')
    hr_hash = generate_password_hash('hr123')
    
    cursor.execute("UPDATE users SET password_hash = %s WHERE role = 'Admin'", (admin_hash,))
    cursor.execute("UPDATE users SET password_hash = %s WHERE role = 'HR'", (hr_hash,))
    
    conn.commit()
    conn.close()
    print('Admin and HR passwords updated!')

if __name__ == '__main__':
    update_passwords()
