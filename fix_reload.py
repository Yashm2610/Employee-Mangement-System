file_path = r'c:\maxworth internship\templates\index.html'

with open(file_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Bring back auto-reload
old_js = '''                // Show Add Employee Button
                const btn = document.getElementById('add-employee-btn');
                if (btn) btn.classList.remove('d-none');
                
                // Don't auto reload anymore since we want them to see the button
                // setTimeout(() => window.location.reload(), 2500);'''

new_js = '''                // Reload the page after 2 seconds if successful so data updates in the table
                setTimeout(() => window.location.reload(), 2000);'''
                
html = html.replace(old_js, new_js)

# 2. Move the Add Employee button next to Employee Directory Header
old_header = '''                        <h4 class="mb-1 fw-bold text-dark d-flex align-items-center">
                            <i class="bi bi-database-check text-primary me-2"></i>
                            Employee Directory
                            <span class="badge bg-secondary ms-2 fs-7 fw-normal">{{ employees|length }} Records</span>
                        </h4>'''

new_header = '''                        <h4 class="mb-1 fw-bold text-dark d-flex align-items-center">
                            <i class="bi bi-database-check text-primary me-2"></i>
                            Employee Directory
                            <span class="badge bg-secondary ms-2 fs-7 fw-normal">{{ employees|length }} Records</span>
                        </h4>
                        {% if employees %}
                        <div class="mt-2">
                            <button id="add-employee-btn-header" class="btn btn-sm btn-dark" data-bs-toggle="modal" data-bs-target="#addEmployeeModal" type="button">
                                <i class="bi bi-person-plus me-1"></i> Add New Employee
                            </button>
                        </div>
                        {% endif %}'''
                        
html = html.replace(old_header, new_header)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(html)
print("index.html updated successfully.")
