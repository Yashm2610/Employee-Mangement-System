import re

def fix_builder():
    with open('templates/payslip_builder.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Replace the Employee ID input with a select
    old_emp_id = """<input type="text" class="form-control border-secondary-subtle" name="emp_id" id="emp_id" placeholder="e.g. EMP-2026" required oninput="updatePreview()">"""
    new_emp_id = """<select class="form-select border-secondary-subtle" name="emp_id" id="emp_id" required onchange="fetchEmployeeDetails(this.value)">
                                <option value="">-- Select Employee --</option>
                                {% for emp in employees %}
                                <option value="{{ emp.emp_id }}">{{ emp.emp_id }} - {{ emp.emp_name }}</option>
                                {% endfor %}
                            </select>"""
    content = content.replace(old_emp_id, new_emp_id)

    # 2. Add readonly to fields
    fields_to_readonly = ['id="emp_name"', 'id="designation"', 'id="department"', 'id="bank_acc"', 'id="basic_salary"']
    for field in fields_to_readonly:
        content = content.replace(field, field + ' readonly bg-light')

    # 3. Add JS functions
    js_funcs = """
    function numberToWords(num) {
        const a = ['','One ','Two ','Three ','Four ', 'Five ','Six ','Seven ','Eight ','Nine ','Ten ','Eleven ','Twelve ','Thirteen ','Fourteen ','Fifteen ','Sixteen ','Seventeen ','Eighteen ','Nineteen '];
        const b = ['', '', 'Twenty','Thirty','Forty','Fifty', 'Sixty','Seventy','Eighty','Ninety'];
        if ((num = num.toString()).length > 9) return 'overflow';
        let n = ('000000000' + num).substr(-9).match(/^(\\d{2})(\\d{2})(\\d{2})(\\d{1})(\\d{2})$/);
        if (!n) return; let str = '';
        str += (n[1] != 0) ? (a[Number(n[1])] || b[n[1][0]] + ' ' + a[n[1][1]]) + 'Crore ' : '';
        str += (n[2] != 0) ? (a[Number(n[2])] || b[n[2][0]] + ' ' + a[n[2][1]]) + 'Lakh ' : '';
        str += (n[3] != 0) ? (a[Number(n[3])] || b[n[3][0]] + ' ' + a[n[3][1]]) + 'Thousand ' : '';
        str += (n[4] != 0) ? (a[Number(n[4])] || b[n[4][0]] + ' ' + a[n[4][1]]) + 'Hundred ' : '';
        str += (n[5] != 0) ? ((str != '') ? 'and ' : '') + (a[Number(n[5])] || b[n[5][0]] + ' ' + a[n[5][1]]) + 'Rupees Only' : 'Rupees Only';
        return str;
    }

    async function fetchEmployeeDetails(empId) {
        if (!empId) {
            document.getElementById('payslip-form').reset();
            document.getElementById('dynamic-components-container').innerHTML = '';
            updateTotals();
            return;
        }
        
        try {
            const response = await fetch('/api/employee/' + empId);
            const data = await response.json();
            
            if (data.employee) {
                document.getElementById('emp_name').value = data.employee.emp_name || '';
                document.getElementById('designation').value = data.employee.title || '';
                document.getElementById('department').value = data.employee.department || '';
                document.getElementById('bank_acc').value = data.employee.bank_account_num || '';
                document.getElementById('basic_salary').value = data.employee.basic_salary || 0;
                
                // Auto set period based on current month/year
                const d = new Date();
                const month = d.toLocaleString('default', { month: 'long' });
                document.getElementById('period').value = month + " " + d.getFullYear();
                document.getElementById('period').readOnly = true;
                document.getElementById('period').classList.add('bg-light');
                
                // Clear components
                const container = document.getElementById('dynamic-components-container');
                container.innerHTML = '';
                
                // Add components
                if (data.components && data.components.length > 0) {
                    data.components.forEach(comp => {
                        const row = document.createElement('div');
                        row.className = 'input-group input-group-sm component-row mb-2';
                        row.innerHTML = `
                            <select class="form-select border-secondary-subtle w-25 bg-light" name="component_code[]" readonly tabindex="-1" style="pointer-events: none;">
                                <option value="1" ${comp.component_code === 1 ? 'selected' : ''}>Allowance (1)</option>
                                <option value="2" ${comp.component_code === 2 ? 'selected' : ''}>Deduction (2)</option>
                            </select>
                            <input type="text" class="form-control border-secondary-subtle w-50 bg-light" name="component_name[]" value="${comp.component_name}" readonly>
                            <input type="number" class="form-control border-secondary-subtle w-25 component-amt bg-light" name="component_amount[]" value="${comp.amount}" readonly>
                        `;
                        container.appendChild(row);
                    });
                }
                
                updateTotals();
            }
        } catch (error) {
            console.error("Error fetching employee details", error);
        }
    }
"""
    content = content.replace("function addComponentRow() {", js_funcs + "\n    function addComponentRow() {")
    
    # 4. Inject words logic in updatePreview
    update_words = """
        updateElements('.dyn-net', net.toFixed(2));
        
        let words = numberToWords(Math.round(net));
        updateElements('.dyn-words', words);
"""
    content = content.replace("updateElements('.dyn-net', net.toFixed(2));", update_words)
    
    # Add Company Info and Words to Modern
    content = content.replace('Your business name', 'Maxworth Solutions')
    content = content.replace('Business Address<br>\n                            Contact Number', '123 Tech Park, Bangalore, 560001<br>+91-80-555-1234')
    
    # Add dyn-words placeholder in Modern
    modern_net = """<tr class="modern-net">
                                    <td>Net Pay</td>
                                    <td></td>
                                    <td></td>
                                    <td></td>
                                    <td class="text-end dyn-net">0.00</td>
                                </tr>
                                <tr>
                                    <td colspan="5" class="text-end fw-bold text-muted small"><span class="dyn-words">Zero Rupees Only</span></td>
                                </tr>"""
    content = content.replace("""<tr class="modern-net">
                                    <td>Net Pay</td>
                                    <td></td>
                                    <td></td>
                                    <td></td>
                                    <td class="text-end dyn-net">0.00</td>
                                </tr>""", modern_net)
                                
    # Add dyn-words placeholder in Minimal
    minimal_net = """<div class="d-flex justify-content-between fw-bold fs-6 mt-3">
                                    <span>NET Salary</span><span class="dyn-net">0.00</span>
                                </div>
                                <div class="text-end fw-bold text-muted mt-1 fs-8"><span class="dyn-words">Zero Rupees Only</span></div>"""
    content = content.replace("""<div class="d-flex justify-content-between fw-bold fs-6 mt-3">
                                    <span>NET Salary</span><span class="dyn-net">0.00</span>
                                </div>""", minimal_net)
                                
    # Add dyn-words placeholder in Classic
    classic_net = """<tr class="fw-bold bg-light">
                                    <td colspan="2" class="text-end">NET SALARY:</td>
                                    <td colspan="2" class="fs-5 dyn-net text-end">0.00</td>
                                </tr>
                                <tr class="bg-light">
                                    <td colspan="4" class="text-end fw-bold text-muted fst-italic"><span class="dyn-words">Zero Rupees Only</span></td>
                                </tr>"""
    content = content.replace("""<tr class="fw-bold bg-light">
                                    <td colspan="2" class="text-end">NET SALARY:</td>
                                    <td colspan="2" class="fs-5 dyn-net text-end">0.00</td>
                                </tr>""", classic_net)
                                
    with open('templates/payslip_builder.html', 'w', encoding='utf-8') as f:
        f.write(content)
        
    print("payslip_builder.html updated")

if __name__ == '__main__':
    fix_builder()
