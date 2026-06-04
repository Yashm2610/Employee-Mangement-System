import re

route_code = """
@app.route('/payslip_builder', methods=['GET', 'POST'])
def payslip_builder():
    \"\"\"Interactive UI for generating and customizing a Payslip in real-time.\"\"\"
    if request.method == 'POST':
        # Save the generated payslip to payslip_master
        emp_id = request.form.get('emp_id')
        salary_month = request.form.get('salary_month')
        salary_year = request.form.get('salary_year')
        basic_salary = float(request.form.get('basic_salary') or 0)
        total_allowance = float(request.form.get('total_allowance') or 0)
        total_deduction = float(request.form.get('total_deduction') or 0)
        final_in_hand_salary = float(request.form.get('final_in_hand_salary') or 0)
        
        if emp_id:
            conn = get_db_connection()
            try:
                with conn.cursor() as cursor:
                    cursor.execute(
                        \"\"\"INSERT INTO payslip_master 
                           (emp_id, salary_month, salary_year, basic_salary, total_allowance, total_deduction, final_in_hand_salary) 
                           VALUES (%s, %s, %s, %s, %s, %s, %s)\"\"\",
                        (emp_id, salary_month, salary_year, basic_salary, total_allowance, total_deduction, final_in_hand_salary)
                    )
                conn.commit()
                flash("Payslip saved to master records!", "success")
            except Exception as e:
                flash(f"Error saving payslip: {str(e)}", "danger")
            finally:
                conn.close()
        
        return redirect(url_for('payslip_builder'))
        
    return render_template('payslip_builder.html')
"""

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Append to end before if __name__
content = content.replace("if __name__ == '__main__':", route_code + "\nif __name__ == '__main__':")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Added payslip builder route")
