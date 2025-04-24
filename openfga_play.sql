-- MySQL dump 10.13  Distrib 8.0.36, for Linux (x86_64)
--
-- Host: localhost    Database: openfga_play
-- ------------------------------------------------------
-- Server version	8.0.36

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES UTF8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `assertion`
--

DROP TABLE IF EXISTS `assertion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `assertion` (
  `store` char(26) NOT NULL,
  `authorization_model_id` char(26) NOT NULL,
  `assertions` blob,
  PRIMARY KEY (`store`,`authorization_model_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `assertion`
--

LOCK TABLES `assertion` WRITE;
/*!40000 ALTER TABLE `assertion` DISABLE KEYS */;
/*!40000 ALTER TABLE `assertion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `authorization_model`
--

DROP TABLE IF EXISTS `authorization_model`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `authorization_model` (
  `store` char(26) NOT NULL,
  `authorization_model_id` char(26) NOT NULL,
  `type` varchar(256) NOT NULL,
  `type_definition` blob,
  `schema_version` varchar(5) NOT NULL DEFAULT '1.0',
  `serialized_protobuf` longblob,
  PRIMARY KEY (`store`,`authorization_model_id`,`type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `authorization_model`
--

LOCK TABLES `authorization_model` WRITE;
/*!40000 ALTER TABLE `authorization_model` DISABLE KEYS */;
/*!40000 ALTER TABLE `authorization_model` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `changelog`
--

DROP TABLE IF EXISTS `changelog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `changelog` (
  `store` char(26) NOT NULL,
  `object_type` varchar(256) NOT NULL,
  `object_id` varchar(256) NOT NULL,
  `relation` varchar(50) NOT NULL,
  `_user` varchar(512) NOT NULL,
  `operation` int NOT NULL,
  `ulid` char(26) NOT NULL,
  `inserted_at` timestamp NOT NULL,
  `condition_name` varchar(256) DEFAULT NULL,
  `condition_context` longblob,
  PRIMARY KEY (`store`,`ulid`,`object_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `changelog`
--

LOCK TABLES `changelog` WRITE;
/*!40000 ALTER TABLE `changelog` DISABLE KEYS */;
/*!40000 ALTER TABLE `changelog` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `goose_db_version`
--

DROP TABLE IF EXISTS `goose_db_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `goose_db_version` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `version_id` bigint NOT NULL,
  `is_applied` tinyint(1) NOT NULL,
  `tstamp` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `goose_db_version`
--

LOCK TABLES `goose_db_version` WRITE;
/*!40000 ALTER TABLE `goose_db_version` DISABLE KEYS */;
INSERT INTO `goose_db_version` VALUES (1,0,1,'2025-04-15 13:48:39'),(2,1,1,'2025-04-15 14:00:36'),(3,2,1,'2025-04-15 14:00:36'),(4,3,1,'2025-04-15 14:00:36'),(5,4,1,'2025-04-15 14:00:36'),(6,5,1,'2025-04-15 14:00:36'),(7,6,1,'2025-04-15 14:00:36');
/*!40000 ALTER TABLE `goose_db_version` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `store`
--

DROP TABLE IF EXISTS `store`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `store` (
  `id` char(26) NOT NULL,
  `name` varchar(64) NOT NULL,
  `created_at` timestamp NOT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  `deleted_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `store`
--

LOCK TABLES `store` WRITE;
/*!40000 ALTER TABLE `store` DISABLE KEYS */;
/*!40000 ALTER TABLE `store` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tuple`
--

DROP TABLE IF EXISTS `tuple`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tuple` (
  `store` char(26) NOT NULL,
  `object_type` varchar(128) NOT NULL,
  `object_id` varchar(255) NOT NULL,
  `relation` varchar(50) NOT NULL,
  `_user` varchar(256) NOT NULL,
  `user_type` varchar(7) NOT NULL,
  `ulid` char(26) NOT NULL,
  `inserted_at` timestamp NOT NULL,
  `condition_name` varchar(256) DEFAULT NULL,
  `condition_context` longblob,
  PRIMARY KEY (`store`,`object_type`,`object_id`,`relation`,`_user`),
  UNIQUE KEY `idx_tuple_ulid` (`ulid`),
  KEY `idx_reverse_lookup_user` (`store`,`object_type`,`relation`,`_user`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tuple`
--

LOCK TABLES `tuple` WRITE;
/*!40000 ALTER TABLE `tuple` DISABLE KEYS */;
/*!40000 ALTER TABLE `tuple` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-04-16  8:44:42
