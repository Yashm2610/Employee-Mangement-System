-- MySQL dump 10.13  Distrib 8.0.45, for Win64 (x86_64)
--
-- Host: localhost    Database: employee_db
-- ------------------------------------------------------
-- Server version	8.0.45

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `company_master`
--

-- DROP TABLE IF EXISTS `company_master`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `company_master` (
  `company_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `gst_no` varchar(50) DEFAULT NULL,
  `address` text,
  `logo_url` varchar(255) DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`company_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `department_master`
--

-- DROP TABLE IF EXISTS `department_master`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `department_master` (
  `department_code` int NOT NULL,
  `department_name` varchar(100) DEFAULT NULL,
  `created_by` varchar(100) DEFAULT 'System',
  `created_on` datetime DEFAULT CURRENT_TIMESTAMP,
  `modified_by` varchar(100) DEFAULT 'System',
  `modified_on` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `is_active` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`department_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `designation_master`
--

-- DROP TABLE IF EXISTS `designation_master`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `designation_master` (
  `designation_code` int NOT NULL,
  `designation_name` varchar(100) DEFAULT NULL,
  `salary_band_min` decimal(12,2) DEFAULT NULL,
  `salary_band_max` decimal(12,2) DEFAULT NULL,
  `created_by` varchar(100) DEFAULT 'System',
  `created_on` datetime DEFAULT CURRENT_TIMESTAMP,
  `modified_by` varchar(100) DEFAULT 'System',
  `modified_on` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `is_active` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`designation_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `education_master`
--

-- DROP TABLE IF EXISTS `education_master`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `education_master` (
  `education_code` int NOT NULL,
  `education_name` varchar(100) DEFAULT NULL,
  `created_by` varchar(100) DEFAULT 'System',
  `created_on` datetime DEFAULT CURRENT_TIMESTAMP,
  `modified_by` varchar(100) DEFAULT 'System',
  `modified_on` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `is_active` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`education_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `employee_attendance`
--

-- DROP TABLE IF EXISTS `employee_attendance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `employee_attendance` (
  `id` int NOT NULL AUTO_INCREMENT,
  `emp_id` varchar(20) DEFAULT NULL,
  `attendance_date` date DEFAULT NULL,
  `status` enum('Present','Absent','Half Day','Leave') DEFAULT NULL,
  `in_time` time DEFAULT NULL,
  `out_time` time DEFAULT NULL,
  `remarks` varchar(255) DEFAULT NULL,
  `present_days` int DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_attendance` (`emp_id`,`attendance_date`)
) ENGINE=InnoDB AUTO_INCREMENT=120001 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `employee_bank_details`
--

-- DROP TABLE IF EXISTS `employee_bank_details`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `employee_bank_details` (
  `id` int NOT NULL,
  `emp_id` varchar(50) NOT NULL,
  `bank_name` varchar(100) DEFAULT 'Bank of America',
  `bank_account_num` varchar(50) DEFAULT '0000000000',
  `ifsc_code` varchar(20) DEFAULT 'BOFA0000001',
  `created_by` varchar(100) DEFAULT 'System',
  `created_on` datetime DEFAULT CURRENT_TIMESTAMP,
  `modified_by` varchar(100) DEFAULT 'System',
  `modified_on` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `is_active` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `emp_id` (`emp_id`),
  CONSTRAINT `employee_bank_details_ibfk_1` FOREIGN KEY (`emp_id`) REFERENCES `employees` (`emp_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `employee_emails`
--

-- DROP TABLE IF EXISTS `employee_emails`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `employee_emails` (
  `id` int NOT NULL,
  `emp_id` varchar(50) NOT NULL,
  `sender_email` varchar(100) DEFAULT 'admin@maxworth.com',
  `receiver_email` varchar(100) DEFAULT NULL,
  `sent_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `subject` varchar(255) DEFAULT NULL,
  `body` text,
  `response_received_at` datetime DEFAULT NULL,
  `response_notes` text,
  `status` varchar(20) DEFAULT 'Sent',
  `created_by` varchar(100) DEFAULT 'System',
  `created_on` datetime DEFAULT CURRENT_TIMESTAMP,
  `modified_by` varchar(100) DEFAULT 'System',
  `modified_on` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `is_active` tinyint(1) DEFAULT '1',
  `official_email` varchar(100) DEFAULT NULL,
  `emails_sent` int DEFAULT '0',
  `emails_received` int DEFAULT '0',
  `avg_response_time` decimal(5,2) DEFAULT '0.00',
  `last_activity` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `emp_id` (`emp_id`),
  CONSTRAINT `employee_emails_ibfk_1` FOREIGN KEY (`emp_id`) REFERENCES `employees` (`emp_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `employee_financial_components`
--

-- DROP TABLE IF EXISTS `employee_financial_components`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `employee_financial_components` (
  `id` int NOT NULL,
  `emp_id` varchar(50) NOT NULL,
  `component_name` varchar(100) NOT NULL,
  `component_code` tinyint NOT NULL COMMENT '1 for Allowance, 2 for Deduction',
  `amount` decimal(12,2) DEFAULT '0.00',
  `created_by` varchar(100) DEFAULT 'System',
  `created_on` datetime DEFAULT CURRENT_TIMESTAMP,
  `modified_by` varchar(100) DEFAULT 'System',
  `modified_on` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `is_active` tinyint(1) DEFAULT '1',
  `Cname` varchar(100) DEFAULT 'System',
  `CreatedBy` varchar(100) DEFAULT 'System',
  `CreatedOn` datetime DEFAULT CURRENT_TIMESTAMP,
  `Mname` varchar(100) DEFAULT NULL,
  `ModifiedBy` varchar(100) DEFAULT NULL,
  `ModifiedOn` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  `IActive` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`id`),
  KEY `emp_id` (`emp_id`),
  CONSTRAINT `employee_financial_components_ibfk_1` FOREIGN KEY (`emp_id`) REFERENCES `employees` (`emp_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `employee_holidays`
--

-- DROP TABLE IF EXISTS `employee_holidays`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `employee_holidays` (
  `id` int NOT NULL,
  `emp_id` varchar(50) NOT NULL,
  `holiday_code` tinyint NOT NULL COMMENT 'Codes: 0=Present, 1=Casual Leave, 2=Sick Leave, 3=Paid Holiday, 4=Absent',
  `holiday_name` varchar(50) DEFAULT NULL,
  `created_by` varchar(100) DEFAULT 'System',
  `created_on` datetime DEFAULT CURRENT_TIMESTAMP,
  `modified_by` varchar(100) DEFAULT 'System',
  `modified_on` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `is_active` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`id`),
  KEY `emp_id` (`emp_id`),
  CONSTRAINT `employee_holidays_ibfk_1` FOREIGN KEY (`emp_id`) REFERENCES `employees` (`emp_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `employees`
--

-- DROP TABLE IF EXISTS `employees`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `employees` (
  `id` int NOT NULL,
  `emp_id` varchar(50) NOT NULL,
  `emp_name` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `date_of_birth` date NOT NULL,
  `joining_date` date NOT NULL,
  `basic_salary` decimal(10,2) NOT NULL,
  `age` int NOT NULL,
  `gender` varchar(20) DEFAULT 'Male',
  `education` int DEFAULT '2' COMMENT '0=High School, 1=Diploma, 2=Bachelor''s, 3=Master''s, 4=PhD',
  `title` varchar(100) DEFAULT 'Software Engineer',
  `department` varchar(100) DEFAULT 'General Affairs',
  `posting_location` varchar(100) DEFAULT 'Bangalore',
  `payment_tier` int NOT NULL COMMENT '1=Executive, 2=Professional, 3=Associate',
  `phone_number` varchar(20) DEFAULT NULL,
  `created_by` varchar(100) DEFAULT 'System',
  `created_on` datetime DEFAULT CURRENT_TIMESTAMP,
  `modified_by` varchar(100) DEFAULT 'System',
  `modified_on` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `is_active` tinyint(1) DEFAULT '1',
  `location_code` int DEFAULT NULL,
  `department_code` int DEFAULT NULL,
  `designation_code` int DEFAULT NULL,
  `uan_number` varchar(50) DEFAULT NULL,
  `employment_type` varchar(50) DEFAULT 'Permanent',
  PRIMARY KEY (`id`),
  UNIQUE KEY `emp_id` (`emp_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `financial_component_master`
--

-- DROP TABLE IF EXISTS `financial_component_master`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `financial_component_master` (
  `component_id` int NOT NULL AUTO_INCREMENT,
  `component_name` varchar(100) NOT NULL,
  `component_code` tinyint NOT NULL COMMENT '1 for Allowance, 2 for Deduction',
  `Cname` varchar(100) DEFAULT 'System',
  `CreatedBy` varchar(100) DEFAULT 'System',
  `CreatedOn` datetime DEFAULT CURRENT_TIMESTAMP,
  `Mname` varchar(100) DEFAULT NULL,
  `ModifiedBy` varchar(100) DEFAULT NULL,
  `ModifiedOn` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  `IActive` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`component_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `holiday_master`
--

-- DROP TABLE IF EXISTS `holiday_master`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `holiday_master` (
  `holiday_code` int NOT NULL,
  `holiday_name` varchar(100) DEFAULT NULL,
  `created_by` varchar(100) DEFAULT 'System',
  `created_on` datetime DEFAULT CURRENT_TIMESTAMP,
  `modified_by` varchar(100) DEFAULT 'System',
  `modified_on` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `is_active` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`holiday_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `location_master`
--

-- DROP TABLE IF EXISTS `location_master`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `location_master` (
  `location_code` int NOT NULL,
  `location_name` varchar(100) DEFAULT NULL,
  `created_by` varchar(100) DEFAULT 'System',
  `created_on` datetime DEFAULT CURRENT_TIMESTAMP,
  `modified_by` varchar(100) DEFAULT 'System',
  `modified_on` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `is_active` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`location_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `payroll_snapshots`
--

-- DROP TABLE IF EXISTS `payroll_snapshots`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `payroll_snapshots` (
  `snapshot_id` int NOT NULL AUTO_INCREMENT,
  `company_id` int DEFAULT '1',
  `emp_id` varchar(50) DEFAULT NULL,
  `month` varchar(20) DEFAULT NULL,
  `year` int DEFAULT NULL,
  `basic_salary` decimal(10,2) DEFAULT '0.00',
  `hra` decimal(10,2) DEFAULT '0.00',
  `bonus` decimal(10,2) DEFAULT '0.00',
  `pf` decimal(10,2) DEFAULT '0.00',
  `tax` decimal(10,2) DEFAULT '0.00',
  `net_salary` decimal(10,2) DEFAULT '0.00',
  `status` varchar(50) DEFAULT 'Locked',
  `generated_on` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`snapshot_id`),
  KEY `company_id` (`company_id`),
  CONSTRAINT `payroll_snapshots_ibfk_1` FOREIGN KEY (`company_id`) REFERENCES `company_master` (`company_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `payslip_master`
--

-- DROP TABLE IF EXISTS `payslip_master`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `payslip_master` (
  `payslip_id` int NOT NULL,
  `payslip_no` varchar(20) DEFAULT NULL,
  `emp_id` varchar(50) NOT NULL,
  `salary_month` varchar(20) DEFAULT NULL,
  `salary_year` int DEFAULT NULL,
  `basic_salary` decimal(12,2) DEFAULT '0.00',
  `total_allowance` decimal(12,2) DEFAULT '0.00',
  `total_deduction` decimal(12,2) DEFAULT '0.00',
  `final_in_hand_salary` decimal(12,2) DEFAULT '0.00',
  `generated_on` datetime DEFAULT CURRENT_TIMESTAMP,
  `created_by` varchar(100) DEFAULT 'System',
  `created_on` datetime DEFAULT CURRENT_TIMESTAMP,
  `modified_by` varchar(100) DEFAULT 'System',
  `modified_on` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `is_active` tinyint(1) DEFAULT '1',
  `Cname` varchar(100) DEFAULT 'System',
  `CreatedBy` varchar(100) DEFAULT 'System',
  `CreatedOn` datetime DEFAULT CURRENT_TIMESTAMP,
  `Mname` varchar(100) DEFAULT NULL,
  `ModifiedBy` varchar(100) DEFAULT NULL,
  `ModifiedOn` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  `IActive` tinyint(1) DEFAULT '1',
  `working_days` int DEFAULT '0',
  `present_days` int DEFAULT '0',
  PRIMARY KEY (`payslip_id`),
  UNIQUE KEY `payslip_no` (`payslip_no`),
  KEY `emp_id` (`emp_id`),
  CONSTRAINT `payslip_master_ibfk_1` FOREIGN KEY (`emp_id`) REFERENCES `employees` (`emp_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `payslip_template_audit_log`
--

-- DROP TABLE IF EXISTS `payslip_template_audit_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `payslip_template_audit_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `template_id` int DEFAULT NULL,
  `version_number` int DEFAULT NULL,
  `action_type` varchar(50) DEFAULT NULL,
  `user_id` int DEFAULT NULL,
  `action_time` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `payslip_template_versions`
--

-- DROP TABLE IF EXISTS `payslip_template_versions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `payslip_template_versions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `template_id` int DEFAULT NULL,
  `version_number` int DEFAULT NULL,
  `published_by` int DEFAULT NULL,
  `published_on` datetime DEFAULT CURRENT_TIMESTAMP,
  `change_notes` text,
  `layout_json` longtext,
  PRIMARY KEY (`id`),
  KEY `template_id` (`template_id`),
  CONSTRAINT `payslip_template_versions_ibfk_1` FOREIGN KEY (`template_id`) REFERENCES `payslip_templates` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `payslip_templates`
--

-- DROP TABLE IF EXISTS `payslip_templates`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `payslip_templates` (
  `id` int NOT NULL AUTO_INCREMENT,
  `template_name` varchar(100) NOT NULL,
  `version` int DEFAULT '1',
  `is_default` tinyint(1) DEFAULT '0',
  `layout_json` longtext,
  `status` varchar(20) DEFAULT 'Draft',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `company_id` int DEFAULT '1',
  `formulas_json` longtext,
  `Cname` varchar(100) DEFAULT 'System',
  `CreatedBy` varchar(100) DEFAULT 'System',
  `CreatedOn` datetime DEFAULT CURRENT_TIMESTAMP,
  `Mname` varchar(100) DEFAULT NULL,
  `ModifiedBy` varchar(100) DEFAULT NULL,
  `ModifiedOn` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  `IActive` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `upload_staging`
--

-- DROP TABLE IF EXISTS `upload_staging`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `upload_staging` (
  `id` int NOT NULL,
  `upload_batch_id` varchar(50) NOT NULL,
  `employee_id` varchar(50) DEFAULT NULL,
  `name` varchar(100) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `status` varchar(20) DEFAULT NULL COMMENT 'NEW, EXISTING, INVALID',
  `raw_json` text,
  `created_on` datetime DEFAULT CURRENT_TIMESTAMP,
  `Cname` varchar(100) DEFAULT 'System',
  `CreatedBy` varchar(100) DEFAULT 'System',
  `CreatedOn` datetime DEFAULT CURRENT_TIMESTAMP,
  `Mname` varchar(100) DEFAULT NULL,
  `ModifiedBy` varchar(100) DEFAULT NULL,
  `ModifiedOn` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  `IActive` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_login_logs`
--

-- DROP TABLE IF EXISTS `user_login_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `user_login_logs` (
  `log_id` int NOT NULL,
  `user_id` int NOT NULL,
  `login_time` datetime DEFAULT CURRENT_TIMESTAMP,
  `logout_time` datetime DEFAULT NULL,
  `ip_address` varchar(45) DEFAULT NULL,
  `browser` varchar(255) DEFAULT NULL,
  `device` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`log_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `user_login_logs_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `users`
--

-- DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `users` (
  `user_id` int NOT NULL,
  `employee_id` varchar(50) DEFAULT NULL,
  `username` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `role` varchar(20) DEFAULT 'Employee' COMMENT 'Admin, HR, Employee',
  `is_active` tinyint(1) DEFAULT '1',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `last_login` datetime DEFAULT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `employee_id` (`employee_id`),
  CONSTRAINT `users_ibfk_1` FOREIGN KEY (`employee_id`) REFERENCES `employees` (`emp_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary view structure for view `v_employees`
--

-- DROP TABLE IF EXISTS `v_employees`;
/*!50001 DROP VIEW IF EXISTS `v_employees`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_employees` AS SELECT 
 1 AS `id`,
 1 AS `emp_id`,
 1 AS `emp_name`,
 1 AS `email`,
 1 AS `date_of_birth`,
 1 AS `joining_date`,
 1 AS `basic_salary`,
 1 AS `age`,
 1 AS `gender`,
 1 AS `education`,
 1 AS `payment_tier`,
 1 AS `phone_number`,
 1 AS `location_code`,
 1 AS `department_code`,
 1 AS `designation_code`,
 1 AS `uan_number`,
 1 AS `employment_type`,
 1 AS `posting_location`,
 1 AS `department`,
 1 AS `title`*/;
SET character_set_client = @saved_cs_client;

--
-- Final view structure for view `v_employees`
--

/*!50001 DROP VIEW IF EXISTS `v_employees`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_employees` AS select `e`.`id` AS `id`,`e`.`emp_id` AS `emp_id`,`e`.`emp_name` AS `emp_name`,`e`.`email` AS `email`,`e`.`date_of_birth` AS `date_of_birth`,`e`.`joining_date` AS `joining_date`,`e`.`basic_salary` AS `basic_salary`,`e`.`age` AS `age`,`e`.`gender` AS `gender`,`e`.`education` AS `education`,`e`.`payment_tier` AS `payment_tier`,`e`.`phone_number` AS `phone_number`,`e`.`location_code` AS `location_code`,`e`.`department_code` AS `department_code`,`e`.`designation_code` AS `designation_code`,`e`.`uan_number` AS `uan_number`,`e`.`employment_type` AS `employment_type`,coalesce(`l`.`location_name`,`e`.`posting_location`) AS `posting_location`,coalesce(`d`.`department_name`,`e`.`department`) AS `department`,coalesce(`des`.`designation_name`,`e`.`title`) AS `title` from (((`employee` `e` left join `location_master` `l` on((`e`.`location_code` = `l`.`location_code`))) left join `department_master` `d` on((`e`.`department_code` = `d`.`department_code`))) left join `designation_master` `des` on((`e`.`designation_code` = `des`.`designation_code`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-06-16 11:36:12
