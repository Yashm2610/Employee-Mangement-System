html_content = """{% extends 'base.html' %}

{% block content %}
<script src="https://cdn.jsdelivr.net/npm/sortablejs@latest/Sortable.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/interactjs/dist/interact.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>

<style>
    .designer-container {
        display: flex;
        height: calc(100vh - 100px);
        overflow: hidden;
    }
    .sidebar {
        width: 250px;
        background: #f8f9fa;
        border-right: 1px solid #ddd;
        overflow-y: auto;
        padding: 15px;
    }
    .canvas-container {
        flex: 1;
        background: #e9ecef;
        overflow-y: auto;
        padding: 20px;
        display: flex;
        justify-content: center;
    }
    .properties-panel {
        width: 300px;
        background: #f8f9fa;
        border-left: 1px solid #ddd;
        overflow-y: auto;
        padding: 15px;
    }
    
    .a4-canvas {
        width: 210mm;
        min-height: 297mm;
        background: white;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        position: relative;
        padding: 15mm;
    }
    
    .element-item {
        padding: 8px 12px;
        background: white;
        border: 1px solid #ccc;
        margin-bottom: 5px;
        cursor: grab;
        border-radius: 4px;
        font-size: 0.85rem;
    }
    
    .canvas-block {
        border: 1px dashed #ccc;
        min-height: 40px;
        margin-bottom: 5px;
        padding: 5px;
        position: relative;
    }
    
    .canvas-block:hover {
        border-color: #007bff;
    }
    
    .canvas-block.selected {
        border: 2px solid #28a745;
    }
    
    .absolute-element {
        position: absolute;
        border: 1px dashed transparent;
        cursor: move;
    }
    .absolute-element:hover { border-color: #ffc107; }
    
    .category-title {
        font-size: 0.8rem;
        text-transform: uppercase;
        color: #6c757d;
        font-weight: bold;
        margin-top: 15px;
        margin-bottom: 5px;
    }
</style>

<div class="d-flex justify-content-between align-items-center mb-2">
    <h4 class="mb-0">Enterprise Payslip Designer</h4>
    <div class="d-flex gap-2 align-items-center">
        <select id="emp_id" class="form-select form-select-sm" style="width: auto;">
            <option value="">Select Employee...</option>
            {% for emp in employees %}
            <option value="{{ emp.emp_id }}">{{ emp.emp_name }} ({{ emp.emp_id }})</option>
            {% endfor %}
        </select>
        <select id="month" class="form-select form-select-sm" style="width: auto;">
            <option value="January">January</option>
            <option value="February">February</option>
            <option value="March">March</option>
            <option value="April">April</option>
            <option value="May">May</option>
            <option value="June">June</option>
            <option value="July">July</option>
            <option value="August">August</option>
            <option value="September">September</option>
            <option value="October">October</option>
            <option value="November">November</option>
            <option value="December">December</option>
        </select>
        <select id="year" class="form-select form-select-sm" style="width: auto;">
            <option value="2025">2025</option>
            <option value="2026" selected>2026</option>
        </select>
        
        <div class="btn-group">
            <button class="btn btn-sm btn-outline-secondary" onclick="toggleLayoutMode()">Mode: <span id="mode_lbl">Grid</span></button>
        </div>
        
        <button class="btn btn-sm btn-primary" onclick="saveTemplate()">Publish</button>
        <button class="btn btn-sm btn-success" onclick="generatePdf()">Generate PDF</button>
    </div>
</div>

<div class="designer-container border rounded">
    <div class="sidebar" id="library">
        <h5>Field Library</h5>
        <div id="auto-fields">
            <div class="spinner-border spinner-border-sm text-primary" role="status"></div> Loading DB Fields...
        </div>
        
        <h6 class="category-title">Custom Widgets</h6>
        <div class="element-item" data-type="text">Custom Text</div>
        <div class="element-item" data-type="image">Image / Logo</div>
        <div class="element-item" data-type="table">Smart Table</div>
    </div>
    
    <div class="canvas-container">
        <div class="a4-canvas" id="canvas">
            <div class="text-center text-muted mt-5" id="empty-state">Drag fields here...</div>
        </div>
    </div>
    
    <div class="properties-panel">
        <h5>Properties</h5>
        <div id="prop-empty" class="text-muted fs-7">Select an element to edit properties.</div>
        
        <div id="prop-form" style="display:none;">
            <div class="mb-2">
                <label class="form-label fs-7">Label</label>
                <input type="text" id="prop-label" class="form-control form-control-sm">
            </div>
            <div class="mb-2">
                <label class="form-label fs-7">Font Size (px)</label>
                <input type="number" id="prop-fontsize" class="form-control form-control-sm">
            </div>
            <div class="mb-2">
                <label class="form-label fs-7">Alignment</label>
                <select id="prop-align" class="form-select form-select-sm">
                    <option value="left">Left</option>
                    <option value="center">Center</option>
                    <option value="right">Right</option>
                </select>
            </div>
            
            <div class="mb-2 border p-2 bg-light rounded mt-3">
                <label class="form-label fs-7 text-primary fw-bold">Live Data Inspector</label>
                <div class="fs-7 text-secondary">Source: <span id="prop-source" class="fw-bold">N/A</span></div>
                <div class="fs-7 text-success mt-1">Live Value: <span id="prop-value" class="fw-bold">...</span></div>
            </div>
            
            <button class="btn btn-sm btn-danger mt-3 w-100" onclick="deleteSelected()">Delete Element</button>
        </div>
    </div>
</div>

<script>
let layoutMode = 'grid'; // 'grid' or 'free'
let selectedElement = null;
let currentPreviewData = {};

// Discover Fields
fetch('/api/fields/discover')
    .then(r => r.json())
    .then(schema => {
        const lib = document.getElementById('auto-fields');
        lib.innerHTML = '';
        for (const [table, cols] of Object.entries(schema)) {
            let cat = document.createElement('div');
            cat.className = 'category-title';
            cat.textContent = table;
            lib.appendChild(cat);
            
            let list = document.createElement('div');
            list.id = 'lib-' + table;
            lib.appendChild(list);
            
            cols.forEach(col => {
                let el = document.createElement('div');
                el.className = 'element-item';
                el.textContent = col;
                el.dataset.type = 'db_field';
                el.dataset.source = table + '.' + col;
                list.appendChild(el);
            });
            
            // Make them draggable
            new Sortable(list, {
                group: { name: 'shared', pull: 'clone', put: false },
                sort: false
            });
        }
    });

// Make Canvas Sortable (Grid Mode)
let canvasSortable = new Sortable(document.getElementById('canvas'), {
    group: 'shared',
    animation: 150,
    onAdd: function (evt) {
        document.getElementById('empty-state').style.display = 'none';
        let item = evt.item;
        
        // Transform the dragged item into a canvas block
        let block = document.createElement('div');
        block.className = 'canvas-block';
        if (layoutMode === 'free') {
            block.className = 'absolute-element';
            block.style.left = '50px';
            block.style.top = '50px';
        }
        
        let type = item.dataset.type;
        block.dataset.type = type;
        
        if (type === 'db_field') {
            block.dataset.source = item.dataset.source;
            block.innerHTML = `<strong>${item.textContent}:</strong> <span class="live-val text-primary" data-bind="${item.dataset.source}">[Live Value]</span>`;
        } else if (type === 'text') {
            block.innerHTML = `<div contenteditable="true">Custom Text Block</div>`;
        } else if (type === 'table') {
            block.innerHTML = `<table class="table table-bordered table-sm fs-7"><thead><tr><th>Earnings</th><th>Amount</th><th>Deductions</th><th>Amount</th></tr></thead><tbody><tr><td>Basic</td><td data-bind="allowances">...</td><td>Tax</td><td data-bind="deductions">...</td></tr></tbody></table>`;
        }
        
        block.onclick = function(e) {
            e.stopPropagation();
            selectElement(block);
        };
        
        item.parentNode.replaceChild(block, item);
        updatePreview();
    }
});

// InteractJS for Free Layout Mode
interact('.absolute-element').draggable({
    listeners: {
        move(event) {
            var target = event.target;
            var x = (parseFloat(target.getAttribute('data-x')) || 0) + event.dx;
            var y = (parseFloat(target.getAttribute('data-y')) || 0) + event.dy;
            target.style.transform = 'translate(' + x + 'px, ' + y + 'px)';
            target.setAttribute('data-x', x);
            target.setAttribute('data-y', y);
        }
    }
});

function toggleLayoutMode() {
    layoutMode = layoutMode === 'grid' ? 'free' : 'grid';
    document.getElementById('mode_lbl').textContent = layoutMode === 'grid' ? 'Grid' : 'Free';
}

function selectElement(el) {
    if (selectedElement) selectedElement.classList.remove('selected');
    selectedElement = el;
    el.classList.add('selected');
    
    document.getElementById('prop-empty').style.display = 'none';
    document.getElementById('prop-form').style.display = 'block';
    
    document.getElementById('prop-source').textContent = el.dataset.source || 'N/A';
    
    // Live inspector value
    let bindSpan = el.querySelector('[data-bind]');
    if (bindSpan) {
        document.getElementById('prop-value').textContent = bindSpan.textContent;
    } else {
        document.getElementById('prop-value').textContent = '...';
    }
}

function deleteSelected() {
    if (selectedElement) {
        selectedElement.remove();
        selectedElement = null;
        document.getElementById('prop-empty').style.display = 'block';
        document.getElementById('prop-form').style.display = 'none';
    }
}

// Live Preview AJAX
function updatePreview() {
    let emp = document.getElementById('emp_id').value;
    let month = document.getElementById('month').value;
    let year = document.getElementById('year').value;
    
    if (!emp) return;
    
    fetch(`/api/preview-data?emp_id=${emp}&month=${month}&year=${year}`)
        .then(r => r.json())
        .then(data => {
            currentPreviewData = data;
            
            // Map data to canvas elements
            document.querySelectorAll('[data-bind]').forEach(el => {
                let source = el.dataset.bind; // e.g., employees.emp_name
                let parts = source.split('.');
                if (parts.length === 2) {
                    let table = parts[0];
                    let col = parts[1];
                    if (data[table] && data[table][col] !== undefined) {
                        el.textContent = data[table][col];
                    }
                }
            });
            
            // Update inspector if open
            if (selectedElement) selectElement(selectedElement);
        });
}

document.getElementById('emp_id').addEventListener('change', updatePreview);
document.getElementById('month').addEventListener('change', updatePreview);

function saveTemplate() {
    let html = document.getElementById('canvas').innerHTML;
    fetch('/api/templates', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            template_name: 'Enterprise Template 1',
            layout_json: { html: html, mode: layoutMode },
            status: 'Published'
        })
    }).then(r => r.json()).then(res => {
        Swal.fire('Published!', 'Template Saved and Versioned', 'success');
    });
}

function generatePdf() {
    let html = document.getElementById('canvas').outerHTML;
    // Add basic styles to the HTML before sending to backend
    let fullHtml = `<html><head><style>.a4-canvas{font-family:Arial;} .canvas-block{margin-bottom:10px;}</style></head><body>${html}</body></html>`;
    
    Swal.fire('Generating...', 'Spinning up Headless Chrome...', 'info');
    
    fetch('/api/generate-payslip-pdf', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ html_content: fullHtml })
    })
    .then(r => r.blob())
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = 'Payslip.pdf';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        Swal.close();
    });
}

</script>
{% endblock %}
"""

with open('templates/payslip_designer.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("Generated payslip_designer.html SPA")
