import sys

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Move old builder to legacy
content = content.replace("@app.route('/payslip_builder', methods=['GET', 'POST'])", "@app.route('/payslip_builder_v1', methods=['GET', 'POST'])")
content = content.replace("def payslip_builder():", "def payslip_builder_legacy():", 1)

# 2. Assign new Studio 2.0 to main builder URL
content = content.replace("@app.route('/payslip_designer')", "@app.route('/payslip_builder')")

# 3. Add Template Test Lab API
validation_route = """
@app.route('/api/v1/templates/validate', methods=['POST'])
@hr_required
def api_template_validate():
    data = request.json
    html_content = data.get('layout_html', '')
    formulas = data.get('formulas', {})
    
    warnings = []
    errors = []
    
    if 'undefined' in html_content or 'null' in html_content:
        warnings.append('Template contains undefined data bindings.')
        
    for key, expr in formulas.items():
        if '/' in expr and '0' in expr:
            errors.append(f'Formula error in {key}: Potential division by zero.')
            
    if html_content.count('<tr') > 25:
        warnings.append('Table row count might exceed A4 page boundaries.')
        
    return jsonify({
        'valid': len(errors) == 0, 
        'errors': errors, 
        'warnings': warnings
    })
"""

content = content.replace("if __name__ == '__main__':", validation_route + "\nif __name__ == '__main__':")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Phase 1 Routes Patched Successfully.")
