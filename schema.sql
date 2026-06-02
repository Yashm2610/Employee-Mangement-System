-- ============================================================
-- Normalized SQL Schema for Employee Data Management System
-- 4-Table Design: employees + satellite tables
-- ============================================================

CREATE DATABASE IF NOT EXISTS employee_db;
USE employee_db;

-- ============================================================
-- TABLE 1: employees (core identity + HR/demographic data)
-- ============================================================
CREATE TABLE IF NOT EXISTS employees (
    id                          INT AUTO_INCREMENT PRIMARY KEY,
    emp_id                      VARCHAR(50)     NOT NULL UNIQUE,
    emp_name                    VARCHAR(100)    NOT NULL,
    email                       VARCHAR(100)    NOT NULL,
    date                        DATE            NOT NULL COMMENT 'Date of joining',
    basic_salary                DECIMAL(10,2)   DEFAULT 45000.00,
    allowances                  DECIMAL(10,2)   DEFAULT 0.00 COMMENT 'Calculated total from employee_allowances',
    deductions                  DECIMAL(10,2)   DEFAULT 0.00 COMMENT 'Calculated total from employee_taxes',
    age                         INT             DEFAULT 30,
    gender                      VARCHAR(20)     DEFAULT 'Male',
    education                   VARCHAR(100)    DEFAULT 'B.Tech',
    title                       VARCHAR(100)    DEFAULT 'Software Engineer',
    directorate                 VARCHAR(100)    DEFAULT 'Engineering',
    department                  VARCHAR(100)    DEFAULT 'General Affairs',
    joining_year                INT             DEFAULT 2026,
    city                        VARCHAR(100)    DEFAULT 'Bangalore',
    payment_tier                INT             DEFAULT 3 COMMENT '1=Executive, 2=Professional, 3=Associate',
    ever_benched                VARCHAR(10)     DEFAULT 'No',
    experience_in_current_domain INT            DEFAULT 2,
    leave_or_not                INT             DEFAULT 0 COMMENT '0=Active,1=Leave,2=Medical,3=Parental,4=Unpaid,5=Resigned'
);

-- ============================================================
-- TABLE 2: employee_bank_details (1-to-1 with employees)
-- ============================================================
CREATE TABLE IF NOT EXISTS employee_bank_details (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    emp_id              VARCHAR(50)     NOT NULL UNIQUE,
    bank_name           VARCHAR(100)    DEFAULT 'Bank of America',
    bank_account_num    VARCHAR(50)     DEFAULT '0000000000',
    FOREIGN KEY (emp_id) REFERENCES employees(emp_id) ON DELETE CASCADE
);

-- ============================================================
-- TABLE 3: employee_allowances (many-to-1 with employees)
-- Each row = one type of allowance for one employee.
-- This allows different employees to have different allowance types
-- (e.g., meal_allowance, wife_allowance, housing_allowance, etc.)
-- ============================================================
CREATE TABLE IF NOT EXISTS employee_allowances (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    emp_id          VARCHAR(50)     NOT NULL,
    allowance_type  VARCHAR(100)    NOT NULL COMMENT 'e.g. meal_allowance, transportation_allowance, wife_allowance',
    amount          DECIMAL(10,2)   DEFAULT 0.00,
    FOREIGN KEY (emp_id) REFERENCES employees(emp_id) ON DELETE CASCADE
);

-- ============================================================
-- TABLE 4: employee_taxes (many-to-1 with employees)
-- Each row = one type of tax/deduction for one employee.
-- ============================================================
CREATE TABLE IF NOT EXISTS employee_taxes (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    emp_id      VARCHAR(50)     NOT NULL,
    tax_type    VARCHAR(100)    NOT NULL COMMENT 'e.g. retirement_insurance, professional_tax, income_tax',
    amount      DECIMAL(10,2)   DEFAULT 0.00,
    FOREIGN KEY (emp_id) REFERENCES employees(emp_id) ON DELETE CASCADE
);
