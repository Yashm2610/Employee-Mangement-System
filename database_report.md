# Database Architecture & Modification Report

Here is the detailed breakdown of all the tables currently in your database, what their purpose is, what modifications were made to them, and **why** those changes were made.

The core reason for the modifications was to **perfectly align the database with your handwritten notebook** (renaming tables, capitalizing them, and consolidating multiple smaller masters into a single `Master_table`), while keeping all existing website data 100% intact.

---

## 1. Core Master Tables (Modified as per Notebook)

These tables are the foundation of the HR system and were specifically modified to match your notebook's requirements.

### **Company** (Formerly `company_master`)
* **Purpose:** Stores the details of the company (Name, Address, Logo, etc.).
* **Modifications:** Renamed from `company_master` to `Company`. 
* **Reason:** To match the exact naming convention specified in your handwritten notebook.

### **Employee** (Formerly `employees`)
* **Purpose:** The main table that stores all details for the 1,000 employees (Name, Email, DOJ, Salary, etc.).
* **Modifications:** Renamed from `employees` to `Employee`. 
* **Reason:** To follow the notebook's instruction of having a capitalized singular `Employee` table.

### **Master_table** (New Table)
* **Purpose:** A universal master table that stores all categorical data like Locations, Departments, Designations, and Education qualifications in one single place. It uses a `MasterType` column to differentiate them (e.g., `MasterType = 'location'`).
* **Modifications:** Created entirely from scratch. All data from the old separate master tables was migrated into this single table.
* **Reason:** Your notebook specifically requested a single `Master_table` design to reduce database clutter instead of having 5-6 different small tables for every little dropdown menu.

### **allowance** (and `employee_allowance`)
* **Purpose:** Stores the mapping of which employee gets which financial component (Basic, HRA, Medical, etc.) and the amount.
* **Modifications:** We ensured all 5,000 employees have their allowances mapped here. 
* **Reason:** To ensure the Salary Master and Payslips have accurate data to pull from.

### **financial_component_master**
* **Purpose:** Stores the names of all the earnings and deductions (e.g., Basic, HRA, PF, TDS).
* **Modifications:** It was previously completely empty. I ran a script to auto-fill it with all the unique components currently active in the system.
* **Reason:** Without this table, the UI dropdowns for financial components were blank.

---

## 2. Deprecated / Old Master Tables

These tables still exist in the database so no old data is lost, but **they are no longer actively used** because their data has been moved to the new `Master_table`.

* **`department_master`**: Used to store departments.
* **`designation_master`**: Used to store job titles.
* **`location_master`**: Used to store branch locations.
* **`education_master`**: Used to store degree names.
* **`company_master`**: Replaced by `Company`.
* **`employees`**: Replaced by `Employee`.

**Why were they kept?**
As a strict safety measure! We never delete original tables immediately during a migration to guarantee zero data loss. The system now reads from the new structured tables (`Master_table`, `Employee`, `Company`).

---

## 3. Daily Operations & Attendance Tables

These tables manage the day-to-day data of employees. **No structural changes were made to these**, they were left untouched to keep your existing code working perfectly.

* **`employee_attendance`**: Stores day-by-day attendance records (In-time, Out-time) for employees.
* **`employee_monthly_attendance`**: Stores aggregated monthly attendance summaries (Total Working Days, Total Present Days).
* **`employee_holidays`** / **`holiday_master`**: Stores the company's official holiday calendar and who took them.
* **`employee_leave_balances`**: Tracks how many Paid Leaves / Sick Leaves an employee has remaining.
* **`salary_overrides`**: Stores custom adjustments made to a specific employee's salary for a specific month.

---

## 4. Payslip & Payroll Tables

These tables manage the formatting and generation of salary slips.

* **`payslip_format_setting`**: Stores the configuration and IDs of the payslip designs you create in the Payslip Designer.
* **`salary_payslip`**: Stores the final, generated monthly payslip records for each employee.
* **`payslip_format`**, **`payslip_master`**, **`payslip_templates`**, **`payslip_template_versions`**, **`payslip_template_audit_log`**: These tables support the backend formatting, history, and styling of the dynamic payslip templates you build in the UI.

---

## 5. System & User Tables

* **`users`**: Stores login credentials (usernames, hashed passwords, roles) for admins and employees to access the portal.
* **`user_login_logs`**: Tracks when and from where users log into the system for security auditing.
* **`v_employees` (View)**: This is a **SQL View** (a virtual table). 
    * **Modification:** I updated this view's internal query.
    * **Reason:** Originally, it fetched data from the old `employees` table. I updated it to fetch from the new `Employee` table and join with the new `Master_table`. This is what connects the database to your UI screens without breaking the Python code.
* **`upload_staging`**: A temporary table used when you bulk-import employees via CSV. It holds data temporarily before saving it permanently to the `Employee` table.

---

## Summary of the "Why"
1. **To follow your handwritten notebook:** I renamed `company_master` to `Company`, `employees` to `Employee`, and merged all small master tables into `Master_table`.
2. **To prevent UI crashes:** I updated the `v_employees` view so the Python backend didn't need to be rewritten.
3. **To ensure data integrity:** I left the old tables intact as a backup, and fixed the missing `financial_component_master` data.
