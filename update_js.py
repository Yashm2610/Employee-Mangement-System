def get_amount_words_js():
    return """
function numberToWords(num) {
    if(num === 0) return 'Zero';
    var a = ['','One ','Two ','Three ','Four ', 'Five ','Six ','Seven ','Eight ','Nine ','Ten ','Eleven ','Twelve ','Thirteen ','Fourteen ','Fifteen ','Sixteen ','Seventeen ','Eighteen ','Nineteen '];
    var b = ['', '', 'Twenty','Thirty','Forty','Fifty', 'Sixty','Seventy','Eighty','Ninety'];
    if ((num = num.toString()).length > 9) return 'overflow';
    n = ('000000000' + num).substr(-9).match(/^(\d{2})(\d{2})(\d{2})(\d{1})(\d{2})$/);
    if (!n) return; var str = '';
    str += (n[1] != 0) ? (a[Number(n[1])] || b[n[1][0]] + ' ' + a[n[1][1]]) + 'Crore ' : '';
    str += (n[2] != 0) ? (a[Number(n[2])] || b[n[2][0]] + ' ' + a[n[2][1]]) + 'Lakh ' : '';
    str += (n[3] != 0) ? (a[Number(n[3])] || b[n[3][0]] + ' ' + a[n[3][1]]) + 'Thousand ' : '';
    str += (n[4] != 0) ? (a[Number(n[4])] || b[n[4][0]] + ' ' + a[n[4][1]]) + 'Hundred ' : '';
    str += (n[5] != 0) ? ((str != '') ? 'and ' : '') + (a[Number(n[5])] || b[n[5][0]] + ' ' + a[n[5][1]]) + 'Only' : '';
    return str.trim() + ' Only';
}
"""

def update_payslip_designer():
    with open('templates/payslip_designer.html', 'r', encoding='utf-8') as f:
        c = f.read()
        
    # Insert numberToWords before saveState()
    if 'function numberToWords' not in c:
        c = c.replace('saveState();\nrebindCanvasElements();', get_amount_words_js() + '\n\nsaveState();\nrebindCanvasElements();')
        
    # Update bindLiveUpdate calls
    bind_updates = """
bindLiveUpdate('f-month', 'tpl-month', '[Month]');
bindLiveUpdate('f-month-days', 'tpl-month-days', '[Month Days]');
bindLiveUpdate('f-paid-days', 'tpl-paid-days', '[Days]');
bindLiveUpdate('f-cl-bal', 'tpl-cl-bal', '0');
bindLiveUpdate('f-el-bal', 'tpl-el-bal', '0');
bindLiveUpdate('f-pay-date', 'tpl-pay-date', '[Payment Date]');
"""
    if "bindLiveUpdate('f-month'" not in c:
        c = c.replace("bindLiveUpdate('f-uan', 'tpl-uan', '[Drop UAN]');", "bindLiveUpdate('f-uan', 'tpl-uan', '[Drop UAN]');\n" + bind_updates)

    # Now, update fetchEmployeeData to generate Earnings/Deductions tables
    # Find the place where it does: document.getElementById('loading-overlay').style.display = 'none';
    # Actually, we can inject the table building logic inside fetchEmployeeData after the components are added to left lists
    
    # We will search for: document.getElementById('f-net').value = (total_earn - total_ded).toFixed(2);
    
    table_build_logic = """
        document.getElementById('f-net').value = (total_earn - total_ded).toFixed(2);
        
        // --- Auto-Populate Payslip Templates ---
        let earnLabels = '';
        let earnAmts = '';
        let dedLabels = '';
        let dedAmts = '';
        
        // Basic
        earnLabels += '<div>Basic Salary</div>';
        earnAmts += '<div>' + (emp.basic_salary || 0).toFixed(2) + '</div>';
        
        emp.components.forEach(c => {
            if(c.type === 'Earning') {
                earnLabels += '<div>' + c.name + '</div>';
                earnAmts += '<div>' + c.amount.toFixed(2) + '</div>';
            } else if(c.type === 'Deduction') {
                dedLabels += '<div>' + c.name + '</div>';
                dedAmts += '<div>' + c.amount.toFixed(2) + '</div>';
            }
        });
        
        if(document.getElementById('tpl-earn-lbls')) document.getElementById('tpl-earn-lbls').innerHTML = earnLabels;
        if(document.getElementById('tpl-earn-amts')) document.getElementById('tpl-earn-amts').innerHTML = earnAmts;
        if(document.getElementById('tpl-ded-lbls')) document.getElementById('tpl-ded-lbls').innerHTML = dedLabels;
        if(document.getElementById('tpl-ded-amts')) document.getElementById('tpl-ded-amts').innerHTML = dedAmts;
        
        if(document.getElementById('tpl-earn-total')) document.getElementById('tpl-earn-total').innerHTML = total_earn.toFixed(2);
        if(document.getElementById('tpl-ded-total')) document.getElementById('tpl-ded-total').innerHTML = total_ded.toFixed(2);
        
        let netPay = (total_earn - total_ded);
        if(document.getElementById('tpl-net-pay')) document.getElementById('tpl-net-pay').innerHTML = netPay.toFixed(2);
        if(document.getElementById('tpl-amt-words')) document.getElementById('tpl-amt-words').innerHTML = 'Rupees ' + numberToWords(Math.round(netPay));
        
        // Dispatch inputs to trigger regular bindLiveUpdate
        ['f-month', 'f-month-days', 'f-paid-days', 'f-cl-bal', 'f-el-bal', 'f-pay-date'].forEach(id => {
            let el = document.getElementById(id);
            if(el) el.dispatchEvent(new Event('input'));
        });
"""
    c = c.replace("document.getElementById('f-net').value = (total_earn - total_ded).toFixed(2);", table_build_logic)

    with open('templates/payslip_designer.html', 'w', encoding='utf-8') as f:
        f.write(c)

update_payslip_designer()
print("done")
