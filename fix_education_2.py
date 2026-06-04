import re
file_path = r'c:\maxworth internship\templates\index.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

target = '''<td>
                                                    {% if emp.education == 0 %}
                                                        <span class="badge bg-light text-dark border px-2.5 py-1.5 fs-7">High School</span>
                                                    {% elif emp.education == 1 %}
                                                        <span class="badge bg-light text-dark border px-2.5 py-1.5 fs-7">Diploma</span>
                                                    {% elif emp.education == 2 %}
                                                        <span class="badge bg-light text-dark border px-2.5 py-1.5 fs-7">Bachelors</span>
                                                    {% elif emp.education == 3 %}
                                                        <span class="badge bg-light text-dark border px-2.5 py-1.5 fs-7">Masters</span>
                                                    {% elif emp.education == 4 %}
                                                        <span class="badge bg-light text-dark border px-2.5 py-1.5 fs-7">PhD</span>
                                                    {% else %}
                                                        <span class="badge bg-light text-dark border px-2.5 py-1.5 fs-7">{{ emp.education }}</span>
                                                    {% endif %}
                                                </td>'''

replacement = '''<td>
                                                    {% if emp.education == 0 %}
                                                        <span class="badge bg-light text-dark border px-2.5 py-1.5 fs-7">10th</span>
                                                    {% elif emp.education == 1 %}
                                                        <span class="badge bg-light text-dark border px-2.5 py-1.5 fs-7">12th</span>
                                                    {% elif emp.education == 2 %}
                                                        <span class="badge bg-light text-dark border px-2.5 py-1.5 fs-7">B.Tech</span>
                                                    {% elif emp.education == 3 %}
                                                        <span class="badge bg-light text-dark border px-2.5 py-1.5 fs-7">M.Tech</span>
                                                    {% elif emp.education == 4 %}
                                                        <span class="badge bg-light text-dark border px-2.5 py-1.5 fs-7">PhD</span>
                                                    {% else %}
                                                        <span class="badge bg-light text-dark border px-2.5 py-1.5 fs-7">{{ emp.education }}</span>
                                                    {% endif %}
                                                </td>'''

if target in content:
    content = content.replace(target, replacement)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Education column updated successfully.")
else:
    print("Could not find the target string. Let's try regex.")
    
    # Backup regex replace if exact match fails
    pattern = re.compile(r'<td>\s*{% if emp\.education == 0 %}.*?{% endif %}\s*</td>', re.DOTALL)
    if pattern.search(content):
        content = pattern.sub(replacement, content)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("Regex replaced successfully.")
    else:
        print("Regex also failed.")
