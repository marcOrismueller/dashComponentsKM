-- MySQL dump 10.13  Distrib 8.0.20, for Win64 (x86_64)
--
-- Host: localhost    Database: betadb
-- ------------------------------------------------------
-- Server version	5.5.5-10.1.37-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `account_configs`
--

DROP TABLE IF EXISTS `account_configs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `account_configs` (
  `user_id` int(11) NOT NULL,
  `orders_folderPath` varchar(255) NOT NULL,
  `lastFileTimestamp` varchar(255) DEFAULT NULL,
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `fk_l_id` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `current_production_cards_tmp`
--

DROP TABLE IF EXISTS `current_production_cards_tmp`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `current_production_cards_tmp` (
  `user_id` int(11) NOT NULL,
  `type_id_int` int(11) NOT NULL,
  UNIQUE KEY `unique_current_production_cards_tmp` (`user_id`,`type_id_int`),
  CONSTRAINT `FK_user_id` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `current_selected_items_tmp`
--

DROP TABLE IF EXISTS `current_selected_items_tmp`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `current_selected_items_tmp` (
  `user_id` int(11) NOT NULL,
  `type_id_int` int(11) NOT NULL,
  `gang_number` int(11) DEFAULT NULL,
  `type_id_str` int(11) NOT NULL,
  UNIQUE KEY `unique_current_selected_items_tmp` (`user_id`,`type_id_int`,`type_id_str`,`gang_number`) USING BTREE,
  CONSTRAINT `current_selected_items_tmp_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `food`
--

DROP TABLE IF EXISTS `food`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `food` (
  `food_id` int(11) NOT NULL AUTO_INCREMENT,
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
  `user_id` int(11) NOT NULL,
  `order_type` varchar(15) NOT NULL DEFAULT 'order',
  PRIMARY KEY (`food_id`,`user_id`),
  UNIQUE KEY `unique_foods_by_user` (`user_id`,`food_type_id_str`,`food_table`,`order_type`) USING BTREE,
  KEY `fk_food_user1_idx` (`user_id`),
  CONSTRAINT `fk_food_user1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2061 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `historical_sales`
--

DROP TABLE IF EXISTS `historical_sales`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `historical_sales` (
  `sales_id` int(11) NOT NULL AUTO_INCREMENT,
  `food_food_id` int(11) NOT NULL,
  `food_user_id` int(11) NOT NULL,
  `sales_created` datetime DEFAULT CURRENT_TIMESTAMP,
  `sales_updated` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `sales_price` float DEFAULT NULL,
  `sales_quantity` int(11) DEFAULT NULL,
  PRIMARY KEY (`sales_id`,`food_food_id`,`food_user_id`),
  KEY `fk_sales_food1_idx` (`food_food_id`,`food_user_id`),
  CONSTRAINT `fk_sales_food1` FOREIGN KEY (`food_food_id`, `food_user_id`) REFERENCES `food` (`food_id`, `user_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2293 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `restaurant`
--

DROP TABLE IF EXISTS `restaurant`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `restaurant` (
  `restaurant_id` int(11) NOT NULL AUTO_INCREMENT,
  `restaurant_name` varchar(45) DEFAULT NULL,
  `restaurant_addr_street` varchar(255) DEFAULT NULL,
  `restaurant_addr_zip_code` varchar(30) NOT NULL,
  `restaurant_addr_zip_type` varchar(20) NOT NULL,
  `restaurant_addr_country` varchar(45) NOT NULL,
  `restaurant_created` datetime DEFAULT CURRENT_TIMESTAMP,
  `restaurant_modified` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`restaurant_id`,`user_id`),
  KEY `fk_restaurant_user_idx` (`user_id`),
  CONSTRAINT `fk_restaurant_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_fname` varchar(45) NOT NULL,
  `user_lname` varchar(45) NOT NULL,
  `user_email` varchar(45) NOT NULL,
  `user_phone` varchar(45) DEFAULT NULL,
  `user_password` text NOT NULL,
  `user_created` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `user_modified` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_email_UNIQUE` (`user_email`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping events for database 'betadb'
--

--
-- Dumping routines for database 'betadb'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2021-10-03 13:32:13
