import re

with open('templates/payslip_designer.html', 'r', encoding='utf-8') as f:
    c = f.read()

# Replace addFieldWithValue to attach oninput="recalculateFinancials()" to value inputs
old_func = """function addFieldWithValue(listId, lbl, val) {
    let borderCls = listId === 'earnings-list' ? 'border-success' : (listId === 'deductions-list' ? 'border-danger' : '');
    let html = `
        <div class="field-row drag-source">
            <i class="bi bi-list field-drag"></i>
            <div class="field-input-wrap ${borderCls}">
                <input type="text" class="field-label-input bg-light" value="${lbl}">
                <input type="text" class="field-value-input" value="${val}">
            </div>
        </div>`;
    document.getElementById(listId).insertAdjacentHTML('beforeend', html);
}"""

new_func = """function addFieldWithValue(listId, lbl, val) {
    let borderCls = listId === 'earnings-list' ? 'border-success' : (listId === 'deductions-list' ? 'border-danger' : '');
    let html = `
        <div class="field-row drag-source">
            <i class="bi bi-list field-drag"></i>
            <div class="field-input-wrap ${borderCls}">
                <input type="text" class="field-label-input bg-light" value="${lbl}" oninput="recalculateFinancials()">
                <input type="text" class="field-value-input" value="${val}" oninput="recalculateFinancials()">
            </div>
        </div>`;
    document.getElementById(listId).insertAdjacentHTML('beforeend', html);
}

function recalculateFinancials() {
    let total_earn = 0;
    let total_ded = 0;
    
    let earnLabels = '';
    let earnAmts = '';
    let dedLabels = '';
    let dedAmts = '';
    
    // Iterate over earnings-list
    document.querySelectorAll('#earnings-list .field-row').forEach(row => {
        let lbl = row.querySelector('.field-label-input').value;
        let val = parseFloat(row.querySelector('.field-value-input').value || 0);
        total_earn += val;
        earnLabels += '<div>' + lbl + '</div>';
        earnAmts += '<div>' + val.toFixed(2) + '</div>';
    });
    
    // Iterate over deductions-list
    document.querySelectorAll('#deductions-list .field-row').forEach(row => {
        let lbl = row.querySelector('.field-label-input').value;
        let val = parseFloat(row.querySelector('.field-value-input').value || 0);
        total_ded += val;
        dedLabels += '<div>' + lbl + '</div>';
        dedAmts += '<div>' + val.toFixed(2) + '</div>';
    });
    
    document.getElementById('f-net').value = (total_earn - total_ded).toFixed(2);
    
    if(document.getElementById('tpl-earn-lbls')) document.getElementById('tpl-earn-lbls').innerHTML = earnLabels;
    if(document.getElementById('tpl-earn-amts')) document.getElementById('tpl-earn-amts').innerHTML = earnAmts;
    if(document.getElementById('tpl-ded-lbls')) document.getElementById('tpl-ded-lbls').innerHTML = dedLabels;
    if(document.getElementById('tpl-ded-amts')) document.getElementById('tpl-ded-amts').innerHTML = dedAmts;
    
    if(document.getElementById('tpl-earn-total')) document.getElementById('tpl-earn-total').innerHTML = total_earn.toFixed(2);
    if(document.getElementById('tpl-ded-total')) document.getElementById('tpl-ded-total').innerHTML = total_ded.toFixed(2);
    
    let netPay = (total_earn - total_ded);
    if(document.getElementById('tpl-net-pay')) document.getElementById('tpl-net-pay').innerHTML = netPay.toFixed(2);
    if(document.getElementById('tpl-amt-words')) document.getElementById('tpl-amt-words').innerHTML = 'Rupees ' + numberToWords(Math.round(netPay));
}"""

c = c.replace(old_func, new_func)

with open('templates/payslip_designer.html', 'w', encoding='utf-8') as f:
    f.write(c)

print("done")
