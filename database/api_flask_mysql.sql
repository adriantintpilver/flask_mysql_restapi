-- Data base scripts

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "-03:00";
--
-- Base de datos: `globantdatastudy`
--
-- --------------------------------------------------------
    CREATE DATABASE IF NOT EXISTS `globantdatastudy`;
        
    USE globantdatastudy;
        --
        -- Table departments script
        --
        CREATE TABLE IF NOT EXISTS `departments` (
          `id` INT  AUTO_INCREMENT PRIMARY KEY NOT NULL,
          `department` varchar(100) NOT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=UTF8MB4 COMMENT='table for departments.';
        --
        -- Table jobs script
        --
        CREATE TABLE IF NOT EXISTS `jobs` (
          `id` INT  AUTO_INCREMENT PRIMARY KEY NOT NULL,
          `job` varchar(100) NOT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=UTF8MB4 COMMENT='table for jobs.';
        --
        -- Table hired_employees script
        --
        CREATE TABLE `hired_employees` (
          `id` int NOT NULL,
          `name` varchar(100) NOT NULL,
          `datetime` varchar(20) NOT NULL,
          `department_id` int NOT NULL,
          `job_id` int NOT NULL,
          PRIMARY KEY (`id`),
          KEY `fk_hired_employees_jobs` (`job_id`),
          KEY `fk_hired_employees_departments` (`department_id`),
          CONSTRAINT `fk_hired_employees_departments` FOREIGN KEY (`department_id`) REFERENCES `departments` (`id`),
          CONSTRAINT `fk_hired_employees_jobs` FOREIGN KEY (`job_id`) REFERENCES `jobs` (`id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='table for hired employees.';
        --
        -- Stored procedure to truncate all tables in the backup restore feature
        --
        DROP procedure IF EXISTS `truncate_all`;
        DELIMITER $$
        USE `globantdatastudy`$$
        CREATE PROCEDURE `truncate_all` ()
        BEGIN
          TRUNCATE TABLE globantdatastudy.hired_employees;
          SET FOREIGN_KEY_CHECKS = 0;
          TRUNCATE TABLE globantdatastudy.departments;
          TRUNCATE TABLE globantdatastudy.jobs;
          SET FOREIGN_KEY_CHECKS = 1;
        END$$

        DELIMITER ;
        --
        -- Stored procedure to count by Q hires employees by department and job 
        --
         DROP procedure IF EXISTS `hires_by_Q_for_year`;
        
        DELIMITER $$
        
        CREATE PROCEDURE `hires_by_Q_for_year`(IN year INT)
        BEGIN
          SELECT  D.department, J.job,
              COUNT(CASE WHEN QUARTER(HE.datetime) = 1 THEN 0 ELSE NULL END) 'Q1',
              COUNT(CASE WHEN QUARTER(HE.datetime) = 2 THEN 0 ELSE NULL END) 'Q2',
              COUNT(CASE WHEN QUARTER(HE.datetime) = 3 THEN 0 ELSE NULL END) 'Q3',
              COUNT(CASE WHEN QUARTER(HE.datetime) = 4 THEN 0 ELSE NULL END) 'Q4'
          FROM globantdatastudy.hired_employees as HE
          inner join globantdatastudy.departments as D on D.id = HE.department_id 
          inner join globantdatastudy.jobs as J on J.id = HE.job_id 
          where YEAR(HE.datetime) = YEAR
          GROUP BY HE.department_id, HE.job_id
          ORDER BY D.department, J.job;
        END
        
        DELIMITER ;