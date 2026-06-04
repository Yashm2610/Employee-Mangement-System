import re
file_path = r'c:\maxworth internship\templates\index.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Remove headers
content = re.sub(r'\s*<th scope="col" class="py-3 resizable-th text-end">Basic \(₹\)</th>.*?</th\s*>', '', content, flags=re.DOTALL)
# The above regex might be too greedy or not match. Let's be specific for headers:

headers_to_remove = """                                        <th scope="col" class="py-3 resizable-th text-end">Basic (₹)</th>
                                        <th scope="col" class="py-3 resizable-th text-end">Meal Allowance (₹)</th>
                                        <th scope="col" class="py-3 resizable-th text-end">Transport Allowance (₹)</th>
                                        <th scope="col" class="py-3 resizable-th text-end">Medical Allowance (₹)</th>
                                        <th scope="col" class="py-3 resizable-th text-end">Allowances Total (₹)</th>
                                        <th scope="col" class="py-3 resizable-th text-end">Retirement Ins. (₹)</th>
                                        <th scope="col" class="py-3 resizable-th text-end">Professional Tax (₹)</th>
                                        <th scope="col" class="py-3 resizable-th text-end">Deductions Total (₹)</th>
                                        <th scope="col" class="py-3 resizable-th text-end">Net Pay (₹)</th>"""

data_to_remove = """                                                <td class="text-end text-dark font-monospace">₹{{ "{:,.2f}".format(emp.basic_salary) }}</td>
                                                <td class="text-end text-muted font-monospace">₹{{ "{:,.2f}".format(emp.meal_allowance or 0) }}</td>
                                                <td class="text-end text-muted font-monospace">₹{{ "{:,.2f}".format(emp.transportation_allowance or 0) }}</td>
                                                <td class="text-end text-muted font-monospace">₹{{ "{:,.2f}".format(emp.medical_allowance or 0) }}</td>
                                                <td class="text-end text-success-emphasis font-monospace fw-semibold">₹{{ "{:,.2f}".format(emp.allowances or 0) }}</td>
                                                <td class="text-end text-muted font-monospace">₹{{ "{:,.2f}".format(emp.retirement_insurance or 0) }}</td>
                                                <td class="text-end text-muted font-monospace">₹{{ "{:,.2f}".format(emp.tax or 0) }}</td>
                                                <td class="text-end text-danger-emphasis font-monospace fw-semibold">₹{{ "{:,.2f}".format(emp.deductions or 0) }}</td>
                                                <td class="text-end text-success fw-bold font-monospace">₹{{ "{:,.2f}".format((emp.basic_salary or 0) + (emp.allowances or 0) - (emp.deductions or 0)) }}</td>"""

if headers_to_remove in content:
    content = content.replace(headers_to_remove, '')
    print("Headers removed.")
else:
    print("Headers not found.")

if data_to_remove in content:
    content = content.replace(data_to_remove, '')
    print("Data cells removed.")
else:
    print("Data cells not found.")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("index.html updated successfully.")
