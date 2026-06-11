html_content = """{% extends 'base.html' %}

{% block content %}
<script src="https://cdn.jsdelivr.net/npm/interactjs/dist/interact.min.js"></script>

<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    body { background-color: #f5f6f8; font-family: 'Inter', sans-serif; overflow: hidden; margin: 0; }
    
    .studio-topbar { height: 50px; background: #fff; border-bottom: 1px solid #e0e0e0; display: flex; align-items: center; justify-content: space-between; padding: 0 15px; }
    .studio-container { display: flex; height: calc(100vh - 100px); }
    
    .sidebar-left { width: 300px; background: #fff; border-right: 1px solid #e0e0e0; display: flex; flex-direction: column; overflow-y: auto; }
    .form-section { padding: 15px; border-bottom: 1px solid #f0f0f0; }
    .section-title { font-size: 11px; font-weight: 700; color: #888; text-transform: uppercase; margin-bottom: 10px; }
    
    .field-row { display: flex; align-items: center; margin-bottom: 8px; }
    .field-drag { cursor: grab; padding: 5px; color: #aaa; margin-right: 5px; font-size: 14px; }
    .field-drag:hover { color: #0d6efd; }
    .field-input-wrap { flex: 1; display: flex; border: 1px solid #ccc; border-radius: 4px; overflow: hidden; }
    .field-label-input { width: 40%; border: none; background: #f8f9fa; padding: 6px; font-size: 11px; font-weight: 600; color: #555; border-right: 1px solid #ccc; }
    .field-value-input { width: 60%; border: none; padding: 6px; font-size: 12px; }
    .field-input-wrap input:focus { outline: none; }
    
    .add-btn { font-size: 11px; font-weight: 600; color: #0d6efd; background: none; border: none; cursor: pointer; padding: 0; margin-top: 5px; }
    .add-btn:hover { text-decoration: underline; }
    
    .workspace { flex: 1; display: flex; flex-direction: column; background: #eef0f4; position: relative; overflow: hidden; }
    .canvas-scroll-area { flex: 1; overflow: auto; display: flex; justify-content: center; padding: 40px; position: relative; }
    
    .a4-canvas {
        width: 210mm; height: 297mm; background: #fff; box-shadow: 0 8px 24px rgba(0,0,0,0.08);
        position: relative; transform-origin: top center; overflow: hidden;
    }
    
    /* Payslip Skeleton Grid */
    .skeleton-grid {
        position: absolute; top: 0; left: 0; right: 0; bottom: 0;
        padding: 40px; pointer-events: none;
    }
    .sk-border { border: 1px solid #000; width: 100%; height: 100%; display: flex; flex-direction: column; }
    .sk-header { border-bottom: 1px solid #000; padding: 15px; text-align: center; }
    .sk-title { font-size: 20px; font-weight: bold; text-transform: uppercase; margin-bottom: 5px; }
    .sk-emp-info { display: flex; border-bottom: 1px solid #000; min-height: 120px; }
    .sk-emp-col { flex: 1; border-right: 1px solid #000; padding: 10px; }
    .sk-emp-col:last-child { border-right: none; }
    .sk-table { flex: 1; display: flex; flex-direction: column; }
    .sk-th { display: flex; border-bottom: 1px solid #000; background: #f9f9f9; font-weight: bold; font-size: 13px; }
    .sk-th > div { flex: 1; padding: 8px; border-right: 1px solid #000; text-align: center; }
    .sk-th > div:last-child { border-right: none; }
    .sk-tr-space { flex: 1; display: flex; }
    .sk-tr-space > div { flex: 1; border-right: 1px solid #000; }
    .sk-tr-space > div:last-child { border-right: none; }
    .sk-totals { border-top: 1px solid #000; border-bottom: 1px solid #000; display: flex; min-height: 40px; background: #f9f9f9; }
    .sk-net { min-height: 80px; display: flex; align-items: center; justify-content: space-between; padding: 15px; border-bottom: 1px solid #000; }
    .sk-footer { padding: 15px; display: flex; justify-content: space-between; align-items: flex-end; min-height: 100px; }
    
    .canvas-field {
        position: absolute; padding: 2px 5px; cursor: move; box-sizing: border-box;
        font-size: 14px; white-space: nowrap; border: 1px dashed transparent;
        display: flex; gap: 8px; align-items: center; background: rgba(255,255,255,0.8);
    }
    .canvas-field:hover { border-color: #b0c4de; background: #fff; }
    .canvas-field.selected { border: 1px solid #0d6efd; background: rgba(13, 110, 253, 0.1); z-index: 100; }
    
    .c-label { font-weight: 600; }
    .c-value { font-weight: 400; }
    
    .element-toolbar {
        position: absolute; top: -30px; left: 0; background: #222; color: white;
        border-radius: 4px; padding: 4px 8px; display: none; gap: 8px; align-items: center;
        font-size: 12px; z-index: 20; pointer-events: auto;
    }
    .canvas-field.selected .element-toolbar { display: flex; }
    .element-toolbar i { cursor: pointer; }
    .element-toolbar i:hover { color: #dc3545; }
    
    .sidebar-right { width: 280px; background: #fff; border-left: 1px solid #e0e0e0; display: flex; flex-direction: column; }
    .prop-section { padding: 15px; border-bottom: 1px solid #eee; }
    .prop-title { font-size: 12px; font-weight: 700; color: #555; margin-bottom: 15px; }
    .prop-row { display: flex; gap: 10px; margin-bottom: 10px; }
    .prop-field { flex: 1; }
    .prop-label { font-size: 11px; color: #555; margin-bottom: 4px; display: block; font-weight: 600; }
    .prop-input { width: 100%; padding: 6px 8px; font-size: 12px; border: 1px solid #ddd; border-radius: 4px; outline: none; }
    
    /* Loading Spinner */
    #loading-overlay { display:none; position:absolute; top:0; left:0; right:0; bottom:0; background:rgba(255,255,255,0.8); z-index:1000; align-items:center; justify-content:center; }
</style>

<div class="studio-topbar">
    <div class="fw-bold"><i class="bi bi-chevron-left"></i> Field-Based Payslip Designer</div>
    <div>
        <button class="btn btn-sm btn-light" onclick="undo()">Undo (Ctrl+Z)</button>
        <button class="btn btn-sm btn-primary ms-2">Publish Payslip</button>
    </div>
</div>

<div class="studio-container position-relative">
    <div id="loading-overlay">
        <div class="spinner-border text-primary" role="status"></div><span class="ms-2 fw-bold text-primary">Fetching Employee Data...</span>
    </div>

    <!-- Left Sidebar (Data Entry Form) -->
    <div class="sidebar-left">
        <!-- Employee Auto-Fill Box -->
        <div class="form-section bg-primary bg-opacity-10">
            <label class="fs-7 fw-bold mb-1 text-primary"><i class="bi bi-lightning-charge-fill"></i> Auto-Fill Details</label>
            <p class="fs-7 text-muted" style="font-size:10px;">Select an employee to instantly fill their basic details.</p>
            <select class="form-select form-select-sm" id="emp-selector" onchange="fetchEmployeeData(this.value)">
                <option value="">-- Start Blank or Select --</option>
                {% if employees %}
                    {% for e in employees %}
                    <option value="{{ e.emp_id }}">{{ e.emp_name }} ({{ e.emp_id }})</option>
                    {% endfor %}
                {% endif %}
            </select>
        </div>
        
        <div class="form-section">
            <div class="section-title">Company Info</div>
            <div class="field-row drag-source">
                <i class="bi bi-list field-drag"></i>
                <div class="field-input-wrap">
                    <input type="text" class="field-label-input" value="Company">
                    <input type="text" class="field-value-input" value="Apex Global Tech">
                </div>
            </div>
            <div class="field-row drag-source">
                <i class="bi bi-list field-drag"></i>
                <div class="field-input-wrap">
                    <input type="text" class="field-label-input" value="Address">
                    <input type="text" class="field-value-input" value="123 Tech Park">
                </div>
            </div>
            <div class="field-row drag-source">
                <i class="bi bi-list field-drag"></i>
                <div class="field-input-wrap">
                    <input type="text" class="field-label-input" value="Month">
                    <input type="text" class="field-value-input" value="June 2026">
                </div>
            </div>
        </div>
        
        <div class="form-section">
            <div class="section-title">Employee Details</div>
            <div class="field-row drag-source"><i class="bi bi-list field-drag"></i><div class="field-input-wrap"><input type="text" class="field-label-input" value="Employee ID"><input type="text" class="field-value-input" id="f-emp-id" value="EMP-001"></div></div>
            <div class="field-row drag-source"><i class="bi bi-list field-drag"></i><div class="field-input-wrap"><input type="text" class="field-label-input" value="Employee Name"><input type="text" class="field-value-input" id="f-emp-name" value="Rahul Sharma"></div></div>
            <div class="field-row drag-source"><i class="bi bi-list field-drag"></i><div class="field-input-wrap"><input type="text" class="field-label-input" value="Department"><input type="text" class="field-value-input" id="f-dept" value="Engineering"></div></div>
            <div class="field-row drag-source"><i class="bi bi-list field-drag"></i><div class="field-input-wrap"><input type="text" class="field-label-input" value="Designation"><input type="text" class="field-value-input" id="f-desig" value="Software Engineer"></div></div>
            <div class="field-row drag-source"><i class="bi bi-list field-drag"></i><div class="field-input-wrap"><input type="text" class="field-label-input" value="Bank Name"><input type="text" class="field-value-input" id="f-bank" value="HDFC Bank"></div></div>
            <div class="field-row drag-source"><i class="bi bi-list field-drag"></i><div class="field-input-wrap"><input type="text" class="field-label-input" value="Account No."><input type="text" class="field-value-input" id="f-acc" value="******6789"></div></div>
        </div>
        
        <div class="form-section">
            <div class="section-title">Earnings</div>
            <div id="earnings-list">
                <div class="field-row drag-source"><i class="bi bi-list field-drag"></i><div class="field-input-wrap border-success"><input type="text" class="field-label-input bg-light" value="Basic Salary"><input type="text" class="field-value-input" id="f-basic" value="65,000"></div></div>
                <div class="field-row drag-source"><i class="bi bi-list field-drag"></i><div class="field-input-wrap border-success"><input type="text" class="field-label-input bg-light" value="HRA"><input type="text" class="field-value-input" value="26,000"></div></div>
            </div>
            <button class="add-btn mt-2" onclick="addField('earnings-list', 'Earning', '0')">+ Add Earning</button>
        </div>
        
        <div class="form-section">
            <div class="section-title">Deductions</div>
            <div id="deductions-list">
                <div class="field-row drag-source"><i class="bi bi-list field-drag"></i><div class="field-input-wrap border-danger"><input type="text" class="field-label-input bg-light" value="PF"><input type="text" class="field-value-input" value="1,800"></div></div>
                <div class="field-row drag-source"><i class="bi bi-list field-drag"></i><div class="field-input-wrap border-danger"><input type="text" class="field-label-input bg-light" value="Income Tax"><input type="text" class="field-value-input" value="12,000"></div></div>
            </div>
            <button class="add-btn mt-2 text-danger" onclick="addField('deductions-list', 'Deduction', '0')">+ Add Deduction</button>
        </div>
        
        <div class="form-section mt-auto">
            <div class="section-title">Net Pay</div>
            <div class="field-row drag-source"><i class="bi bi-list field-drag"></i><div class="field-input-wrap border-primary"><input type="text" class="field-label-input bg-primary text-white" value="Net Payable"><input type="text" class="field-value-input fw-bold" id="f-net" value="113,000"></div></div>
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
                <!-- STRUCTURAL SKELETON -->
                <div class="skeleton-grid">
                    <div class="sk-border">
                        <div class="sk-header">
                            <div class="sk-title">Salary Slip</div>
                            <div style="color:#aaa;">[Drop Company Header Here]</div>
                        </div>
                        <div class="sk-emp-info">
                            <div class="sk-emp-col"><span style="color:#aaa;">[Drop Employee Info]</span></div>
                            <div class="sk-emp-col"><span style="color:#aaa;">[Drop Bank Info]</span></div>
                        </div>
                        <div class="sk-table">
                            <div class="sk-th">
                                <div>Earnings</div>
                                <div>Amount</div>
                                <div>Deductions</div>
                                <div>Amount</div>
                            </div>
                            <div class="sk-tr-space">
                                <div></div><div></div><div></div><div></div>
                            </div>
                        </div>
                        <div class="sk-totals"></div>
                        <div class="sk-net">
                            <div><span style="color:#aaa;">[Drop Net Pay Here]</span></div>
                        </div>
                        <div class="sk-footer">
                            <div style="border-top:1px solid #000; padding-top:5px; width:150px; text-align:center;">Employer Signature</div>
                            <div style="border-top:1px solid #000; padding-top:5px; width:150px; text-align:center;">Employee Signature</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Right Sidebar -->
    <div class="sidebar-right">
        <div class="prop-section bg-light border-bottom">
            <div class="prop-title text-primary m-0"><i class="bi bi-sliders"></i> Field Properties</div>
        </div>
        
        <div id="prop-empty" class="text-center py-5 text-muted">
            <i class="bi bi-cursor fs-1"></i>
            <p class="mt-3 fs-7 px-3">Select a dropped field to edit it.</p>
        </div>
        
        <div id="prop-form" style="display:none;">
            <div class="prop-section border-bottom">
                <div class="prop-label">Label Text</div>
                <input type="text" id="prop-lbl" class="prop-input mb-3" oninput="updateSelectedText()">
                
                <div class="prop-label">Value Text</div>
                <input type="text" id="prop-val" class="prop-input" oninput="updateSelectedText()">
                
                <div class="form-check mt-3">
                    <input class="form-check-input" type="checkbox" id="prop-hide-label" onchange="toggleLabelVisibility()">
                    <label class="form-check-label fs-7">Hide Label (Show Value Only)</label>
                </div>
            </div>
            
            <div class="prop-section">
                <div class="prop-row">
                    <div class="prop-field">
                        <span class="prop-label">X Axis (px)</span>
                        <input type="number" id="prop-x" class="prop-input">
                    </div>
                    <div class="prop-field">
                        <span class="prop-label">Y Axis (px)</span>
                        <input type="number" id="prop-y" class="prop-input">
                    </div>
                </div>
                
                <div class="prop-label mt-2">Font Size (px)</div>
                <input type="number" id="prop-font" class="prop-input" value="14">
                
                <div class="mt-3">
                    <label class="prop-label">Format</label>
                    <div class="btn-group w-100">
                        <button class="btn btn-sm btn-outline-secondary" onclick="toggleStyle('bold')">B</button>
                        <button class="btn btn-sm btn-outline-secondary" onclick="toggleStyle('italic')">I</button>
                    </div>
                </div>
            </div>
            
            <div class="prop-section mt-auto">
                <button class="btn btn-outline-danger w-100 btn-sm" onclick="deleteSelected()"><i class="bi bi-trash"></i> Remove from Canvas</button>
            </div>
        </div>
    </div>
</div>

<script>
// Auto-fill logic
async function fetchEmployeeData(empId) {
    if(!empId) return;
    document.getElementById('loading-overlay').style.display = 'flex';
    
    try {
        let res = await fetch('/api/employee/' + empId);
        let data = await res.json();
        
        let emp = data.employee;
        
        // Update basic fields
        document.getElementById('f-emp-name').value = emp.emp_name || '';
        document.getElementById('f-emp-id').value = emp.emp_id || '';
        document.getElementById('f-dept').value = emp.department || '';
        document.getElementById('f-desig').value = emp.title || '';
        document.getElementById('f-bank').value = emp.bank_name || '';
        document.getElementById('f-acc').value = emp.bank_account_num || '';
        document.getElementById('f-basic').value = emp.basic_salary || '0';
        
        // Clear dynamic lists
        document.getElementById('earnings-list').innerHTML = '';
        document.getElementById('deductions-list').innerHTML = '';
        
        // Add Basic Salary
        let basicHtml = `
            <div class="field-row drag-source">
                <i class="bi bi-list field-drag"></i>
                <div class="field-input-wrap border-success">
                    <input type="text" class="field-label-input bg-light" value="Basic Salary">
                    <input type="text" class="field-value-input" value="${emp.basic_salary || '0'}">
                </div>
            </div>`;
        document.getElementById('earnings-list').insertAdjacentHTML('beforeend', basicHtml);

        // Add Components
        let total_earn = parseFloat(emp.basic_salary || 0);
        let total_ded = 0;
        
        if(data.components) {
            data.components.forEach(c => {
                let isEarn = c.component_code === 1;
                let listId = isEarn ? 'earnings-list' : 'deductions-list';
                addFieldWithValue(listId, c.component_name, c.amount);
                
                if(isEarn) total_earn += parseFloat(c.amount);
                else total_ded += parseFloat(c.amount);
            });
        }
        
        document.getElementById('f-net').value = (total_earn - total_ded).toFixed(2);
        
        // Rebind drag sources
        bindDragSources();
        
    } catch(err) {
        console.error(err);
        alert('Failed to load employee data.');
    } finally {
        document.getElementById('loading-overlay').style.display = 'none';
    }
}

function addFieldWithValue(listId, lbl, val) {
    let borderCls = listId === 'earnings-list' ? 'border-success' : 'border-danger';
    let html = `
        <div class="field-row drag-source">
            <i class="bi bi-list field-drag"></i>
            <div class="field-input-wrap ${borderCls}">
                <input type="text" class="field-label-input bg-light" value="${lbl}">
                <input type="text" class="field-value-input" value="${val}">
            </div>
        </div>
    `;
    document.getElementById(listId).insertAdjacentHTML('beforeend', html);
}

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
    if(selectedEl) selectedEl.classList.remove('selected');
    selectedEl = el;
    el.classList.add('selected');
    
    document.getElementById('prop-empty').style.display = 'none';
    document.getElementById('prop-form').style.display = 'block';
    
    document.getElementById('prop-x').value = Math.round(parseFloat(el.getAttribute('data-x')) || 0);
    document.getElementById('prop-y').value = Math.round(parseFloat(el.getAttribute('data-y')) || 0);
    
    let lblNode = el.querySelector('.c-label');
    let valNode = el.querySelector('.c-value');
    
    document.getElementById('prop-lbl').value = lblNode ? lblNode.innerText.replace(':', '').trim() : '';
    document.getElementById('prop-val').value = valNode ? valNode.innerText.trim() : '';
    
    document.getElementById('prop-hide-label').checked = lblNode && lblNode.style.display === 'none';
    
    let fontSize = window.getComputedStyle(el).fontSize;
    document.getElementById('prop-font').value = parseInt(fontSize);
}

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

function toggleLabelVisibility() {
    if(selectedEl) {
        let lblNode = selectedEl.querySelector('.c-label');
        if(lblNode) {
            lblNode.style.display = document.getElementById('prop-hide-label').checked ? 'none' : 'inline';
        }
    }
}

document.getElementById('prop-font').addEventListener('input', function() {
    if(selectedEl) {
        selectedEl.style.fontSize = this.value + 'px';
    }
});

function toggleStyle(style) {
    if(selectedEl) {
        if(style === 'bold') {
            let fw = selectedEl.style.fontWeight;
            selectedEl.style.fontWeight = fw === 'bold' ? 'normal' : 'bold';
        }
        if(style === 'italic') {
            let fs = selectedEl.style.fontStyle;
            selectedEl.style.fontStyle = fs === 'italic' ? 'normal' : 'italic';
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

function rebindCanvasElements() {
    interact('.canvas-field')
        .draggable({
            modifiers: [
                interact.modifiers.restrictRect({ restriction: 'parent', endOnly: false })
            ],
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
                `;
                
                document.getElementById('canvas').appendChild(newEl);
                selectElement(newEl);
                rebindCanvasElements();
            }
        }
    });
}

saveState();
rebindCanvasElements();
bindDragSources();
</script>
{% endblock %}
"""

with open('templates/payslip_designer.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("Studio 6.0 created with Auto-Fill Employee Selection Dropdown.")
