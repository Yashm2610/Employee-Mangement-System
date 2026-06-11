import app
def update_admin_hr():
    conn = app.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, role, username FROM users WHERE role IN ('Admin', 'HR') ORDER BY role, user_id")
    rows = cursor.fetchall()
    
    admin_count = 1
    hr_count = 1
    
    for r in rows:
        if r['username'] in ('admin', 'hr1', 'hr2'): # Skip predefined
            continue
            
        while True:
            if r['role'] == 'Admin':
                username = f'admin{admin_count}'
                admin_count += 1
            else:
                username = f'hr{hr_count}'
                hr_count += 1
                
            # check if exists
            cursor.execute("SELECT user_id FROM users WHERE username = %s", (username,))
            if not cursor.fetchone():
                break
                
        cursor.execute('UPDATE users SET username = %s WHERE user_id = %s', (username, r['user_id']))
        
    conn.commit()
    conn.close()
    print('Admin/HR usernames updated!')

if __name__ == '__main__':
    update_admin_hr()
