SET FOREIGN_KEY_CHECKS=0;

CREATE TABLE `attendance` (
  `attendance_id` int NOT NULL,
  `employee_id` int DEFAULT NULL,
  `attendance_date` date DEFAULT NULL,
  `status` varchar(20) DEFAULT NULL,
  `check_in` time DEFAULT NULL,
  `check_out` time DEFAULT NULL,
  PRIMARY KEY (`attendance_id`),
  KEY `employee_id` (`employee_id`),
  CONSTRAINT `attendance_ibfk_1` FOREIGN KEY (`employee_id`) REFERENCES `employees` (`employee_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `data_quality_results` (
  `check_id` int NOT NULL AUTO_INCREMENT,
  `check_name` varchar(100) NOT NULL,
  `check_status` varchar(20) NOT NULL,
  `issue_count` int NOT NULL,
  `checked_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`check_id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `departments` (
  `department_id` int NOT NULL,
  `department_name` varchar(100) NOT NULL,
  `location` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`department_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `employee_projects` (
  `employee_id` int NOT NULL,
  `project_id` int NOT NULL,
  `assigned_date` date DEFAULT NULL,
  `role` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`employee_id`,`project_id`),
  KEY `project_id` (`project_id`),
  CONSTRAINT `employee_projects_ibfk_1` FOREIGN KEY (`employee_id`) REFERENCES `employees` (`employee_id`),
  CONSTRAINT `employee_projects_ibfk_2` FOREIGN KEY (`project_id`) REFERENCES `projects` (`project_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `employee_salary_analytics` (
  `employee_id` int NOT NULL,
  `employee_name` varchar(150) NOT NULL,
  `job_title` varchar(100) DEFAULT NULL,
  `department_name` varchar(100) NOT NULL,
  `location` varchar(100) DEFAULT NULL,
  `salary_amount` decimal(12,2) NOT NULL,
  `bonus` decimal(12,2) NOT NULL DEFAULT '0.00',
  `total_compensation` decimal(12,2) NOT NULL,
  `last_updated` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`employee_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `employees` (
  `employee_id` int NOT NULL,
  `first_name` varchar(50) NOT NULL,
  `last_name` varchar(50) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `age` int DEFAULT NULL,
  `department_id` int DEFAULT NULL,
  `hire_date` date DEFAULT NULL,
  `job_title` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`employee_id`),
  UNIQUE KEY `email` (`email`),
  KEY `department_id` (`department_id`),
  CONSTRAINT `employees_ibfk_1` FOREIGN KEY (`department_id`) REFERENCES `departments` (`department_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `etl_pipeline_runs` (
  `run_id` int NOT NULL AUTO_INCREMENT,
  `pipeline_name` varchar(100) NOT NULL,
  `start_time` datetime NOT NULL,
  `end_time` datetime DEFAULT NULL,
  `status` varchar(20) NOT NULL,
  `extracted_records` int DEFAULT '0',
  `loaded_records` int DEFAULT '0',
  `execution_seconds` decimal(10,3) DEFAULT NULL,
  `error_message` text,
  PRIMARY KEY (`run_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `projects` (
  `project_id` int NOT NULL,
  `project_name` varchar(100) DEFAULT NULL,
  `department_id` int DEFAULT NULL,
  `start_date` date DEFAULT NULL,
  `end_date` date DEFAULT NULL,
  `project_status` varchar(30) DEFAULT NULL,
  PRIMARY KEY (`project_id`),
  KEY `department_id` (`department_id`),
  CONSTRAINT `projects_ibfk_1` FOREIGN KEY (`department_id`) REFERENCES `departments` (`department_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `salaries` (
  `salary_id` int NOT NULL,
  `employee_id` int DEFAULT NULL,
  `salary_amount` decimal(10,2) DEFAULT NULL,
  `bonus` decimal(10,2) DEFAULT NULL,
  `effective_date` date DEFAULT NULL,
  PRIMARY KEY (`salary_id`),
  KEY `employee_id` (`employee_id`),
  CONSTRAINT `salaries_ibfk_1` FOREIGN KEY (`employee_id`) REFERENCES `employees` (`employee_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

SET FOREIGN_KEY_CHECKS=1;


-- Incremental ETL checkpoint table

CREATE TABLE IF NOT EXISTS etl_checkpoints (
    pipeline_name VARCHAR(100) PRIMARY KEY,
    last_processed_timestamp DATETIME(6),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP
);

-- Initialize checkpoint for GitHub Actions tests

INSERT INTO etl_checkpoints (
    pipeline_name,
    last_processed_timestamp
)
VALUES (
    'Employee Incremental ETL',
    '2026-10-29 00:00:00.000000'
)
ON DUPLICATE KEY UPDATE
    pipeline_name = VALUES(pipeline_name);

