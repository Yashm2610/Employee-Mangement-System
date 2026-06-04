file_path = r'c:\maxworth internship\templates\financial_master.html'

with open(file_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Replace header section
old_header = '''<div class="row mb-4">
    <div class="col-12 d-flex justify-content-between align-items-center">
        <div>
            <h4 class="mb-1 text-primary d-flex align-items-center fw-bold">
                <i class="bi bi-cash-coin me-2"></i> Employee Financials
            </h4>
            <p class="text-secondary small mb-0">Manage individual Bank Details, Basic Salary, Allowances, and Deductions.</p>
        </div>
    </div>
</div>'''

new_header = '''<div class="row mb-4">
    <div class="col-12 d-flex justify-content-between align-items-center">
        <div>
            <h4 class="mb-1 text-primary d-flex align-items-center fw-bold">
                <i class="bi bi-cash-coin me-2"></i> Employee Financials
            </h4>
            <p class="text-secondary small mb-0">Manage individual Bank Details, Basic Salary, Allowances, and Deductions.</p>
        </div>
        <div class="w-25">
            <div class="input-group input-group-sm shadow-sm">
                <span class="input-group-text bg-white border-end-0"><i class="bi bi-search text-muted"></i></span>
                <input type="text" id="financialSearch" class="form-control border-start-0 ps-0" placeholder="Search by Name, Emp ID, A/c No..." onkeyup="filterFinancials()">
            </div>
        </div>
    </div>
</div>'''

html = html.replace(old_header, new_header)

# Inject JS function at the end, right before {% endblock %}
js_func = '''
    function filterFinancials() {
        const input = document.getElementById("financialSearch").value.toLowerCase();
        const table = document.querySelector(".custom-table");
        const tr = table.getElementsByTagName("tr");
        
        for (let i = 1; i < tr.length; i++) {
            if (tr[i].cells.length < 3) continue; // Skip 'No records' row
            
            const empId = tr[i].cells[0].textContent.toLowerCase();
            const empName = tr[i].cells[1].textContent.toLowerCase();
            const bankDetails = tr[i].cells[2].textContent.toLowerCase();
            
            if (empId.indexOf(input) > -1 || empName.indexOf(input) > -1 || bankDetails.indexOf(input) > -1) {
                tr[i].style.display = "";
            } else {
                tr[i].style.display = "none";
            }
        }
    }
</script>'''

html = html.replace('</script>', js_func)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(html)
print("Search filter added successfully.")
