import re

with open('templates/payslip_designer.html', 'r', encoding='utf-8') as f:
    c = f.read()

old_recalc = """function recalculateFinancials() {
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

new_recalc = """function recalculateFinancials() {
    let total_earn = 0;
    let total_ded = 0;
    
    // Update Earnings
    let earnIndex = 0;
    document.querySelectorAll('#earnings-list .field-row').forEach(row => {
        let lbl = row.querySelector('.field-label-input').value;
        let val = parseFloat(row.querySelector('.field-value-input').value || 0);
        total_earn += val;
        
        let lblContainer = document.getElementById('tpl-earn-lbls');
        let amtContainer = document.getElementById('tpl-earn-amts');
        
        if (lblContainer && amtContainer) {
            let lblEl = document.getElementById('earn-lbl-' + earnIndex);
            let amtEl = document.getElementById('earn-amt-' + earnIndex);
            
            if (lblEl) {
                lblEl.innerText = lbl;
                amtEl.innerText = val.toFixed(2);
            } else {
                lblContainer.insertAdjacentHTML('beforeend', `<div id="earn-lbl-${earnIndex}" class="movable-label" style="display:inline-block; cursor:move; position:relative; min-width: 100px;">${lbl}</div><br id="earn-br-lbl-${earnIndex}">`);
                amtContainer.insertAdjacentHTML('beforeend', `<div id="earn-amt-${earnIndex}" class="movable-label" style="display:inline-block; cursor:move; position:relative; min-width: 50px;">${val.toFixed(2)}</div><br id="earn-br-amt-${earnIndex}">`);
            }
        }
        earnIndex++;
    });
    
    // Update Deductions
    let dedIndex = 0;
    document.querySelectorAll('#deductions-list .field-row').forEach(row => {
        let lbl = row.querySelector('.field-label-input').value;
        let val = parseFloat(row.querySelector('.field-value-input').value || 0);
        total_ded += val;
        
        let lblContainer = document.getElementById('tpl-ded-lbls');
        let amtContainer = document.getElementById('tpl-ded-amts');
        
        if (lblContainer && amtContainer) {
            let lblEl = document.getElementById('ded-lbl-' + dedIndex);
            let amtEl = document.getElementById('ded-amt-' + dedIndex);
            
            if (lblEl) {
                lblEl.innerText = lbl;
                amtEl.innerText = val.toFixed(2);
            } else {
                lblContainer.insertAdjacentHTML('beforeend', `<div id="ded-lbl-${dedIndex}" class="movable-label" style="display:inline-block; cursor:move; position:relative; min-width: 100px;">${lbl}</div><br id="ded-br-lbl-${dedIndex}">`);
                amtContainer.insertAdjacentHTML('beforeend', `<div id="ded-amt-${dedIndex}" class="movable-label" style="display:inline-block; cursor:move; position:relative; min-width: 50px;">${val.toFixed(2)}</div><br id="ded-br-amt-${dedIndex}">`);
            }
        }
        dedIndex++;
    });
    
    // Clean up any extra elements if rows were removed
    // (Optional, but good for robust sync)
    
    document.getElementById('f-net').value = (total_earn - total_ded).toFixed(2);
    
    if(document.getElementById('tpl-earn-total')) document.getElementById('tpl-earn-total').innerHTML = total_earn.toFixed(2);
    if(document.getElementById('tpl-ded-total')) document.getElementById('tpl-ded-total').innerHTML = total_ded.toFixed(2);
    
    let netPay = (total_earn - total_ded);
    if(document.getElementById('tpl-net-pay')) document.getElementById('tpl-net-pay').innerHTML = netPay.toFixed(2);
    if(document.getElementById('tpl-amt-words')) document.getElementById('tpl-amt-words').innerHTML = 'Rupees ' + numberToWords(Math.round(netPay));
}"""

c = c.replace(old_recalc, new_recalc)

# We also need to update fetchEmployeeData to CLEAR the containers initially, so recalculateFinancials rebuilds them cleanly as movable labels!
old_fetch_end = """        document.getElementById('f-net').value = (total_earn - total_ded).toFixed(2);
        
        // Dispatch inputs to trigger regular bindLiveUpdate"""

new_fetch_end = """        document.getElementById('f-net').value = (total_earn - total_ded).toFixed(2);
        
        // Clear containers so recalculateFinancials builds them as movable labels
        if(document.getElementById('tpl-earn-lbls')) document.getElementById('tpl-earn-lbls').innerHTML = '';
        if(document.getElementById('tpl-earn-amts')) document.getElementById('tpl-earn-amts').innerHTML = '';
        if(document.getElementById('tpl-ded-lbls')) document.getElementById('tpl-ded-lbls').innerHTML = '';
        if(document.getElementById('tpl-ded-amts')) document.getElementById('tpl-ded-amts').innerHTML = '';
        
        // Force sync to build the template
        recalculateFinancials();
        
        // Dispatch inputs to trigger regular bindLiveUpdate"""

c = c.replace(old_fetch_end, new_fetch_end)

# Also remove the hardcoded string building inside fetchEmployeeData since recalculateFinancials handles it now.
old_earn_str = """            earnLabels += '<div>' + label + '</div>';
            earnAmts += '<div>' + amt.toFixed(2) + '</div>';"""
c = c.replace(old_earn_str, "")

old_ded_str = """            dedLabels += '<div>' + label + '</div>';
            dedAmts += '<div>' + amt.toFixed(2) + '</div>';"""
c = c.replace(old_ded_str, "")

old_extra_str = """                        earnLabels += '<div>' + c.component_name + '</div>';
                        earnAmts += '<div>' + amt.toFixed(2) + '</div>';"""
c = c.replace(old_extra_str, "")

old_extra_ded = """                        dedLabels += '<div>' + c.component_name + '</div>';
                        dedAmts += '<div>' + amt.toFixed(2) + '</div>';"""
c = c.replace(old_extra_ded, "")

with open('templates/payslip_designer.html', 'w', encoding='utf-8') as f:
    f.write(c)

print("done")
