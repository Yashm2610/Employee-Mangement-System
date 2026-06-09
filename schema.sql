-- ============================================================
-- Normalized SQL Schema for Employee Data Management System
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
    date_of_birth               DATE            NOT NULL,
    joining_date                DATE            NOT NULL,
    basic_salary                DECIMAL(10,2)   NOT NULL,
    age                         INT             NOT NULL,
    gender                      VARCHAR(20)     DEFAULT 'Male',
    education                   INT             DEFAULT 2 COMMENT '0=High School, 1=Diploma, 2=Bachelor''s, 3=Master''s, 4=PhD',
    title                       VARCHAR(100)    DEFAULT 'Software Engineer',
    department                  VARCHAR(100)    DEFAULT 'General Affairs',
    posting_location            VARCHAR(100)    DEFAULT 'Bangalore',
    payment_tier                INT             NOT NULL COMMENT '1=Executive, 2=Professional, 3=Associate'
);

-- ============================================================
-- TABLE 2: employee_bank_details (1-to-1 with employees)
-- ============================================================
CREATE TABLE IF NOT EXISTS employee_bank_details (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    emp_id              VARCHAR(50)     NOT NULL UNIQUE,
    bank_name           VARCHAR(100)    DEFAULT 'Bank of America',
    bank_account_num    VARCHAR(50)     DEFAULT '0000000000',
    ifsc_code           VARCHAR(20)     DEFAULT 'BOFA0000001',
    FOREIGN KEY (emp_id) REFERENCES employees(emp_id) ON DELETE CASCADE
);

-- ============================================================
-- TABLE 3: employee_financial_components (many-to-1 with employees)
-- Unified table for both allowances and deductions.
-- ============================================================
CREATE TABLE IF NOT EXISTS employee_financial_components (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    emp_id          VARCHAR(50)     NOT NULL,
    component_name  VARCHAR(100)    NOT NULL,
    component_code  TINYINT         NOT NULL COMMENT '1 for Allowance, 2 for Deduction',
    amount          DECIMAL(12,2)   DEFAULT 0.00,
    FOREIGN KEY (emp_id) REFERENCES employees(emp_id) ON DELETE CASCADE
);

-- ============================================================
-- TABLE 4: payslip_master (History of Payslips)
-- ============================================================
CREATE TABLE IF NOT EXISTS payslip_master (
    payslip_id           INT AUTO_INCREMENT PRIMARY KEY,
    payslip_no           VARCHAR(20) UNIQUE,
    emp_id               VARCHAR(50) NOT NULL,
    salary_month         VARCHAR(20),
    salary_year          INT,
    basic_salary         DECIMAL(12,2) DEFAULT 0.00,
    total_allowance      DECIMAL(12,2) DEFAULT 0.00,
    total_deduction      DECIMAL(12,2) DEFAULT 0.00,
    final_in_hand_salary DECIMAL(12,2) DEFAULT 0.00,
    generated_on         DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (emp_id) REFERENCES employees(emp_id) ON DELETE CASCADE
);

-- ============================================================
-- TABLE 5: employee_holidays
-- ============================================================
CREATE TABLE IF NOT EXISTS employee_holidays (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    emp_id      VARCHAR(50) NOT NULL,
    holiday_code TINYINT NOT NULL COMMENT 'Codes: 0=Present, 1=Casual Leave, 2=Sick Leave, 3=Paid Holiday, 4=Absent',
    FOREIGN KEY (emp_id) REFERENCES employees(emp_id) ON DELETE CASCADE
);

-- ============================================================
-- TABLE 6: employee_emails (Communication Log)
-- ============================================================
CREATE TABLE IF NOT EXISTS employee_emails (
    id INT AUTO_INCREMENT PRIMARY KEY,
    emp_id VARCHAR(50) NOT NULL,
    sender_email VARCHAR(100) DEFAULT 'admin@maxworth.com',
    receiver_email VARCHAR(100),
    sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    subject VARCHAR(255),
    body TEXT,
    response_received_at DATETIME,
    response_notes TEXT,
    status VARCHAR(20) DEFAULT 'Sent',
    FOREIGN KEY (emp_id) REFERENCES employees(emp_id) ON DELETE CASCADE
);

-- ============================================================
-- TABLE 7: users (Authentication & Role Management)
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id VARCHAR(50) UNIQUE,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'Employee' COMMENT 'Admin, HR, Employee',
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME,
    FOREIGN KEY (employee_id) REFERENCES employees(emp_id) ON DELETE SET NULL
);

-- ============================================================
-- TABLE 8: user_login_logs (Audit Trail)
-- ============================================================
CREATE TABLE IF NOT EXISTS user_login_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    login_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    logout_time DATETIME,
    ip_address VARCHAR(45),
    browser VARCHAR(255),
    device VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
