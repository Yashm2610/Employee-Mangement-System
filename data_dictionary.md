# Employee & Payroll Data Dictionary

This document serves as the data dictionary for the Employee Data Management System database (`employee_db`), which follows a normalized 4-table schema.

## Table: `employees`

| Column Name | Data Type | Constraints / Defaults | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| **id** | `INT` | `PRIMARY KEY AUTO_INCREMENT` | Unique internal record identifier. | `42` |
| **emp_id** | `VARCHAR(50)` | `UNIQUE NOT NULL` | Unique corporate employee identifier. | `EMP-2024-1001` |
| **emp_name** | `VARCHAR(100)` | `NOT NULL` | Full legal name of the employee. | `John Doe` |
| **email** | `VARCHAR(100)` | `NOT NULL` | Corporate email address. | `john.doe@company.com` |
| **date_of_birth** | `DATE` | `NOT NULL` | Date of birth of the employee. | `1990-05-15` |
| **joining_date** | `DATE` | `NOT NULL` | Date when the employee joined the company. | `2024-01-10` |
| **basic_salary** | `DECIMAL(12,2)` | Default: `0.00` | Base monthly salary. | `50000.00` |
| **age** | `INT` | Default: `30` | Age of the employee in years. | `34` |
| **gender** | `VARCHAR(20)` | Default: `'Male'` | Gender identification. | `'Male'` |
| **education** | `TINYINT` | Default: `2` | Education level code (0=High School, 1=Diploma, 2=Bachelor's, 3=Master's, 4=PhD). | `2` |
| **title** | `VARCHAR(100)` | Default: `'Software Engineer'` | Job designation / position title. | `'Senior Developer'` |
| **department** | `VARCHAR(100)` | Default: `'IT Department'` | Specific corporate department. | `'Core Development'` |
| **posting_location** | `VARCHAR(100)` | Default: `'Bangalore'` | City of employment. | `'Mumbai'` |
| **payment_tier** | `INT` | Default: `3` | Salary tier (1=Executive, 2=Professional, 3=Associate). | `2` |

---

## Table: `employee_bank_details`

| Column Name | Data Type | Constraints / Defaults | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| **id** | `INT` | `PRIMARY KEY AUTO_INCREMENT` | Unique internal record identifier. | `1` |
| **emp_id** | `VARCHAR(50)` | `FK` (employees.emp_id) | Employee identifier. | `EMP-2024-1001` |
| **bank_name** | `VARCHAR(100)` | Default: `'Bank of America'` | Name of the bank used for salary credit. | `'HDFC Bank'` |
| **bank_account_num** | `VARCHAR(50)` | Default: `'1234567890'` | Employee's bank account number. | `'0987654321'` |
| **ifsc_code** | `VARCHAR(20)` | Default: `'BOFA0000001'` | IFSC code of the bank branch. | `'HDFC0001234'` |

---

## Table: `employee_financial_components`

| Column Name | Data Type | Constraints / Defaults | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| **id** | `INT` | `PRIMARY KEY AUTO_INCREMENT` | Unique internal record identifier. | `1` |
| **emp_id** | `VARCHAR(50)` | `FK` (employees.emp_id) | Employee identifier. | `EMP-2024-1001` |
| **component_name** | `VARCHAR(100)` | `NOT NULL` | Name of the allowance or deduction. | `'Meal Allowance'` |
| **component_code** | `TINYINT` | `NOT NULL` | Type of component (1 = Allowance, 2 = Deduction). | `1` |
| **amount** | `DECIMAL(12,2)` | `NOT NULL` | Monthly amount for this component. | `1500.00` |

---

## Table: `employee_holidays`

| Column Name | Data Type | Constraints / Defaults | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| **id** | `INT` | `PRIMARY KEY AUTO_INCREMENT` | Unique internal record identifier. | `1` |
| **emp_id** | `VARCHAR(50)` | `FK` (employees.emp_id) | Employee identifier. | `EMP-2024-1001` |
| **holiday_code** | `TINYINT` | `NOT NULL` | Status code (0=Present, 1=Casual Leave, 2=Sick Leave, 3=Paid Holiday, 4=Absent). | `2` |

---

## Table: `payslip_master`

| Column Name | Data Type | Constraints / Defaults | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| **payslip_id** | `INT` | `PRIMARY KEY AUTO_INCREMENT` | Unique internal record identifier. | `101` |
| **emp_id** | `VARCHAR(50)` | `FK` (employees.emp_id) | Employee identifier. | `EMP-2024-1001` |
| **basic_salary** | `DECIMAL(12,2)` | Default: `0.00` | Basic salary at the time of payslip generation. | `50000.00` |
| **total_allowance** | `DECIMAL(12,2)` | Default: `0.00` | Total sum of all allowances. | `3000.00` |
| **total_deduction** | `DECIMAL(12,2)` | Default: `0.00` | Total sum of all deductions. | `1000.00` |
| **final_in_hand_salary**| `DECIMAL(12,2)` | Default: `0.00` | Net pay after basic + allowances - deductions. | `52000.00` |
| **generated_on** | `DATETIME` | Default: `CURRENT_TIMESTAMP` | Timestamp of when the payslip was created. | `2024-06-03 12:00:00` |

---

## Derived Calculation Rules for Payslip Generation

- **Total Allowances** = Sum of all `employee_financial_components` where `component_code = 1` for an employee.
- **Total Deductions** = Sum of all `employee_financial_components` where `component_code = 2` for an employee.
- **Gross Salary** = `basic_salary` + **Total Allowances**
- **Net Pay (Final In Hand Salary)** = `basic_salary` + **Total Allowances** - **Total Deductions**
