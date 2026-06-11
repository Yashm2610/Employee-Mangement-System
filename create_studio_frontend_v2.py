html_content = """{% extends 'base.html' %}

{% block content %}
<script src="https://cdn.jsdelivr.net/npm/interactjs/dist/interact.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>

<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    body { background-color: #f5f6f8; font-family: 'Inter', sans-serif; overflow: hidden; margin: 0; }
    
    .studio-topbar { height: 50px; background: #fff; border-bottom: 1px solid #e0e0e0; display: flex; align-items: center; justify-content: space-between; padding: 0 15px; }
    .topbar-left { display: flex; align-items: center; gap: 15px; }
    .topbar-center { display: flex; align-items: center; gap: 10px; }
    .topbar-right { display: flex; align-items: center; gap: 8px; }
    
    .studio-container { display: flex; height: calc(100vh - 100px); }
    
    .sidebar-left { width: 260px; background: #fff; border-right: 1px solid #e0e0e0; display: flex; flex-direction: column; overflow-y: auto; }
    .sidebar-section { padding: 15px; border-bottom: 1px solid #f0f0f0; }
    .section-title { font-size: 11px; font-weight: 700; color: #888; text-transform: uppercase; margin-bottom: 10px; letter-spacing: 0.5px; }
    
    .template-gallery { display: flex; gap: 10px; }
    .template-thumb { flex: 1; border: 2px solid transparent; border-radius: 4px; text-align: center; cursor: pointer; padding: 5px; background: #f8f9fa; }
    .template-thumb.active { border-color: #0d6efd; background: #eef2fa; }
    .template-thumb img { width: 100%; height: auto; background: white; border: 1px solid #ddd; margin-bottom: 5px; }
    .template-thumb span { font-size: 11px; font-weight: 500; }
    
    .comp-item { 
        display: flex; align-items: center; padding: 8px 10px; border-radius: 6px; 
        cursor: grab; margin-bottom: 4px; transition: background 0.15s;
    }
    .comp-item:hover { background: #f0f4ff; }
    .comp-icon { width: 32px; height: 32px; border-radius: 6px; background: #f0f4ff; color: #0d6efd; display: flex; align-items: center; justify-content: center; margin-right: 12px; }
    .comp-details { flex: 1; }
    .comp-title { font-size: 13px; font-weight: 600; color: #333; margin-bottom: 2px; }
    .comp-desc { font-size: 11px; color: #777; }
    
    .workspace { flex: 1; display: flex; flex-direction: column; background: #eef0f4; position: relative; overflow: hidden; }
    
    .canvas-scroll-area { flex: 1; overflow: auto; display: flex; justify-content: center; padding: 40px; position: relative; }
    
    .a4-canvas {
        width: 210mm; min-height: 297mm; background: #fff; box-shadow: 0 8px 24px rgba(0,0,0,0.08);
        position: relative; transform-origin: top center; transition: transform 0.2s ease;
    }
    
    .canvas-element { position: absolute; box-sizing: border-box; cursor: move; }
    
    .canvas-element:hover::after {
        content: ''; position: absolute; top: -1px; left: -1px; right: -1px; bottom: -1px;
        border: 1px dashed #b0c4de; pointer-events: none;
    }
    
    .canvas-element.selected { border: 1px solid #0d6efd; }
    
    .resize-handle {
        position: absolute; width: 8px; height: 8px; background: #fff; border: 1px solid #0d6efd;
        border-radius: 50%; display: none; z-index: 10;
    }
    .canvas-element.selected .resize-handle { display: block; }
    .resize-nw { top: -4px; left: -4px; cursor: nwse-resize; }
    .resize-ne { top: -4px; right: -4px; cursor: nesw-resize; }
    .resize-sw { bottom: -4px; left: -4px; cursor: nesw-resize; }
    .resize-se { bottom: -4px; right: -4px; cursor: nwse-resize; }
    
    .element-toolbar {
        position: absolute; top: -35px; left: 0; background: #222; color: white;
        border-radius: 4px; padding: 4px 8px; display: none; gap: 8px; align-items: center;
        font-size: 14px; box-shadow: 0 4px 8px rgba(0,0,0,0.2); white-space: nowrap; z-index: 20;
    }
    .canvas-element.selected .element-toolbar { display: flex; }
    .element-toolbar i { cursor: pointer; padding: 4px; border-radius: 3px; }
    .element-toolbar i:hover { background: #444; }
    
    .sidebar-right { width: 300px; background: #fff; border-left: 1px solid #e0e0e0; display: flex; flex-direction: column; }
    .tabs-header { display: flex; border-bottom: 1px solid #e0e0e0; }
    .tab-btn { flex: 1; text-align: center; padding: 12px 0; font-size: 12px; font-weight: 600; color: #666; cursor: pointer; border-bottom: 2px solid transparent; }
    .tab-btn.active { color: #0d6efd; border-bottom-color: #0d6efd; }
    
    .tab-content { flex: 1; overflow-y: auto; padding: 15px; display: none; }
    .tab-content.active { display: block; }
    
    .prop-group { margin-bottom: 20px; }
    .prop-group-title { font-size: 11px; font-weight: 700; color: #888; text-transform: uppercase; margin-bottom: 10px; }
    .prop-row { display: flex; gap: 10px; margin-bottom: 10px; }
    .prop-field { flex: 1; }
    .prop-label { font-size: 11px; color: #555; margin-bottom: 4px; display: block; }
    .prop-input-wrap { position: relative; display: flex; align-items: center; }
    .prop-input { width: 100%; padding: 6px 8px; font-size: 12px; border: 1px solid #ddd; border-radius: 4px; outline: none; }
    .prop-input:focus { border-color: #0d6efd; }
    .prop-unit { position: absolute; right: 8px; font-size: 10px; color: #999; pointer-events: none; }
    
    .payslip-header { text-align: center; border-bottom: 2px solid #000; padding-bottom: 10px; }
    .payslip-emp-info { display: flex; border-bottom: 1px dashed #ccc; padding: 15px 0; font-size: 13px; }
    .payslip-emp-info > div { flex: 1; display: grid; grid-template-columns: 120px 1fr; row-gap: 5px; }
    
    .payslip-tables { display: flex; gap: 20px; margin-top: 15px; }
    .payslip-table-col { flex: 1; }
    .p-table { width: 100%; border-collapse: collapse; font-size: 12px; }
    .p-table th { background: #f8f9fa; border-top: 1px solid #000; border-bottom: 1px solid #000; padding: 8px; text-align: left; }
    .p-table td { padding: 8px; border-bottom: 1px solid #eee; }
    
    .payslip-net { background: #fcfcfc; border: 1px solid #e0e0e0; padding: 15px; margin-top: 15px; display: flex; justify-content: space-between; align-items: center; font-weight: bold; }
    
    .mapping-box { border: 1px solid #ddd; border-radius: 6px; padding: 12px; background: #fafafa; }
    .mapping-select { width: 100%; padding: 8px; font-size: 12px; border: 1px solid #ccc; border-radius: 4px; margin-bottom: 10px; }
    .live-preview-box { background: #fff; border: 1px solid #0d6efd; border-radius: 4px; padding: 10px; border-left: 4px solid #0d6efd; }
</style>

<!-- Top Navbar -->
<div class="studio-topbar">
    <div class="topbar-left">
        <a href="#" class="text-decoration-none text-dark fw-bold"><i class="bi bi-chevron-left"></i> Back</a>
        <div class="d-flex align-items-center gap-2 border-start ps-3 ms-2">
            <span class="fs-7 text-muted">Employee</span>
            <select class="form-select form-select-sm" style="width: 200px; font-size: 12px;">
                <option>Select Employee...</option>
            </select>
            <select class="form-select form-select-sm" style="width: 100px; font-size: 12px;">
                <option>May</option>
                <option>June</option>
            </select>
            <select class="form-select form-select-sm" style="width: 90px; font-size: 12px;">
                <option>2026</option>
            </select>
        </div>
    </div>
    <div class="topbar-center">
        <button class="btn btn-sm btn-light" onclick="undo()" title="Undo (Ctrl+Z)"><i class="bi bi-arrow-counterclockwise"></i> Undo</button>
        <button class="btn btn-sm btn-light" onclick="redo()" title="Redo (Ctrl+Y)"><i class="bi bi-arrow-clockwise"></i> Redo</button>
        <div class="border-start mx-1" style="height:20px;"></div>
        <button class="btn btn-sm btn-light"><i class="bi bi-eye"></i> Preview</button>
    </div>
    <div class="topbar-right">
        <button class="btn btn-sm btn-outline-primary fw-bold" style="background:#f0f4ff;">Save Draft</button>
        <button class="btn btn-sm btn-success fw-bold"><i class="bi bi-cloud-arrow-up"></i> Publish</button>
        <button class="btn btn-sm btn-primary fw-bold"><i class="bi bi-file-earmark-pdf"></i> Generate PDF</button>
    </div>
</div>

<div class="studio-container">
    
    <!-- Left Sidebar -->
    <div class="sidebar-left">
        <div class="sidebar-section">
            <div class="section-title">Template Gallery</div>
            <div class="template-gallery">
                <div class="template-thumb active">
                    <div style="height:40px; background:#fff; border:1px solid #ccc; margin-bottom:4px;"></div>
                    <span>Corporate</span>
                </div>
                <div class="template-thumb">
                    <div style="height:40px; background:#fff; border:1px solid #ccc; margin-bottom:4px;"></div>
                    <span>Executive</span>
                </div>
                <div class="template-thumb">
                    <div style="height:40px; background:#fff; border:1px solid #ccc; margin-bottom:4px;"></div>
                    <span>Modern</span>
                </div>
            </div>
        </div>
        
        <div class="sidebar-section border-0 flex-1 overflow-auto">
            <div class="section-title">Business Components</div>
            
            <div class="comp-list">
                <div class="comp-item drag-source" data-comp="header">
                    <div class="comp-icon"><i class="bi bi-person-vcard"></i></div>
                    <div class="comp-details">
                        <div class="comp-title">Employee Header</div>
                        <div class="comp-desc">Name, ID, Designation</div>
                    </div>
                </div>
                <div class="comp-item drag-source" data-comp="text">
                    <div class="comp-icon"><i class="bi bi-fonts"></i></div>
                    <div class="comp-details">
                        <div class="comp-title">Custom Text</div>
                        <div class="comp-desc">Add editable text block</div>
                    </div>
                </div>
                <div class="comp-item drag-source" data-comp="earnings">
                    <div class="comp-icon"><i class="bi bi-table"></i></div>
                    <div class="comp-details">
                        <div class="comp-title">Earnings Table</div>
                        <div class="comp-desc">Earnings breakdown</div>
                    </div>
                </div>
                <div class="comp-item drag-source" data-comp="deductions">
                    <div class="comp-icon"><i class="bi bi-table text-danger"></i></div>
                    <div class="comp-details">
                        <div class="comp-title">Deductions Table</div>
                        <div class="comp-desc">Deductions breakdown</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Center Workspace -->
    <div class="workspace">
        <div class="d-flex align-items-center justify-content-center p-2 bg-white border-bottom gap-2">
            <button class="btn btn-sm btn-light px-2" onclick="setZoom(currentZoom - 0.25)"><i class="bi bi-dash"></i></button>
            <span id="zoom-level" class="fs-7 fw-bold" style="width: 50px; text-align: center;">100%</span>
            <button class="btn btn-sm btn-light px-2" onclick="setZoom(currentZoom + 0.25)"><i class="bi bi-plus"></i></button>
        </div>
        
        <div class="canvas-scroll-area">
            <div class="a4-canvas" id="canvas">
                
                <!-- DEFAULT CORPORATE TEMPLATE PRE-LOADED -->
                
                <!-- Logo & Company Name -->
                <div class="canvas-element" data-x="40" data-y="30" style="transform: translate(40px, 30px); width: 710px; height: 80px;">
                    <div class="element-toolbar">
                        <i class="bi bi-arrows-move"></i> <i class="bi bi-files"></i> <i class="bi bi-trash text-danger" onclick="deleteSelected()"></i>
                    </div>
                    <div class="d-flex justify-content-between align-items-center h-100">
                        <div class="d-flex align-items-center gap-3">
                            <div style="width: 60px; height: 60px; background: #0d6efd; color: white; display: flex; align-items: center; justify-content: center; font-size: 30px; font-weight: bold; border-radius: 8px;">C</div>
                            <div class="editable-content" contenteditable="true">
                                <h2 style="margin:0; color:#003366;">Your Company Name</h2>
                                <div style="font-size: 11px; color:#555;">Company Address Line 1, City</div>
                            </div>
                        </div>
                        <div style="text-align: right; border: 1px solid #ccc; padding: 10px;" class="editable-content" contenteditable="true">
                            <div style="font-size: 11px; font-weight: bold;">Payslip For The Month</div>
                            <div style="font-size: 16px; font-weight: bold; margin-top: 5px;">Month Year</div>
                        </div>
                    </div>
                    <div class="resize-handle resize-nw"></div><div class="resize-handle resize-ne"></div>
                    <div class="resize-handle resize-sw"></div><div class="resize-handle resize-se"></div>
                </div>

                <!-- Employee Information -->
                <div class="canvas-element" data-x="40" data-y="130" style="transform: translate(40px, 130px); width: 710px; height: 110px;">
                    <div class="element-toolbar"><i class="bi bi-arrows-move"></i> <i class="bi bi-trash text-danger" onclick="deleteSelected()"></i></div>
                    <div class="payslip-emp-info h-100 editable-content" contenteditable="true" style="border: 1px solid #0d6efd; padding: 15px;">
                        <div>
                            <div><strong>Employee ID</strong> <span>: [Edit ID]</span></div>
                            <div><strong>Employee Name</strong> <span>: [Edit Name]</span></div>
                            <div><strong>Designation</strong> <span>: [Edit Designation]</span></div>
                            <div><strong>Phone</strong> <span>: [Edit Phone]</span></div>
                        </div>
                        <div>
                            <div><strong>Date of Joining</strong> <span>: [Edit Date]</span></div>
                            <div><strong>Bank Name</strong> <span>: [Edit Bank]</span></div>
                            <div><strong>A/C No.</strong> <span>: [Edit A/C]</span></div>
                            <div><strong>IFSC Code</strong> <span>: [Edit IFSC]</span></div>
                        </div>
                    </div>
                    <div class="resize-handle resize-nw"></div><div class="resize-handle resize-ne"></div>
                    <div class="resize-handle resize-sw"></div><div class="resize-handle resize-se"></div>
                </div>

            </div>
        </div>
    </div>
    
    <!-- Right Sidebar -->
    <div class="sidebar-right">
        <div class="tabs-header">
            <div class="tab-btn active" onclick="switchTab('props')">PROPERTIES</div>
            <div class="tab-btn" onclick="switchTab('data')">DATA MAPPING</div>
        </div>
        
        <!-- Properties Tab -->
        <div class="tab-content active" id="tab-props">
            
            <div id="prop-empty" class="text-center py-5 text-muted">
                <i class="bi bi-mouse-2 fs-1"></i>
                <p class="mt-3 fs-7">Select a component on the canvas to view and edit its properties.</p>
            </div>
            
            <div id="prop-form" style="display:none;">
                <div class="d-flex align-items-center mb-3 pb-3 border-bottom">
                    <i class="bi bi-bounding-box text-primary me-2"></i> 
                    <span class="fs-7 fw-bold" id="prop-comp-name">Component</span>
                </div>
                
                <div class="prop-group">
                    <div class="prop-group-title">Text Content</div>
                    <textarea id="prop-text-content" class="form-control form-control-sm" rows="3" placeholder="Edit text here..."></textarea>
                </div>

                <div class="prop-group">
                    <div class="prop-group-title">Position & Size</div>
                    <div class="prop-row">
                        <div class="prop-field">
                            <span class="prop-label">X Axis</span>
                            <div class="prop-input-wrap">
                                <input type="number" id="prop-x" class="prop-input">
                                <span class="prop-unit">px</span>
                            </div>
                        </div>
                        <div class="prop-field">
                            <span class="prop-label">Y Axis</span>
                            <div class="prop-input-wrap">
                                <input type="number" id="prop-y" class="prop-input">
                                <span class="prop-unit">px</span>
                            </div>
                        </div>
                    </div>
                    <div class="prop-row">
                        <div class="prop-field">
                            <span class="prop-label">Width</span>
                            <div class="prop-input-wrap">
                                <input type="number" id="prop-w" class="prop-input">
                                <span class="prop-unit">px</span>
                            </div>
                        </div>
                        <div class="prop-field">
                            <span class="prop-label">Height</span>
                            <div class="prop-input-wrap">
                                <input type="number" id="prop-h" class="prop-input">
                                <span class="prop-unit">px</span>
                            </div>
                        </div>
                    </div>
                    <div class="form-check mt-2 ps-4">
                        <input class="form-check-input" type="checkbox" id="prop-lock" style="font-size:12px;">
                        <label class="form-check-label fs-7 fw-bold">Lock Aspect Ratio</label>
                    </div>
                </div>
                
                <button class="btn btn-outline-danger w-100 mt-2" onclick="deleteSelected()" style="font-size:12px; font-weight:bold;"><i class="bi bi-trash"></i> Delete Component</button>
            </div>
        </div>
        
        <!-- Data Mapping Tab -->
        <div class="tab-content" id="tab-data">
            <div id="data-empty" class="text-center py-5 text-muted">
                <i class="bi bi-database-add fs-1"></i>
                <p class="mt-3 fs-7">Select an element to bind it to a database field.</p>
            </div>
            
            <div id="data-form" style="display:none;">
                <div class="mapping-box">
                    <div class="fw-bold fs-7 mb-2 text-primary">Data Source Mapping</div>
                    <select class="mapping-select">
                        <option value="">Static Text</option>
                        <option value="emp_name">employees.employee_name</option>
                        <option value="emp_phone">employees.phone</option>
                    </select>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
function switchTab(tab) {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    event.target.classList.add('active');
    document.getElementById('tab-' + tab).classList.add('active');
}

let currentZoom = 1; // Default to 100% 
function setZoom(scale) {
    if(scale < 0.25 || scale > 2) return;
    currentZoom = scale;
    document.getElementById('canvas').style.transform = `scale(${scale})`;
    document.getElementById('zoom-level').textContent = Math.round(scale * 100) + '%';
}

let historyStack = [];
let redoStack = [];

function saveState() {
    historyStack.push(document.getElementById('canvas').innerHTML);
    if(historyStack.length > 30) historyStack.shift();
    redoStack = [];
}

function undo() {
    if (historyStack.length > 0) {
        redoStack.push(document.getElementById('canvas').innerHTML);
        document.getElementById('canvas').innerHTML = historyStack.pop();
        rebindInteract();
    }
}
function redo() {
    if (redoStack.length > 0) {
        historyStack.push(document.getElementById('canvas').innerHTML);
        document.getElementById('canvas').innerHTML = redoStack.pop();
        rebindInteract();
    }
}

document.addEventListener('keydown', function(e) {
    if (e.ctrlKey && e.key === 'z') { e.preventDefault(); undo(); }
    if (e.ctrlKey && e.key === 'y') { e.preventDefault(); redo(); }
});

let selectedEl = null;

function selectElement(el) {
    if(selectedEl) selectedEl.classList.remove('selected');
    selectedEl = el;
    el.classList.add('selected');
    
    document.getElementById('prop-empty').style.display = 'none';
    document.getElementById('prop-form').style.display = 'block';
    document.getElementById('data-empty').style.display = 'none';
    document.getElementById('data-form').style.display = 'block';
    
    document.getElementById('prop-x').value = Math.round(parseFloat(el.getAttribute('data-x')) || 0);
    document.getElementById('prop-y').value = Math.round(parseFloat(el.getAttribute('data-y')) || 0);
    document.getElementById('prop-w').value = Math.round(el.offsetWidth);
    document.getElementById('prop-h').value = Math.round(el.offsetHeight);

    let editable = el.querySelector('.editable-content');
    if(editable) {
        document.getElementById('prop-text-content').value = editable.innerText;
    } else {
        document.getElementById('prop-text-content').value = el.innerText;
    }
}

document.getElementById('canvas').addEventListener('mousedown', function(e) {
    let el = e.target.closest('.canvas-element');
    if(e.target.classList.contains('resize-handle') || e.target.closest('.element-toolbar')) return;
    
    if(el) {
        selectElement(el);
    } else {
        if(selectedEl) selectedEl.classList.remove('selected');
        selectedEl = null;
        document.getElementById('prop-empty').style.display = 'block';
        document.getElementById('prop-form').style.display = 'none';
        document.getElementById('data-empty').style.display = 'block';
        document.getElementById('data-form').style.display = 'none';
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

document.getElementById('prop-text-content').addEventListener('input', function(e) {
    if(selectedEl) {
        let editable = selectedEl.querySelector('.editable-content');
        if(editable) {
            editable.innerText = this.value;
        } else {
            // Very simple fallback
            selectedEl.innerText = this.value;
        }
    }
});

function rebindInteract() {
    interact('.canvas-element')
        .draggable({
            listeners: {
                start(event) { saveState(); },
                move(event) {
                    var target = event.target;
                    var x = (parseFloat(target.getAttribute('data-x')) || 0) + event.dx / currentZoom;
                    var y = (parseFloat(target.getAttribute('data-y')) || 0) + event.dy / currentZoom;

                    target.style.transform = 'translate(' + x + 'px, ' + y + 'px)';
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
            edges: { left: '.resize-nw, .resize-sw', right: '.resize-ne, .resize-se', bottom: '.resize-sw, .resize-se', top: '.resize-nw, .resize-ne' },
            listeners: {
                start(event) { saveState(); },
                move: function (event) {
                    let target = event.target;
                    let x = (parseFloat(target.getAttribute('data-x')) || 0);
                    let y = (parseFloat(target.getAttribute('data-y')) || 0);

                    let newWidth = event.rect.width / currentZoom;
                    let newHeight = event.rect.height / currentZoom;
                    
                    if(document.getElementById('prop-lock').checked) {
                        let ratio = target.offsetWidth / target.offsetHeight;
                        newHeight = newWidth / ratio;
                    }

                    target.style.width = newWidth + 'px';
                    target.style.height = newHeight + 'px';

                    x += event.deltaRect.left / currentZoom;
                    y += event.deltaRect.top / currentZoom;

                    target.style.transform = 'translate(' + x + 'px,' + y + 'px)';
                    target.setAttribute('data-x', x);
                    target.setAttribute('data-y', y);

                    if(selectedEl === target) {
                        document.getElementById('prop-w').value = Math.round(newWidth);
                        document.getElementById('prop-h').value = Math.round(newHeight);
                        document.getElementById('prop-x').value = Math.round(x);
                        document.getElementById('prop-y').value = Math.round(y);
                    }
                }
            }
        });
}

['prop-x', 'prop-y', 'prop-w', 'prop-h'].forEach(id => {
    document.getElementById(id).addEventListener('change', function() {
        if(selectedEl) {
            saveState();
            let val = parseFloat(this.value);
            if(id === 'prop-w') selectedEl.style.width = val + 'px';
            if(id === 'prop-h') selectedEl.style.height = val + 'px';
            if(id === 'prop-x' || id === 'prop-y') {
                let x = id === 'prop-x' ? val : parseFloat(selectedEl.getAttribute('data-x'));
                let y = id === 'prop-y' ? val : parseFloat(selectedEl.getAttribute('data-y'));
                selectedEl.setAttribute('data-x', x);
                selectedEl.setAttribute('data-y', y);
                selectedEl.style.transform = `translate(${x}px, ${y}px)`;
            }
        }
    });
});

interact('.drag-source').draggable({
    clone: true,
    listeners: {
        move: function(e) {},
        end: function(e) {
            saveState();
            let newEl = document.createElement('div');
            newEl.className = 'canvas-element';
            newEl.setAttribute('data-x', 100);
            newEl.setAttribute('data-y', 100);
            newEl.style.transform = `translate(100px, 100px)`;
            newEl.style.width = '300px';
            newEl.style.height = '100px';
            
            let type = e.target.getAttribute('data-comp');
            newEl.innerHTML = `<div class="editable-content" style="border:1px solid #ccc; background:#fff; height:100%; display:flex; align-items:center; justify-content:center;" contenteditable="true">New ${type}</div>
            <div class="element-toolbar"><i class="bi bi-arrows-move"></i> <i class="bi bi-trash text-danger" onclick="deleteSelected()"></i></div>
            <div class="resize-handle resize-nw"></div><div class="resize-handle resize-ne"></div>
            <div class="resize-handle resize-sw"></div><div class="resize-handle resize-se"></div>`;
            
            document.getElementById('canvas').appendChild(newEl);
            selectElement(newEl);
        }
    }
});

saveState();
rebindInteract();
// setZoom(1.0); // Make sure it fits nicely
</script>

{% endblock %}
"""

with open('templates/payslip_designer.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("Applied fixes for editable text, company name, and input fields.")
