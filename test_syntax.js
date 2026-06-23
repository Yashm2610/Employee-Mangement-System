async function fetchEmployeeData() {
    let empId = document.getElementById('emp-selector').value;
    if (!empId) return;
    
    let month = document.getElementById('month-selector').value;
    let year = document.getElementById('year-selector').value;
    
    document.getElementById('loading-overlay').style.display = 'flex';
    try {
        let url = `/api/employee/${empId}`;
        if (month && year) {
            url += `?month=${month}&year=${year}`;
        }
        const res = await fetch(url);
        let data = await res.json();
        
        let emp = data.employee;
        
        // Update basic fields
        document.getElementById('f-emp-name').value = emp.emp_name || '';
        document.getElementById('f-emp-id').value = emp.emp_id || '';
        document.getElementById('f-dept').value = emp.department || '';
        document.getElementById('f-desig').value = emp.title || '';
        window.currentEmployeeDesignation = emp.title || '';
        
        let fDoj = document.getElementById('f-doj');
        if(fDoj) fDoj.value = emp.joining_date || '';
        
        if(document.getElementById('f-month-days')) document.getElementById('f-month-days').value = emp.month_days || 31;
        if(document.getElementById('f-paid-days')) document.getElementById('f-paid-days').value = emp.paid_days || 31;
        if(document.getElementById('f-cl-bal')) document.getElementById('f-cl-bal').value = emp.cl_balance || 0;
        if(document.getElementById('f-el-bal')) document.getElementById('f-el-bal').value = emp.el_balance || 0;
        if(document.getElementById('f-sl-bal')) document.getElementById('f-sl-bal').value = emp.sl_balance || 0;
        
        let fBank = document.getElementById('f-bank');
        if(fBank) fBank.value = emp.bank_name || '';
        
        let fUan = document.getElementById('f-uan');
        if(fUan) fUan.value = emp.uan_number || ('100' + String(Math.floor(Math.random() * 90000000) + 10000000));
        
        let fMonth = document.getElementById('f-month');
        if(fMonth) {
            if (month && year) {
                const monthNames = ["", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
                fMonth.value = monthNames[parseInt(month)] + ' ' + year;
            } else {
                fMonth.value = emp.current_month || 'June 2026';
            }
        }
        
        let processedComponents = [];
        let total_earn = 0;
        let total_ded = 0;
        
        // Save to global for right sidebar calculation
        lastFetchedEmployeeData = data;
        
        // Auto-generate serial and dates
        let d = new Date();
        let payslipNo = "PSL-" + d.getFullYear() + "-" + String(Math.floor(Math.random() * 900000) + 100000);
        let genDate = d.toLocaleDateString();
        let genTime = d.toLocaleTimeString();
        let currentYear = d.getFullYear();
        
        if(!document.getElementById('tpl-payslip-no')) {
            document.querySelector('.a4-canvas').insertAdjacentHTML('afterbegin', `<div style="text-align:right; font-size:10px; color:#555; margin-bottom:5px;">Payslip No: <span id="tpl-payslip-no">${payslipNo}</span> | Generated: <span id="tpl-gen-date">${genDate} ${genTime}</span></div>`);
        } else {
            document.getElementById('tpl-payslip-no').innerText = payslipNo;
            document.getElementById('tpl-gen-date').innerText = genDate + " " + genTime;
        }
        
        let ifscInput = document.getElementById('f-ifsc');
        if(ifscInput) ifscInput.value = emp.ifsc_code || '';
        
        let payDateInput = document.getElementById('f-pay-date');
        let currentMonth = '';
        if(payDateInput) {
            let d = new Date();
            payDateInput.value = d.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
            currentMonth = d.toLocaleString('default', { month: 'long', year: 'numeric' });
        }
        
        let fCompany = document.getElementById('f-company');
        if(fCompany) fCompany.value = emp.company_name || 'Maxworth';
        
        let fAddress = document.getElementById('f-address');
        if(fAddress) fAddress.value = emp.company_address || '123 Tech Park';
        
        let fBasic = document.getElementById('f-basic');
        if(fBasic) fBasic.value = emp.basic_salary || '0';
        
        // Clear dynamic lists
        document.getElementById('earnings-list').innerHTML = '';
        document.getElementById('deductions-list').innerHTML = '';
        
        const FIXED_EARNINGS = ["Basic", "HRA", "Special Allowance", "Arrear", "Special Incentive", "Conveyance", "Leave encashment", "Bonus"];
        const FIXED_DEDUCTIONS = ["ESI", "PF", "TDS", "Loan", "Professional Tax", "Other Deduction", "Late coming/Unapproved", "TDS excess deduction Arrears"];

        total_earn = 0;
        total_ded = 0;
        
        let earnLabels = '';
        let earnAmts = '';
        let dedLabels = '';
        let dedAmts = '';
        
        processedComponents = [];

        function getAliases(label) {
            let l = label.toLowerCase();
            if (l === 'hra') return ['hra', 'house rent'];
            if (l === 'arrear') return ['arrear', 'arrears'];
            if (l === 'conveyance') return ['conveyance', 'transport', 'travel'];
            if (l === 'pf') return ['pf', 'provident fund'];
            if (l === 'tds') return ['tds', 'income tax'];
            if (l === 'esi') return ['esi', 'insurance', 'medical'];
            return [l];
        }

        function matchComponent(components, typeCode, aliases) {
            if(!components) return null;
            return components.find(c => {
                if (c.component_code !== typeCode) return false;
                let cname = c.component_name.toLowerCase();
                return aliases.some(alias => cname.includes(alias) || cname === alias);
            });
        }

        // Build Earnings
        FIXED_EARNINGS.forEach(label => {
            let amt = 0;
            if (label === 'Basic') {
                amt = parseFloat(emp.basic_salary || 0);
            } else {
                let aliases = getAliases(label);
                let comp = matchComponent(data.components, 1, aliases);
                if (comp) {
                    amt = parseFloat(comp.amount || 0);
                    processedComponents.push(comp.component_name);
                }
            }
            addFieldWithValue('earnings-list', label, amt.toFixed(2));
            total_earn += amt;
        });

        // Build Deductions
        FIXED_DEDUCTIONS.forEach(label => {
            let amt = 0;
            let aliases = getAliases(label);
            let comp = matchComponent(data.components, 2, aliases);
            if (comp) {
                amt = parseFloat(comp.amount || 0);
                processedComponents.push(comp.component_name);
            } else {
                if (label === 'PF') {
                    let basic = parseFloat(emp.basic_salary || 0);
                    amt = basic > 0 ? Math.min(basic * 0.12, 1800.0) : 0;
                } else if (label === 'ESI') {
                    // ESI needs gross, approximate if missing
                    let gross = parseFloat(emp.gross_salary || (parseFloat(emp.basic_salary || 0) * 1.5));
                    amt = (gross > 0 && gross <= 21000) ? (gross * 0.0075) : 0;
                } else if (label === 'TDS') {
                    let gross = parseFloat(emp.gross_salary || (parseFloat(emp.basic_salary || 0) * 1.5));
                    amt = gross > 40000 ? (gross * 0.05) : 0;
                }
            }
            addFieldWithValue('deductions-list', label, amt.toFixed(2));
            total_ded += amt;
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
                    } else {
                        addFieldWithValue('deductions-list', c.component_name, amt.toFixed(2));
                        total_ded += amt;
                    }
                }
            });
        }
        
        document.getElementById('f-net').value = (total_earn - total_ded).toFixed(2);
        
        // Clear containers so recalculateFinancials builds them as movable labels
        if(document.getElementById('tpl-earn-lbls')) document.getElementById('tpl-earn-lbls').innerHTML = '';
        if(document.getElementById('tpl-earn-amts')) document.getElementById('tpl-earn-amts').innerHTML = '';
        if(document.getElementById('tpl-ded-lbls')) document.getElementById('tpl-ded-lbls').innerHTML = '';
        if(document.getElementById('tpl-ded-amts')) document.getElementById('tpl-ded-amts').innerHTML = '';
        
        // Force sync to build the template
        recalculateFinancials();
        let bankRow = document.getElementById('f-bank');
        if(bankRow) bankRow.value = emp.bank_name || '';
        let accRow = document.getElementById('f-acc');
        if(accRow) accRow.value = emp.bank_account_num || '';
        
        // Dispatch inputs to trigger regular bindLiveUpdate
        ['f-month', 'f-month-days', 'f-paid-days', 'f-cl-bal', 'f-el-bal', 'f-sl-bal', 'f-pay-date', 'f-acc'].forEach(id => {
            let el = document.getElementById(id);
            if(el) el.dispatchEvent(new Event('input'));
        });

        // Update Calculation Panel
        updateSalaryCalculationPanel();
        
        // Rebind drag sources
        bindDragSources();
        
    } catch(err) {
        console.error(err);
        alert('Failed to load employee data.');
    } finally {
        document.getElementById('loading-overlay').style.display = 'none';
        ['f-emp-id', 'f-emp-name', 'f-dept', 'f-doj', 'f-uan', 'f-acc'].forEach(id => {
            let el = document.getElementById(id);
            if(el) el.dispatchEvent(new Event('input'));
        });
    }
}

function updateSalaryCalculationPanel() {
    if (!lastFetchedEmployeeData || !lastFetchedEmployeeData.employee) return;
    
    document.getElementById('calc-empty').style.display = 'none';
    document.getElementById('calc-content').style.display = 'block';
    
    let emp = lastFetchedEmployeeData.employee;
    let data = lastFetchedEmployeeData;
    
    document.getElementById('calc-pos').innerText = emp.designation || 'N/A';
    document.getElementById('calc-month').innerText = document.getElementById('f-month').value || 'N/A';
    
    let monthDays = parseFloat(emp.month_days) || 31;
    let paidDays = parseFloat(emp.paid_days) || 0;
    
    document.getElementById('calc-month-days').innerText = monthDays;
    document.getElementById('calc-present-days').innerText = paidDays;
    
    let factor = monthDays > 0 ? (paidDays / monthDays) : 0;
    document.getElementById('calc-factor').innerText = `(Base / ${monthDays}) * ${paidDays} = ${factor.toFixed(4)}`;
    
    let earnHtml = '';
    let dedHtml = '';
    
    const formatAmt = (amt) => amt.toLocaleString('en-IN', {minimumFractionDigits: 2, maximumFractionDigits: 2});
    
    // Earnings Math
    let baseBasic = parseFloat(emp.basic_salary) || 0;
    let finalBasic = baseBasic * factor;
    earnHtml += `<tr><td>Basic Salary</td><td class="text-end text-muted">${formatAmt(baseBasic)}</td><td class="text-end fw-bold text-success">${formatAmt(finalBasic)}</td></tr>`;
    
    // Build from components
    if (data.components) {
        data.components.forEach(c => {
            let baseAmt = parseFloat(c.amount || 0);
            let finalAmt = baseAmt * factor;
            let row = `<tr><td>${c.component_name}</td><td class="text-end text-muted">${formatAmt(baseAmt)}</td><td class="text-end fw-bold">${formatAmt(finalAmt)}</td></tr>`;
            if (c.component_code === 1) {
                earnHtml += row;
            } else if (c.component_code === 2) {
                dedHtml += row;
            }
        });
    }
    
    document.getElementById('calc-earn-body').innerHTML = earnHtml;
    document.getElementById('calc-ded-body').innerHTML = dedHtml;
}

function addFieldWithValue(listId, lbl, val) {
    let borderCls = listId === 'earnings-list' ? 'border-success' : (listId === 'deductions-list' ? 'border-danger' : '');
    let html = `
        <div class="field-row drag-source">
            <i class="bi bi-list field-drag"></i>
            <div class="field-input-wrap ${borderCls}">
                <input type="text" class="field-label-input bg-light" value="${lbl}" oninput="recalculateFinancials()">
                <input type="text" class="field-value-input" value="${val}" oninput="recalculateFinancials()">
            </div>
        </div>
    `;
    document.getElementById(listId).insertAdjacentHTML('beforeend', html);
}

function recalculateFinancials() {
    let total_earn = 0;
    let total_ded = 0;
    
    let fMonthDays = document.getElementById('f-month-days');
    let fPaidDays = document.getElementById('f-paid-days');
    let monthDays = fMonthDays ? (parseFloat(fMonthDays.value) || 31) : 31;
    let paidDays = fPaidDays ? (parseFloat(fPaidDays.value) || monthDays) : monthDays;
    
    let desig = window.currentEmployeeDesignation || '';
    let proRataFactor = 1;
    let desigLower = desig.toLowerCase();
    
    if (desigLower.includes('director') || desigLower.includes('manager')) {
        proRataFactor = 1;
    } else if (desigLower.includes('intern') || desigLower.includes('trainee')) {
        proRataFactor = paidDays / 30;
    } else {
        proRataFactor = monthDays > 0 ? (paidDays / monthDays) : 1;
    }
    
    // Update Earnings
    let earnIndex = 0;
    document.querySelectorAll('#earnings-list .field-row').forEach(row => {
        let lbl = row.querySelector('.field-label-input').value;
        let baseVal = parseFloat(row.querySelector('.field-value-input').value || 0);
        let val = baseVal * proRataFactor;
        total_earn += val;
        
        let lblContainer = document.getElementById('tpl-earn-lbls');
        let amtContainer = document.getElementById('tpl-earn-amts');
        
        if (lblContainer && amtContainer) {
            let lblEl = document.getElementById('earn-lbl-' + earnIndex);
            let amtEl = document.getElementById('earn-amt-' + earnIndex);
            
            if (lblEl) {
                lblEl.innerHTML = lbl;
                amtEl.innerHTML = val.toFixed(2);
            } else {
                lblContainer.insertAdjacentHTML('beforeend', `<div id="earn-lbl-${earnIndex}" class="movable-label" style="display:flex; align-items:center; min-height:30px; position:relative; min-width:100px; line-height:1.2; word-break:break-word;">${lbl}</div>`);
                amtContainer.insertAdjacentHTML('beforeend', `<div id="earn-amt-${earnIndex}" class="movable-label" style="display:flex; align-items:center; min-height:30px; position:relative; min-width:50px; justify-content:flex-end;">${val.toFixed(2)}</div>`);
            }
        }
        earnIndex++;
    });
    
    // Update Deductions
    let dedIndex = 0;
    document.querySelectorAll('#deductions-list .field-row').forEach(row => {
        let lbl = row.querySelector('.field-label-input').value;
        let val = parseFloat(row.querySelector('.field-value-input').value || 0);
        // Note: Deductions usually apply full pro-rata factor as well unless specifically configured otherwise.
        let valDeducted = val * proRataFactor;
        total_ded += valDeducted;
        
        let lblContainer = document.getElementById('tpl-ded-lbls');
        let amtContainer = document.getElementById('tpl-ded-amts');
        
        if (lblContainer && amtContainer) {
            let lblEl = document.getElementById('ded-lbl-' + dedIndex);
            let amtEl = document.getElementById('ded-amt-' + dedIndex);
            
            if (lblEl) {
                lblEl.innerHTML = lbl;
                amtEl.innerHTML = valDeducted.toFixed(2);
            } else {
                lblContainer.insertAdjacentHTML('beforeend', `<div id="ded-lbl-${dedIndex}" class="movable-label" style="display:flex; align-items:center; min-height:30px; position:relative; min-width:100px; line-height:1.2; word-break:break-word;">${lbl}</div>`);
                amtContainer.insertAdjacentHTML('beforeend', `<div id="ded-amt-${dedIndex}" class="movable-label" style="display:flex; align-items:center; min-height:30px; position:relative; min-width:50px; justify-content:flex-end;">${valDeducted.toFixed(2)}</div>`);
            }
        }
        dedIndex++;
    });
    
    // Sync heights to ensure perfectly horizontal alignment even if labels wrap
    // Need a tiny timeout to allow the DOM to reflow and calculate offsetHeight correctly
    setTimeout(() => {
        for (let i = 0; i < earnIndex; i++) {
            let lblEl = document.getElementById('earn-lbl-' + i);
            let amtEl = document.getElementById('earn-amt-' + i);
            if (lblEl && amtEl) {
                // Reset heights to auto first in case it shrunk
                lblEl.style.height = 'auto';
                amtEl.style.height = 'auto';
                let maxH = Math.max(lblEl.offsetHeight, amtEl.offsetHeight);
                lblEl.style.height = maxH + 'px';
                amtEl.style.height = maxH + 'px';
            }
        }
        for (let i = 0; i < dedIndex; i++) {
            let lblEl = document.getElementById('ded-lbl-' + i);
            let amtEl = document.getElementById('ded-amt-' + i);
            if (lblEl && amtEl) {
                lblEl.style.height = 'auto';
                amtEl.style.height = 'auto';
                let maxH = Math.max(lblEl.offsetHeight, amtEl.offsetHeight);
                lblEl.style.height = maxH + 'px';
                amtEl.style.height = maxH + 'px';
            }
        }
    }, 10);
    
    addDragHandles();
    
    document.getElementById('f-net').value = (total_earn - total_ded).toFixed(2);
    
    if(document.getElementById('tpl-earn-total')) document.getElementById('tpl-earn-total').innerHTML = total_earn.toFixed(2);
    if(document.getElementById('tpl-ded-total')) document.getElementById('tpl-ded-total').innerHTML = total_ded.toFixed(2);
    
    let netPay = (total_earn - total_ded);
    if(document.getElementById('tpl-net-pay')) document.getElementById('tpl-net-pay').innerHTML = netPay.toFixed(2);
    if(document.getElementById('tpl-amt-words')) document.getElementById('tpl-amt-words').innerHTML = 'Rupees ' + numberToWords(Math.round(netPay));
}

function recalculateFromCanvas() {
    let total_earn = 0;
    let total_ded = 0;
    
    let earnEl = document.getElementById('tpl-earn-amts');
    if (earnEl) {
        let lines = earnEl.innerText.split('\n');
        lines.forEach(line => {
            let val = parseFloat(line.replace(/,/g, '').trim());
            if (!isNaN(val)) total_earn += val;
        });
    }
    
    let dedEl = document.getElementById('tpl-ded-amts');
    if (dedEl) {
        let lines = dedEl.innerText.split('\n');
        lines.forEach(line => {
            let val = parseFloat(line.replace(/,/g, '').trim());
            if (!isNaN(val)) total_ded += val;
        });
    }
    
    if(document.getElementById('tpl-earn-total')) document.getElementById('tpl-earn-total').innerHTML = total_earn.toFixed(2);
    if(document.getElementById('tpl-ded-total')) document.getElementById('tpl-ded-total').innerHTML = total_ded.toFixed(2);
    
    let netPay = (total_earn - total_ded);
    if(document.getElementById('tpl-net-pay')) document.getElementById('tpl-net-pay').innerHTML = netPay.toFixed(2);
    if(document.getElementById('tpl-amt-words')) document.getElementById('tpl-amt-words').innerHTML = 'Rupees ' + numberToWords(Math.round(netPay));
}

document.addEventListener('DOMContentLoaded', () => {
    let earnAmts = document.getElementById('tpl-earn-amts');
    if(earnAmts) earnAmts.addEventListener('input', recalculateFromCanvas);
    let dedAmts = document.getElementById('tpl-ded-amts');
    if(dedAmts) dedAmts.addEventListener('input', recalculateFromCanvas);
    
    addDragHandles();
});

// Visuals & Logic
let currentZoom = 1;
function setZoom(scale) {
    if(scale < 0.25 || scale > 2) return;
    currentZoom = scale;
    document.getElementById('canvas').style.transform = `scale(${scale})`;
    document.getElementById('zoom-level').textContent = Math.round(scale * 100) + '%';
}

function addField(listId, defaultLbl, defaultVal) {
    addFieldWithValue(listId, 'New ' + defaultLbl, defaultVal);
    bindDragSources();
}

let historyStack = [];
function saveState() {
    let clones = document.querySelectorAll('.canvas-field');
    let state = [];
    clones.forEach(c => state.push(c.outerHTML));
    historyStack.push(state.join(''));
    if(historyStack.length > 30) historyStack.shift();
}
function undo() {
    if(historyStack.length > 0) {
        let state = historyStack.pop();
        document.querySelectorAll('.canvas-field').forEach(e => e.remove());
        document.getElementById('canvas').insertAdjacentHTML('beforeend', state);
        rebindCanvasElements();
    }
}
document.addEventListener('keydown', function(e) {
    if (e.ctrlKey && e.key === 'z') { e.preventDefault(); undo(); }
});

let selectedEl = null;

function selectElement(el) {
    if(selectedEl) {
        selectedEl.classList.remove('selected');
    }
    selectedEl = el;
    selectedEl.classList.add('selected');
    
    document.getElementById('prop-empty').style.display = 'none';
    document.getElementById('prop-form').style.display = 'block';
    
    // Switch to Properties Tab automatically
    let propTab = new bootstrap.Tab(document.getElementById('prop-tab'));
    propTab.show();
    
    let lblNode = el.querySelector('.c-label');
    let valNode = el.querySelector('.c-value');
    
    document.getElementById('prop-lbl').value = lblNode ? lblNode.innerText.replace(':', '').trim() : '';
    document.getElementById('prop-val').value = valNode ? valNode.innerText.trim() : '';
    
    document.getElementById('prop-hide-label').checked = lblNode && lblNode.style.display === 'none';
    document.getElementById('prop-hide-value').checked = valNode && valNode.style.display === 'none';
    
    let fontSize = window.getComputedStyle(el).fontSize;
    document.getElementById('prop-font').value = parseInt(fontSize);
};

function updateSelectedText() {
    if(selectedEl) {
        let lbl = document.getElementById('prop-lbl').value;
        let val = document.getElementById('prop-val').value;
        
        let lblNode = selectedEl.querySelector('.c-label');
        let valNode = selectedEl.querySelector('.c-value');
        
        if(lblNode) lblNode.innerText = lbl ? lbl + ' : ' : '';
        if(valNode) valNode.innerText = val;
    }
}

function toggleVisibility() {
    if(selectedEl) {
        let hideLabel = document.getElementById('prop-hide-label').checked;
        let hideValue = document.getElementById('prop-hide-value').checked;
        let lblNode = selectedEl.querySelector('.c-label');
        let valNode = selectedEl.querySelector('.c-value');
        if(lblNode) lblNode.style.display = hideLabel ? 'none' : 'inline';
        if(valNode) valNode.style.display = hideValue ? 'none' : 'inline';
    }
}

document.getElementById('prop-font').addEventListener('input', function() {
    if(selectedEl) {
        let lblNode = selectedEl.querySelector('.c-label');
        let valNode = selectedEl.querySelector('.c-value');
        if (lblNode) lblNode.style.fontSize = this.value + 'px';
        if (valNode) valNode.style.fontSize = this.value + 'px';
        selectedEl.style.fontSize = this.value + 'px'; // fallback
    }
});

function toggleStyle(style) {
    if(selectedEl) {
        let lblNode = selectedEl.querySelector('.c-label');
        let valNode = selectedEl.querySelector('.c-value');
        
        if(style === 'bold') {
            let isBold = selectedEl.getAttribute('data-bold') === 'true';
            let newVal = isBold ? 'normal' : 'bold';
            selectedEl.setAttribute('data-bold', isBold ? 'false' : 'true');
            if (lblNode) lblNode.style.fontWeight = newVal;
            if (valNode) valNode.style.fontWeight = newVal;
        }
        if(style === 'italic') {
            let isItalic = selectedEl.getAttribute('data-italic') === 'true';
            let newVal = isItalic ? 'normal' : 'italic';
            selectedEl.setAttribute('data-italic', isItalic ? 'false' : 'true');
            if (lblNode) lblNode.style.fontStyle = newVal;
            if (valNode) valNode.style.fontStyle = newVal;
        }
    }
}

document.getElementById('canvas').addEventListener('mousedown', function(e) {
    let el = e.target.closest('.canvas-field');
    if(e.target.classList.contains('resize-handle') || e.target.closest('.element-toolbar')) return;
    
    if(el) {
        selectElement(el);
    } else {
        if(selectedEl) selectedEl.classList.remove('selected');
        selectedEl = null;
        document.getElementById('prop-empty').style.display = 'block';
        document.getElementById('prop-form').style.display = 'none';
    }
});

function deleteSelected() {
    if(selectedEl) {
        saveState();
        selectedEl.remove();
        selectedEl = null;
        document.getElementById('prop-form').style.display = 'none';
        document.getElementById('prop-empty').style.display = 'block';
    }
}

function addDragHandles() {
    document.querySelectorAll('.movable-label').forEach(el => {
        if(!el.querySelector('.drag-handle')) {
            el.insertAdjacentHTML('afterbegin', `<span class="drag-handle" contenteditable="false" style="cursor:grab; color:#ccc; margin-right:4px; font-size:14px; user-select:none;" title="Drag to move or swap">&#10021;</span>`);
            el.style.cursor = 'text'; // Make the rest of the label editable cursor
        }
    });
}

function rebindCanvasElements() {
    interact('.canvas-field').on('tap', function(event) {
        selectElement(event.currentTarget);
    });

    interact('.canvas-field')
        .draggable({
            listeners: {
                start() { saveState(); },
                move(event) {
                    var target = event.target;
                    var x = (parseFloat(target.getAttribute('data-x')) || 0) + event.dx / currentZoom;
                    var y = (parseFloat(target.getAttribute('data-y')) || 0) + event.dy / currentZoom;

                    target.style.transform = `translate(${x}px, ${y}px)`;
                    target.setAttribute('data-x', x);
                    target.setAttribute('data-y', y);
                    
                    if(selectedEl === target) {
                        document.getElementById('prop-x').value = Math.round(x);
                        document.getElementById('prop-y').value = Math.round(y);
                    }
                }
            }
        })
        .resizable({
            edges: { left: false, right: '.resize-handle', bottom: '.resize-handle', top: false },
            listeners: {
                start() { saveState(); },
                move(event) {
                    var target = event.target;
                    var x = (parseFloat(target.getAttribute('data-x')) || 0);
                    var y = (parseFloat(target.getAttribute('data-y')) || 0);

                    target.style.width = event.rect.width / currentZoom + 'px';
                    target.style.height = event.rect.height / currentZoom + 'px';

                    x += event.deltaRect.left / currentZoom;
                    y += event.deltaRect.top / currentZoom;

                    target.style.transform = `translate(${x}px, ${y}px)`;
                    target.setAttribute('data-x', x);
                    target.setAttribute('data-y', y);
                }
            }
        });

    interact('.movable-label')
        .draggable({
            allowFrom: '.drag-handle',
            listeners: {
                start() { saveState(); },
                move(event) {
                    var target = event.target;
                    var x = (parseFloat(target.getAttribute('data-x')) || 0) + event.dx / currentZoom;
                    var y = (parseFloat(target.getAttribute('data-y')) || 0) + event.dy / currentZoom;

                    target.style.transform = `translate(${x}px, ${y}px)`;
                    target.setAttribute('data-x', x);
                    target.setAttribute('data-y', y);
                }
            }
        })
        .dropzone({
            accept: '.movable-label',
            overlap: 0.5,
            ondrop: function(event) {
                let dragged = event.relatedTarget;
                let target = event.target;
                
                if (dragged !== target) {
                    let marker1 = document.createElement('div');
                    let marker2 = document.createElement('div');
                    dragged.parentNode.insertBefore(marker1, dragged);
                    target.parentNode.insertBefore(marker2, target);
                    
                    marker1.parentNode.insertBefore(target, marker1);
                    marker2.parentNode.insertBefore(dragged, marker2);
                    
                    marker1.parentNode.removeChild(marker1);
                    marker2.parentNode.removeChild(marker2);
                    
                    dragged.style.transform = 'none';
                    dragged.setAttribute('data-x', 0);
                    dragged.setAttribute('data-y', 0);
                    
                    target.style.transform = 'none';
                    target.setAttribute('data-x', 0);
                    target.setAttribute('data-y', 0);
                }
            }
        });
}

function bindDragSources() {
    interact('.drag-source').draggable({
        clone: true,
        listeners: {
            end: function(event) {
                let row = event.target.closest('.field-row');
                let lbl = row.querySelector('.field-label-input').value;
                let val = row.querySelector('.field-value-input').value;
                
                saveState();
                
                let newEl = document.createElement('div');
                newEl.className = 'canvas-field';
                
                let dropX = 150;
                let dropY = 150 + (document.querySelectorAll('.canvas-field').length * 20);
                
                newEl.setAttribute('data-x', dropX);
                newEl.setAttribute('data-y', dropY);
                newEl.style.transform = `translate(${dropX}px, ${dropY}px)`;
                
                newEl.innerHTML = `
                    <span class="c-label">${lbl} : </span>
                    <span class="c-value">${val}</span>
                    <div class="element-toolbar"><i class="bi bi-trash" onclick="deleteSelected()"></i></div>
                    <div class="resize-handle"></div>
                `;
                
                document.getElementById('canvas').appendChild(newEl);
                selectElement(newEl);
                rebindCanvasElements();
                
                // Hide helper placeholders
                document.querySelectorAll('.placeholder-text').forEach(el => el.style.display = 'none');
            }
        }
    });
}


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


saveState();
rebindCanvasElements();
bindDragSources();
function bindLiveUpdate(inputId, tplId, placeholderText) {
    let input = document.getElementById(inputId);
    let tpl = document.getElementById(tplId);
    if(input && tpl) {
        input.addEventListener('input', function() {
            if(this.value.trim() !== '') {
                tpl.innerHTML = `<span class="movable-label c-value" style="color:#000; display:inline-block; position:relative;">${this.value}</span>`;
                addDragHandles();
            } else {
                tpl.innerHTML = `<span class="placeholder-text" style="color:#aaa; pointer-events:none;">${placeholderText}</span>`;
            }
        });
    }
}

bindLiveUpdate('f-emp-id', 'tpl-emp-id', '[Drop ID]');
bindLiveUpdate('f-emp-name', 'tpl-emp-name', '[Drop Name]');
bindLiveUpdate('f-dept', 'tpl-dept', '[Drop Dept]');
bindLiveUpdate('f-doj', 'tpl-doj', '[Drop DOJ]');
bindLiveUpdate('f-uan', 'tpl-uan', '[Drop UAN]');
bindLiveUpdate('f-acc', 'tpl-acc', '[Drop Account]');

bindLiveUpdate('f-month', 'tpl-month', '[Month]');
bindLiveUpdate('f-month-days', 'tpl-month-days', '[Month Days]');
bindLiveUpdate('f-paid-days', 'tpl-paid-days', '[Days]');
bindLiveUpdate('f-cl-bal', 'tpl-cl-bal', '0');
bindLiveUpdate('f-el-bal', 'tpl-el-bal', '0');
bindLiveUpdate('f-sl-bal', 'tpl-sl-bal', '0');
bindLiveUpdate('f-pay-date', 'tpl-pay-date', '[Payment Date]');

document.getElementById('f-month-days').addEventListener('input', recalculateFinancials);
document.getElementById('f-paid-days').addEventListener('input', recalculateFinancials);

function printPayslip() {
    let canvas = document.getElementById('canvas');
    let originalTransform = canvas.style.transform;
    canvas.style.transform = 'none';
    
    let printWin = window.open('', '_blank');
    printWin.document.write('<html><head><title>Print Payslip</title>');
    let styles = document.querySelectorAll('style, link[rel="stylesheet"]');
    styles.forEach(s => printWin.document.write(s.outerHTML));
    printWin.document.write('</head><body style="background:white; margin:0; padding:20px;">');
    printWin.document.write(canvas.outerHTML);
    printWin.document.write('</body></html>');
    printWin.document.close();
    printWin.focus();
    
    setTimeout(() => {
        printWin.print();
        printWin.close();
        canvas.style.transform = originalTransform;
    }, 500);
}

function downloadPDF() {
    let canvas = document.getElementById('canvas');
    let originalTransform = canvas.style.transform;
    canvas.style.transform = 'none';
    
    let opt = {
      margin:       10,
      filename:     (document.getElementById('tpl-payslip-no')?.innerText || 'Payslip') + '.pdf',
      image:        { type: 'jpeg', quality: 0.98 },
      html2canvas:  { scale: 2, useCORS: true },
      jsPDF:        { unit: 'mm', format: 'a4', orientation: 'portrait' }
    };
    
    html2pdf().set(opt).from(canvas).save().then(() => {
        canvas.style.transform = originalTransform;
    });
}

async function saveTemplate() {
    let templateName = prompt("Enter a name for this Payslip Template:");
    if(!templateName) return;
    
    let canvas = document.getElementById('canvas');
    let layoutHtml = canvas.innerHTML;
    
    try {
        let res = await fetch('/api/templates/save', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                template_name: templateName,
                layout_json: layoutHtml
            })
        });
        let data = await res.json();
        if(data.success) {
            alert('Template Saved Successfully!');
        } else {
            alert('Error saving template: ' + data.error);
        }
    } catch(err) {
        console.error(err);
        alert('Failed to save template.');
    }
}

async function loadTemplate() {
    try {
        let res = await fetch('/api/templates/load');
        let data = await res.json();
        
        if(data.templates && data.templates.length > 0) {
            let names = data.templates.map((t, i) => `${i+1}. ${t.template_name}`).join('\\n');
            let sel = prompt("Select Template Number to load:\\n" + names);
            let idx = parseInt(sel) - 1;
            
            if(data.templates[idx]) {
                document.getElementById('canvas').innerHTML = data.templates[idx].layout_json;
                bindDragSources();
                rebindCanvasElements();
                alert('Template Loaded!');
            }
        } else {
            alert("No templates found.");
        }
    } catch(err) {
        console.error(err);
        alert("Failed to load templates.");
    }
}

