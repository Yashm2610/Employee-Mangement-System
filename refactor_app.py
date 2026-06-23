import re

def update_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    # Safe SQL table replacements
    replacements = [
        # Employee
        (r'\bFROM employees\b', 'FROM Employee'),
        (r'\bJOIN employees\b', 'JOIN Employee'),
        (r'\bINTO employees\b', 'INTO Employee'),
        (r'\bUPDATE employees\b', 'UPDATE Employee'),
        (r'\bTABLE employees\b', 'TABLE Employee'),
        # Company
        (r'\bFROM company_master\b', 'FROM Company'),
        (r'\bJOIN company_master\b', 'JOIN Company'),
        (r'\bINTO company_master\b', 'INTO Company'),
        (r'\bUPDATE company_master\b', 'UPDATE Company'),
        (r'\bTABLE company_master\b', 'TABLE Company'),
        # Allowance
        (r'\bFROM financial_component_master\b', 'FROM Allowance'),
        (r'\bJOIN financial_component_master\b', 'JOIN Allowance'),
        (r'\bINTO financial_component_master\b', 'INTO Allowance'),
        (r'\bUPDATE financial_component_master\b', 'UPDATE Allowance'),
        (r'\bTABLE financial_component_master\b', 'TABLE Allowance'),
        # Employee_Allowance
        (r'\bFROM employee_financial_components\b', 'FROM Employee_Allowance'),
        (r'\bJOIN employee_financial_components\b', 'JOIN Employee_Allowance'),
        (r'\bINTO employee_financial_components\b', 'INTO Employee_Allowance'),
        (r'\bUPDATE employee_financial_components\b', 'UPDATE Employee_Allowance'),
        (r'\bTABLE employee_financial_components\b', 'TABLE Employee_Allowance'),
        # Payslip_format
        (r'\bFROM payslip_templates\b', 'FROM Payslip_format'),
        (r'\bJOIN payslip_templates\b', 'JOIN Payslip_format'),
        (r'\bINTO payslip_templates\b', 'INTO Payslip_format'),
        (r'\bUPDATE payslip_templates\b', 'UPDATE Payslip_format'),
        (r'\bTABLE payslip_templates\b', 'TABLE Payslip_format'),
        # Payslip_format_setting
        (r'\bFROM payslip_template_versions\b', 'FROM Payslip_format_setting'),
        (r'\bJOIN payslip_template_versions\b', 'JOIN Payslip_format_setting'),
        (r'\bINTO payslip_template_versions\b', 'INTO Payslip_format_setting'),
        (r'\bUPDATE payslip_template_versions\b', 'UPDATE Payslip_format_setting'),
        (r'\bTABLE payslip_template_versions\b', 'TABLE Payslip_format_setting'),
        # Salary_Payslip
        (r'\bFROM salary_overrides\b', 'FROM Salary_Payslip'),
        (r'\bJOIN salary_overrides\b', 'JOIN Salary_Payslip'),
        (r'\bINTO salary_overrides\b', 'INTO Salary_Payslip'),
        (r'\bUPDATE salary_overrides\b', 'UPDATE Salary_Payslip'),
        (r'\bTABLE salary_overrides\b', 'TABLE Salary_Payslip'),
        
        (r'\bFROM payslip_master\b', 'FROM Salary_Payslip'),
        (r'\bJOIN payslip_master\b', 'JOIN Salary_Payslip'),
        (r'\bINTO payslip_master\b', 'INTO Salary_Payslip'),
        (r'\bUPDATE payslip_master\b', 'UPDATE Salary_Payslip'),
        (r'\bTABLE payslip_master\b', 'TABLE Salary_Payslip'),
        
        (r'\bFROM payroll_snapshots\b', 'FROM Salary_Payslip'),
        (r'\bJOIN payroll_snapshots\b', 'JOIN Salary_Payslip'),
        (r'\bINTO payroll_snapshots\b', 'INTO Salary_Payslip'),
        (r'\bUPDATE payroll_snapshots\b', 'UPDATE Salary_Payslip'),
        (r'\bTABLE payroll_snapshots\b', 'TABLE Salary_Payslip'),
        
        # Masters
        (r'\bFROM department_master\b', "FROM Master_table WHERE MasterType='department'"),
        (r'\bFROM education_master\b', "FROM Master_table WHERE MasterType='education'"),
        (r'\bFROM designation_master\b', "FROM Master_table WHERE MasterType='designation'"),
        (r'\bFROM location_master\b', "FROM Master_table WHERE MasterType='location'"),
        (r'\bFROM holiday_master\b', "FROM Master_table WHERE MasterType='holiday'")
    ]

    new_content = content
    for old, new in replacements:
        new_content = re.sub(old, new, new_content)

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(new_content)
        
update_file('app.py')
