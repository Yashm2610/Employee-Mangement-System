# Employee & Payroll Data Dictionary

This document serves as the data dictionary for the `employees` table in the Employee Data Management System database (`employee_db`).

## Table: `employees`

| Column Name | Data Type | Constraints / Defaults | Description | Source / Generation Logic | Example Value |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **id** | `INT` | `PRIMARY KEY`, `AUTO_INCREMENT`, `NOT NULL` | Unique internal record identifier. | Generated automatically by the database on record creation. | `42` |
| **emp_id** | `VARCHAR(50)` | `UNIQUE`, `NOT NULL` | Unique corporate employee identifier. | Input manually or generated via format: `EMP-[JoiningYear]-[Count + 1001]` | `EMP-2017-1005` |
| **emp_name** | `VARCHAR(100)` | `NOT NULL` | Full name of the employee. | Input manually or randomly combined from pre-selected first and last names. | `Wayne Doorprize` |
| **email** | `VARCHAR(100)` | `NOT NULL` | Professional email address. | Input manually or derived as `firstname.lastname[Index]@company.com` | `wayne.doorprize@company.com` |
| **date** | `DATE` | `NOT NULL` | Date when the employee joined the company. | Input manually or read from joining/registration year in the CSV. | `2017-01-28` |
| **basic_salary** | `DECIMAL(10,2)` | Default: `45000.00` | Monthly base pay (pre-allowances and deductions). | Input manually, read from CSV, or generated based on the Kaggle `PaymentTier`. | `2000.00` |
| **allowances** | `DECIMAL(10,2)` | Default: `12000.00` | Aggregated allowances (sum of meal, transport, and medical allowances). | Calculated automatically as `meal_allowance + transportation_allowance + medical_allowance`. | `900.00` |
| **deductions** | `DECIMAL(10,2)` | Default: `5000.00` | Aggregated salary deductions (sum of retirement and tax deductions). | Calculated automatically as `retirement_insurance + tax`. | `50.00` |
| **age** | `INT` | Default: `30` | Age of the employee in years. | Input manually, mapped from CSV, or randomized between 21 and 58. | `34` |
| **gender** | `VARCHAR(20)` | Default: `'Male'` | Employee's gender identification. | Input manually, read from CSV, or assigned. | `'Male'` |
| **education** | `VARCHAR(100)` | Default: `'B.Tech'` | Highest level of education attained. | Input manually or mapped from CSV (e.g. Bachelors, Masters, PHD). | `'Bachelors'` |
| **title** | `VARCHAR(100)` | Default: `'Staff'` | Job designation / post. | Mapped from CSV column synonyms or dynamically generated based on experience/education. | `'Cleaning Service Staff'` |
| **directorate** | `VARCHAR(100)` | Default: `'Operation'` | Corporate board division or directorate. | Mapped from CSV column synonyms or generated randomly based on the designation. | `'Operation'` |
| **department** | `VARCHAR(100)` | Default: `'General Affairs'` | Specific corporate department. | Mapped from CSV column synonyms or generated randomly. | `'General Affairs'` |
| **bank_name** | `VARCHAR(100)` | Default: `'Bank of America'` | Name of the bank where salary is credited. | Mapped from CSV column synonyms or defaults. | `'Bank of America'` |
| **bank_account_num** | `VARCHAR(50)` | Default: `'1234567890'` | Employee's bank account number. | Mapped from CSV column synonyms or generated as a random 10-digit string. | `'1234567890'` |
| **meal_allowance** | `DECIMAL(10,2)` | Default: `300.00` | Monthly meal allowance amount. | Input manually, read from CSV, or defaults. | `300.00` |
| **transportation_allowance** | `DECIMAL(10,2)` | Default: `300.00` | Monthly transport allowance amount. | Input manually, read from CSV, or defaults. | `300.00` |
| **medical_allowance** | `DECIMAL(10,2)` | Default: `300.00` | Monthly medical allowance amount. | Input manually, read from CSV, or defaults. | `300.00` |
| **retirement_insurance** | `DECIMAL(10,2)` | Default: `25.00` | Monthly retirement insurance deduction. | Input manually, read from CSV, or defaults. | `25.00` |
| **tax** | `DECIMAL(10,2)` | Default: `25.00` | Monthly tax / professional tax deduction. | Input manually, read from CSV, or defaults. | `25.00` |

---

## Derived Calculation Rules for Payslip Generation

- **Gross Earnings** = $\text{basic\_salary} + \text{meal\_allowance} + \text{transportation\_allowance} + \text{medical\_allowance}$
- **Total Deductions** = $\text{retirement\_insurance} + \text{tax}$
- **Net Pay** = $\text{Gross Earnings} - \text{Total Deductions}$
- **Net Pay in Words** = Dynamically converted from Net Pay value using the English Dollars standard formatting.
