-- MySQL dump 10.13  Distrib 8.0.41, for Win64 (x86_64)
--
-- Host: localhost    Database: pharm_engeneering_project_management
-- ------------------------------------------------------
-- Server version	8.0.41

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
-- Table structure for table `audit_log`
--

DROP TABLE IF EXISTS `audit_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `audit_log` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `event_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `event_type` varchar(64) NOT NULL,
  `actor_username` varchar(64) DEFAULT NULL,
  `target_username` varchar(64) DEFAULT NULL,
  `details` text,
  `success` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  KEY `idx_audit_event_time` (`event_time`),
  KEY `idx_audit_event_type` (`event_type`),
  KEY `idx_audit_actor` (`actor_username`),
  KEY `idx_audit_target` (`target_username`)
) ENGINE=InnoDB AUTO_INCREMENT=172 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `audit_log`
--

LOCK TABLES `audit_log` WRITE;
/*!40000 ALTER TABLE `audit_log` DISABLE KEYS */;
INSERT INTO `audit_log` VALUES (1,'2026-05-30 01:15:11','login_failed','dba_user',NULL,'Неверный логин или пароль',0),(2,'2026-05-30 01:28:36','login_success','dba_user',NULL,'Роль: dba',1),(3,'2026-05-30 01:29:07','login_success','dba_user',NULL,'Роль: dba',1),(4,'2026-05-30 01:45:04','login_success','dba_user',NULL,'Роль: dba',1),(5,'2026-05-30 01:46:40','login_failed','dba_user',NULL,'Неверный логин или пароль',0),(6,'2026-05-30 01:47:39','login_success','dba_user',NULL,'Роль: dba',1),(7,'2026-05-30 01:48:19','login_success','dba_user',NULL,'Роль: dba',1),(8,'2026-05-30 01:49:05','logout','dba_user',NULL,'Выход из панели администратора',1),(9,'2026-05-30 01:49:10','login_success','dba_user',NULL,'Роль: dba',1),(10,'2026-06-05 12:37:26','login_success','dba_user',NULL,'Роль: dba',1),(11,'2026-06-05 12:49:57','login_success','dba_user',NULL,'Роль: dba',1),(12,'2026-06-05 12:53:04','user_create','dba_user','ыиа','Роль: director, worker_id: 7',1),(13,'2026-06-05 12:53:12','user_create','dba_user','ваи','Роль: project_manager, worker_id: 12',1),(14,'2026-06-05 12:53:24','user_create','dba_user','ваи','Роль: director, worker_id: 10',1),(15,'2026-06-05 12:55:36','user_delete','dba_user','ваи',NULL,1),(16,'2026-06-05 12:55:46','user_create','dba_user','фвм','Роль: foreman, worker_id: 1',1),(17,'2026-06-05 12:56:10','user_create','dba_user','авив','Роль: director, worker_id: 8',1),(18,'2026-06-05 12:56:15','user_delete','dba_user','ыиа',NULL,1),(19,'2026-06-05 12:56:20','user_delete','dba_user','авив',NULL,1),(20,'2026-06-05 12:56:24','user_delete','dba_user','фвм',NULL,1),(21,'2026-06-05 12:56:42','logout','dba_user',NULL,'Выход из панели администратора',1),(22,'2026-06-05 12:56:51','login_success','director_user',NULL,'Роль: director',1),(23,'2026-06-05 13:00:25','login_success','director_user',NULL,'Роль: director',1),(24,'2026-06-05 13:06:09','login_success','dba_user',NULL,'Роль: dba',1),(25,'2026-06-05 13:06:43','logout','dba_user',NULL,'Выход из панели администратора',1),(26,'2026-06-05 13:06:50','login_success','director_user',NULL,'Роль: director',1),(27,'2026-06-05 13:07:18','logout','director_user',NULL,'Выход (директор)',1),(28,'2026-06-05 13:09:15','login_success','dba_user',NULL,'Роль: dba',1),(29,'2026-06-05 13:09:52','user_create','dba_user','accountant_user','Роль: accountant, worker_id: 15',1),(30,'2026-06-05 13:10:01','logout','dba_user',NULL,'Выход из панели администратора',1),(31,'2026-06-05 13:10:10','login_success','accountant_user',NULL,'Роль: accountant',1),(32,'2026-06-05 13:10:40','logout','accountant_user',NULL,'Выход (бухгалтер)',1),(33,'2026-06-05 13:10:44','login_success','dba_user',NULL,'Роль: dba',1),(34,'2026-06-05 13:11:11','user_create','dba_user','manager_user','Роль: project_manager, worker_id: 12',1),(35,'2026-06-05 13:11:58','user_create','dba_user','foreman_user','Роль: foreman, worker_id: 1',1),(36,'2026-06-05 13:12:42','logout','dba_user',NULL,'Выход из панели администратора',1),(37,'2026-06-05 13:12:51','login_success','foreman_user',NULL,'Роль: foreman',1),(38,'2026-06-05 13:13:16','logout','foreman_user',NULL,'Выход (бригадир)',1),(39,'2026-06-05 13:13:26','login_success','manager_user',NULL,'Роль: project_manager',1),(40,'2026-06-05 13:17:35','logout','manager_user',NULL,'Выход (руководитель проекта)',1),(41,'2026-06-05 13:17:39','login_success','dba_user',NULL,'Роль: dba',1),(42,'2026-06-05 13:41:49','login_failed','dba_user',NULL,'Неверный логин или пароль',0),(43,'2026-06-05 13:42:57','login_success','director_user',NULL,'Роль: director',1),(44,'2026-06-05 13:44:54','login_success','director_user',NULL,'Роль: director',1),(45,'2026-06-05 13:50:28','login_success','director_user',NULL,'Роль: director',1),(46,'2026-06-05 13:55:27','login_success','director_user',NULL,'Роль: director',1),(47,'2026-06-05 14:00:56','login_success','director_user',NULL,'Роль: director',1),(48,'2026-06-05 14:02:28','login_success','director_user',NULL,'Роль: director',1),(49,'2026-06-05 14:07:09','login_success','director_user',NULL,'Роль: director',1),(50,'2026-06-05 14:17:12','logout','director_user',NULL,'Выход (директор)',1),(51,'2026-06-05 14:18:14','login_success','manager_user',NULL,'Роль: project_manager',1),(52,'2026-06-05 14:19:10','login_success','manager_user',NULL,'Роль: project_manager',1),(53,'2026-06-05 14:20:35','login_success','manager_user',NULL,'Роль: project_manager',1),(54,'2026-06-05 14:21:22','data_change','manager_user',NULL,'Создан проект «tb»',1),(55,'2026-06-05 14:31:22','login_success','manager_user',NULL,'Роль: project_manager',1),(56,'2026-06-05 14:32:17','login_success','manager_user',NULL,'Роль: project_manager',1),(57,'2026-06-05 14:33:39','data_change','manager_user',NULL,'Удалён проект id=7 «tb»',1),(58,'2026-06-05 14:35:09','logout','manager_user',NULL,'Выход (руководитель проекта)',1),(59,'2026-06-05 14:35:12','login_success','manager_user',NULL,'Роль: project_manager',1),(60,'2026-06-05 14:37:28','data_change','manager_user',NULL,'Создан проект «ывс»',1),(61,'2026-06-05 14:38:37','data_change','manager_user',NULL,'Удалён проект id=8 «ывс»',1),(62,'2026-06-05 14:39:00','logout','manager_user',NULL,'Выход (руководитель проекта)',1),(63,'2026-06-05 14:39:03','login_success','manager_user',NULL,'Роль: project_manager',1),(64,'2026-06-05 14:41:52','login_success','manager_user',NULL,'Роль: project_manager',1),(65,'2026-06-05 14:42:38','data_change_declined','manager_user',NULL,'Отмена изменения проекта «Демонстрационный проект»',0),(66,'2026-06-05 14:43:00','data_change_declined','manager_user',NULL,'Отмена удаления проекта «Демонстрационный проект»',0),(67,'2026-06-05 14:43:08','data_change','manager_user',NULL,'Создан проект «впт»',1),(68,'2026-06-05 14:43:26','data_change','manager_user',NULL,'Этап «Проектирование» в проекте id=9',1),(69,'2026-06-05 14:43:30','data_change','manager_user',NULL,'Этап «Подготовка» в проекте id=9',1),(70,'2026-06-05 14:43:32','data_change','manager_user',NULL,'Этап «Монтаж» в проекте id=9',1),(71,'2026-06-05 14:43:35','data_change','manager_user',NULL,'Этап «Настройка и проверка» в проекте id=9',1),(72,'2026-06-05 14:43:38','data_change','manager_user',NULL,'Этап «Сдача» в проекте id=9',1),(73,'2026-06-05 14:43:43','data_change','manager_user',NULL,'Проект id=9 переведён в работу',1),(74,'2026-06-05 14:44:00','data_change','manager_user',NULL,'Удалён проект id=9 «впт»',1),(75,'2026-06-05 14:44:07','data_change','manager_user',NULL,'Создан проект «ар»',1),(76,'2026-06-05 14:44:13','data_change','manager_user',NULL,'Этап «Подготовка» в проекте id=10',1),(77,'2026-06-05 14:44:14','data_change','manager_user',NULL,'Этап «Монтаж» в проекте id=10',1),(78,'2026-06-05 14:44:16','data_change','manager_user',NULL,'Этап «Настройка и проверка» в проекте id=10',1),(79,'2026-06-05 14:44:17','data_change','manager_user',NULL,'Этап «Сдача» в проекте id=10',1),(80,'2026-06-05 14:44:34','data_change','manager_user',NULL,'Проект id=10 переведён в работу',1),(81,'2026-06-05 14:45:07','data_change','manager_user',NULL,'Создан проект «Тест»',1),(82,'2026-06-05 14:45:53','data_change','manager_user',NULL,'Этап «Проектирование» в проекте id=11',1),(83,'2026-06-05 14:48:01','data_change','manager_user',NULL,'Этап id=36 «Проектирование»: статус → «В работе»',1),(84,'2026-06-05 14:48:07','data_change','manager_user',NULL,'Добавлена задача «впи» на этапе id=36',1),(85,'2026-06-05 14:48:38','data_change','manager_user',NULL,'Изменена задача id=32 «впи»',1),(86,'2026-06-05 14:48:41','data_change','manager_user',NULL,'Изменена задача id=32 «впи»',1),(87,'2026-06-05 14:48:59','data_change','manager_user',NULL,'Этап id=36 «Проектирование»: статус → «Завершен»',1),(88,'2026-06-05 14:49:59','data_change_declined','manager_user',NULL,'Отмена добавления задачи',0),(89,'2026-06-05 14:50:05','data_change','manager_user',NULL,'Добавлена задача «тест» на этапе id=37',1),(90,'2026-06-05 14:50:38','data_change_declined','manager_user',NULL,'Отмена удаления задачи id=33',0),(91,'2026-06-05 14:51:10','data_change_declined','manager_user',NULL,'Отмена изменения задачи id=33',0),(92,'2026-06-05 14:53:30','data_change','manager_user',NULL,'Материал id=5 на этапе id=37',1),(93,'2026-06-05 14:53:44','data_change_declined','manager_user',NULL,'Отмена добавления материала к этапу',0),(94,'2026-06-05 14:54:47','data_change','manager_user',NULL,'Фактическое кол-во материала id=5 +1.0 (этап sm=25)',1),(95,'2026-06-05 14:55:04','data_change','manager_user',NULL,'Удалён материал этапа id=25',1),(96,'2026-06-05 14:55:33','data_change','manager_user',NULL,'Этап id=37 «Подготовка»: статус → «В работе»',1),(97,'2026-06-05 14:55:41','data_change','manager_user',NULL,'Изменена задача id=33 «тест»',1),(98,'2026-06-05 14:55:46','data_change','manager_user',NULL,'Изменена задача id=33 «тест»',1),(99,'2026-06-05 14:55:47','data_change','manager_user',NULL,'Этап id=37 «Подготовка»: статус → «Завершен»',1),(100,'2026-06-05 14:55:50','data_change','manager_user',NULL,'Этап id=38 «Монтаж»: статус → «В работе»',1),(101,'2026-06-05 14:55:51','data_change','manager_user',NULL,'Этап id=38 «Монтаж»: статус → «Завершен»',1),(102,'2026-06-05 14:55:52','data_change','manager_user',NULL,'Этап id=39 «Настройка и проверка»: статус → «В работе»',1),(103,'2026-06-05 14:55:54','data_change','manager_user',NULL,'Этап id=39 «Настройка и проверка»: статус → «Завершен»',1),(104,'2026-06-05 14:55:56','data_change','manager_user',NULL,'Этап id=40 «Сдача»: статус → «В работе»',1),(105,'2026-06-05 14:55:57','data_change','manager_user',NULL,'Этап id=40 «Сдача»: статус → «Завершен»',1),(106,'2026-06-05 14:56:21','data_change','manager_user',NULL,'Изменён проект id=10 «арвс»',1),(107,'2026-06-05 14:56:53','data_change_declined','manager_user',NULL,'Отмена завершения проекта «арвс»',0),(108,'2026-06-05 14:56:56','data_change','manager_user',NULL,'Удалён проект id=11 «Тест»',1),(109,'2026-06-05 14:56:58','data_change','manager_user',NULL,'Удалён проект id=10 «арвс»',1),(110,'2026-06-05 14:57:00','logout','manager_user',NULL,'Выход (руководитель проекта)',1),(111,'2026-06-05 14:57:09','login_success','foreman_user',NULL,'Роль: foreman',1),(112,'2026-06-05 15:05:01','login_success','foreman_user',NULL,'Роль: foreman',1),(113,'2026-06-05 15:05:28','login_success','foreman_user',NULL,'Роль: foreman',1),(114,'2026-06-05 15:07:16','login_success','foreman_user',NULL,'Роль: foreman',1),(115,'2026-06-05 15:10:08','data_change_declined','foreman_user',NULL,'Отмена завершения задачи id=4',0),(116,'2026-06-05 15:10:09','logout','foreman_user',NULL,'Выход (бригадир)',1),(117,'2026-06-05 15:10:17','login_failed','employee_user',NULL,'Неверный логин или пароль',0),(118,'2026-06-05 15:10:23','login_failed','employe_user',NULL,'Неверный логин или пароль',0),(119,'2026-06-05 15:10:31','login_success','dba_user',NULL,'Роль: dba',1),(120,'2026-06-05 15:18:25','login_success','dba_user',NULL,'Роль: dba',1),(121,'2026-06-05 15:22:45','login_success','dba_user',NULL,'Роль: dba',1),(122,'2026-06-05 15:23:13','user_create','dba_user','employee_user','Роль: employee, worker_id: 8',1),(123,'2026-06-05 15:23:23','logout','dba_user',NULL,'Выход из панели администратора',1),(124,'2026-06-05 15:23:29','login_success','employee_user',NULL,'Роль: employee',1),(125,'2026-06-05 15:24:59','login_success','employee_user',NULL,'Роль: employee',1),(126,'2026-06-05 15:26:28','logout','employee_user',NULL,'Выход (сотрудник)',1),(127,'2026-06-05 15:26:38','login_success','accountant_user',NULL,'Роль: accountant',1),(128,'2026-06-05 15:56:52','logout','accountant_user',NULL,'Выход (бухгалтер)',1),(129,'2026-06-05 15:56:56','login_success','manager_user',NULL,'Роль: project_manager',1),(130,'2026-06-05 16:13:07','logout','manager_user',NULL,'Выход (руководитель проекта)',1),(131,'2026-06-05 16:13:17','login_success','accountant_user',NULL,'Роль: accountant',1),(132,'2026-06-05 16:19:09','login_success','accountant_user',NULL,'Роль: accountant',1),(133,'2026-06-06 00:50:27','login_success','dba_user',NULL,'Роль: dba',1),(134,'2026-06-06 00:52:21','login_success','dba_user',NULL,'Роль: dba',1),(135,'2026-06-06 00:54:26','login_success','dba_user',NULL,'Роль: dba',1),(136,'2026-06-06 00:55:53','login_success','dba_user',NULL,'Роль: dba',1),(137,'2026-06-06 01:03:14','data_change','dba_user',NULL,'Добавлено 1.0 ч. (задача id=27)',1),(138,'2026-06-06 01:12:11','login_success','dba_user',NULL,'Роль: dba',1),(139,'2026-06-06 01:13:59','login_success','dba_user',NULL,'Роль: dba',1),(140,'2026-06-06 01:14:16','logout','dba_user',NULL,'Выход из панели администратора',1),(141,'2026-06-06 01:16:18','login_success','dba_user',NULL,'Роль: dba',1),(142,'2026-06-06 01:19:15','login_success','dba_user',NULL,'Роль: dba',1),(143,'2026-06-06 01:20:58','data_change','dba_user',NULL,'Добавлено 1.0 ч. (задача id=29)',1),(144,'2026-06-06 01:25:43','data_change','dba_user',NULL,'Часы изменены на 0.0 (work_log id=38)',1),(145,'2026-06-06 01:27:19','logout','dba_user',NULL,'Выход из панели администратора',1),(146,'2026-06-06 01:27:22','login_success','dba_user',NULL,'Роль: dba',1),(147,'2026-06-06 01:37:13','login_success','dba_user',NULL,'Роль: dba',1),(148,'2026-06-06 01:37:39','login_success','dba_user',NULL,'Роль: dba',1),(149,'2026-06-06 01:38:41','login_success','dba_user',NULL,'Роль: dba',1),(150,'2026-06-06 01:39:13','login_success','dba_user',NULL,'Роль: dba',1),(151,'2026-06-06 01:40:00','data_change','dba_user',NULL,'Часы изменены на 7.5 (work_log id=46)',1),(152,'2026-06-06 01:43:57','user_create','dba_user','пив','Роль: employee, worker_id: 10',1),(153,'2026-06-06 01:46:28','user_update','dba_user','апи','Логин был: пив; роль: employee',1),(154,'2026-06-06 01:47:07','user_delete','dba_user','апи',NULL,1),(155,'2026-06-06 02:03:23','user_create','dba_user','логин','Роль: employee, worker_id: 7',1),(156,'2026-06-06 02:10:22','user_update','dba_user','логин','Логин был: логин; роль: employee',1),(157,'2026-06-06 02:13:31','user_delete','dba_user','логин',NULL,1),(158,'2026-06-06 02:13:59','user_create','dba_user','логин','Роль: employee, worker_id: 7',1),(159,'2026-06-06 02:14:04','user_delete','dba_user','логин',NULL,1),(160,'2026-06-06 02:18:18','logout','dba_user',NULL,'Выход из панели администратора',1),(161,'2026-06-06 02:18:21','login_success','dba_user',NULL,'Роль: dba',1),(162,'2026-06-06 02:24:04','login_success','dba_user',NULL,'Роль: dba',1),(163,'2026-06-06 02:24:35','login_success','dba_user',NULL,'Роль: dba',1),(164,'2026-06-20 14:56:23','login_success','dba_user',NULL,'Роль: dba',1),(165,'2026-06-20 14:56:55','data_change_declined','dba_user',NULL,'Отмена создания проекта «rb»',0),(166,'2026-06-20 14:57:17','data_change','dba_user',NULL,'Создан проект «sv»',1),(167,'2026-06-20 14:57:52','login_success','dba_user',NULL,'Роль: dba',1),(168,'2026-06-20 14:58:15','data_change','dba_user',NULL,'Добавлено 1.0 ч. (задача id=30)',1),(169,'2026-06-20 15:01:15','login_success','dba_user',NULL,'Роль: dba',1),(170,'2026-06-20 15:01:52','login_success','dba_user',NULL,'Роль: dba',1),(171,'2026-06-20 15:02:28','login_success','dba_user',NULL,'Роль: dba',1);
/*!40000 ALTER TABLE `audit_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `brigade`
--

DROP TABLE IF EXISTS `brigade`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `brigade` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `note` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `brigade`
--

LOCK TABLES `brigade` WRITE;
/*!40000 ALTER TABLE `brigade` DISABLE KEYS */;
INSERT INTO `brigade` VALUES (1,'Бригада №1','Основная'),(2,'Бригада №2','Дополнительная'),(3,'Бригада №3','Пусконаладка');
/*!40000 ALTER TABLE `brigade` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `brigade_composition`
--

DROP TABLE IF EXISTS `brigade_composition`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `brigade_composition` (
  `worker_id` int NOT NULL,
  `brigade_id` int NOT NULL,
  PRIMARY KEY (`worker_id`,`brigade_id`),
  KEY `idx_bc_brigade_id` (`brigade_id`),
  CONSTRAINT `brigade_composition_ibfk_1` FOREIGN KEY (`worker_id`) REFERENCES `worker` (`id`) ON DELETE CASCADE,
  CONSTRAINT `brigade_composition_ibfk_2` FOREIGN KEY (`brigade_id`) REFERENCES `brigade` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `brigade_composition`
--

LOCK TABLES `brigade_composition` WRITE;
/*!40000 ALTER TABLE `brigade_composition` DISABLE KEYS */;
INSERT INTO `brigade_composition` VALUES (1,1),(4,1),(5,1),(8,1),(9,1),(2,2),(6,2),(7,2),(8,2),(3,3),(7,3),(10,3),(11,3);
/*!40000 ALTER TABLE `brigade_composition` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `material`
--

DROP TABLE IF EXISTS `material`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `material` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `unit_of_measurement` varchar(20) NOT NULL,
  `quantity_in_stock` decimal(10,2) NOT NULL DEFAULT '0.00',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `material`
--

LOCK TABLES `material` WRITE;
/*!40000 ALTER TABLE `material` DISABLE KEYS */;
INSERT INTO `material` VALUES (1,'Сэндвич-панели','м2',5000.00),(2,'Профиль алюминиевый','м',8000.00),(3,'Герметик','кг',1200.00),(4,'Фильтры HEPA','шт',300.00),(5,'Воздуховоды','м',3999.00),(6,'Кабель силовой','м',10000.00),(7,'Осветительные панели','шт',800.00),(8,'Двери герметичные','шт',200.00),(9,'Крепежные элементы','шт',20000.00);
/*!40000 ALTER TABLE `material` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `performance_log`
--

DROP TABLE IF EXISTS `performance_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `performance_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `access_time` datetime DEFAULT NULL,
  `user_name` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `performance_log`
--

LOCK TABLES `performance_log` WRITE;
/*!40000 ALTER TABLE `performance_log` DISABLE KEYS */;
INSERT INTO `performance_log` VALUES (1,'2026-05-30 01:03:49','root@localhost'),(2,'2026-06-05 12:59:29','root@localhost');
/*!40000 ALTER TABLE `performance_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `project`
--

DROP TABLE IF EXISTS `project`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `project` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `address` varchar(200) NOT NULL,
  `start_date` date DEFAULT NULL,
  `end_date` date DEFAULT NULL,
  `status` varchar(30) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_project_status` (`status`),
  KEY `idx_project_dates` (`start_date`,`end_date`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `project`
--

LOCK TABLES `project` WRITE;
/*!40000 ALTER TABLE `project` DISABLE KEYS */;
INSERT INTO `project` VALUES (1,'Чистые помещения для ООО \"БиоФарм\"','Москва, индустриальный парк Южный','2026-01-01',NULL,'Планируется'),(2,'Реконструкция стерильного блока АО \"НеоФарм\"','Санкт-Петербург, ул. Софийская, 12','2026-02-01',NULL,'В работе'),(3,'Производственный участок вакцин ООО \"ИммуноТех\"','Казань, ОЭЗ Иннополис','2026-02-15',NULL,'В работе'),(4,'Лабораторный комплекс ГК \"ФармЛайн\"','Новосибирск, ул. Кирова, 20','2025-10-01','2026-02-01','Завершен'),(5,'Цех асептического розлива ООО \"МедСинтез\"','Екатеринбург, ул. Мира, 15','2025-09-01','2026-01-15','Завершен'),(6,'Демонстрационный проект','Москва, тестовая площадка №1','2026-04-01',NULL,'В работе'),(12,'sv','sdv, sdv,sv',NULL,NULL,'Планируется');
/*!40000 ALTER TABLE `project` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `validate_project_dates` BEFORE INSERT ON `project` FOR EACH ROW BEGIN
    IF NEW.end_date IS NOT NULL AND NEW.end_date < NEW.start_date THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Дата окончания не может быть раньше даты начала';
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `audit_project_update` AFTER UPDATE ON `project` FOR EACH ROW BEGIN
    IF 
        OLD.name <> NEW.name OR
        OLD.address <> NEW.address OR
        OLD.start_date <> NEW.start_date OR
        OLD.end_date <> NEW.end_date OR
        OLD.status <> NEW.status
    THEN
        INSERT INTO project_audit (
            project_id,
            old_name, new_name,
            old_address, new_address,
            old_start_date, new_start_date,
            old_end_date, new_end_date,
            old_status, new_status,
            change_time,
            changed_by
        )
        VALUES (
            OLD.id,
            OLD.name, NEW.name,
            OLD.address, NEW.address,
            OLD.start_date, NEW.start_date,
            OLD.end_date, NEW.end_date,
            OLD.status, NEW.status,
            NOW(),
            CURRENT_USER()
        );
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `project_audit`
--

DROP TABLE IF EXISTS `project_audit`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `project_audit` (
  `id` int NOT NULL AUTO_INCREMENT,
  `project_id` int DEFAULT NULL,
  `old_name` varchar(100) DEFAULT NULL,
  `new_name` varchar(100) DEFAULT NULL,
  `old_address` varchar(200) DEFAULT NULL,
  `new_address` varchar(200) DEFAULT NULL,
  `old_start_date` date DEFAULT NULL,
  `new_start_date` date DEFAULT NULL,
  `old_end_date` date DEFAULT NULL,
  `new_end_date` date DEFAULT NULL,
  `old_status` varchar(30) DEFAULT NULL,
  `new_status` varchar(30) DEFAULT NULL,
  `change_time` datetime DEFAULT NULL,
  `changed_by` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `project_audit`
--

LOCK TABLES `project_audit` WRITE;
/*!40000 ALTER TABLE `project_audit` DISABLE KEYS */;
INSERT INTO `project_audit` VALUES (1,9,'впт','впт','а, пт,вп','а, пт,вп',NULL,'2026-06-05',NULL,NULL,'Планируется','В работе','2026-06-05 14:43:43','root@localhost'),(2,10,'ар','ар','трт, вр, впт','трт, вр, впт',NULL,'2026-06-05',NULL,NULL,'Планируется','В работе','2026-06-05 14:44:34','root@localhost'),(3,10,'ар','арвс','трт, вр, впт','трт, вр, впт','2026-06-05','2026-06-05',NULL,NULL,'В работе','В работе','2026-06-05 14:56:21','root@localhost');
/*!40000 ALTER TABLE `project_audit` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `project_stage`
--

DROP TABLE IF EXISTS `project_stage`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `project_stage` (
  `id` int NOT NULL AUTO_INCREMENT,
  `stage_id` int NOT NULL,
  `project_id` int NOT NULL,
  `planned_start_date` date NOT NULL,
  `planned_end_date` date NOT NULL,
  `actual_start_date` date DEFAULT NULL,
  `actual_end_date` date DEFAULT NULL,
  `status` varchar(30) DEFAULT NULL,
  `brigade_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_ps_project_id` (`project_id`),
  KEY `idx_ps_stage_id` (`stage_id`),
  KEY `idx_ps_brigade_id` (`brigade_id`),
  KEY `idx_ps_status` (`status`),
  KEY `idx_ps_dates` (`planned_start_date`,`planned_end_date`),
  CONSTRAINT `project_stage_ibfk_1` FOREIGN KEY (`brigade_id`) REFERENCES `brigade` (`id`),
  CONSTRAINT `project_stage_ibfk_2` FOREIGN KEY (`stage_id`) REFERENCES `stage` (`id`) ON DELETE CASCADE,
  CONSTRAINT `project_stage_ibfk_3` FOREIGN KEY (`project_id`) REFERENCES `project` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=42 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `project_stage`
--

LOCK TABLES `project_stage` WRITE;
/*!40000 ALTER TABLE `project_stage` DISABLE KEYS */;
INSERT INTO `project_stage` VALUES (1,1,1,'2026-01-01','2026-01-15',NULL,NULL,'Планируется',1),(2,2,1,'2026-01-16','2026-01-25',NULL,NULL,'Планируется',1),(3,3,1,'2026-01-26','2026-02-20',NULL,NULL,'Планируется',2),(4,4,1,'2026-02-21','2026-03-01',NULL,NULL,'Планируется',3),(5,5,1,'2026-03-02','2026-03-05',NULL,NULL,'Планируется',3),(6,1,2,'2026-02-01','2026-02-10','2026-02-01','2026-02-10','Завершен',1),(7,2,2,'2026-02-11','2026-02-20','2026-02-11',NULL,'В работе',1),(8,3,2,'2026-02-21','2026-03-10',NULL,NULL,'Планируется',2),(9,4,2,'2026-03-11','2026-03-20',NULL,NULL,'Планируется',3),(10,5,2,'2026-03-21','2026-03-25',NULL,NULL,'Планируется',3),(11,1,3,'2026-02-15','2026-02-25','2026-02-15','2026-02-25','Завершен',1),(12,2,3,'2026-02-26','2026-03-05','2026-02-26','2026-03-05','Завершен',1),(13,3,3,'2026-03-06','2026-03-25','2026-03-06',NULL,'В работе',2),(14,4,3,'2026-03-26','2026-04-05',NULL,NULL,'Планируется',3),(15,5,3,'2026-04-06','2026-04-10',NULL,NULL,'Планируется',3),(16,1,4,'2025-10-01','2025-10-10','2025-10-01','2025-10-09','Завершен',1),(17,2,4,'2025-10-11','2025-10-20','2025-10-11','2025-10-19','Завершен',1),(18,3,4,'2025-10-21','2025-11-20','2025-10-21','2025-11-18','Завершен',2),(19,4,4,'2025-11-21','2025-12-01','2025-11-21','2025-11-30','Завершен',3),(20,5,4,'2025-12-02','2026-02-01','2025-12-02','2026-02-01','Завершен',3),(21,1,5,'2025-09-01','2025-09-10','2025-09-01','2025-09-10','Завершен',1),(22,2,5,'2025-09-11','2025-09-20','2025-09-11','2025-09-19','Завершен',1),(23,3,5,'2025-09-21','2025-10-25','2025-09-21','2025-10-24','Завершен',2),(24,4,5,'2025-10-26','2025-11-10','2025-10-26','2025-11-09','Завершен',3),(25,5,5,'2025-11-11','2026-01-15','2025-11-11','2026-01-15','Завершен',3),(26,1,6,'2026-04-01','2026-04-10','2026-04-01','2026-04-09','Завершен',1),(27,2,6,'2026-04-11','2026-04-20','2026-04-11',NULL,'В работе',2),(28,3,6,'2026-04-21','2026-05-10',NULL,NULL,'Планируется',2),(29,4,6,'2026-05-11','2026-05-20',NULL,NULL,'Планируется',3),(30,5,6,'2026-05-21','2026-05-25',NULL,NULL,'Планируется',3);
/*!40000 ALTER TABLE `project_stage` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `specialty`
--

DROP TABLE IF EXISTS `specialty`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `specialty` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `specialty`
--

LOCK TABLES `specialty` WRITE;
/*!40000 ALTER TABLE `specialty` DISABLE KEYS */;
INSERT INTO `specialty` VALUES (1,'Бригадир'),(2,'Проектировщик'),(3,'Инженер ОВиК'),(4,'Электромонтажник'),(5,'Монтажник'),(6,'Инженер КИПиА'),(7,'Отделочник'),(8,'Технадзор'),(9,'Менеджер проектов'),(10,'Директор'),(11,'Администратор'),(12,'Бухгалтер');
/*!40000 ALTER TABLE `specialty` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `stage`
--

DROP TABLE IF EXISTS `stage`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `stage` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `stage`
--

LOCK TABLES `stage` WRITE;
/*!40000 ALTER TABLE `stage` DISABLE KEYS */;
INSERT INTO `stage` VALUES (1,'Проектирование'),(2,'Подготовка'),(3,'Монтаж'),(4,'Настройка и проверка'),(5,'Сдача');
/*!40000 ALTER TABLE `stage` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `stage_material`
--

DROP TABLE IF EXISTS `stage_material`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `stage_material` (
  `id` int NOT NULL AUTO_INCREMENT,
  `project_stage_id` int NOT NULL,
  `material_id` int NOT NULL,
  `planned_quantity` decimal(10,2) NOT NULL,
  `actual_quantity` decimal(10,2) DEFAULT '0.00',
  PRIMARY KEY (`id`),
  KEY `idx_sm_project_stage_id` (`project_stage_id`),
  KEY `idx_sm_material_id` (`material_id`),
  CONSTRAINT `stage_material_ibfk_1` FOREIGN KEY (`project_stage_id`) REFERENCES `project_stage` (`id`) ON DELETE CASCADE,
  CONSTRAINT `stage_material_ibfk_2` FOREIGN KEY (`material_id`) REFERENCES `material` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `stage_material`
--

LOCK TABLES `stage_material` WRITE;
/*!40000 ALTER TABLE `stage_material` DISABLE KEYS */;
INSERT INTO `stage_material` VALUES (1,6,6,200.00,190.00),(2,6,4,20.00,18.00),(3,7,9,5000.00,3000.00),(4,7,2,1000.00,600.00),(5,13,1,3000.00,1500.00),(6,13,2,2000.00,1200.00),(7,13,3,500.00,200.00),(8,16,6,300.00,280.00),(9,17,9,4000.00,3900.00),(10,18,1,3500.00,3400.00),(11,18,5,1500.00,1450.00),(12,19,4,120.00,115.00),(13,20,8,25.00,25.00),(14,21,6,250.00,240.00),(15,22,9,3000.00,2950.00),(16,23,1,3200.00,3100.00),(17,23,5,1400.00,1350.00),(18,24,4,110.00,105.00),(19,25,8,20.00,20.00),(20,26,1,1000.00,800.00),(21,26,2,500.00,500.00),(22,26,3,100.00,140.00),(23,26,4,50.00,30.00),(24,26,5,300.00,420.00);
/*!40000 ALTER TABLE `stage_material` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `task`
--

DROP TABLE IF EXISTS `task`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `task` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `description` text,
  `project_stage_id` int NOT NULL,
  `planned_start_datetime` datetime NOT NULL,
  `planned_end_datetime` datetime NOT NULL,
  `actual_start_datetime` datetime DEFAULT NULL,
  `actual_end_datetime` datetime DEFAULT NULL,
  `status` varchar(30) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_task_project_stage_id` (`project_stage_id`),
  KEY `idx_task_status` (`status`),
  KEY `idx_task_dates` (`planned_start_datetime`,`planned_end_datetime`),
  CONSTRAINT `task_ibfk_1` FOREIGN KEY (`project_stage_id`) REFERENCES `project_stage` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `task`
--

LOCK TABLES `task` WRITE;
/*!40000 ALTER TABLE `task` DISABLE KEYS */;
INSERT INTO `task` VALUES (1,'Разработка планировочных решений','Создание чертежей чистых помещений',6,'2026-02-01 09:00:00','2026-02-05 18:00:00','2026-02-01 09:00:00','2026-02-05 17:00:00','Завершена'),(2,'Согласование проекта','Утверждение документации',6,'2026-02-06 09:00:00','2026-02-10 18:00:00','2026-02-06 09:00:00','2026-02-10 16:00:00','Завершена'),(3,'Подготовка площадки','Очистка и разметка',7,'2026-02-11 09:00:00','2026-02-12 18:00:00','2026-02-11 09:00:00','2026-02-12 17:00:00','Завершена'),(4,'Доставка материалов','Поставка комплектующих',7,'2026-02-13 09:00:00','2026-02-14 18:00:00','2026-02-13 10:00:00',NULL,'В работе'),(5,'Проверка коммуникаций','Осмотр инженерных систем',7,'2026-02-15 09:00:00','2026-02-16 18:00:00','2026-05-30 01:03:58',NULL,'Планируется'),(6,'Проектирование зон','Разделение чистых зон',11,'2026-02-15 09:00:00','2026-02-20 18:00:00','2026-02-15 09:00:00','2026-02-20 17:00:00','Завершена'),(7,'Подготовка основания','Подготовка пола',12,'2026-02-26 09:00:00','2026-03-01 18:00:00','2026-02-26 09:00:00','2026-03-01 17:00:00','Завершена'),(8,'Монтаж стеновых панелей','Установка каркаса и панелей',13,'2026-03-06 08:00:00','2026-03-15 18:00:00','2026-03-06 08:00:00',NULL,'В работе'),(9,'Монтаж потолков','Установка потолков',13,'2026-03-10 08:00:00','2026-03-18 18:00:00','2026-05-30 01:03:58',NULL,'Планируется'),(10,'Установка дверей','Монтаж герметичных дверей',13,'2026-03-16 08:00:00','2026-03-20 18:00:00','2026-05-30 01:03:58',NULL,'Планируется'),(11,'Проектирование','Разработка проекта',16,'2025-10-01 09:00:00','2025-10-10 18:00:00','2025-10-01 09:00:00','2025-10-09 17:00:00','Завершена'),(12,'Подготовка площадки','Очистка',17,'2025-10-11 09:00:00','2025-10-20 18:00:00','2025-10-11 09:00:00','2025-10-19 17:00:00','Завершена'),(13,'Монтаж стен','Установка панелей',18,'2025-10-21 08:00:00','2025-11-05 18:00:00','2025-10-21 08:00:00','2025-11-04 17:00:00','Завершена'),(14,'Монтаж вентиляции','Воздуховоды',18,'2025-10-25 08:00:00','2025-11-10 18:00:00','2025-10-25 08:00:00','2025-11-09 16:00:00','Завершена'),(15,'Пусконаладка','Настройка систем',19,'2025-11-21 09:00:00','2025-12-01 18:00:00','2025-11-21 09:00:00','2025-11-30 17:00:00','Завершена'),(16,'Сдача объекта','Передача заказчику',20,'2025-12-02 09:00:00','2026-02-01 18:00:00','2025-12-02 09:00:00','2026-02-01 16:00:00','Завершена'),(17,'Разработка концепции','Определение структуры чистых зон',21,'2025-09-01 09:00:00','2025-09-05 18:00:00','2025-09-01 09:00:00','2025-09-05 17:00:00','Завершена'),(18,'Подготовка проектной документации','Чертежи и схемы',21,'2025-09-06 09:00:00','2025-09-10 18:00:00','2025-09-06 09:00:00','2025-09-10 16:00:00','Завершена'),(19,'Очистка площадки','Удаление мусора и подготовка зоны',22,'2025-09-11 09:00:00','2025-09-15 18:00:00','2025-09-11 09:00:00','2025-09-15 17:00:00','Завершена'),(20,'Разметка помещений','Нанесение разметки',22,'2025-09-16 09:00:00','2025-09-20 18:00:00','2025-09-16 09:00:00','2025-09-19 17:00:00','Завершена'),(21,'Монтаж стен','Установка панелей',23,'2025-09-21 08:00:00','2025-10-10 18:00:00','2025-09-21 08:00:00','2025-10-09 17:00:00','Завершена'),(22,'Монтаж инженерных систем','Вентиляция и электрика',23,'2025-09-25 08:00:00','2025-10-20 18:00:00','2025-09-25 08:00:00','2025-10-19 17:00:00','Завершена'),(23,'Пусконаладка вентиляции','Настройка воздухообмена',24,'2025-10-26 09:00:00','2025-11-05 18:00:00','2025-10-26 09:00:00','2025-11-04 17:00:00','Завершена'),(24,'Тестирование систем','Проверка всех систем',24,'2025-11-06 09:00:00','2025-11-10 18:00:00','2025-11-06 09:00:00','2025-11-09 17:00:00','Завершена'),(25,'Контроль чистоты','Замеры',25,'2025-12-20 09:00:00','2025-12-25 18:00:00','2025-12-20 09:00:00','2025-12-25 17:00:00','Завершена'),(26,'Сдача заказчику','Подписание актов',25,'2025-12-26 10:00:00','2026-01-15 16:00:00','2025-12-26 10:00:00','2026-01-15 15:00:00','Завершена'),(27,'Разработка технического задания','Подготовка технической документации',26,'2026-04-01 09:00:00','2026-04-05 18:00:00','2026-04-01 09:00:00','2026-04-03 17:00:00','Завершена'),(28,'Подготовка проектной документации','Создание чертежей и схем',26,'2026-04-04 09:00:00','2026-04-08 18:00:00','2026-04-04 09:00:00','2026-04-08 18:00:00','Завершена'),(29,'Согласование документации','Проверка и утверждение проекта',26,'2026-04-06 09:00:00','2026-04-10 18:00:00','2026-04-06 09:00:00','2026-04-13 18:00:00','Завершена'),(30,'Подготовка строительной площадки','Очистка и разметка территории',27,'2026-04-11 09:00:00','2026-04-15 18:00:00','2026-04-11 09:00:00',NULL,'В работе'),(31,'Поставка материалов','Доставка оборудования и материалов',27,'2026-04-16 09:00:00','2026-04-20 18:00:00','2026-05-30 01:04:10',NULL,'Планируется');
/*!40000 ALTER TABLE `task` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `set_task_start_time` BEFORE INSERT ON `task` FOR EACH ROW BEGIN
    IF NEW.actual_start_datetime IS NULL THEN
        SET NEW.actual_start_datetime = NOW();
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `set_task_end_time` BEFORE UPDATE ON `task` FOR EACH ROW BEGIN
    IF NEW.status = 'завершено' AND OLD.status <> 'завершено' THEN
        SET NEW.actual_end_datetime = NOW();
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `user_presence`
--

DROP TABLE IF EXISTS `user_presence`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_presence` (
  `user_id` int NOT NULL,
  `is_online` tinyint(1) NOT NULL DEFAULT '0',
  `last_seen_at` datetime DEFAULT NULL,
  `last_logout_at` datetime DEFAULT NULL,
  `last_role` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`user_id`),
  CONSTRAINT `fk_user_presence_username` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_presence`
--

LOCK TABLES `user_presence` WRITE;
/*!40000 ALTER TABLE `user_presence` DISABLE KEYS */;
INSERT INTO `user_presence` VALUES (1,1,'2026-06-20 15:02:28','2026-06-06 02:18:18','dba'),(2,0,'2026-06-05 14:07:09','2026-06-05 14:17:12','director'),(8,1,'2026-06-05 16:19:09',NULL,'accountant'),(9,0,'2026-06-05 15:56:56','2026-06-05 16:13:07','project_manager'),(10,1,'2026-06-05 15:07:16',NULL,'foreman'),(11,1,'2026-06-05 15:24:59',NULL,'employee');
/*!40000 ALTER TABLE `user_presence` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(20) NOT NULL,
  `password` varchar(255) NOT NULL,
  `worker_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `worker_id` (`worker_id`),
  CONSTRAINT `users_ibfk_1` FOREIGN KEY (`worker_id`) REFERENCES `worker` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'dba_user','gAAAAABqGg8-tIGK-9Wt33fTcRCqfqc55Y0EfWUeKKtFoWmfj52g4f83aXilhMh9MtFSpUTE1Ya8Q8nB5eQniA-aHRgTAzmpNg==',14),(2,'director_user','gAAAAABqGg-g9joQvAdTp2xoL6V3vVRht9L5fES5z2REpvJKU8u7kSvPrXyD_VsMkLFnFC93m9bhraL8qOj9y7uBkbe8RkLGFQ==',13),(8,'accountant_user','password',15),(9,'manager_user','password',12),(10,'foreman_user','password',1),(11,'employee_user','password',8);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `work_log`
--

DROP TABLE IF EXISTS `work_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `work_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `task_id` int NOT NULL,
  `worker_id` int NOT NULL,
  `hours_spent` decimal(5,2) NOT NULL,
  `work_date` date NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_work_log_task_id` (`task_id`),
  KEY `idx_work_log_worker_id` (`worker_id`),
  KEY `idx_work_log_date` (`work_date`),
  CONSTRAINT `work_log_ibfk_1` FOREIGN KEY (`task_id`) REFERENCES `task` (`id`) ON DELETE CASCADE,
  CONSTRAINT `work_log_ibfk_2` FOREIGN KEY (`worker_id`) REFERENCES `worker` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=54 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `work_log`
--

LOCK TABLES `work_log` WRITE;
/*!40000 ALTER TABLE `work_log` DISABLE KEYS */;
INSERT INTO `work_log` VALUES (1,1,4,6.00,'2026-02-01'),(2,1,5,5.50,'2026-02-01'),(3,2,4,6.00,'2026-02-06'),(4,3,8,7.00,'2026-02-11'),(5,4,8,5.00,'2026-02-13'),(6,4,9,5.50,'2026-02-13'),(7,5,9,0.00,'2026-02-13'),(8,6,4,6.00,'2026-02-15'),(9,7,8,6.50,'2026-02-26'),(10,8,8,7.00,'2026-03-06'),(11,8,9,7.50,'2026-03-06'),(12,9,8,8.00,'2026-03-07'),(13,10,6,6.00,'2026-03-09'),(14,11,4,6.00,'2025-10-01'),(15,12,8,6.00,'2025-10-11'),(16,13,8,7.00,'2025-10-21'),(17,14,6,6.50,'2025-10-25'),(18,15,7,6.00,'2025-11-21'),(19,16,3,5.00,'2025-12-02'),(20,17,7,6.00,'2025-12-20'),(21,18,3,5.50,'2025-12-26'),(22,19,4,6.00,'2025-09-01'),(23,19,5,5.50,'2025-09-01'),(24,20,4,6.00,'2025-09-06'),(25,20,5,5.00,'2025-09-07'),(26,21,8,6.50,'2025-09-11'),(27,21,9,6.00,'2025-09-11'),(28,22,8,5.50,'2025-09-16'),(29,22,9,5.00,'2025-09-16'),(30,23,8,7.00,'2025-09-21'),(31,23,9,7.50,'2025-09-21'),(32,23,6,4.00,'2025-09-22'),(33,24,6,6.50,'2025-09-25'),(34,24,7,6.00,'2025-09-25'),(35,24,10,5.50,'2025-09-26'),(36,25,7,6.00,'2025-10-26'),(37,25,1,5.00,'2025-10-27'),(38,26,7,0.00,'2025-11-06'),(39,26,3,5.50,'2025-11-06'),(40,27,4,6.00,'2026-04-01'),(41,27,5,6.50,'2026-04-02'),(42,28,4,7.00,'2026-04-04'),(43,28,5,6.50,'2026-04-05'),(44,29,4,8.00,'2026-04-06'),(45,29,1,6.00,'2026-04-11'),(46,30,8,8.50,'2026-04-11'),(47,30,9,6.00,'2026-04-12');
/*!40000 ALTER TABLE `work_log` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `validate_work_hours` BEFORE INSERT ON `work_log` FOR EACH ROW BEGIN
    IF NEW.hours_spent > 24 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Некорректное количество часов';
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `worker`
--

DROP TABLE IF EXISTS `worker`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `worker` (
  `id` int NOT NULL AUTO_INCREMENT,
  `surname` varchar(50) NOT NULL,
  `name` varchar(50) NOT NULL,
  `patronymic` varchar(50) DEFAULT NULL,
  `phone_number` varchar(20) DEFAULT NULL,
  `specialty_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `phone_number` (`phone_number`),
  KEY `idx_worker_specialty_id` (`specialty_id`),
  CONSTRAINT `worker_ibfk_1` FOREIGN KEY (`specialty_id`) REFERENCES `specialty` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `worker`
--

LOCK TABLES `worker` WRITE;
/*!40000 ALTER TABLE `worker` DISABLE KEYS */;
INSERT INTO `worker` VALUES (1,'Иванов','Алексей','Петрович','79000000001',1),(2,'Смирнов','Дмитрий','Сергеевич','79000000002',1),(3,'Кузнецов','Игорь','Владимирович','79000000003',1),(4,'Соколов','Андрей','Игоревич','79000000004',2),(5,'Федоров','Антон','Евгеньевич','79000000005',3),(6,'Орлов','Сергей','Дмитриевич','79000000006',4),(7,'Белов','Константин','Юрьевич','79000000007',6),(8,'Петров','Олег','Игоревич','79000000008',5),(9,'Сидоров','Максим','Андреевич','79000000009',5),(10,'Новиков','Роман','Алексеевич','79000000010',7),(11,'Егоров','Илья','Станиславович','79000000011',8),(12,'Иванов','Алексей','Сергеевич','+79161234567',9),(13,'Петрова','Мария','Владимировна','+79162345678',10),(14,'Сидоров','Дмитрий','Анатольевич','+79163456789',11),(15,'Николаева','Елена','Ивановна','+79164567890',12);
/*!40000 ALTER TABLE `worker` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-06-20 18:59:14
