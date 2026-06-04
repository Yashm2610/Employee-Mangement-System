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
                            <option value="modern" selected>Modern Blue</option>
                            <option value="classic">Classic Corporate</option>
                            <option value="minimal">Minimal Clean</option>
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
            <div class="card-body p-4 d-flex justify-content-center align-items-start">
                
                <!-- The Payslip Preview Box -->
                <div id="payslip_preview" class="payslip-theme-modern w-100">
                    <div class="payslip-header">
                        <h2 class="company-name">Maxworth Enterprises</h2>
                        <p class="payslip-title">Payslip</p>
                    </div>
                    
                    <div class="payslip-body">
                        <div class="employee-info row mb-4">
                            <div class="col-6">
                                <strong>Employee Name:</strong> <span id="prev_name">--</span><br>
                                <strong>Employee ID:</strong> <span id="prev_id">--</span>
                            </div>
                            <div class="col-6 text-end">
                                <strong>Designation:</strong> <span id="prev_desig">--</span><br>
                                <strong>Department:</strong> <span id="prev_dept">--</span>
                            </div>
                        </div>

                        <div class="salary-breakdown row">
                            <div class="col-6">
                                <div class="earning-box">
                                    <h4>Earnings</h4>
                                    <div class="d-flex justify-content-between mb-2">
                                        <strong>Basic Salary</strong>
                                        <strong>₹<span id="prev_basic">0.00</span></strong>
                                    </div>
                                    <div id="prev_allowances_list">
                                        <!-- Allowances go here -->
                                    </div>
                                    <div class="d-flex justify-content-between mt-3 pt-2 border-top">
                                        <strong>Total Allowances</strong>
                                        <strong>₹<span id="prev_allow">0.00</span></strong>
                                    </div>
                                </div>
                            </div>
                            <div class="col-6">
                                <div class="deduction-box">
                                    <h4>Deductions</h4>
                                    <div id="prev_deductions_list">
                                        <!-- Deductions go here -->
                                    </div>
                                    <div class="d-flex justify-content-between mt-3 pt-2 border-top">
                                        <strong>Total Deductions</strong>
                                        <strong>₹<span id="prev_deduct">0.00</span></strong>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="net-pay-section mt-4 text-end">
                            <h3 class="net-pay-text">Net Salary: ₹<span id="prev_net">0.00</span></h3>
                        </div>
                    </div>
                </div>

            </div>
        </div>
    </div>
</div>

<style>
/* Base Styles */
#payslip_preview {
    transition: all 0.3s ease;
    margin: 0 auto;
}

/* 1. Modern Blue Theme */
.payslip-theme-modern {
    background: #ffffff;
    border-radius: 12px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.05);
    overflow: hidden;
    border: 1px solid #e2e8f0;
}
.payslip-theme-modern .payslip-header {
    background: linear-gradient(135deg, #2563eb, #1e40af);
    color: white;
    padding: 25px;
    text-align: center;
}
.payslip-theme-modern .company-name { font-weight: 800; font-size: 24px; margin-bottom: 5px; }
.payslip-theme-modern .payslip-title { font-weight: 500; opacity: 0.9; margin: 0; }
.payslip-theme-modern .payslip-body { padding: 30px; }
.payslip-theme-modern .earning-box, .payslip-theme-modern .deduction-box {
    background: #f8fafc;
    border-radius: 8px;
    padding: 15px;
    border: 1px solid #e2e8f0;
    height: 100%;
}
.payslip-theme-modern h4 { font-size: 16px; font-weight: 700; color: #475569; margin-bottom: 15px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px;}
.payslip-theme-modern .net-pay-section {
    background: #f0fdf4;
    border: 1px dashed #22c55e;
    padding: 15px 25px;
    border-radius: 8px;
}
.payslip-theme-modern .net-pay-text { color: #15803d; font-weight: 800; margin: 0; }

/* 2. Classic Corporate Theme */
.payslip-theme-classic {
    background: #ffffff;
    border: 2px solid #000;
    font-family: 'Times New Roman', serif;
}
.payslip-theme-classic .payslip-header {
    border-bottom: 2px solid #000;
    padding: 20px;
    text-align: center;
}
.payslip-theme-classic .company-name { font-weight: bold; font-size: 26px; text-transform: uppercase; color: #000; margin-bottom: 5px; }
.payslip-theme-classic .payslip-title { font-style: italic; color: #333; margin: 0; }
.payslip-theme-classic .payslip-body { padding: 30px; color: #000; }
.payslip-theme-classic .earning-box, .payslip-theme-classic .deduction-box {
    border: 1px solid #000;
    padding: 15px;
    height: 100%;
}
.payslip-theme-classic h4 { font-size: 16px; font-weight: bold; text-transform: uppercase; border-bottom: 1px solid #000; padding-bottom: 5px; color: #000;}
.payslip-theme-classic .net-pay-section {
    border-top: 2px solid #000;
    border-bottom: 2px double #000;
    padding: 15px 0;
    margin-top: 30px;
}
.payslip-theme-classic .net-pay-text { color: #000; font-weight: bold; margin: 0; }

/* 3. Minimal Clean Theme */
.payslip-theme-minimal {
    background: #fafafa;
    border-radius: 0;
    box-shadow: none;
    font-family: 'Inter', sans-serif;
}
.payslip-theme-minimal .payslip-header {
    padding: 40px 30px 20px 30px;
    text-align: left;
}
.payslip-theme-minimal .company-name { font-weight: 300; font-size: 28px; color: #111; letter-spacing: -1px; margin-bottom: 5px; }
.payslip-theme-minimal .payslip-title { font-weight: 400; color: #888; font-size: 14px; margin: 0; text-transform: uppercase; letter-spacing: 1px;}
.payslip-theme-minimal .payslip-body { padding: 0 30px 40px 30px; color: #333; }
.payslip-theme-minimal .earning-box, .payslip-theme-minimal .deduction-box {
    padding: 20px 0;
    height: 100%;
}
.payslip-theme-minimal h4 { font-size: 12px; font-weight: 600; color: #aaa; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 15px;}
.payslip-theme-minimal .net-pay-section {
    margin-top: 40px;
    padding-top: 20px;
    border-top: 1px solid #eee;
}
.payslip-theme-minimal .net-pay-text { color: #111; font-weight: 400; font-size: 32px; letter-spacing: -1px; margin: 0; }
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

    function updatePreview() {
        document.getElementById('prev_id').textContent = document.getElementById('emp_id').value || '--';
        document.getElementById('prev_name').textContent = document.getElementById('emp_name').value || '--';
        document.getElementById('prev_desig').textContent = document.getElementById('designation').value || '--';
        document.getElementById('prev_dept').textContent = document.getElementById('department').value || '--';
        
        let b = parseFloat(document.getElementById('basic_salary').value) || 0;
        document.getElementById('prev_basic').textContent = b.toFixed(2);
        
        let allow_html = '';
        let deduct_html = '';
        let total_allow = 0;
        let total_deduct = 0;

        const rows = document.querySelectorAll('.component-row');
        rows.forEach(row => {
            const code = row.querySelector('select[name="component_code[]"]').value;
            const name = row.querySelector('input[name="component_name[]"]').value || 'Component';
            const amt = parseFloat(row.querySelector('input[name="component_amount[]"]').value) || 0;
            
            if (code === "1" && amt > 0) {
                total_allow += amt;
                allow_html += `<div class="d-flex justify-content-between text-muted small mb-1"><span>${name}</span><span>₹${amt.toFixed(2)}</span></div>`;
            } else if (code === "2" && amt > 0) {
                total_deduct += amt;
                deduct_html += `<div class="d-flex justify-content-between text-muted small mb-1"><span>${name}</span><span>₹${amt.toFixed(2)}</span></div>`;
            }
        });

        document.getElementById('prev_allowances_list').innerHTML = allow_html;
        document.getElementById('prev_deductions_list').innerHTML = deduct_html;

        document.getElementById('prev_allow').textContent = total_allow.toFixed(2);
        document.getElementById('prev_deduct').textContent = total_deduct.toFixed(2);
        
        let net = (b + total_allow) - total_deduct;
        document.getElementById('prev_net').textContent = net.toFixed(2);
    }
    
    function changeTemplate() {
        let sel = document.getElementById('template_selector').value;
        let preview = document.getElementById('payslip_preview');
        preview.className = 'w-100 payslip-theme-' + sel;
    }

    // Initialize on load
    document.addEventListener('DOMContentLoaded', () => {
        updateTotals();
    });
</script>
{% endblock %}
"""

with open('templates/payslip_builder.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated payslip_builder.html!")
