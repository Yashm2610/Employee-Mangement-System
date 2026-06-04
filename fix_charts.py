import re
file_path = r'c:\maxworth internship\templates\index.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the row start to add justify-content-between
content = content.replace('<div class="row mt-4 mb-2">', '<div class="row mt-4 mb-2 justify-content-between">')

# Change col-lg-4 to col-lg-5 for the first chart (Dept Chart)
# Only do this for the charts block
dept_pattern = r'<div class="col-lg-4 col-md-12 mb-3">(\s*<div class="card shadow-sm border-0 h-100 card-glow">\s*<div class="card-body">\s*<h6 class="card-title fw-bold text-dark"><i class="bi bi-pie-chart-fill text-primary me-2"></i>Department Distribution</h6>)'
content = re.sub(dept_pattern, r'<div class="col-lg-5 col-md-12 mb-3">\1', content)

# Remove the gender chart
gender_pattern = r'<div class="col-lg-4 col-md-12 mb-3">\s*<div class="card shadow-sm border-0 h-100 card-glow">\s*<div class="card-body">\s*<h6 class="card-title fw-bold text-dark"><i class="bi bi-gender-ambiguous text-info me-2"></i>Gender Ratio</h6>\s*<div style="position: relative; height:250px; width:100%">\s*<canvas id="genderChart"></canvas>\s*</div>\s*</div>\s*</div>\s*</div>'
content = re.sub(gender_pattern, '', content)

# Change col-lg-4 to col-lg-5 for the third chart (Location Spread)
loc_pattern = r'<div class="col-lg-4 col-md-12 mb-3">(\s*<div class="card shadow-sm border-0 h-100 card-glow">\s*<div class="card-body">\s*<h6 class="card-title fw-bold text-dark"><i class="bi bi-geo-alt-fill text-danger me-2"></i>Location Spread</h6>)'
content = re.sub(loc_pattern, r'<div class="col-lg-5 col-md-12 mb-3">\1', content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Charts updated successfully.")
