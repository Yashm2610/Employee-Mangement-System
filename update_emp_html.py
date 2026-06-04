import re

with open('templates/employee_profile.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace Personal Details
personal_details = """<h5 class="card-title fw-bold text-dark mb-0 d-flex align-items-center">
                        <i class="bi bi-person-badge text-primary me-2"></i>
                        Personal Details
                    </h5>
                </div>
                <div class="card-body p-4">
                    <div class="row g-3">
                        <div class="col-md-6">
                            <span class="d-block text-muted small fw-semibold text-uppercase tracking-wider">Employee ID</span>
                            <span class="fw-medium text-dark">{{ employee.emp_id }}</span>
                        </div>
                        <div class="col-md-6">
                            <span class="d-block text-muted small fw-semibold text-uppercase tracking-wider">Email</span>
                            <span class="fw-medium text-dark">{{ employee.email }}</span>
                        </div>
                        <div class="col-md-6">
                            <span class="d-block text-muted small fw-semibold text-uppercase tracking-wider">Date of Birth</span>
                            <span class="fw-medium text-dark">{{ employee.date_of_birth }}</span>
                        </div>
                        <div class="col-md-6">
                            <span class="d-block text-muted small fw-semibold text-uppercase tracking-wider">Joining Date</span>
                            <span class="fw-medium text-dark">{{ employee.joining_date }}</span>
                        </div>
                        <div class="col-md-4">
                            <span class="d-block text-muted small fw-semibold text-uppercase tracking-wider">Age</span>
                            <span class="fw-medium text-dark">{{ employee.age }} yrs</span>
                        </div>
                        <div class="col-md-4">
                            <span class="d-block text-muted small fw-semibold text-uppercase tracking-wider">Gender</span>
                            <span class="fw-medium text-dark">{{ employee.gender }}</span>
                        </div>
                        <div class="col-md-4">
                            <span class="d-block text-muted small fw-semibold text-uppercase tracking-wider">Education Code</span>
                            <span class="fw-medium text-dark">{{ employee.education }}</span>
                        </div>
                        <div class="col-md-4">
                            <span class="d-block text-muted small fw-semibold text-uppercase tracking-wider">Department</span>
                            <span class="fw-medium text-dark">{{ employee.department }}</span>
                        </div>
                        <div class="col-md-4">
                            <span class="d-block text-muted small fw-semibold text-uppercase tracking-wider">Posting Location</span>
                            <span class="fw-medium text-dark">{{ employee.posting_location }}</span>
                        </div>
                    </div>
                </div>"""

# Replace Bank Details
bank_details = """<h5 class="card-title fw-bold text-dark mb-0 d-flex align-items-center">
                        <i class="bi bi-bank text-primary me-2"></i>
                        Bank & Payroll Details
                    </h5>
                </div>
                <div class="card-body p-4">
                    <div class="row g-3">
                        <div class="col-md-6">
                            <span class="d-block text-muted small fw-semibold text-uppercase tracking-wider">Bank Name</span>
                            <span class="fw-medium text-dark">{{ bank.bank_name or 'N/A' }}</span>
                        </div>
                        <div class="col-md-6">
                            <span class="d-block text-muted small fw-semibold text-uppercase tracking-wider">Account Number</span>
                            <span class="fw-medium text-dark">{{ bank.bank_account_num or 'N/A' }}</span>
                        </div>
                        <div class="col-md-6">
                            <span class="d-block text-muted small fw-semibold text-uppercase tracking-wider">IFSC Code</span>
                            <span class="fw-medium text-dark">{{ bank.ifsc_code or 'N/A' }}</span>
                        </div>
                        <div class="col-md-6">
                            <span class="d-block text-muted small fw-semibold text-uppercase tracking-wider">Payment Tier</span>
                            <span class="fw-medium text-dark">Tier {{ employee.payment_tier }}</span>
                        </div>
                        <div class="col-12 mt-3 pt-3 border-top">
                            <div class="d-flex justify-content-between align-items-center">
                                <div>
                                    <span class="d-block text-muted small fw-semibold text-uppercase tracking-wider">Basic Salary</span>
                                    <h4 class="mb-0 fw-bold text-success">₹{{ "{:,.2f}".format(employee.basic_salary) }}</h4>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>"""

content = re.sub(r'<h5 class="card-title fw-bold text-dark mb-0 d-flex align-items-center">\s*<i class="bi bi-person-badge text-primary me-2"></i>\s*Personal Details\s*</h5>.*?</div>\s*</div>', personal_details, content, flags=re.DOTALL)
content = re.sub(r'<h5 class="card-title fw-bold text-dark mb-0 d-flex align-items-center">\s*<i class="bi bi-bank text-primary me-2"></i>\s*Bank & Payroll Details\s*</h5>.*?</div>\s*</div>', bank_details, content, flags=re.DOTALL)

with open('templates/employee_profile.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated employee_profile.html!")
