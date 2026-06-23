import re

with open('templates/financial_master.html', 'r', encoding='utf-8') as f:
    c = f.read()

# Replace the onclick button
old_btn = """<button type="button" class="btn btn-sm btn-outline-primary" onclick='openEditModal({{ emp.emp_id|tojson }}, {{ emp.emp_name|default("", true)|tojson }}, {{ emp.bank_name|default("", true)|tojson }}, {{ emp.bank_account_num|default("", true)|tojson }}, {{ emp.ifsc_code|default("", true)|tojson }}, {{ emp.basic_salary|default(0, true)|tojson }})' title="Edit Financials">"""
new_btn = """<button type="button" class="btn btn-sm btn-outline-primary" 
                                    data-emp-id="{{ emp.emp_id }}"
                                    data-emp-name="{{ emp.emp_name|default('', true) }}"
                                    data-bank-name="{{ emp.bank_name|default('', true) }}"
                                    data-bank-acc="{{ emp.bank_account_num|default('', true) }}"
                                    data-ifsc="{{ emp.ifsc_code|default('', true) }}"
                                    data-basic-salary="{{ emp.basic_salary|default(0, true) }}"
                                    onclick='openEditModalFromBtn(this)' title="Edit Financials">"""
c = c.replace(old_btn, new_btn)

# Replace the empComponentsData JS block
old_js_block = """    const empComponentsData = {
        {% for emp_id, comps in emp_components.items() %}
            "{{ emp_id }}": [
                {% for c in comps %}
                    {"name": "{{ c.component_name|replace('"', '\\"') }}", "code": {{ c.component_code }}, "amount": {{ c.amount }} }{% if not loop.last %},{% endif %}
                {% endfor %}
            ]{% if not loop.last %},{% endif %}
        {% endfor %}
    };"""
    
new_js_block = """</script>
<script type="application/json" id="empComponentsDataJson">
{{ emp_components | tojson }}
</script>
<script>
    const empComponentsDataRaw = JSON.parse(document.getElementById('empComponentsDataJson').textContent);
    // Convert to the exact format the old code expected if needed.
    // Wait, emp_components is a dict mapping emp_id to a list of dicts.
    // The previous format was: {"EMP-01": [{"name": "Basic", "code": 1, "amount": 500}, ...]}
    // But emp_components from python has component_name, component_code, amount.
    const empComponentsData = {};
    for (const [empId, comps] of Object.entries(empComponentsDataRaw)) {
        empComponentsData[empId] = comps.map(c => ({
            name: c.component_name,
            code: c.component_code,
            amount: c.amount
        }));
    }"""

c = c.replace(old_js_block, new_js_block)

# Add openEditModalFromBtn function right before openEditModal
new_func = """    function openEditModalFromBtn(btn) {
        const d = btn.dataset;
        openEditModal(d.empId, d.empName, d.bankName, d.bankAcc, d.ifsc, d.basicSalary);
    }
    
    function openEditModal"""
    
c = c.replace("    function openEditModal", new_func)

with open('templates/financial_master.html', 'w', encoding='utf-8') as f:
    f.write(c)

print("done")
