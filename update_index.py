import re

def update_index_html():
    with open('templates/index.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Replace the old CSV Upload Component with Drag and Drop UI
    old_upload_pattern = re.compile(r"<!-- CSV Upload Component -->.*?</div>\s*</div>\s*</div>", re.DOTALL)
    
    new_upload_ui = """<!-- File Import & Export Component -->
    <div class="col-lg-6 col-md-12">
        <div class="card shadow-sm border-0 h-100 card-glow">
            <div class="card-header bg-primary text-white border-0 py-3 d-flex justify-content-between align-items-center">
                <h5 class="card-title mb-0 d-flex align-items-center">
                    <i class="bi bi-file-earmark-spreadsheet me-2"></i>
                    Bulk Import & Export
                </h5>
                <div class="dropdown">
                    <button class="btn btn-sm btn-light dropdown-toggle" type="button" id="exportMenu" data-bs-toggle="dropdown" aria-expanded="false">
                        <i class="bi bi-download me-1"></i> Export
                    </button>
                    <ul class="dropdown-menu dropdown-menu-end shadow" aria-labelledby="exportMenu">
                        <li><h6 class="dropdown-header">Employees Data</h6></li>
                        <li><a class="dropdown-item" href="/export/employees?format=csv"><i class="bi bi-filetype-csv me-2 text-success"></i>CSV Format</a></li>
                        <li><a class="dropdown-item" href="/export/employees?format=xlsx"><i class="bi bi-file-excel me-2 text-success"></i>Excel (XLSX) Format</a></li>
                        <li><hr class="dropdown-divider"></li>
                        <li><h6 class="dropdown-header">Payslip History</h6></li>
                        <li><a class="dropdown-item" href="/export/payslips?format=csv"><i class="bi bi-filetype-csv me-2 text-primary"></i>CSV Format</a></li>
                        <li><a class="dropdown-item" href="/export/payslips?format=xlsx"><i class="bi bi-file-excel me-2 text-primary"></i>Excel (XLSX) Format</a></li>
                    </ul>
                </div>
            </div>
            <div class="card-body p-4 d-flex flex-column">
                <p class="text-muted small mb-3">Drag and drop a <code>.csv</code>, <code>.xlsx</code>, or <code>.xls</code> file to bulk import employees. Invalid rows will be skipped and reported.</p>
                
                <div id="drop-zone" class="border border-2 border-dashed border-primary rounded-3 bg-light text-center p-5 mb-3" style="cursor: pointer; transition: all 0.3s;">
                    <i class="bi bi-cloud-arrow-up display-4 text-primary mb-2 d-block"></i>
                    <h6 class="fw-bold text-dark">Drag & Drop file here</h6>
                    <span class="text-muted small">or click to browse files</span>
                    <input type="file" id="file-input" class="d-none" accept=".csv, .xlsx, .xls">
                </div>

                <div id="upload-progress-container" class="d-none mb-3">
                    <div class="d-flex justify-content-between small mb-1">
                        <span class="fw-semibold text-primary">Uploading & Validating...</span>
                        <span id="progress-text" class="text-muted">0%</span>
                    </div>
                    <div class="progress" style="height: 6px;">
                        <div id="upload-progress-bar" class="progress-bar progress-bar-striped progress-bar-animated bg-primary" role="progressbar" style="width: 0%"></div>
                    </div>
                </div>

                <div id="import-summary" class="alert d-none mb-0 p-3">
                    <h6 class="alert-heading fw-bold mb-1"><i id="summary-icon" class="bi me-2"></i>Import Summary</h6>
                    <p id="summary-message" class="small mb-2"></p>
                    <div class="d-flex gap-2">
                        <span id="success-badge" class="badge bg-success">0 Success</span>
                        <span id="error-badge" class="badge bg-danger">0 Failed</span>
                    </div>
                    <a id="error-download-btn" href="#" class="btn btn-sm btn-outline-danger mt-2 d-none w-100">
                        <i class="bi bi-exclamation-triangle me-1"></i> Download Error Report
                    </a>
                </div>
            </div>
        </div>
    </div>"""

    if old_upload_pattern.search(content):
        content = old_upload_pattern.sub(new_upload_ui, content)
        
    # 2. Add JavaScript at the end of the file
    js_code = """
<script>
document.addEventListener('DOMContentLoaded', function() {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const progressContainer = document.getElementById('upload-progress-container');
    const progressBar = document.getElementById('upload-progress-bar');
    const progressText = document.getElementById('progress-text');
    const summaryAlert = document.getElementById('import-summary');
    const summaryIcon = document.getElementById('summary-icon');
    const summaryMsg = document.getElementById('summary-message');
    const successBadge = document.getElementById('success-badge');
    const errorBadge = document.getElementById('error-badge');
    const errorBtn = document.getElementById('error-download-btn');

    dropZone.addEventListener('click', () => fileInput.click());

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('bg-primary-subtle');
        dropZone.classList.remove('bg-light');
    });

    dropZone.addEventListener('dragleave', (e) => {
        e.preventDefault();
        dropZone.classList.remove('bg-primary-subtle');
        dropZone.classList.add('bg-light');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('bg-primary-subtle');
        dropZone.classList.add('bg-light');
        if (e.dataTransfer.files.length) {
            handleUpload(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) {
            handleUpload(e.target.files[0]);
        }
    });

    function handleUpload(file) {
        // Reset UI
        summaryAlert.classList.add('d-none');
        errorBtn.classList.add('d-none');
        progressContainer.classList.remove('d-none');
        progressBar.style.width = '0%';
        progressText.innerText = '0%';

        const formData = new FormData();
        formData.append('csv_file', file);

        const xhr = new XMLHttpRequest();
        xhr.open('POST', '/upload', true);

        xhr.upload.onprogress = function(e) {
            if (e.lengthComputable) {
                const percent = Math.round((e.loaded / e.total) * 50); // Upload takes 50%
                progressBar.style.width = percent + '%';
                progressText.innerText = percent + '%';
            }
        };

        xhr.onload = function() {
            // Fake processing progress 50% to 100%
            let p = 50;
            const interval = setInterval(() => {
                p += 10;
                progressBar.style.width = p + '%';
                progressText.innerText = p + '%';
                if (p >= 100) {
                    clearInterval(interval);
                    progressContainer.classList.add('d-none');
                    showSummary(xhr);
                }
            }, 100);
        };
        
        xhr.onerror = function() {
            progressContainer.classList.add('d-none');
            alert("An error occurred during the upload.");
        };

        xhr.send(formData);
    }

    function showSummary(xhr) {
        summaryAlert.classList.remove('d-none', 'alert-success', 'alert-danger', 'alert-warning');
        summaryIcon.className = 'bi me-2';
        
        try {
            const res = JSON.parse(xhr.responseText);
            if (xhr.status === 200 && res.success) {
                successBadge.innerText = res.success_count + ' Success';
                errorBadge.innerText = res.error_count + ' Failed';
                
                if (res.error_count > 0) {
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
            } else {
                summaryAlert.classList.add('alert-danger');
                summaryIcon.classList.add('bi-x-circle-fill');
                summaryMsg.innerText = res.error || 'Server error occurred.';
                successBadge.innerText = '0 Success';
                errorBadge.innerText = '0 Failed';
            }
        } catch(e) {
            summaryAlert.classList.add('alert-danger');
            summaryIcon.classList.add('bi-x-circle-fill');
            summaryMsg.innerText = 'Invalid response from server.';
        }
    }
});
</script>
"""

    if "id=\"drop-zone\"" not in content:
        content = content.replace("{% endblock %}", js_code + "\n{% endblock %}")

    with open('templates/index.html', 'w', encoding='utf-8') as f:
        f.write(content)

    print("Updated index.html!")

if __name__ == '__main__':
    update_index_html()
