-- phpMyAdmin SQL Dump
-- version 4.8.4
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jun 01, 2021 at 07:12 PM
-- Server version: 10.1.37-MariaDB
-- PHP Version: 7.3.0

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `betadb`
--

-- --------------------------------------------------------

--
-- Table structure for table `food`
--

CREATE TABLE `food` (
  `food_id` int(11) NOT NULL,
  `food_bonus` text,
  `food_bonus_sep` varchar(20) DEFAULT NULL,
  `food_card_date` date DEFAULT NULL,
  `food_card_datetime` datetime DEFAULT NULL,
  `food_card_time` varchar(20) DEFAULT NULL,
  `food_gang_id` varchar(20) DEFAULT NULL,
  `food_gang_number` int(11) DEFAULT NULL,
  `food_gang_title` varchar(20) DEFAULT NULL,
  `food_price` float DEFAULT NULL,
  `food_totquantity` int(11) DEFAULT NULL,
  `food_available_quantity` int(11) DEFAULT NULL,
  `food_process` float DEFAULT NULL,
  `food_station` varchar(100) DEFAULT NULL,
  `food_table` varchar(20) DEFAULT NULL,
  `food_type` varchar(100) DEFAULT NULL,
  `food_type_id_int` int(11) DEFAULT NULL,
  `food_type_id_str` varchar(45) DEFAULT NULL,
  `food_type_only` varchar(45) DEFAULT NULL,
  `food_waitress` varchar(45) DEFAULT NULL,
  `food_opt_id` int(11) NOT NULL,
  `food_production` int(11) NOT NULL DEFAULT '0',
  `user_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `historical_sales`
--

CREATE TABLE `historical_sales` (
  `sales_id` int(11) NOT NULL,
  `food_food_id` int(11) NOT NULL,
  `food_user_id` int(11) NOT NULL,
  `sales_created` datetime DEFAULT CURRENT_TIMESTAMP,
  `sales_updated` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `sales_price` float DEFAULT NULL,
  `sales_quantity` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `restaurant`
--

CREATE TABLE `restaurant` (
  `restaurant_id` int(11) NOT NULL,
  `restaurant_name` varchar(45) DEFAULT NULL,
  `restaurant_addr_street` varchar(255) DEFAULT NULL,
  `restaurant_addr_zip_code` varchar(30) NOT NULL,
  `restaurant_addr_zip_type` varchar(20) NOT NULL,
  `restaurant_addr_country` varchar(45) NOT NULL,
  `restaurant_created` datetime DEFAULT CURRENT_TIMESTAMP,
  `restaurant_modified` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `user_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `user`
--

CREATE TABLE `user` (
  `id` int(11) NOT NULL,
  `user_fname` varchar(45) NOT NULL,
  `user_lname` varchar(45) NOT NULL,
  `user_email` varchar(45) NOT NULL,
  `user_phone` varchar(45) DEFAULT NULL,
  `user_password` text NOT NULL,
  `user_created` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `user_modified` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `food`
--
ALTER TABLE `food`
  ADD PRIMARY KEY (`food_id`,`user_id`),
  ADD UNIQUE KEY `unique_foods_by_user` (`user_id`,`food_type_id_str`,`food_table`),
  ADD KEY `fk_food_user1_idx` (`user_id`);

--
-- Indexes for table `historical_sales`
--
ALTER TABLE `historical_sales`
  ADD PRIMARY KEY (`sales_id`,`food_food_id`,`food_user_id`),
  ADD KEY `fk_sales_food1_idx` (`food_food_id`,`food_user_id`);

--
-- Indexes for table `restaurant`
--
ALTER TABLE `restaurant`
  ADD PRIMARY KEY (`restaurant_id`,`user_id`),
  ADD KEY `fk_restaurant_user_idx` (`user_id`);

--
-- Indexes for table `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `user_email_UNIQUE` (`user_email`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `food`
--
ALTER TABLE `food`
  MODIFY `food_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `historical_sales`
--
ALTER TABLE `historical_sales`
  MODIFY `sales_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `restaurant`
--
ALTER TABLE `restaurant`
  MODIFY `restaurant_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `user`
--
ALTER TABLE `user`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `food`
--
ALTER TABLE `food`
  ADD CONSTRAINT `fk_food_user1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `historical_sales`
--
ALTER TABLE `historical_sales`
  ADD CONSTRAINT `fk_sales_food1` FOREIGN KEY (`food_food_id`,`food_user_id`) REFERENCES `food` (`food_id`, `user_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `restaurant`
--
ALTER TABLE `restaurant`
  ADD CONSTRAINT `fk_restaurant_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
