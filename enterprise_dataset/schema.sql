-- Enterprise Database Schema
CREATE TABLE IF NOT EXISTS employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    emp_id VARCHAR(50) UNIQUE NOT NULL,
    emp_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    date_of_birth DATE NOT NULL,
    joining_date DATE NOT NULL,
    basic_salary DECIMAL(12,2) NOT NULL,
    age INT NOT NULL,
    gender VARCHAR(20),
    education INT,
    title VARCHAR(100),
    department VARCHAR(100),
    posting_location VARCHAR(100),
    payment_tier INT
);
CREATE TABLE IF NOT EXISTS employee_bank_details (
    id INT AUTO_INCREMENT PRIMARY KEY,
    emp_id VARCHAR(50) UNIQUE NOT NULL,
    bank_name VARCHAR(100),
    bank_account_num VARCHAR(50) UNIQUE NOT NULL,
    ifsc_code VARCHAR(20)
);
CREATE TABLE IF NOT EXISTS employee_financial_components (
    id INT AUTO_INCREMENT PRIMARY KEY,
    emp_id VARCHAR(50) NOT NULL,
    component_name VARCHAR(100) NOT NULL,
    component_code TINYINT NOT NULL,
    amount DECIMAL(12,2)
);
CREATE TABLE IF NOT EXISTS payslip_master (
    payslip_id INT AUTO_INCREMENT PRIMARY KEY,
    payslip_no VARCHAR(50) UNIQUE,
    emp_id VARCHAR(50) NOT NULL,
    salary_month VARCHAR(20),
    salary_year INT,
    basic_salary DECIMAL(12,2),
    total_allowance DECIMAL(12,2),
    total_deduction DECIMAL(12,2),
    final_in_hand_salary DECIMAL(12,2),
    generated_on DATETIME
);
CREATE TABLE IF NOT EXISTS employee_holidays (
    id INT AUTO_INCREMENT PRIMARY KEY,
    emp_id VARCHAR(50) NOT NULL,
    holiday_code TINYINT
);
CREATE TABLE IF NOT EXISTS employee_emails (
    id INT AUTO_INCREMENT PRIMARY KEY,
    emp_id VARCHAR(50) NOT NULL,
    sender_email VARCHAR(100),
    receiver_email VARCHAR(100),
    subject VARCHAR(255),
    email_type VARCHAR(100),
    sent_timestamp DATETIME,
    response_timestamp DATETIME,
    response_time_hours DECIMAL(6,2),
    status VARCHAR(20)
);
