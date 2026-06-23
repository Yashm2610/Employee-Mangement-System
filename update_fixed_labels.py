import re

with open('templates/payslip_designer.html', 'r', encoding='utf-8') as f:
    c = f.read()

# We need to replace the entire logic from "// Clear dynamic lists" down to "if(document.getElementById('tpl-earn-lbls'))"
# with our new fixed list logic.

old_logic = """        // Add Basic Salary
        let basicHtml = `
            <div class="field-row drag-source">
                <i class="bi bi-list field-drag"></i>
                <div class="field-input-wrap border-success">
                    <input type="text" class="field-label-input bg-light" value="Basic Salary">
                    <input type="text" class="field-value-input" value="${emp.basic_salary || '0'}">
                </div>
            </div>`;
        document.getElementById('earnings-list').insertAdjacentHTML('beforeend', basicHtml);

        // Add Components
        let total_earn = parseFloat(emp.basic_salary || 0);
        let total_ded = 0;
        
        if(data.components) {
            data.components.forEach(c => {
                let isEarn = c.component_code === 1;
                let listId = isEarn ? 'earnings-list' : 'deductions-list';
                addFieldWithValue(listId, c.component_name, c.amount);
                
                if(isEarn) total_earn += parseFloat(c.amount);
                else total_ded += parseFloat(c.amount);
            });
        }
        
        
        document.getElementById('f-net').value = (total_earn - total_ded).toFixed(2);
        
        // --- Auto-Populate Payslip Templates ---
        let earnLabels = '';
        let earnAmts = '';
        let dedLabels = '';
        let dedAmts = '';
        
        // Basic
        earnLabels += '<div>Basic Salary</div>';
        earnAmts += '<div>' + (emp.basic_salary || 0).toFixed(2) + '</div>';
        
        if (data.components) {
            data.components.forEach(c => {
                let isEarn = c.component_code === 1;
                if(isEarn) {
                    earnLabels += '<div>' + c.component_name + '</div>';
                    earnAmts += '<div>' + parseFloat(c.amount).toFixed(2) + '</div>';
                } else {
                    dedLabels += '<div>' + c.component_name + '</div>';
                    dedAmts += '<div>' + parseFloat(c.amount).toFixed(2) + '</div>';
                }
            });
        }"""

new_logic = """        const FIXED_EARNINGS = ["Basic", "HRA", "Special Allowance", "Arrear", "Special Incentive", "Conveyance", "Leave encashment", "Bonus"];
        const FIXED_DEDUCTIONS = ["ESI", "PF", "TDS", "Loan", "Professional Tax", "Other Deduction", "Late coming/Unapproved", "TDS excess deduction Arrears"];

        let total_earn = 0;
        let total_ded = 0;
        
        let earnLabels = '';
        let earnAmts = '';
        let dedLabels = '';
        let dedAmts = '';
        
        let processedComponents = [];

        // Build Earnings
        FIXED_EARNINGS.forEach(label => {
            let amt = 0;
            if (label === 'Basic') {
                amt = parseFloat(emp.basic_salary || 0);
            } else {
                if (data.components) {
                    let comp = data.components.find(c => c.component_name.toLowerCase() === label.toLowerCase() && c.component_code === 1);
                    if (comp) {
                        amt = parseFloat(comp.amount || 0);
                        processedComponents.push(comp.component_name);
                    }
                }
            }
            addFieldWithValue('earnings-list', label, amt.toFixed(2));
            total_earn += amt;
            
            earnLabels += '<div>' + label + '</div>';
            earnAmts += '<div>' + amt.toFixed(2) + '</div>';
        });

        // Build Deductions
        FIXED_DEDUCTIONS.forEach(label => {
            let amt = 0;
            if (data.components) {
                let comp = data.components.find(c => c.component_name.toLowerCase() === label.toLowerCase() && c.component_code === 2);
                if (comp) {
                    amt = parseFloat(comp.amount || 0);
                    processedComponents.push(comp.component_name);
                }
            }
            addFieldWithValue('deductions-list', label, amt.toFixed(2));
            total_ded += amt;
            
            dedLabels += '<div>' + label + '</div>';
            dedAmts += '<div>' + amt.toFixed(2) + '</div>';
        });
        
        // Add any remaining components from the database not in the fixed list
        if (data.components) {
            data.components.forEach(c => {
                if (!processedComponents.includes(c.component_name)) {
                    let amt = parseFloat(c.amount || 0);
                    let isEarn = c.component_code === 1;
                    if (isEarn) {
                        addFieldWithValue('earnings-list', c.component_name, amt.toFixed(2));
                        total_earn += amt;
                        earnLabels += '<div>' + c.component_name + '</div>';
                        earnAmts += '<div>' + amt.toFixed(2) + '</div>';
                    } else {
                        addFieldWithValue('deductions-list', c.component_name, amt.toFixed(2));
                        total_ded += amt;
                        dedLabels += '<div>' + c.component_name + '</div>';
                        dedAmts += '<div>' + amt.toFixed(2) + '</div>';
                    }
                }
            });
        }
        
        document.getElementById('f-net').value = (total_earn - total_ded).toFixed(2);"""

c = c.replace(old_logic, new_logic)

with open('templates/payslip_designer.html', 'w', encoding='utf-8') as f:
    f.write(c)

print("done")
