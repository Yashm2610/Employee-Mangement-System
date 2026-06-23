import io

html = """
        <div class="table-responsive">
            <table class="table table-hover table-bordered align-middle mb-0 text-nowrap" style="font-size: 0.85rem;">
                <thead class="table-dark text-uppercase fs-8 tracking-wider">
                    <tr>
                        <th class="ps-3">Emp ID</th>
                        <th>Name</th>
                        <th>DOJ</th>
                        <th>Working Days</th>
                        <th>MONTH GROSS</th>
                        <th>MONTH BASIC</th>
                        <th>HRA</th>
                        <th>SA</th>
                        <th>Total Dys</th>
                        <th class="bg-primary text-white">Final Basic</th>
                        <th class="bg-primary text-white">final HRA</th>
                        <th class="bg-primary text-white">Final SA</th>
                        <th class="bg-success text-white">Final Gross</th>
                        <th>Arrier</th>
                        <th>Bonus</th>
                        <th>Telephone</th>
                        <th>Special Incentive</th>
                        <th class="bg-success text-white">TOTAL EARNING</th>
                        <th class="bg-danger text-white">PF</th>
                        <th class="bg-danger text-white">ESIC</th>
                        <th class="bg-danger text-white">ADVANCE</th>
                        <th class="bg-danger text-white">TDS</th>
                        <th class="bg-danger text-white">OTHER DEDN</th>
                        <th class="bg-danger text-white">super Annuation</th>
                        <th class="bg-danger text-white fw-bold">TOTAL DEDN</th>
                        <th class="bg-info text-dark fw-bold">NET SALARY (ACTUAL)</th>
                        <th>NET SALARY (ACTUAL) Word</th>
                        <th>Basic+DA(for PF)</th>
                        <th>PF Employer</th>
                        <th>ESIC (Employer)</th>
                        <th class="bg-warning text-dark fw-bold">CTC</th>
                        <th class="text-end pe-4">Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {% for emp in employees %}
                    <tr>
                        <td class="ps-3 fw-medium"><code>{{ emp.emp_id }}</code></td>
                        <td class="fw-bold">{{ emp.emp_name }}</td>
                        <td>{{ emp.joining_date.strftime('%d-%b-%y') if emp.joining_date else 'NA' }}</td>
                        <td>21</td>
                        <td>{{ "{:,.2f}".format(emp.month_gross) }}</td>
                        <td>{{ "{:,.2f}".format(emp.month_basic) }}</td>
                        <td>{{ "{:,.2f}".format(emp.month_hra) }}</td>
                        <td>{{ "{:,.2f}".format(emp.month_sa) }}</td>
                        <td class="fw-bold">{{ emp.total_dys }}</td>
                        <td class="bg-primary-subtle">{{ "{:,.2f}".format(emp.final_basic) }}</td>
                        <td class="bg-primary-subtle">{{ "{:,.2f}".format(emp.final_hra) }}</td>
                        <td class="bg-primary-subtle">{{ "{:,.2f}".format(emp.final_sa) }}</td>
                        <td class="bg-success-subtle fw-bold">{{ "{:,.2f}".format(emp.final_gross) }}</td>
                        <td>{{ "{:,.2f}".format(emp.arrier) }}</td>
                        <td>{{ "{:,.2f}".format(emp.bonus) }}</td>
                        <td>{{ "{:,.2f}".format(emp.telephone) }}</td>
                        <td>{{ "{:,.2f}".format(emp.special_incentive) }}</td>
                        <td class="bg-success-subtle fw-bold text-success">{{ "{:,.2f}".format(emp.total_earning) }}</td>
                        <td class="bg-danger-subtle">{{ "{:,.2f}".format(emp.pf) }}</td>
                        <td class="bg-danger-subtle">{{ "{:,.2f}".format(emp.esic) }}</td>
                        <td class="bg-danger-subtle">{{ "{:,.2f}".format(emp.advance) }}</td>
                        <td class="bg-danger-subtle">{{ "{:,.2f}".format(emp.tds) }}</td>
                        <td class="bg-danger-subtle">{{ "{:,.2f}".format(emp.other_dedn) }}</td>
                        <td class="bg-danger-subtle">{{ "{:,.2f}".format(emp.super_annuation) }}</td>
                        <td class="bg-danger-subtle fw-bold text-danger">{{ "{:,.2f}".format(emp.total_dedn) }}</td>
                        <td class="bg-info-subtle fw-bold fs-6">{{ "{:,.2f}".format(emp.net_salary) }}</td>
                        <td class="small">{{ emp.net_salary_word }}</td>
                        <td>{{ "{:,.2f}".format(emp.basic_da_pf) }}</td>
                        <td>{{ "{:,.2f}".format(emp.pf_employer) }}</td>
                        <td>{{ "{:,.2f}".format(emp.esic_employer) }}</td>
                        <td class="bg-warning-subtle fw-bold">{{ "{:,.2f}".format(emp.ctc) }}</td>
                        <td class="text-end pe-3 bg-white position-sticky end-0">
                            <div class="d-flex gap-2 justify-content-end">
                                <a href="{{ url_for('payslip_builder', selected_emp_id=emp.emp_id) }}" class="btn btn-sm btn-outline-success" title="Prepare Payslip">
                                    <i class="bi bi-file-earmark-text"></i> Payslip
                                </a>
                                <button type="button" class="btn btn-sm btn-outline-primary" onclick="openEditModal('{{ emp.emp_id }}', '{{ emp.emp_name|replace(\'\\'\', \'\\\\\\'\') }}', '{{ emp.bank_name|default(\'\', true)|replace(\'\\'\', \'\\\\\\'\') }}', '{{ emp.bank_account_num|default(\'\', true)|replace(\'\\'\', \'\\\\\\'\') }}', '{{ emp.ifsc_code|default(\'\', true)|replace(\'\\'\', \'\\\\\\'\') }}', {{ emp.basic_salary }})" title="Edit Financials">
                                    <i class="bi bi-pencil-square"></i> Edit
                                </button>
                            </div>
                        </td>
                    </tr>
                    {% endfor %}
                    {% if not employees %}
                    <tr>
                        <td colspan="32" class="text-center py-5 text-muted">No employees found.</td>
                    </tr>
                    {% endif %}
                </tbody>
            </table>
        </div>
"""

with io.open("new_table.html", "w", encoding="utf-8") as f:
    f.write(html)
