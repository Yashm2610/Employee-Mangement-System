import os

file_path = r'c:\maxworth internship\templates\index.html'

with open(file_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update grid layout
html = html.replace('<div class="row g-4">\n    <!-- File Import & Export Component -->\n    <div class="col-lg-6 col-md-12">', 
                    '<div class="row justify-content-center">\n    <!-- File Import & Export Component -->\n    <div class="col-lg-8 col-md-12">')

# 2. Add 'Add Employee' button to import summary
old_btn_block = '''                    <a id="error-download-btn" href="#" class="btn btn-sm btn-outline-danger mt-2 d-none w-100">
                        <i class="bi bi-exclamation-triangle me-1"></i> Download Error Report
                    </a>
                </div>'''
new_btn_block = '''                    <a id="error-download-btn" href="#" class="btn btn-sm btn-outline-danger mt-2 d-none w-100">
                        <i class="bi bi-exclamation-triangle me-1"></i> Download Error Report
                    </a>
                    <button id="add-employee-btn" class="btn btn-sm btn-dark mt-2 w-100 d-none" data-bs-toggle="modal" data-bs-target="#addEmployeeModal" type="button">
                        <i class="bi bi-person-plus me-1"></i> Add an Employee Manually
                    </button>
                </div>'''
html = html.replace(old_btn_block, new_btn_block)

# 3. Transform the form column into a modal
old_form_start = '''    <!-- Manual Entry Component -->
    <div class="col-lg-6 col-md-12">
        <div class="card shadow-sm border-0 h-100 card-glow">
            <div class="card-header bg-dark text-white border-0 py-3">
                <h5 class="card-title mb-0 d-flex align-items-center">
                    <i class="bi bi-person-plus me-2"></i>
                    Add Employee Manually
                </h5>
            </div>
            <div class="card-body p-4">
                <form action="{{ url_for('add_employee') }}" method="POST">'''

new_form_start = '''    <!-- Add Employee Modal -->
    <div class="modal fade" id="addEmployeeModal" tabindex="-1" aria-hidden="true">
        <div class="modal-dialog modal-xl modal-dialog-centered modal-dialog-scrollable">
            <div class="modal-content border-0 shadow">
                <div class="modal-header bg-dark text-white">
                    <h5 class="modal-title"><i class="bi bi-person-plus me-2"></i>Add Employee Manually</h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body bg-light p-4">
                    <form action="{{ url_for('add_employee') }}" method="POST" class="bg-white p-4 rounded shadow-sm border">'''

html = html.replace(old_form_start, new_form_start)

old_form_end = '''                    <button type="submit" class="btn btn-dark w-100 py-2 mt-4 d-flex align-items-center justify-content-center">
                        <i class="bi bi-plus-circle me-2"></i>
                        <span>Save Record to Database</span>
                    </button>
                </form>
            </div>
        </div>
    </div>
</div>'''

new_form_end = '''                    <button type="submit" class="btn btn-dark w-100 py-2 mt-4 d-flex align-items-center justify-content-center">
                        <i class="bi bi-plus-circle me-2"></i>
                        <span>Save Record to Database</span>
                    </button>
                    </form>
                </div>
            </div>
        </div>
    </div>
<!-- End Add Employee Modal -->'''

html = html.replace(old_form_end, new_form_end)

# 4. Modify JS to show the Add Employee button on successful upload
old_js_success = '''                if (res.error_count > 0) {
                    summaryAlert.classList.add('alert-warning');
                    summaryIcon.classList.add('bi-exclamation-triangle-fill');
                    summaryMsg.innerText = 'Import completed with some errors. Download the report to see skipped rows.';
                    errorBtn.href = res.error_file;
                    errorBtn.classList.remove('d-none');
                } else {
                    summaryAlert.classList.add('alert-success');
                    summaryIcon.classList.add('bi-check-circle-fill');
                    summaryMsg.innerText = 'All records imported successfully!';
                }
                
                // Reload the page after 2 seconds if successful so data updates in the table
                setTimeout(() => window.location.reload(), 2500);'''

new_js_success = '''                if (res.error_count > 0) {
                    summaryAlert.classList.add('alert-warning');
                    summaryIcon.classList.add('bi-exclamation-triangle-fill');
                    summaryMsg.innerText = 'Import completed with some errors. Download the report to see skipped rows.';
                    errorBtn.href = res.error_file;
                    errorBtn.classList.remove('d-none');
                } else {
                    summaryAlert.classList.add('alert-success');
                    summaryIcon.classList.add('bi-check-circle-fill');
                    summaryMsg.innerText = 'All records imported successfully! You can now add individual employees if needed.';
                }
                
                // Show Add Employee Button
                const btn = document.getElementById('add-employee-btn');
                if (btn) btn.classList.remove('d-none');
                
                // Don't auto reload anymore since we want them to see the button
                // setTimeout(() => window.location.reload(), 2500);'''

html = html.replace(old_js_success, new_js_success)

# Reset button UI before upload starts
old_js_handle = '''    function handleUpload(file) {
        summaryAlert.classList.add('d-none');
        errorBtn.classList.add('d-none');'''

new_js_handle = '''    function handleUpload(file) {
        summaryAlert.classList.add('d-none');
        errorBtn.classList.add('d-none');
        const btn = document.getElementById('add-employee-btn');
        if (btn) btn.classList.add('d-none');'''

html = html.replace(old_js_handle, new_js_handle)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(html)
print("index.html updated successfully.")
