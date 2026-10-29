-- MySQL dump 10.13  Distrib 8.0.40, for macos14 (arm64)
--
-- Host: localhost    Database: company_db
-- ------------------------------------------------------
-- Server version	8.0.40

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
-- Dumping data for table `departments`
--

/*!40000 ALTER TABLE `departments` DISABLE KEYS */;
INSERT INTO `departments` VALUES (1,'Information Technology','Chicago'),(2,'Human Resources','New York'),(3,'Finance','Dallas'),(4,'Data Engineering','Seattle'),(5,'Quality Assurance','Austin');
/*!40000 ALTER TABLE `departments` ENABLE KEYS */;

--
-- Dumping data for table `employees`
--

/*!40000 ALTER TABLE `employees` DISABLE KEYS */;
INSERT INTO `employees` VALUES (101,'Arjun','Reddy','arjun@company.com',28,4,'2024-01-15','Data Engineer'),(102,'Priya','Sharma','priya@company.com',30,1,'2023-06-10','Software Developer'),(103,'Rahul','Verma','rahul@company.com',27,5,'2024-03-20','QA Engineer'),(104,'Sneha','Patel','sneha@company.com',32,2,'2022-09-05','HR Manager'),(105,'Vikram','Singh','vikram@company.com',35,3,'2021-11-12','Financial Analyst'),(106,'Ananya','Rao','ananya@company.com',26,4,'2025-02-01','Junior Data Engineer'),(107,'Karan','Mehta','karan@company.com',29,1,'2023-08-18','Backend Developer'),(108,'Divya','Nair','divya@company.com',31,5,'2022-04-25','QA Lead'),(109,'Rohit','Kumar','rohit@company.com',33,3,'2023-01-09','Accountant'),(110,'Meera','Iyer','meera@company.com',28,4,'2024-07-22','Data Analyst');
/*!40000 ALTER TABLE `employees` ENABLE KEYS */;

--
-- Dumping data for table `salaries`
--

/*!40000 ALTER TABLE `salaries` DISABLE KEYS */;
INSERT INTO `salaries` VALUES (1,101,120000.00,10000.00,'2026-01-01'),(2,102,110000.00,8000.00,'2026-01-01'),(3,103,90000.00,5000.00,'2026-01-01'),(4,104,95000.00,7000.00,'2026-01-01'),(5,105,115000.00,9000.00,'2026-01-01'),(6,106,85000.00,4000.00,'2026-01-01'),(7,107,105000.00,7500.00,'2026-01-01'),(8,108,125000.00,12000.00,'2026-01-01'),(9,109,98000.00,6000.00,'2026-01-01'),(10,110,92000.00,5500.00,'2026-01-01');
/*!40000 ALTER TABLE `salaries` ENABLE KEYS */;

--
-- Dumping data for table `projects`
--

/*!40000 ALTER TABLE `projects` DISABLE KEYS */;
INSERT INTO `projects` VALUES (201,'Cloud Migration',1,'2026-01-10','2026-12-31','In Progress'),(202,'Data Warehouse Development',4,'2026-02-01','2026-11-30','In Progress'),(203,'Automation Testing',5,'2026-03-01','2026-10-31','In Progress'),(204,'Financial Reporting',3,'2026-01-15','2026-09-30','Completed'),(205,'HR Management System',2,'2026-04-01','2027-03-31','In Progress');
/*!40000 ALTER TABLE `projects` ENABLE KEYS */;

--
-- Dumping data for table `employee_projects`
--

/*!40000 ALTER TABLE `employee_projects` DISABLE KEYS */;
INSERT INTO `employee_projects` VALUES (101,202,'2026-02-01','Lead Data Engineer'),(102,201,'2026-01-10','Software Developer'),(103,203,'2026-03-01','QA Engineer'),(104,205,'2026-04-01','Project Manager'),(105,204,'2026-01-15','Financial Analyst'),(106,202,'2026-02-05','Data Engineer'),(107,201,'2026-01-15','Backend Developer'),(108,203,'2026-03-01','QA Lead'),(109,204,'2026-01-20','Accountant'),(110,202,'2026-02-10','Data Analyst');
/*!40000 ALTER TABLE `employee_projects` ENABLE KEYS */;

--
-- Dumping data for table `attendance`
--

/*!40000 ALTER TABLE `attendance` DISABLE KEYS */;
INSERT INTO `attendance` VALUES (1,101,'2026-10-26','Present','09:00:00','17:30:00'),(2,102,'2026-10-26','Present','09:15:00','18:00:00'),(3,103,'2026-10-26','Absent',NULL,NULL),(4,104,'2026-10-26','Present','08:45:00','17:00:00'),(5,105,'2026-10-26','Present','09:30:00','18:15:00'),(6,101,'2026-10-27','Present','09:05:00','17:45:00'),(7,102,'2026-10-27','Present','09:10:00','17:30:00'),(8,103,'2026-10-27','Present','09:00:00','17:00:00'),(9,104,'2026-10-27','On Leave',NULL,NULL),(10,105,'2026-10-27','Present','09:20:00','18:00:00');
/*!40000 ALTER TABLE `attendance` ENABLE KEYS */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-10-29 11:41:58
