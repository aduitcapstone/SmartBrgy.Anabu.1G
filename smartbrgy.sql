SET sql_require_primary_key = 0;
SET FOREIGN_KEY_CHECKS = 0;
SET sql_require_primary_key = 0;
-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: May 09, 2026 at 09:57 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `smartbrgy`
--

-- --------------------------------------------------------

--
-- Table structure for table `audit_log`
--

CREATE TABLE `audit_log` (
  `id` int(11) NOT NULL,
  `icon` varchar(100) DEFAULT NULL,
  `category` varchar(100) DEFAULT NULL,
  `action` varchar(500) NOT NULL,
  `detail` text DEFAULT NULL,
  `user` varchar(255) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `audit_log`
--

INSERT INTO `audit_log` (`id`, `icon`, `category`, `action`, `detail`, `user`, `created_at`) VALUES
(1, '🔐', 'auth', 'Login - Credentials', 'System login - Super Administrator access granted', 'Admin', '2026-05-09 21:01:44'),
(2, 'zone', 'record', 'Purok Added', 'Sitio Sto.NIno Phase 1', 'Staff', '2026-05-09 21:02:08'),
(3, '🏘️', 'record', 'Purok Added', 'Sitio Sto.NIno Phase 1 — Sitio Sto.NIno Phase 1', 'Staff', '2026-05-09 21:02:08'),
(4, 'zone', 'record', 'Purok Added', 'Sitio Sto.Nino Phase 2', 'Staff', '2026-05-09 21:02:38'),
(5, '🏘️', 'record', 'Purok Added', 'Sitio Sto.Nino Phase 2 — Sitio Sto.Nino Phase 2', 'Staff', '2026-05-09 21:02:39'),
(6, '✏️', 'auth', 'User Updated', 'Robin Silla — USR-001', 'Admin', '2026-05-09 21:22:05'),
(7, '✏️', 'auth', 'User Updated', 'Robin Silla — Barangay Captain — USR-001', 'Admin', '2026-05-09 21:22:05'),
(8, 'zone', 'record', 'Purok Added', 'Silla Compound', 'Staff', '2026-05-09 21:58:00'),
(9, '🏘️', 'record', 'Purok Added', 'Silla Compound — Silla Compound', 'Staff', '2026-05-09 21:58:01'),
(10, 'zone', 'record', 'Purok Added', 'Northfield Subdivision', 'Staff', '2026-05-09 21:58:20'),
(11, '🏘️', 'record', 'Purok Added', 'Northfield Subdivision — Northfield Subdivision', 'Staff', '2026-05-09 21:58:21'),
(12, 'zone', 'record', 'Purok Added', 'Appletown Subdivision', 'Staff', '2026-05-09 21:58:45'),
(13, '🏘️', 'record', 'Purok Added', 'Appletown Subdivision — Appletown Subdivision', 'Staff', '2026-05-09 21:58:46'),
(14, '✏️', 'record', 'Purok Updated', 'Appletown Subdivision → Appletown Subd.', 'Staff', '2026-05-09 21:58:59'),
(15, '✏️', 'record', 'Purok Updated', 'Appletown Subdivision', 'Staff', '2026-05-09 21:59:00'),
(16, 'zone', 'record', 'Purok Added', 'Ragatan Proper', 'Staff', '2026-05-09 21:59:28'),
(17, '🏘️', 'record', 'Purok Added', 'Ragatan Proper — Ragatan Proper', 'Staff', '2026-05-09 21:59:28'),
(18, '✏️', 'record', 'Purok Updated', 'Ragatan Proper → Ragatan Proper', 'Staff', '2026-05-09 21:59:48'),
(19, '✏️', 'record', 'Purok Updated', 'Ragatan Proper', 'Staff', '2026-05-09 21:59:48'),
(20, '🧑', 'record', 'New Resident Registered', 'Ramirez Kyan — ANB-A994D9FA', 'Staff', '2026-05-09 22:00:50'),
(21, '🧑', 'record', 'New Resident Registered', 'Janelle Santos — ANB-C7E66D02', 'Staff', '2026-05-09 22:01:44'),
(22, '🧑', 'record', 'New Resident Registered', 'Rodolfo Manaloto — ANB-B62958DE', 'Staff', '2026-05-09 22:02:57'),
(23, '🧑', 'record', 'New Resident Registered', 'Ramon Cruz — ANB-3A1D61B4', 'Staff', '2026-05-09 22:04:00'),
(24, '🧑', 'record', 'New Resident Registered', 'Kyan Ramirez — ANB-5ACF1C97', 'Staff', '2026-05-09 22:04:54'),
(25, '🧑', 'record', 'New Resident Registered', 'Amy Narvasa — ANB-AA559E78', 'Staff', '2026-05-09 22:06:10'),
(26, '📨', 'cert', 'Certificate Request Submitted', 'REQ-2026-0001 — Kyan ramirez — Certificate of Residency', 'Online', '2026-05-09 22:37:42'),
(27, '🚨', 'incident', 'Incident Report Filed', 'INC-2026-001 — Physical Assault', 'Ramon Cruz', '2026-05-09 22:41:49'),
(28, '🚨', 'incident', 'Incident Report Filed', 'INC-2026-001 — Physical Assault', 'Staff', '2026-05-09 22:41:49'),
(29, '✏️', 'incident', 'Incident Report Updated', 'INC-2026-001', 'Staff', '2026-05-09 22:42:22'),
(30, '✏️', 'incident', 'Incident Report Updated', 'INC-2026-001', 'Staff', '2026-05-09 22:42:22'),
(31, '📨', 'cert', 'Certificate Request Submitted', 'REQ-2026-0002 — Maverick Jan marquez — Certificate of Residency', 'Online', '2026-05-09 22:44:07'),
(32, '✏️', 'incident', 'Incident Report Updated', 'INC-2026-001', 'Staff', '2026-05-09 22:48:14'),
(33, '✏️', 'incident', 'Incident Report Updated', 'INC-2026-001', 'Staff', '2026-05-09 22:48:14'),
(34, '✏️', 'incident', 'Incident Report Updated', 'INC-2026-001', 'Staff', '2026-05-09 22:54:51'),
(35, '✏️', 'incident', 'Incident Report Updated', 'INC-2026-001', 'Staff', '2026-05-09 22:54:52'),
(36, '👤', 'auth', 'New User Created', 'Kyan Ramirez — Data Encoder — USR-002', 'Admin', '2026-05-09 22:58:40'),
(37, '👤', 'auth', 'New User Created', 'Kyan Ramirez — Data Encoder — USR-002', 'Admin', '2026-05-09 22:58:41'),
(38, '👤', 'auth', 'New User Created', 'Maverick Jan Marquez — Tanod Captain — USR-003', 'Admin', '2026-05-09 22:59:13'),
(39, '👤', 'auth', 'New User Created', 'Maverick Jan Marquez — Tanod Captain — USR-003', 'Admin', '2026-05-09 22:59:13'),
(40, '👤', 'auth', 'New User Created', 'Mark  Justin Manalac — Barangay Clerk — USR-004', 'Admin', '2026-05-09 23:00:04'),
(41, '👤', 'auth', 'New User Created', 'Mark  Justin Manalac — Barangay Clerk — USR-004', 'Admin', '2026-05-09 23:00:04'),
(42, '✏️', 'incident', 'Incident Report Updated', 'INC-2026-001', 'Staff', '2026-05-09 23:01:03'),
(43, '✏️', 'incident', 'Incident Report Updated', 'INC-2026-001', 'Staff', '2026-05-09 23:01:03'),
(44, '🔍', 'cert', 'Eligibility Check', 'Kyan Ramirez — Barangay Clearance — ELIGIBLE', 'Staff', '2026-05-09 23:02:31'),
(45, '🔍', 'cert', 'Eligibility Check', 'Kyan Ramirez — Barangay Clearance — ELIGIBLE', 'Staff', '2026-05-09 23:07:48'),
(46, '📨', 'cert', 'Certificate Request Submitted', 'REQ-2026-0003 — Kyan Ramirez — Certificate of Residency', 'Walk-in', '2026-05-09 23:07:52'),
(47, '📨', 'cert', 'Certificate Request Created', 'REQ-2026-0003 — Kyan Ramirez — Certificate of Residency', 'Staff', '2026-05-09 23:07:53'),
(48, '🔍', 'cert', 'Eligibility Check', 'Kyan Ramirez — Certificate of Indigency — ELIGIBLE', 'Staff', '2026-05-09 23:07:59'),
(49, '📨', 'cert', 'Certificate Request Submitted', 'REQ-2026-0004 — Kyan Ramirez — Barangay Clearance', 'Walk-in', '2026-05-09 23:08:16'),
(50, '📨', 'cert', 'Certificate Request Created', 'REQ-2026-0004 — Kyan Ramirez — Barangay Clearance', 'Staff', '2026-05-09 23:08:17'),
(51, '🗑️', 'cert', 'Certificate Request Removed', 'REQ-2026-0004 — Naalis sa kanban board', 'Staff', '2026-05-09 23:08:25'),
(52, '🔍', 'cert', 'Eligibility Check', 'Janelle Santos — Barangay Clearance — ELIGIBLE', 'Staff', '2026-05-09 23:09:10'),
(53, '📨', 'cert', 'Certificate Request Submitted', 'REQ-2026-0005 — Janelle Santos — Barangay Clearance', 'Walk-in', '2026-05-09 23:09:11'),
(54, '📨', 'cert', 'Certificate Request Created', 'REQ-2026-0005 — Janelle Santos — Barangay Clearance', 'Staff', '2026-05-09 23:09:12'),
(55, '🔍', 'cert', 'Eligibility Check', 'Kyan Ramirez — Barangay Clearance — ELIGIBLE', 'Staff', '2026-05-10 00:13:41'),
(56, '🔐', 'auth', 'Login - Credentials', 'System login - Super Administrator access granted', 'Admin', '2026-05-10 00:23:34'),
(57, '📋', 'cert', 'Certificate Status → Ready to Print', 'REQ-2026-0005 — Janelle Santos', 'Staff', '2026-05-10 00:25:20'),
(58, '📋', 'cert', 'Certificate → Ready to Print', 'REQ-2026-0005', 'Staff', '2026-05-10 00:25:20'),
(59, '🔍', 'cert', 'Eligibility Check', 'Ramon Cruz — First Time Jobseeker — ELIGIBLE', 'Staff', '2026-05-10 00:25:34'),
(60, '📨', 'cert', 'Certificate Request Submitted', 'REQ-2026-0006 — Ramon Cruz — First Time Jobseeker', 'Walk-in', '2026-05-10 00:25:35'),
(61, '📨', 'cert', 'Certificate Request Created', 'REQ-2026-0006 — Ramon Cruz — First Time Jobseeker', 'Staff', '2026-05-10 00:25:36'),
(62, '📋', 'cert', 'Certificate Status → Ready to Print', 'REQ-2026-0003 — Kyan Ramirez', 'Staff', '2026-05-10 00:25:42'),
(63, '📋', 'cert', 'Certificate → Ready to Print', 'REQ-2026-0003', 'Staff', '2026-05-10 00:25:43'),
(64, '📋', 'cert', 'Certificate Status → Completed', 'REQ-2026-0003 — Kyan Ramirez', 'Staff', '2026-05-10 00:25:44'),
(65, '🖨️', 'cert', 'Certificate Printed', 'REQ-2026-0003', 'Staff', '2026-05-10 00:25:44'),
(66, '📨', 'cert', 'Certificate Request Submitted', 'REQ-2026-0007 — Maverick Jan — Barangay Clearance', 'Online', '2026-05-10 00:28:05'),
(67, '🔐', 'auth', 'Login - Credentials', 'System login - Barangay Clerk access granted', 'Mark  Justin Manalac', '2026-05-10 01:01:51'),
(68, '🔐', 'auth', 'Login - Credentials', 'System login - Data Encoder access granted', 'Kyan Ramirez', '2026-05-10 01:02:18'),
(69, '🔐', 'auth', 'Login - Credentials', 'System login - Super Administrator access granted', 'Admin', '2026-05-10 01:02:35'),
(70, '🔐', 'auth', 'Login - Credentials', 'System login - Tanod Captain access granted', 'Maverick Jan Marquez', '2026-05-10 01:03:17'),
(71, '🔐', 'auth', 'Login - Credentials', 'System login - Super Administrator access granted', 'Admin', '2026-05-10 01:03:38'),
(72, '🔍', 'cert', 'Eligibility Check', 'Kyan Ramirez — Barangay Clearance — ELIGIBLE', 'Staff', '2026-05-10 01:06:24'),
(73, '🔍', 'cert', 'Eligibility Check', 'Kyan Ramirez — Barangay Clearance — ELIGIBLE', 'Staff', '2026-05-10 01:22:58'),
(74, '🔍', 'cert', 'Eligibility Check', 'Kyan Ramirez — Barangay Clearance — ELIGIBLE', 'Staff', '2026-05-10 01:34:25'),
(75, '🔍', 'cert', 'Eligibility Check', 'Kyan Ramirez — Certificate of Residency — ELIGIBLE', 'Staff', '2026-05-10 01:34:47'),
(76, '🔍', 'cert', 'Eligibility Check', 'Kyan Ramirez — Barangay Clearance — NOT ELIGIBLE', 'Staff', '2026-05-10 01:48:22'),
(77, '🔍', 'cert', 'Eligibility Check', 'Kyan Ramirez — Barangay Clearance — NOT ELIGIBLE', 'Staff', '2026-05-10 01:48:37'),
(78, '🔍', 'cert', 'Eligibility Check', 'Kyan Ramirez — Barangay ID — ELIGIBLE', 'Staff', '2026-05-10 01:48:43'),
(79, '🔍', 'cert', 'Eligibility Check', 'Kyan Ramirez — Certificate of Residency — ELIGIBLE', 'Staff', '2026-05-10 01:48:52'),
(80, '🔍', 'cert', 'Eligibility Check', 'Kyan Ramirez — Business Clearance — NOT ELIGIBLE', 'Staff', '2026-05-10 01:48:59'),
(81, '🔍', 'cert', 'Eligibility Check', 'Janelle Santos — First Time Jobseeker — ELIGIBLE', 'Staff', '2026-05-10 01:49:32'),
(82, '📨', 'cert', 'Certificate Request Submitted', 'REQ-2026-0008 — Janelle Santos — First Time Jobseeker', 'Walk-in', '2026-05-10 01:49:34'),
(83, '📨', 'cert', 'Certificate Request Created', 'REQ-2026-0008 — Janelle Santos — First Time Jobseeker', 'Staff', '2026-05-10 01:49:35'),
(84, '📋', 'cert', 'Certificate Status → Ready to Print', 'REQ-2026-0008 — Janelle Santos', 'Staff', '2026-05-10 01:49:41'),
(85, '📋', 'cert', 'Certificate → Ready to Print', 'REQ-2026-0008', 'Staff', '2026-05-10 01:49:41'),
(86, '📋', 'cert', 'Certificate Status → Completed', 'REQ-2026-0005 — Janelle Santos', 'Staff', '2026-05-10 01:49:43'),
(87, '🖨️', 'cert', 'Certificate Printed', 'REQ-2026-0005', 'Staff', '2026-05-10 01:49:43'),
(88, '🔍', 'cert', 'Eligibility Check', 'Janelle Santos — First Time Jobseeker — ELIGIBLE', 'Staff', '2026-05-10 01:49:49'),
(89, '🔍', 'cert', 'Eligibility Check', 'Janelle Santos — First Time Jobseeker — ELIGIBLE', 'Staff', '2026-05-10 01:49:51'),
(90, '🔍', 'cert', 'Eligibility Check', 'Janelle Santos — First Time Jobseeker — ELIGIBLE', 'Staff', '2026-05-10 01:49:53'),
(91, '🔍', 'cert', 'Eligibility Check', 'Janelle Santos — First Time Jobseeker — ELIGIBLE', 'Staff', '2026-05-10 01:49:55'),
(92, '🔍', 'cert', 'Eligibility Check', 'Janelle Santos — First Time Jobseeker — ELIGIBLE', 'Staff', '2026-05-10 01:49:56'),
(93, '🔍', 'cert', 'Eligibility Check', 'Janelle Santos — First Time Jobseeker — ELIGIBLE', 'Staff', '2026-05-10 01:49:56'),
(94, '🔍', 'cert', 'Eligibility Check', 'Janelle Santos — First Time Jobseeker — ELIGIBLE', 'Staff', '2026-05-10 01:49:56'),
(95, '🔍', 'cert', 'Eligibility Check', 'Janelle Santos — First Time Jobseeker — ELIGIBLE', 'Staff', '2026-05-10 01:51:45'),
(96, '🔍', 'cert', 'Eligibility Check', 'Janelle Santos — First Time Jobseeker — ELIGIBLE', 'Staff', '2026-05-10 01:56:05'),
(97, '🔍', 'cert', 'Eligibility Check', 'Janelle Santos — First Time Jobseeker — ELIGIBLE', 'Staff', '2026-05-10 01:56:27'),
(98, '📨', 'cert', 'Certificate Request Submitted', 'REQ-2026-0009 — Janelle Santos — First Time Jobseeker', 'Walk-in', '2026-05-10 01:56:29'),
(99, '📨', 'cert', 'Certificate Request Created', 'REQ-2026-0009 — Janelle Santos — First Time Jobseeker', 'Staff', '2026-05-10 01:56:30'),
(100, '📋', 'cert', 'Certificate Status → Ready to Print', 'REQ-2026-0009 — Janelle Santos', 'Staff', '2026-05-10 01:56:36'),
(101, '📋', 'cert', 'Certificate → Ready to Print', 'REQ-2026-0009', 'Staff', '2026-05-10 01:56:37'),
(102, '📋', 'cert', 'Certificate Status → Completed', 'REQ-2026-0008 — Janelle Santos', 'Staff', '2026-05-10 01:56:38'),
(103, '🖨️', 'cert', 'Certificate Printed', 'REQ-2026-0008', 'Staff', '2026-05-10 01:56:39'),
(104, '🔍', 'cert', 'Eligibility Check', 'Janelle Santos — First Time Jobseeker — NOT ELIGIBLE', 'Staff', '2026-05-10 01:56:44'),
(105, '🗑️', 'cert', 'Certificate Request Removed', 'REQ-2026-0008 — Naalis sa kanban board', 'Staff', '2026-05-10 01:58:58'),
(106, '🔍', 'cert', 'Eligibility Check', 'Janelle Santos — First Time Jobseeker — NOT ELIGIBLE', 'Staff', '2026-05-10 01:59:03'),
(107, '🔐', 'auth', 'Login - Credentials', 'System login - Super Administrator access granted', 'Admin', '2026-05-10 02:58:13'),
(108, '📨', 'cert', 'Certificate Request Submitted', 'REQ-2026-0010 — Maverick Jan — Barangay Clearance', 'Online', '2026-05-10 03:45:27');

-- --------------------------------------------------------

--
-- Table structure for table `cabinet_folders`
--

CREATE TABLE `cabinet_folders` (
  `id` varchar(50) NOT NULL,
  `name` varchar(255) NOT NULL,
  `rfid` varchar(50) DEFAULT NULL,
  `drawer` varchar(100) DEFAULT NULL,
  `status` varchar(50) NOT NULL DEFAULT 'In Cabinet'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `cabinet_log`
--

CREATE TABLE `cabinet_log` (
  `id` int(11) NOT NULL,
  `drawer_id` varchar(50) DEFAULT NULL,
  `drawer_label` varchar(255) DEFAULT NULL,
  `action` varchar(255) DEFAULT NULL,
  `user` varchar(255) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `cert_requests`
--

CREATE TABLE `cert_requests` (
  `code` varchar(50) NOT NULL,
  `resident_id` varchar(50) DEFAULT NULL,
  `name` varchar(255) NOT NULL,
  `type` varchar(100) NOT NULL,
  `cert_id` varchar(50) DEFAULT NULL,
  `purpose` text DEFAULT NULL,
  `address` text DEFAULT NULL,
  `contact` varchar(50) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `dob` date DEFAULT NULL,
  `status` varchar(50) NOT NULL DEFAULT 'Processing',
  `via` varchar(50) NOT NULL DEFAULT 'Online',
  `source` varchar(50) NOT NULL DEFAULT 'portal',
  `attachment` text DEFAULT NULL,
  `hidden` tinyint(1) NOT NULL DEFAULT 0,
  `requested` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `cert_requests`
--

INSERT INTO `cert_requests` (`code`, `resident_id`, `name`, `type`, `cert_id`, `purpose`, `address`, `contact`, `email`, `dob`, `status`, `via`, `source`, `attachment`, `hidden`, `requested`) VALUES
('REQ-2026-0001', NULL, 'Kyan ramirez', 'Certificate of Residency', 'CR', 'loan', 'Silla Compound', '', 'yvammmmm@gmail.com', '2005-03-01', 'Processing', 'Online', 'portal', '/uploads/2AA45C94_Screenshot_2026-03-07_111051.png', 0, '2026-05-09 22:37:42'),
('REQ-2026-0002', NULL, 'Maverick Jan marquez', 'Certificate of Residency', 'CR', 'laon', 'Ragatan Compound', '', 'yvammmmm@gmail.com', '2005-03-01', 'Processing', 'Online', 'portal', '/uploads/F9145014_Screenshot_2026-03-07_111051.png', 0, '2026-05-09 22:44:07'),
('REQ-2026-0003', 'ANB-5ACF1C97', 'Kyan Ramirez', 'Certificate of Residency', 'CR', 'Issued via Eligibility Check', 'Appletown Subdivision', '0977743838', '', NULL, 'Completed', 'Walk-in', 'staff', '', 0, '2026-05-09 23:07:52'),
('REQ-2026-0004', 'ANB-5ACF1C97', 'Kyan Ramirez', 'Barangay Clearance', 'BC', 'Issued via Eligibility Check', 'Appletown Subdivision', '0977743838', '', NULL, 'Processing', 'Walk-in', 'staff', '', 1, '2026-05-09 23:08:16'),
('REQ-2026-0005', 'ANB-C7E66D02', 'Janelle Santos', 'Barangay Clearance', 'BC', 'Issued via Eligibility Check', 'Sitio Sto.Nino Phase 2', '09665854744', '', NULL, 'Completed', 'Walk-in', 'staff', '', 0, '2026-05-09 23:09:11'),
('REQ-2026-0006', 'ANB-3A1D61B4', 'Ramon Cruz', 'First Time Jobseeker', 'CTFJ', 'Issued via Eligibility Check', 'Northfield Subdivision', '', '', NULL, 'Processing', 'Walk-in', 'staff', '', 0, '2026-05-10 00:25:35'),
('REQ-2026-0007', NULL, 'Maverick Jan', 'Barangay Clearance', 'BC', 'laon', 'Silla Compound', '', 'yvammmmm@gmail.com', '9122-09-09', 'Processing', 'Online', 'portal', '/uploads/54E1B37E_Screenshot_2026-03-07_111051.png', 0, '2026-05-10 00:28:05'),
('REQ-2026-0008', 'ANB-C7E66D02', 'Janelle Santos', 'First Time Jobseeker', 'CTFJ', 'Issued via Eligibility Check', 'Sitio Sto.Nino Phase 2', '09665854744', '', NULL, 'Completed', 'Walk-in', 'staff', '', 1, '2026-05-10 01:49:34'),
('REQ-2026-0009', 'ANB-C7E66D02', 'Janelle Santos', 'First Time Jobseeker', 'CTFJ', 'Issued via Eligibility Check', 'Sitio Sto.Nino Phase 2', '09665854744', '', NULL, 'Ready to Print', 'Walk-in', 'staff', '', 0, '2026-05-10 01:56:29'),
('REQ-2026-0010', NULL, 'Maverick Jan', 'Barangay Clearance', 'BC', 'loan', 'silla compound', '', 'yvammmmm@gmail.com', '2001-02-23', 'Processing', 'Online', 'portal', '/uploads/C8E98C8C_anabu_logo.jpg', 0, '2026-05-10 03:45:27');

-- --------------------------------------------------------

--
-- Table structure for table `incidents`
--

CREATE TABLE `incidents` (
  `id` varchar(50) NOT NULL,
  `type` varchar(100) NOT NULL,
  `location` varchar(255) DEFAULT NULL,
  `date` date DEFAULT NULL,
  `reported_by` varchar(255) DEFAULT NULL,
  `complainee` varchar(255) DEFAULT NULL,
  `status` varchar(50) NOT NULL DEFAULT 'Pending',
  `severity` varchar(30) NOT NULL DEFAULT 'Medium',
  `description` text DEFAULT NULL,
  `attachments` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `incidents`
--

INSERT INTO `incidents` (`id`, `type`, `location`, `date`, `reported_by`, `complainee`, `status`, `severity`, `description`, `attachments`, `created_at`) VALUES
('INC-2026-001', 'Physical Assault', 'Silla Compound', '2026-03-01', 'Ramon Cruz', 'Kyan Ramirez', 'Pending', 'High', 'Nanapak sa sobrang kalasingan', '[]', '2026-05-09 22:41:49');

-- --------------------------------------------------------

--
-- Table structure for table `portal_terms_log`
--

CREATE TABLE `portal_terms_log` (
  `id` int(11) NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `contact` varchar(50) DEFAULT NULL,
  `ip` varchar(45) DEFAULT NULL,
  `agreed_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `portal_terms_log`
--

INSERT INTO `portal_terms_log` (`id`, `name`, `contact`, `ip`, `agreed_at`) VALUES
(1, 'Portal User', '', NULL, '2026-05-09 22:08:19'),
(2, 'Portal User', '', NULL, '2026-05-09 22:19:13'),
(3, 'Portal User', '', NULL, '2026-05-09 22:32:29'),
(4, 'Portal User', '', NULL, '2026-05-09 22:34:32'),
(5, 'Portal User', '', NULL, '2026-05-10 00:26:58'),
(6, 'Portal User', '', NULL, '2026-05-10 03:44:48');

-- --------------------------------------------------------

--
-- Table structure for table `purok_data`
--

CREATE TABLE `purok_data` (
  `key_name` varchar(100) NOT NULL,
  `label` varchar(255) DEFAULT NULL,
  `total` int(11) NOT NULL DEFAULT 0,
  `color` varchar(50) DEFAULT NULL,
  `pct` int(11) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `purok_data`
--

INSERT INTO `purok_data` (`key_name`, `label`, `total`, `color`, `pct`) VALUES
('Appletown Subdivision', 'Appletown Subd.', 0, '#85938a', 0),
('Northfield Subdivision', 'Northfield Subdivision', 0, '#22c55e', 0),
('Ragatan Proper', 'Ragatan Proper', 0, '#26a199', 0),
('Silla Compound', 'Silla Compound', 0, '#9e7061', 0),
('Sitio Sto.NIno Phase 1', 'Sitio Sto.NIno Phase 1', 0, '#7e79c8', 0),
('Sitio Sto.Nino Phase 2', 'Sitio Sto.Nino Phase 2', 0, '#c421a1', 0);

-- --------------------------------------------------------

--
-- Table structure for table `residents`
--

CREATE TABLE `residents` (
  `id` varchar(50) NOT NULL,
  `name` varchar(255) NOT NULL,
  `purok` varchar(100) DEFAULT NULL,
  `dob` date DEFAULT NULL,
  `gender` varchar(20) DEFAULT NULL,
  `civil` varchar(50) DEFAULT NULL,
  `contact` varchar(50) DEFAULT NULL,
  `status` varchar(30) NOT NULL DEFAULT 'Active',
  `household` varchar(100) DEFAULT NULL,
  `type` varchar(50) DEFAULT NULL,
  `address` text DEFAULT NULL,
  `special_groups` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `residents`
--

INSERT INTO `residents` (`id`, `name`, `purok`, `dob`, `gender`, `civil`, `contact`, `status`, `household`, `type`, `address`, `special_groups`, `created_at`, `updated_at`) VALUES
('ANB-3A1D61B4', 'Ramon Cruz', 'Northfield Subdivision', '1982-03-21', 'Male', 'Single', '', 'Active', '', 'Renter', '4511 Northfield Subd.', '[\"Indigenous People\", \"4Ps Beneficiary\"]', '2026-05-09 22:04:00', '2026-05-09 22:04:00'),
('ANB-5ACF1C97', 'Kyan Ramirez', 'Appletown Subdivision', '2016-12-24', 'Male', 'Single', '0977743838', 'Active', '', 'Homeowner', '6666 Appletown Subd.', '[\"Out-of-School Youth\", \"Malnourished Child\"]', '2026-05-09 22:04:54', '2026-05-09 22:04:54'),
('ANB-A994D9FA', 'Ramirez Kyan', 'Sitio Sto.NIno Phase 1', '2000-03-24', 'Male', 'Single', '09511484553', 'Active', '', 'Homeowner', '4557 Sto.Nino Phase 1', '[\"Solo Parent\", \"Indigenous People\", \"Unemployed Adult\"]', '2026-05-09 22:00:50', '2026-05-09 22:00:50'),
('ANB-AA559E78', 'Amy Narvasa', 'Ragatan Proper', '2010-11-26', 'Female', 'Single', '09884721285', 'Active', '', 'Renter', '5446 Ragatan Proper', '[\"Teenage Mother\", \"Out-of-School Youth\", \"Malnourished Child\"]', '2026-05-09 22:06:10', '2026-05-09 22:06:10'),
('ANB-B62958DE', 'Rodolfo Manaloto', 'Silla Compound', '1948-02-24', 'Male', 'Single', '09911584777', 'Active', '', 'Renter', '6547 Silla Compound', '[\"PWD\", \"Solo Parent\"]', '2026-05-09 22:02:57', '2026-05-09 22:02:57'),
('ANB-C7E66D02', 'Janelle Santos', 'Sitio Sto.Nino Phase 2', '2005-03-01', 'Female', 'Single', '09665854744', 'Active', '', 'Homeowner', '5626 Sto.Nino Phase 2', '[\"Teenage Mother\", \"Out-of-School Youth\", \"Unemployed Adult\"]', '2026-05-09 22:01:43', '2026-05-09 22:01:43');

-- --------------------------------------------------------

--
-- Table structure for table `resident_status`
--

CREATE TABLE `resident_status` (
  `resident_id` varchar(50) NOT NULL,
  `good_standing` tinyint(1) NOT NULL DEFAULT 1,
  `blotter` tinyint(1) NOT NULL DEFAULT 0,
  `blotter_details` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `resident_status`
--

INSERT INTO `resident_status` (`resident_id`, `good_standing`, `blotter`, `blotter_details`) VALUES
('ANB-3A1D61B4', 1, 0, '[]'),
('ANB-5ACF1C97', 1, 0, '[]'),
('ANB-A994D9FA', 1, 0, '[]'),
('ANB-AA559E78', 1, 0, '[]'),
('ANB-B62958DE', 1, 0, '[]'),
('ANB-C7E66D02', 1, 0, '[]');

-- --------------------------------------------------------

--
-- Table structure for table `rfid_tags`
--

CREATE TABLE `rfid_tags` (
  `id` varchar(50) NOT NULL,
  `name` varchar(255) NOT NULL,
  `location` varchar(255) DEFAULT NULL,
  `type` varchar(100) DEFAULT NULL,
  `status` varchar(50) NOT NULL DEFAULT 'In Cabinet',
  `last_scan` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` varchar(50) NOT NULL,
  `name` varchar(255) NOT NULL,
  `role` varchar(100) DEFAULT NULL,
  `access` varchar(100) NOT NULL DEFAULT 'View Only',
  `username` varchar(100) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `face` tinyint(1) NOT NULL DEFAULT 0,
  `rfid` tinyint(1) NOT NULL DEFAULT 0,
  `status` varchar(30) NOT NULL DEFAULT 'Active',
  `last_login` datetime DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `name`, `role`, `access`, `username`, `password`, `face`, `rfid`, `status`, `last_login`, `created_at`) VALUES
('USR-001', 'Robin Silla', 'Barangay Captain', 'Full Access', 'admin', 'Admin@1234!', 1, 1, 'Active', NULL, '2026-05-09 21:00:41'),
('USR-002', 'Kyan Ramirez', 'Data Encoder', 'Records & Certificates', 'kyan.ramirez', '00000000', 1, 0, 'Active', NULL, '2026-05-09 22:58:40'),
('USR-003', 'Maverick Jan Marquez', 'Tanod Captain', 'Incidents Only', 'maverick.jan', '00000000', 1, 0, 'Active', NULL, '2026-05-09 22:59:13'),
('USR-004', 'Mark  Justin Manalac', 'Barangay Clerk', 'View Only', 'mark.justin', '00000000', 1, 0, 'Active', NULL, '2026-05-09 23:00:04');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `audit_log`
--
ALTER TABLE `audit_log`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_audit_log_category` (`category`),
  ADD KEY `idx_audit_log_created` (`created_at`);

--
-- Indexes for table `cabinet_folders`
--
ALTER TABLE `cabinet_folders`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_cf_rfid` (`rfid`);

--
-- Indexes for table `cabinet_log`
--
ALTER TABLE `cabinet_log`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `cert_requests`
--
ALTER TABLE `cert_requests`
  ADD PRIMARY KEY (`code`),
  ADD KEY `fk_cr_resident` (`resident_id`),
  ADD KEY `idx_cert_requests_status` (`status`),
  ADD KEY `idx_cert_requests_requested` (`requested`);

--
-- Indexes for table `incidents`
--
ALTER TABLE `incidents`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_incidents_status` (`status`),
  ADD KEY `idx_incidents_date` (`date`);

--
-- Indexes for table `portal_terms_log`
--
ALTER TABLE `portal_terms_log`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `purok_data`
--
ALTER TABLE `purok_data`
  ADD PRIMARY KEY (`key_name`);

--
-- Indexes for table `residents`
--
ALTER TABLE `residents`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_residents_status` (`status`),
  ADD KEY `idx_residents_purok` (`purok`);

--
-- Indexes for table `resident_status`
--
ALTER TABLE `resident_status`
  ADD PRIMARY KEY (`resident_id`);

--
-- Indexes for table `rfid_tags`
--
ALTER TABLE `rfid_tags`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uk_users_username` (`username`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `audit_log`
--
ALTER TABLE `audit_log`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=109;

--
-- AUTO_INCREMENT for table `cabinet_log`
--
ALTER TABLE `cabinet_log`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `portal_terms_log`
--
ALTER TABLE `portal_terms_log`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `cabinet_folders`
--
ALTER TABLE `cabinet_folders`
  ADD CONSTRAINT `fk_cf_rfid` FOREIGN KEY (`rfid`) REFERENCES `rfid_tags` (`id`) ON DELETE SET NULL ON UPDATE CASCADE;

--
-- Constraints for table `cert_requests`
--
ALTER TABLE `cert_requests`
  ADD CONSTRAINT `fk_cr_resident` FOREIGN KEY (`resident_id`) REFERENCES `residents` (`id`) ON DELETE SET NULL ON UPDATE CASCADE;

--
-- Constraints for table `resident_status`
--
ALTER TABLE `resident_status`
  ADD CONSTRAINT `fk_rs_resident` FOREIGN KEY (`resident_id`) REFERENCES `residents` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

-- --------------------------------------------------------

--
-- Table structure for table `voter_registry`
--

CREATE TABLE `voter_registry` (
  `id` varchar(50) NOT NULL,
  `resident_id` varchar(50) NOT NULL,
  `precinct_no` varchar(50) DEFAULT NULL,
  `cluster_no` varchar(50) DEFAULT NULL,
  `registered_date` date DEFAULT NULL,
  `status` varchar(30) NOT NULL DEFAULT 'Active',
  `verified_by` varchar(100) DEFAULT NULL,
  `verified_at` datetime DEFAULT NULL,
  `remarks` text DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Constraints for table `voter_registry`
--
ALTER TABLE `voter_registry`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_vr_resident` (`resident_id`),
  ADD CONSTRAINT `fk_vr_resident` FOREIGN KEY (`resident_id`) REFERENCES `residents` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
SET FOREIGN_KEY_CHECKS = 1;
