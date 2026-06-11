html_content = """{% extends 'base.html' %}

{% block content %}
<script src="https://cdn.jsdelivr.net/npm/interactjs/dist/interact.min.js"></script>

<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    body { background-color: #f5f6f8; font-family: 'Inter', sans-serif; overflow: hidden; margin: 0; }
    
    .studio-topbar { height: 50px; background: #fff; border-bottom: 1px solid #e0e0e0; display: flex; align-items: center; justify-content: space-between; padding: 0 15px; }
    .studio-container { display: flex; height: calc(100vh - 100px); }
    
    .sidebar-left { width: 260px; background: #fff; border-right: 1px solid #e0e0e0; display: flex; flex-direction: column; overflow-y: auto; }
    .sidebar-section { padding: 15px; border-bottom: 1px solid #f0f0f0; }
    .section-title { font-size: 11px; font-weight: 700; color: #888; text-transform: uppercase; margin-bottom: 10px; }
    
    .comp-item { display: flex; align-items: center; padding: 8px 10px; border-radius: 6px; cursor: grab; margin-bottom: 4px; }
    .comp-item:hover { background: #f0f4ff; }
    .comp-icon { width: 32px; height: 32px; border-radius: 6px; background: #f0f4ff; color: #0d6efd; display: flex; align-items: center; justify-content: center; margin-right: 12px; }
    .comp-title { font-size: 13px; font-weight: 600; color: #333; }
    
    .workspace { flex: 1; display: flex; flex-direction: column; background: #eef0f4; position: relative; overflow: hidden; }
    .canvas-scroll-area { flex: 1; overflow: auto; display: flex; justify-content: center; padding: 40px; position: relative; }
    
    .a4-canvas {
        width: 210mm; height: 297mm; background: #fff; box-shadow: 0 8px 24px rgba(0,0,0,0.08);
        position: relative; transform-origin: top center; overflow: hidden;
    }
    
    .canvas-element { position: absolute; box-sizing: border-box; cursor: move; }
    .canvas-element.selected { border: 2px solid #0d6efd; }
    
    .resize-handle {
        position: absolute; width: 10px; height: 10px; background: #fff; border: 2px solid #0d6efd;
        border-radius: 50%; display: none; z-index: 10;
    }
    .canvas-element.selected .resize-handle { display: block; }
    .resize-nw { top: -5px; left: -5px; cursor: nwse-resize; }
    .resize-ne { top: -5px; right: -5px; cursor: nesw-resize; }
    .resize-sw { bottom: -5px; left: -5px; cursor: nesw-resize; }
    .resize-se { bottom: -5px; right: -5px; cursor: nwse-resize; }
    
    .sidebar-right { width: 320px; background: #fff; border-left: 1px solid #e0e0e0; display: flex; flex-direction: column; overflow-y: auto; }
    .prop-section { padding: 15px; border-bottom: 1px solid #eee; }
    .prop-title { font-size: 12px; font-weight: 700; color: #555; margin-bottom: 15px; }
    
    .prop-field { margin-bottom: 12px; }
    .prop-label { font-size: 11px; color: #555; margin-bottom: 4px; display: block; font-weight: 600; }
    .prop-input { width: 100%; padding: 6px 8px; font-size: 12px; border: 1px solid #ddd; border-radius: 4px; outline: none; }
    .prop-input:focus { border-color: #0d6efd; }
    
    /* Component Specific Styles */
    .comp-header { display: flex; justify-content: space-between; align-items: center; padding: 15px; border-bottom: 2px solid #000; height: 100%; }
    .comp-emp { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; border: 1px solid #0d6efd; padding: 15px; font-size: 13px; height: 100%; }
    .comp-emp > div > div { margin-bottom: 5px; }
    .comp-table { width: 100%; border-collapse: collapse; font-size: 12px; height: 100%; }
    .comp-table th { background: #f8f9fa; border-top: 1px solid #000; border-bottom: 1px solid #000; padding: 8px; text-align: left; }
    .comp-table td { padding: 8px; border-bottom: 1px solid #eee; }
</style>

<div class="studio-topbar">
    <div class="fw-bold"><i class="bi bi-chevron-left"></i> Payslip Designer 3.0</div>
    <div>
        <button class="btn btn-sm btn-light" onclick="undo()">Undo</button>
        <button class="btn btn-sm btn-primary ms-2">Publish</button>
    </div>
</div>

<div class="studio-container">
    
    <!-- Left Sidebar -->
    <div class="sidebar-left">
        <div class="sidebar-section">
            <div class="section-title">Draggable Components</div>
            <div class="comp-item drag-source" data-comp="header">
                <div class="comp-icon"><i class="bi bi-building"></i></div>
                <div class="comp-title">Company Header</div>
            </div>
            <div class="comp-item drag-source" data-comp="emp">
                <div class="comp-icon"><i class="bi bi-person-vcard"></i></div>
                <div class="comp-title">Employee Profile</div>
            </div>
            <div class="comp-item drag-source" data-comp="earnings">
                <div class="comp-icon"><i class="bi bi-table"></i></div>
                <div class="comp-title">Earnings Table</div>
            </div>
        </div>
    </div>
    
    <!-- Center Canvas -->
    <div class="workspace">
        <div class="canvas-scroll-area">
            <div class="a4-canvas" id="canvas">
                
                <!-- Company Header -->
                <div class="canvas-element" data-type="header" data-x="40" data-y="30" style="transform: translate(40px, 30px); width: 710px; height: 80px;">
                    <div class="comp-header">
                        <div>
                            <h2 style="margin:0; color:#003366;" class="d-company">Your Company Name</h2>
                            <div class="d-address" style="font-size: 11px; color:#555;">Company Address Line 1</div>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-size: 11px; font-weight: bold;">Payslip For The Month</div>
                            <div class="d-month" style="font-size: 16px; font-weight: bold; margin-top: 5px;">Month Year</div>
                        </div>
                    </div>
                    <div class="resize-handle resize-nw"></div><div class="resize-handle resize-ne"></div><div class="resize-handle resize-sw"></div><div class="resize-handle resize-se"></div>
                </div>

                <!-- Employee Info -->
                <div class="canvas-element" data-type="emp" data-x="40" data-y="130" style="transform: translate(40px, 130px); width: 710px; height: 110px;">
                    <div class="comp-emp bg-white">
                        <div>
                            <div><strong>Employee ID:</strong> <span class="d-id">EMP-001</span></div>
                            <div><strong>Employee Name:</strong> <span class="d-name">Rahul Sharma</span></div>
                            <div><strong>Phone:</strong> <span class="d-phone">+91 9876543210</span></div>
                        </div>
                        <div>
                            <div><strong>Designation:</strong> <span class="d-desig">Software Engineer</span></div>
                            <div><strong>Department:</strong> <span class="d-dept">Engineering</span></div>
                            <div><strong>Bank A/C:</strong> <span class="d-bank">123456789</span></div>
                        </div>
                    </div>
                    <div class="resize-handle resize-nw"></div><div class="resize-handle resize-ne"></div><div class="resize-handle resize-sw"></div><div class="resize-handle resize-se"></div>
                </div>

            </div>
        </div>
    </div>
    
    <!-- Right Sidebar (Dynamic Form) -->
    <div class="sidebar-right">
        <div class="prop-section bg-light border-bottom">
            <div class="prop-title text-primary"><i class="bi bi-pencil-square"></i> Editable Details</div>
            <p class="fs-7 text-muted m-0">Select a box on the left to edit its details separately here.</p>
        </div>
        
        <div id="prop-empty" class="text-center py-5 text-muted">
            <i class="bi bi-mouse2 fs-1"></i>
            <p class="mt-3 fs-7">No component selected.</p>
        </div>
        
        <div id="dynamic-form" style="display:none;" class="p-3">
            <!-- Populated via JS -->
        </div>
    </div>
</div>

<script>
let selectedEl = null;
let historyStack = [];

function saveState() {
    historyStack.push(document.getElementById('canvas').innerHTML);
}
function undo() {
    if(historyStack.length > 0) {
        document.getElementById('canvas').innerHTML = historyStack.pop();
        rebindInteract();
    }
}

// Map component types to their editable fields
const compFields = {
    'header': [
        { key: 'd-company', label: 'Company Name' },
        { key: 'd-address', label: 'Address' },
        { key: 'd-month', label: 'Month & Year' }
    ],
    'emp': [
        { key: 'd-name', label: 'Employee Name' },
        { key: 'd-id', label: 'Employee ID' },
        { key: 'd-phone', label: 'Phone Number' },
        { key: 'd-desig', label: 'Designation' },
        { key: 'd-dept', label: 'Department' },
        { key: 'd-bank', label: 'Bank A/C Number' }
    ]
};

function selectElement(el) {
    if(selectedEl) selectedEl.classList.remove('selected');
    selectedEl = el;
    el.classList.add('selected');
    
    let type = el.getAttribute('data-type');
    
    document.getElementById('prop-empty').style.display = 'none';
    let form = document.getElementById('dynamic-form');
    form.style.display = 'block';
    form.innerHTML = '';
    
    if(compFields[type]) {
        compFields[type].forEach(field => {
            let val = el.querySelector('.' + field.key).innerText;
            
            let html = `
            <div class="prop-field">
                <span class="prop-label">${field.label}</span>
                <input type="text" class="prop-input" value="${val}" oninput="updateField('${field.key}', this.value)">
            </div>`;
            form.innerHTML += html;
        });
    } else {
        form.innerHTML = '<p class="fs-7">This component has no separate editable text fields.</p>';
    }
}

function updateField(cls, val) {
    if(selectedEl) {
        selectedEl.querySelector('.' + cls).innerText = val;
    }
}

document.getElementById('canvas').addEventListener('mousedown', function(e) {
    let el = e.target.closest('.canvas-element');
    if(e.target.classList.contains('resize-handle')) return;
    
    if(el) {
        selectElement(el);
    } else {
        if(selectedEl) selectedEl.classList.remove('selected');
        selectedEl = null;
        document.getElementById('prop-empty').style.display = 'block';
        document.getElementById('dynamic-form').style.display = 'none';
    }
});

function rebindInteract() {
    interact('.canvas-element')
        .draggable({
            modifiers: [
                interact.modifiers.restrictRect({
                    restriction: 'parent',
                    endOnly: false
                })
            ],
            listeners: {
                start() { saveState(); },
                move(event) {
                    var target = event.target;
                    var x = (parseFloat(target.getAttribute('data-x')) || 0) + event.dx;
                    var y = (parseFloat(target.getAttribute('data-y')) || 0) + event.dy;
                    target.style.transform = `translate(${x}px, ${y}px)`;
                    target.setAttribute('data-x', x);
                    target.setAttribute('data-y', y);
                }
            }
        })
        .resizable({
            edges: { left: '.resize-nw, .resize-sw', right: '.resize-ne, .resize-se', bottom: '.resize-sw, .resize-se', top: '.resize-nw, .resize-ne' },
            modifiers: [
                interact.modifiers.restrictEdges({
                    outer: 'parent'
                })
            ],
            listeners: {
                start() { saveState(); },
                move: function (event) {
                    let target = event.target;
                    let x = (parseFloat(target.getAttribute('data-x')) || 0);
                    let y = (parseFloat(target.getAttribute('data-y')) || 0);

                    target.style.width = event.rect.width + 'px';
                    target.style.height = event.rect.height + 'px';

                    x += event.deltaRect.left;
                    y += event.deltaRect.top;

                    target.style.transform = `translate(${x}px, ${y}px)`;
                    target.setAttribute('data-x', x);
                    target.setAttribute('data-y', y);
                }
            }
        });
}

interact('.drag-source').draggable({
    clone: true,
    listeners: {
        end: function(e) {
            saveState();
            let type = e.target.getAttribute('data-comp');
            let newEl = document.createElement('div');
            newEl.className = 'canvas-element';
            newEl.setAttribute('data-type', type);
            newEl.setAttribute('data-x', 50);
            newEl.setAttribute('data-y', 50);
            newEl.style.transform = `translate(50px, 50px)`;
            
            if(type === 'header') {
                newEl.style.width = '710px';
                newEl.style.height = '80px';
                newEl.innerHTML = `
                    <div class="comp-header">
                        <div>
                            <h2 style="margin:0; color:#003366;" class="d-company">Company Name</h2>
                            <div class="d-address" style="font-size: 11px; color:#555;">Address Line</div>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-size: 11px; font-weight: bold;">Payslip For The Month</div>
                            <div class="d-month" style="font-size: 16px; font-weight: bold; margin-top: 5px;">Month Year</div>
                        </div>
                    </div>
                `;
            } else if(type === 'emp') {
                newEl.style.width = '710px';
                newEl.style.height = '110px';
                newEl.innerHTML = `
                    <div class="comp-emp bg-white">
                        <div>
                            <div><strong>ID:</strong> <span class="d-id">EMP-001</span></div>
                            <div><strong>Name:</strong> <span class="d-name">Name</span></div>
                            <div><strong>Phone:</strong> <span class="d-phone">Phone</span></div>
                        </div>
                        <div>
                            <div><strong>Designation:</strong> <span class="d-desig">Designation</span></div>
                            <div><strong>Department:</strong> <span class="d-dept">Department</span></div>
                            <div><strong>Bank:</strong> <span class="d-bank">Bank A/C</span></div>
                        </div>
                    </div>
                `;
            } else if(type === 'earnings') {
                newEl.style.width = '350px';
                newEl.style.height = '150px';
                newEl.innerHTML = `
                    <table class="comp-table">
                        <thead><tr><th>EARNINGS</th><th align="right">AMOUNT</th></tr></thead>
                        <tbody>
                            <tr><td>Basic</td><td align="right">50000</td></tr>
                        </tbody>
                    </table>
                `;
            }
            
            newEl.innerHTML += `<div class="resize-handle resize-nw"></div><div class="resize-handle resize-ne"></div><div class="resize-handle resize-sw"></div><div class="resize-handle resize-se"></div>`;
            document.getElementById('canvas').appendChild(newEl);
            selectElement(newEl);
        }
    }
});

saveState();
rebindInteract();
</script>
{% endblock %}
"""

with open('templates/payslip_designer.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("Applied boundary constraints and dynamic right-panel editable fields.")
