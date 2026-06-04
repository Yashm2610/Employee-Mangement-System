import re

route_code = """
@app.route('/payslip_builder', methods=['GET', 'POST'])
def payslip_builder():
    \"\"\"Interactive UI for generating and customizing a Payslip in real-time.\"\"\"
    if request.method == 'POST':
        # Save the generated payslip to payslip_master
        emp_id = request.form.get('emp_id')
        basic_salary = float(request.form.get('basic_salary') or 0)
        total_allowance = float(request.form.get('total_allowance') or 0)
        total_deduction = float(request.form.get('total_deduction') or 0)
        final_in_hand_salary = float(request.form.get('final_in_hand_salary') or 0)
        
        # Dynamic components
        comp_names = request.form.getlist('component_name[]')
        comp_codes = request.form.getlist('component_code[]')
        comp_amounts = request.form.getlist('component_amount[]')
        
        if emp_id:
            conn = get_db_connection()
            try:
                with conn.cursor() as cursor:
                    # Insert into payslip_master
                    cursor.execute(
                        \"\"\"INSERT INTO payslip_master 
                           (emp_id, basic_salary, total_allowance, total_deduction, final_in_hand_salary) 
                           VALUES (%s, %s, %s, %s, %s)\"\"\",
                        (emp_id, basic_salary, total_allowance, total_deduction, final_in_hand_salary)
                    )
                    
                    # Delete existing components to replace them with the new generated ones
                    cursor.execute("DELETE FROM employee_financial_components WHERE emp_id = %s", (emp_id,))
                    
                    # Insert dynamic components into employee_financial_components
                    for i in range(len(comp_names)):
                        name = comp_names[i].strip()
                        code = int(comp_codes[i]) if i < len(comp_codes) else 1
                        amt = float(comp_amounts[i]) if i < len(comp_amounts) else 0.0
                        if name:
                            cursor.execute(
                                \"\"\"INSERT INTO employee_financial_components
                                (emp_id, component_name, component_code, amount)
                                VALUES (%s, %s, %s, %s)\"\"\",
                                (emp_id, name, code, amt)
                            )
                conn.commit()
                flash("Payslip and components saved successfully!", "success")
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
if "def payslip_builder():" not in content:
    content = content.replace("if __name__ == '__main__':", route_code + "\nif __name__ == '__main__':")
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Added payslip builder route")
else:
    print("Route already exists!")
