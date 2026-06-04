content = """{% extends 'base.html' %}

{% block content %}
<div class="row g-4">
    <div class="col-12">
        <h4 class="mb-1 fw-bold text-dark d-flex align-items-center">
            <i class="bi bi-receipt text-primary me-2"></i>
            Live Payslip Builder
        </h4>
        <p class="text-muted small mb-0">Create custom payslips and instantly preview them with multiple templates before saving to the master records.</p>
    </div>

    <!-- Builder Controls -->
    <div class="col-lg-5 col-md-12">
        <div class="card shadow-sm border-0 h-100 card-glow">
            <div class="card-header bg-dark text-white border-0 py-3">
                <h5 class="card-title mb-0 d-flex align-items-center">
                    <i class="bi bi-sliders me-2"></i>
                    Payslip Parameters
                </h5>
            </div>
            <div class="card-body p-4">
                <form action="{{ url_for('payslip_builder') }}" method="POST" id="payslip-form">
                    
                    <div class="mb-3">
                        <label class="form-label fw-medium text-dark">Select Template Theme</label>
                        <select class="form-select border-secondary-subtle" id="template_selector" onchange="changeTemplate()">
                            <option value="modern" selected>Modern Teal (Enerpize)</option>
                            <option value="minimal">Minimal Elegant (Starwell)</option>
                            <option value="classic">Classic Table (TankhaPay)</option>
                        </select>
                    </div>

                    <div class="row g-3">
                        <div class="col-md-6 col-12">
                            <label class="form-label fw-medium text-dark">Employee ID</label>
                            <input type="text" class="form-control border-secondary-subtle" name="emp_id" id="emp_id" placeholder="e.g. EMP-2026" required oninput="updatePreview()">
                        </div>
                        <div class="col-md-6 col-12">
                            <label class="form-label fw-medium text-dark">Employee Name</label>
                            <input type="text" class="form-control border-secondary-subtle" id="emp_name" placeholder="John Doe" oninput="updatePreview()">
                        </div>
                        <div class="col-md-6 col-12">
                            <label class="form-label fw-medium text-dark">Designation</label>
                            <input type="text" class="form-control border-secondary-subtle" name="designation" id="designation" placeholder="e.g. Software Engineer" oninput="updatePreview()">
                        </div>
                        <div class="col-md-6 col-12">
                            <label class="form-label fw-medium text-dark">Department</label>
                            <input type="text" class="form-control border-secondary-subtle" name="department" id="department" placeholder="e.g. IT" oninput="updatePreview()">
                        </div>
                        <div class="col-md-6 col-12">
                            <label class="form-label fw-medium text-dark">Bank Account</label>
                            <input type="text" class="form-control border-secondary-subtle" id="bank_acc" placeholder="123456789" oninput="updatePreview()">
                        </div>
                        <div class="col-md-6 col-12">
                            <label class="form-label fw-medium text-dark">Month/Period</label>
                            <input type="text" class="form-control border-secondary-subtle" id="period" placeholder="01/01/2026" oninput="updatePreview()">
                        </div>
                    </div>
                    
                    <div class="row g-3 mt-1">
                        <div class="col-md-12 col-12">
                            <label class="form-label fw-medium text-dark">Basic Salary (₹)</label>
                            <input type="number" class="form-control border-secondary-subtle" name="basic_salary" id="basic_salary" placeholder="0" oninput="updateTotals()">
                        </div>
                        
                        <div class="col-12 mt-3">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <label class="form-label fw-medium text-dark mb-0">Financial Components</label>
                                <button type="button" class="btn btn-sm btn-outline-primary py-0 px-2 fs-7" onclick="addComponentRow()"><i class="bi bi-plus-lg"></i> Add Component</button>
                            </div>
                            <div id="dynamic-components-container" class="d-flex flex-column gap-2">
                                <!-- Default empty row -->
                                <div class="input-group input-group-sm component-row">
                                    <select class="form-select border-secondary-subtle w-25" name="component_code[]" onchange="updateTotals()">
                                        <option value="1" selected>Allowance (1)</option>
                                        <option value="2">Deduction (2)</option>
                                    </select>
                                    <input type="text" class="form-control border-secondary-subtle w-50" name="component_name[]" placeholder="Component Name" oninput="updatePreview()">
                                    <input type="number" class="form-control border-secondary-subtle w-25 component-amt" name="component_amount[]" placeholder="Amount" value="0" oninput="updateTotals()">
                                    <button type="button" class="btn btn-outline-danger px-2" onclick="this.parentElement.remove(); updateTotals();"><i class="bi bi-x"></i></button>
                                </div>
                            </div>
                        </div>

                        <!-- Hidden fields for backend to know total allowance/deduction -->
                        <input type="hidden" name="total_allowance" id="total_allowance" value="0">
                        <input type="hidden" name="total_deduction" id="total_deduction" value="0">

                        <div class="col-12 mt-3">
                            <label class="form-label fw-medium text-dark fw-bold text-success">Net Pay (₹)</label>
                            <input type="number" class="form-control border-success text-success fw-bold bg-success-subtle fs-5" name="final_in_hand_salary" id="final_in_hand_salary" readonly>
                        </div>
                    </div>

                    <button type="submit" class="btn btn-primary w-100 py-2 mt-4 d-flex align-items-center justify-content-center">
                        <i class="bi bi-save me-2"></i>
                        <span>Save to Payslip Master</span>
                    </button>
                </form>
            </div>
        </div>
    </div>

    <!-- Live Preview -->
    <div class="col-lg-7 col-md-12">
        <div class="card shadow-sm border-0 h-100 bg-light">
            <div class="card-header bg-transparent border-0 py-3 text-center">
                <span class="badge bg-primary px-3 py-2 rounded-pill tracking-wider text-uppercase">Live Preview</span>
            </div>
            <div class="card-body p-4 d-flex justify-content-center align-items-start" style="overflow-x: auto;">
                
                <!-- 1. MODERN TEAL (Enerpize style) -->
                <div id="tpl_modern" class="payslip-wrapper d-none w-100">
                    <div class="modern-inner">
                        <div class="modern-header d-flex justify-content-between align-items-start">
                            <h1 class="modern-title">PAYSLIP<br>TEMPLATE</h1>
                            <div class="modern-logo d-flex align-items-center text-primary fw-bold fs-3">
                                <i class="bi bi-lightning-charge-fill me-1"></i> enerpize
                            </div>
                        </div>
                        
                        <div class="modern-sec-header mt-4">Your business name</div>
                        <div class="modern-sec-body">
                            Business Address<br>
                            Contact Number
                        </div>
                        <hr class="modern-hr">

                        <div class="row gx-4">
                            <div class="col-6">
                                <div class="modern-sec-header">Employee details</div>
                                <div class="modern-sec-body d-flex justify-content-between">
                                    <span>Employee name</span>
                                    <span class="dyn-name">--</span>
                                </div>
                                <div class="modern-sec-body-light mt-1 mb-2">Employee address</div>
                                <div class="modern-sec-body-light d-flex justify-content-between">
                                    <span>Designation</span>
                                    <span class="dyn-desig">--</span>
                                </div>
                            </div>
                            <div class="col-6">
                                <div class="modern-sec-header">Direct Credit Details</div>
                                <div class="modern-sec-body d-flex justify-content-between">
                                    <span>Primary Bank Account</span>
                                    <span class="dyn-bank">--</span>
                                </div>
                            </div>
                        </div>

                        <hr class="modern-hr mt-4">
                        <div class="row text-center modern-meta">
                            <div class="col-3 text-start">Period end</div>
                            <div class="col-3 fw-bold dyn-period">01/01/2026</div>
                            <div class="col-3">Tax code</div>
                            <div class="col-3 fw-bold">XX</div>
                        </div>
                        <hr class="modern-hr mb-4">

                        <table class="modern-table w-100">
                            <thead>
                                <tr>
                                    <th>Payments</th>
                                    <th>Type</th>
                                    <th>Rate</th>
                                    <th>Hours</th>
                                    <th class="text-end">Amount</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr class="bg-light">
                                    <td>Basic Salary</td>
                                    <td>Salary</td>
                                    <td></td>
                                    <td></td>
                                    <td class="text-end dyn-basic">0.00</td>
                                </tr>
                                <tr id="modern_allow_list"></tr>
                            </tbody>
                            <tfoot>
                                <tr>
                                    <td>Total Ordinary Payment</td>
                                    <td></td>
                                    <td></td>
                                    <td></td>
                                    <td class="text-end dyn-gross">0.00</td>
                                </tr>
                            </tfoot>
                        </table>

                        <table class="modern-table w-100 mt-3">
                            <thead>
                                <tr>
                                    <th>Deductions</th>
                                    <th></th>
                                    <th></th>
                                    <th></th>
                                    <th class="text-end">Amount</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr id="modern_deduct_list"></tr>
                            </tbody>
                            <tfoot>
                                <tr>
                                    <td>Total Deductions</td>
                                    <td></td>
                                    <td></td>
                                    <td></td>
                                    <td class="text-end dyn-tot-deduct">0.00</td>
                                </tr>
                                <tr class="modern-net">
                                    <td>Net Pay</td>
                                    <td></td>
                                    <td></td>
                                    <td></td>
                                    <td class="text-end dyn-net">0.00</td>
                                </tr>
                            </tfoot>
                        </table>
                    </div>
                </div>

                <!-- 2. MINIMAL ELEGANT (Starwell style) -->
                <div id="tpl_minimal" class="payslip-wrapper d-none w-100">
                    <div class="minimal-inner">
                        <div class="minimal-header d-flex justify-content-between align-items-center mb-4">
                            <div class="minimal-co">
                                <h3>Starwell Inc.</h3>
                                <p>1234 Parkway St, Los Angeles CA 90003<br>info@yourcompany.com | 1 (555) 123 1234</p>
                            </div>
                            <div class="minimal-logo text-end">
                                <i class="bi bi-globe fs-1"></i>
                                <h2 class="mt-1 tracking-widest">PAYSLIP</h2>
                            </div>
                        </div>
                        
                        <div class="minimal-black-bar d-flex justify-content-between text-white p-2 mb-3">
                            <span>Employee Details</span>
                            <span>Net Pay: <strong class="dyn-net">$0.00</strong></span>
                        </div>

                        <div class="row minimal-info mb-4">
                            <div class="col-6">
                                <div class="d-flex"><span class="w-50">Employee Name :</span> <span class="dyn-name w-50">--</span></div>
                                <div class="d-flex"><span class="w-50">Employee ID :</span> <span class="dyn-id w-50">--</span></div>
                                <div class="d-flex"><span class="w-50">E-mail ID :</span> <span class="w-50">employee@company</span></div>
                                <div class="d-flex"><span class="w-50">Contact No :</span> <span class="w-50">555-1234</span></div>
                            </div>
                            <div class="col-6">
                                <div class="d-flex"><span class="w-50">Department :</span> <span class="dyn-dept w-50">--</span></div>
                                <div class="d-flex"><span class="w-50">Designation :</span> <span class="dyn-desig w-50">--</span></div>
                                <div class="d-flex"><span class="w-50">Bank Account No. :</span> <span class="dyn-bank w-50">--</span></div>
                                <div class="d-flex"><span class="w-50">Pay Period:</span> <span class="dyn-period w-50">--</span></div>
                            </div>
                        </div>

                        <div class="row">
                            <div class="col-6">
                                <div class="minimal-col-header d-flex justify-content-between border-bottom pb-1 mb-2 fw-bold">
                                    <span>EARNINGS</span><span>AMOUNT</span>
                                </div>
                                <div class="d-flex justify-content-between minimal-row">
                                    <span>Basic Salary</span><span class="dyn-basic">0.00</span>
                                </div>
                                <div id="minimal_allow_list"></div>
                            </div>
                            <div class="col-6">
                                <div class="minimal-col-header d-flex justify-content-between border-bottom pb-1 mb-2 fw-bold">
                                    <span>DEDUCTIONS</span><span>AMOUNT</span>
                                </div>
                                <div id="minimal_deduct_list"></div>
                            </div>
                        </div>

                        <div class="row mt-4 pt-3 border-top minimal-totals">
                            <div class="col-6">
                                <div class="d-flex justify-content-between fw-bold">
                                    <span>Gross Salary</span><span class="dyn-gross">0.00</span>
                                </div>
                            </div>
                            <div class="col-6">
                                <div class="d-flex justify-content-between fw-bold mb-2">
                                    <span>Total Deductions</span><span class="dyn-tot-deduct">0.00</span>
                                </div>
                                <div class="d-flex justify-content-between fw-bold fs-6 mt-3">
                                    <span>NET Salary</span><span class="dyn-net">0.00</span>
                                </div>
                            </div>
                        </div>

                        <div class="row mt-5 pt-4 minimal-sigs">
                            <div class="col-6">
                                <span>Employee Signature : _________________</span>
                            </div>
                            <div class="col-6 text-end">
                                <span>Employer Signature : _________________</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 3. CLASSIC TABLE (TankhaPay style) -->
                <div id="tpl_classic" class="payslip-wrapper d-none w-100">
                    <div class="classic-inner">
                        <div class="classic-logo text-center mb-2">
                            <i class="bi bi-shield-shaded fs-2 text-primary"></i>
                            <h3 class="text-primary d-inline fw-bold">TankhaPay</h3>
                        </div>
                        
                        <table class="table table-bordered classic-table">
                            <tbody>
                                <tr class="classic-blue text-center fw-bold fs-5"><td colspan="4">Company Name</td></tr>
                                <tr class="classic-light-blue text-center fw-bold"><td colspan="4">Pay Slip</td></tr>
                                <tr>
                                    <td colspan="4"><strong>Employee Name :</strong> <span class="dyn-name">--</span></td>
                                </tr>
                                <tr>
                                    <td colspan="4"><strong>Designation :</strong> <span class="dyn-desig">--</span></td>
                                </tr>
                                <tr>
                                    <td colspan="4"><strong>Department :</strong> <span class="dyn-dept">--</span></td>
                                </tr>
                                <tr>
                                    <td colspan="4"><strong>Month :</strong> <span class="dyn-period">--</span></td>
                                </tr>
                                <tr class="classic-blue text-center fw-bold">
                                    <td colspan="2" class="w-50">Earnings</td>
                                    <td colspan="2" class="w-50">Deductions</td>
                                </tr>
                                <tr class="classic-light-blue fw-bold">
                                    <td>Salary head</td>
                                    <td class="text-end">Amount</td>
                                    <td>Salary head</td>
                                    <td class="text-end">Amount</td>
                                </tr>
                                
                                <!-- Table body is generated via JS row matching -->
                                <tbody id="classic_body">
                                </tbody>

                                <tr class="fw-bold classic-totals">
                                    <td>Salary (GROSS) / PM</td>
                                    <td class="text-end dyn-gross">0.00</td>
                                    <td>Total Deduction</td>
                                    <td class="text-end dyn-tot-deduct">0.00</td>
                                </tr>
                                <tr class="fw-bold bg-light">
                                    <td colspan="2" class="text-end">NET SALARY:</td>
                                    <td colspan="2" class="fs-5 dyn-net text-end">0.00</td>
                                </tr>
                            </tbody>
                        </table>
                        
                        <div class="d-flex justify-content-between mt-5 pt-3 classic-footer">
                            <div class="border-top pt-1 px-3">Prepared by</div>
                            <div class="border-top pt-1 px-3">Checked by</div>
                            <div class="border-top pt-1 px-3">Authorized by</div>
                        </div>
                    </div>
                </div>

            </div>
        </div>
    </div>
</div>

<style>
/* Base Wrapper */
.payslip-wrapper {
    background: #fff;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    margin: 0 auto;
    font-size: 14px;
}

/* 1. MODERN TEAL (Enerpize) */
.modern-inner { padding: 40px; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #333; }
.modern-title { font-weight: 900; color: #64748b; letter-spacing: 2px; line-height: 1.1; margin: 0;}
.modern-logo { color: #6366f1; }
.modern-sec-header { background: #71b4bd; color: #fff; padding: 5px 10px; font-weight: 600; margin-bottom: 5px; }
.modern-sec-body { background: #e0f2f1; padding: 5px 10px; }
.modern-sec-body-light { background: #f1f8f8; padding: 5px 10px; }
.modern-hr { border-top: 1px solid #71b4bd; opacity: 1; margin: 10px 0; }
.modern-meta { font-size: 12px; }
.modern-table { border-collapse: collapse; }
.modern-table th { background: #71b4bd; color: #fff; padding: 6px 10px; font-weight: normal; }
.modern-table td { padding: 6px 10px; border-bottom: 1px solid #e2e8f0; }
.modern-net td { font-weight: bold; background: #f1f8f8; font-size: 16px;}

/* 2. MINIMAL ELEGANT (Starwell) */
.minimal-inner { padding: 50px; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; color: #000; border: 1px solid #ddd;}
.minimal-co h3 { font-style: italic; font-weight: bold; margin-bottom: 0;}
.minimal-co p { font-size: 11px; color: #666; }
.minimal-logo h2 { letter-spacing: 5px; font-weight: normal; font-size: 20px;}
.minimal-black-bar { background: #333; font-weight: bold; font-size: 13px;}
.minimal-info { font-size: 11px; line-height: 1.8; }
.minimal-col-header { font-size: 11px; }
.minimal-row { font-size: 12px; margin-bottom: 4px;}
.minimal-totals { font-size: 12px; }
.minimal-sigs { font-size: 11px; color: #333;}

/* 3. CLASSIC TABLE (TankhaPay) */
.classic-inner { padding: 30px; font-family: Arial, sans-serif; color: #000; }
.classic-table { border: 2px solid #000; margin-bottom: 0; font-size: 12px;}
.classic-table td, .classic-table th { border: 1px solid #000 !important; padding: 6px; }
.classic-blue { background-color: #8bb3e0 !important; }
.classic-light-blue { background-color: #d0def0 !important; }
.classic-footer { font-size: 12px; }
</style>

<script>
    function addComponentRow() {
        const container = document.getElementById('dynamic-components-container');
        const row = document.createElement('div');
        row.className = 'input-group input-group-sm component-row';
        row.innerHTML = `
            <select class="form-select border-secondary-subtle w-25" name="component_code[]" onchange="updateTotals()">
                <option value="1" selected>Allowance (1)</option>
                <option value="2">Deduction (2)</option>
            </select>
            <input type="text" class="form-control border-secondary-subtle w-50" name="component_name[]" placeholder="Component Name" oninput="updatePreview()">
            <input type="number" class="form-control border-secondary-subtle w-25 component-amt" name="component_amount[]" placeholder="Amount" value="0" oninput="updateTotals()">
            <button type="button" class="btn btn-outline-danger px-2" onclick="this.parentElement.remove(); updateTotals();"><i class="bi bi-x"></i></button>
        `;
        container.appendChild(row);
    }

    function updateTotals() {
        let b = parseFloat(document.getElementById('basic_salary').value) || 0;
        
        let total_allow = 0;
        let total_deduct = 0;

        const rows = document.querySelectorAll('.component-row');
        rows.forEach(row => {
            const code = row.querySelector('select[name="component_code[]"]').value;
            const amt = parseFloat(row.querySelector('input[name="component_amount[]"]').value) || 0;
            if (code === "1") {
                total_allow += amt;
            } else if (code === "2") {
                total_deduct += amt;
            }
        });

        document.getElementById('total_allowance').value = total_allow;
        document.getElementById('total_deduction').value = total_deduct;

        let net = (b + total_allow) - total_deduct;
        document.getElementById('final_in_hand_salary').value = net.toFixed(2);
        
        updatePreview();
    }

    function updateElements(selector, value) {
        document.querySelectorAll(selector).forEach(el => el.textContent = value);
    }

    function updatePreview() {
        let b = parseFloat(document.getElementById('basic_salary').value) || 0;
        let id = document.getElementById('emp_id').value || '--';
        let name = document.getElementById('emp_name').value || '--';
        let desig = document.getElementById('designation').value || '--';
        let dept = document.getElementById('department').value || '--';
        let bank = document.getElementById('bank_acc').value || '--';
        let period = document.getElementById('period').value || '--';

        // Update static fields across all themes
        updateElements('.dyn-id', id);
        updateElements('.dyn-name', name);
        updateElements('.dyn-desig', desig);
        updateElements('.dyn-dept', dept);
        updateElements('.dyn-bank', bank);
        updateElements('.dyn-period', period);
        updateElements('.dyn-basic', b.toFixed(2));
        
        let allows = [];
        let deducts = [];
        let total_allow = 0;
        let total_deduct = 0;

        const rows = document.querySelectorAll('.component-row');
        rows.forEach(row => {
            const code = row.querySelector('select[name="component_code[]"]').value;
            const cname = row.querySelector('input[name="component_name[]"]').value || 'Component';
            const amt = parseFloat(row.querySelector('input[name="component_amount[]"]').value) || 0;
            
            if (code === "1" && amt > 0) {
                total_allow += amt;
                allows.push({name: cname, amt: amt});
            } else if (code === "2" && amt > 0) {
                total_deduct += amt;
                deducts.push({name: cname, amt: amt});
            }
        });

        let gross = b + total_allow;
        let net = gross - total_deduct;

        updateElements('.dyn-gross', gross.toFixed(2));
        updateElements('.dyn-tot-deduct', total_deduct.toFixed(2));
        updateElements('.dyn-net', net.toFixed(2));

        // 1. Modern List
        let ml_allow = '';
        allows.forEach(a => {
            ml_allow += `<tr><td>${a.name}</td><td>Allowance</td><td></td><td></td><td class="text-end">${a.amt.toFixed(2)}</td></tr>`;
        });
        document.getElementById('modern_allow_list').innerHTML = ml_allow;

        let ml_deduct = '';
        deducts.forEach(d => {
            ml_deduct += `<tr><td>${d.name}</td><td></td><td></td><td></td><td class="text-end">${d.amt.toFixed(2)}</td></tr>`;
        });
        document.getElementById('modern_deduct_list').innerHTML = ml_deduct;

        // 2. Minimal List
        let min_allow = '';
        allows.forEach(a => {
            min_allow += `<div class="d-flex justify-content-between minimal-row"><span>${a.name}</span><span>${a.amt.toFixed(2)}</span></div>`;
        });
        document.getElementById('minimal_allow_list').innerHTML = min_allow;

        let min_deduct = '';
        deducts.forEach(d => {
            min_deduct += `<div class="d-flex justify-content-between minimal-row"><span>${d.name}</span><span>${d.amt.toFixed(2)}</span></div>`;
        });
        document.getElementById('minimal_deduct_list').innerHTML = min_deduct;

        // 3. Classic Table Matrix (Match rows)
        let classic_html = '<tr><td>Basic</td><td class="text-end">'+b.toFixed(2)+'</td><td></td><td></td></tr>';
        let max_rows = Math.max(allows.length, deducts.length);
        for (let i = 0; i < max_rows; i++) {
            let aname = allows[i] ? allows[i].name : '';
            let aamt = allows[i] ? allows[i].amt.toFixed(2) : '';
            let dname = deducts[i] ? deducts[i].name : '';
            let damt = deducts[i] ? deducts[i].amt.toFixed(2) : '';
            classic_html += `<tr><td>${aname}</td><td class="text-end">${aamt}</td><td>${dname}</td><td class="text-end">${damt}</td></tr>`;
        }
        document.getElementById('classic_body').innerHTML = classic_html;
    }
    
    function changeTemplate() {
        let sel = document.getElementById('template_selector').value;
        document.getElementById('tpl_modern').classList.add('d-none');
        document.getElementById('tpl_minimal').classList.add('d-none');
        document.getElementById('tpl_classic').classList.add('d-none');
        
        document.getElementById('tpl_' + sel).classList.remove('d-none');
        updatePreview();
    }

    // Initialize on load
    document.addEventListener('DOMContentLoaded', () => {
        changeTemplate();
        updateTotals();
    });
</script>
{% endblock %}
"""

with open('templates/payslip_builder.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated templates/payslip_builder.html")
