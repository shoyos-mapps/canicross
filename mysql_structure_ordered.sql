-- MySQL Script para Canicross - Generado desde Django
-- Versión ajustada para MySQL con orden correcto de creación de tablas

-- -----------------------------------------------------
-- Desactivar verificación de llaves foráneas temporalmente
-- -----------------------------------------------------
SET FOREIGN_KEY_CHECKS = 0;

-- -----------------------------------------------------
-- Tablas de sistema de Django (deben crearse primero)
-- -----------------------------------------------------

-- Tabla django_content_type
CREATE TABLE IF NOT EXISTS `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model` (`app_label`,`model`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla auth_group
CREATE TABLE IF NOT EXISTS `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla auth_permission
CREATE TABLE IF NOT EXISTS `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_ibfk_1` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla django_migrations
CREATE TABLE IF NOT EXISTS `django_migrations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla django_session
CREATE TABLE IF NOT EXISTS `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------
-- Tablas de autenticación y usuarios
-- -----------------------------------------------------

-- Tabla accounts_user
CREATE TABLE IF NOT EXISTS `accounts_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime NOT NULL,
  `user_type` varchar(20) NOT NULL,
  `phone_number` varchar(20) DEFAULT NULL,
  `profile_picture` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla accounts_user_groups
CREATE TABLE IF NOT EXISTS `accounts_user_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `accounts_user_groups_user_id_group_id` (`user_id`,`group_id`),
  KEY `group_id` (`group_id`),
  CONSTRAINT `accounts_user_groups_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `accounts_user_groups_ibfk_2` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla accounts_user_user_permissions
CREATE TABLE IF NOT EXISTS `accounts_user_user_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `accounts_user_user_permissions_user_id_permission_id` (`user_id`,`permission_id`),
  KEY `permission_id` (`permission_id`),
  CONSTRAINT `accounts_user_user_permissions_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `accounts_user_user_permissions_ibfk_2` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla django_admin_log
CREATE TABLE IF NOT EXISTS `django_admin_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_time` datetime NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint UNSIGNED NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `content_type_id` (`content_type_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `django_admin_log_ibfk_1` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------
-- Tablas de eventos
-- -----------------------------------------------------

-- Tabla events_category
CREATE TABLE IF NOT EXISTS `events_category` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `gender` varchar(1) NOT NULL,
  `min_age` smallint UNSIGNED NOT NULL,
  `max_age` smallint UNSIGNED NOT NULL,
  `description` text NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla events_event
CREATE TABLE IF NOT EXISTS `events_event` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `slug` varchar(255) NOT NULL,
  `description` text NOT NULL,
  `location` varchar(255) NOT NULL,
  `start_date` date NOT NULL,
  `end_date` date NOT NULL,
  `rules` text NOT NULL,
  `registration_start` datetime NOT NULL,
  `registration_end` datetime NOT NULL,
  `required_documents` json NOT NULL,
  `required_vaccines` json NOT NULL,
  `status` varchar(20) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `slug` (`slug`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla events_modality
CREATE TABLE IF NOT EXISTS `events_modality` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `description` text NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla events_penaltytype
CREATE TABLE IF NOT EXISTS `events_penaltytype` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `description` text NOT NULL,
  `time_penalty` time DEFAULT NULL,
  `is_disqualification` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla events_race
CREATE TABLE IF NOT EXISTS `events_race` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `distance` decimal(5,2) NOT NULL,
  `description` text NOT NULL,
  `start_type` varchar(10) NOT NULL,
  `participants_per_interval` smallint UNSIGNED NOT NULL,
  `interval_seconds` smallint UNSIGNED NOT NULL,
  `max_participants` int(11) UNSIGNED NOT NULL,
  `race_date` date NOT NULL,
  `race_time` time NOT NULL,
  `actual_start_time` datetime DEFAULT NULL,
  `event_id` int(11) NOT NULL,
  `modality_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `event_id` (`event_id`),
  KEY `modality_id` (`modality_id`),
  CONSTRAINT `events_race_ibfk_1` FOREIGN KEY (`event_id`) REFERENCES `events_event` (`id`),
  CONSTRAINT `events_race_ibfk_2` FOREIGN KEY (`modality_id`) REFERENCES `events_modality` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla events_racecategory
CREATE TABLE IF NOT EXISTS `events_racecategory` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `price` decimal(8,2) NOT NULL,
  `quota` int(11) UNSIGNED NOT NULL,
  `category_id` int(11) NOT NULL,
  `race_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `events_racecategory_race_id_category_id` (`race_id`,`category_id`),
  KEY `category_id` (`category_id`),
  CONSTRAINT `events_racecategory_ibfk_1` FOREIGN KEY (`category_id`) REFERENCES `events_category` (`id`),
  CONSTRAINT `events_racecategory_ibfk_2` FOREIGN KEY (`race_id`) REFERENCES `events_race` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------
-- Tablas de participantes
-- -----------------------------------------------------

-- Tabla participants_participant
CREATE TABLE IF NOT EXISTS `participants_participant` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `first_name` varchar(100) NOT NULL,
  `last_name` varchar(100) NOT NULL,
  `id_document` varchar(20) NOT NULL,
  `date_of_birth` date NOT NULL,
  `gender` varchar(1) NOT NULL,
  `email` varchar(254) NOT NULL,
  `phone` varchar(20) NOT NULL,
  `address` varchar(255) NOT NULL,
  `city` varchar(100) NOT NULL,
  `state_province` varchar(100) NOT NULL,
  `country` varchar(100) NOT NULL,
  `postal_code` varchar(20) NOT NULL,
  `club` varchar(100) NOT NULL,
  `emergency_contact_name` varchar(200) NOT NULL,
  `emergency_contact_phone` varchar(20) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `participants_participant_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla participants_dog
CREATE TABLE IF NOT EXISTS `participants_dog` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `breed` varchar(100) NOT NULL,
  `date_of_birth` date DEFAULT NULL,
  `gender` varchar(1) NOT NULL,
  `microchip_number` varchar(100) NOT NULL,
  `veterinary_book_number` varchar(100) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `owner_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `owner_id` (`owner_id`),
  CONSTRAINT `participants_dog_ibfk_1` FOREIGN KEY (`owner_id`) REFERENCES `participants_participant` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------
-- Tablas de inscripciones
-- -----------------------------------------------------

-- Tabla registrations_registration
CREATE TABLE IF NOT EXISTS `registrations_registration` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `bib_number` int(11) UNSIGNED DEFAULT NULL,
  `registration_status` varchar(20) NOT NULL,
  `payment_status` varchar(20) NOT NULL,
  `payment_method` varchar(50) NOT NULL,
  `payment_reference` varchar(100) NOT NULL,
  `ai_vaccine_status` varchar(20) NOT NULL,
  `vet_check_status` varchar(20) NOT NULL,
  `vet_check_time` datetime DEFAULT NULL,
  `vet_checker_details` text NOT NULL,
  `kit_delivered` tinyint(1) NOT NULL,
  `kit_delivery_time` datetime DEFAULT NULL,
  `checked_in` tinyint(1) NOT NULL,
  `checkin_time` datetime DEFAULT NULL,
  `notes` text NOT NULL,
  `waiver_accepted` tinyint(1) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `dog_id` int(11) NOT NULL,
  `participant_id` int(11) NOT NULL,
  `race_id` int(11) NOT NULL,
  `race_category_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `registrations_registration_race_id_bib_number` (`race_id`,`bib_number`),
  KEY `dog_id` (`dog_id`),
  KEY `participant_id` (`participant_id`),
  KEY `race_category_id` (`race_category_id`),
  CONSTRAINT `registrations_registration_ibfk_1` FOREIGN KEY (`dog_id`) REFERENCES `participants_dog` (`id`),
  CONSTRAINT `registrations_registration_ibfk_2` FOREIGN KEY (`participant_id`) REFERENCES `participants_participant` (`id`),
  CONSTRAINT `registrations_registration_ibfk_3` FOREIGN KEY (`race_id`) REFERENCES `events_race` (`id`),
  CONSTRAINT `registrations_registration_ibfk_4` FOREIGN KEY (`race_category_id`) REFERENCES `events_racecategory` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla registrations_participantannotation
CREATE TABLE IF NOT EXISTS `registrations_participantannotation` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `status` varchar(20) NOT NULL,
  `notes` text NOT NULL,
  `location` varchar(100) NOT NULL,
  `recorded_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `confirmed_by_id` int(11) DEFAULT NULL,
  `penalty_type_id` int(11) NOT NULL,
  `recorded_by_id` int(11) NOT NULL,
  `registration_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `confirmed_by_id` (`confirmed_by_id`),
  KEY `penalty_type_id` (`penalty_type_id`),
  KEY `recorded_by_id` (`recorded_by_id`),
  KEY `registration_id` (`registration_id`),
  CONSTRAINT `registrations_participantannotation_ibfk_1` FOREIGN KEY (`confirmed_by_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `registrations_participantannotation_ibfk_2` FOREIGN KEY (`penalty_type_id`) REFERENCES `events_penaltytype` (`id`),
  CONSTRAINT `registrations_participantannotation_ibfk_3` FOREIGN KEY (`recorded_by_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `registrations_participantannotation_ibfk_4` FOREIGN KEY (`registration_id`) REFERENCES `registrations_registration` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla registrations_document
CREATE TABLE IF NOT EXISTS `registrations_document` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `document_type` varchar(50) NOT NULL,
  `file` varchar(100) NOT NULL,
  `description` varchar(255) NOT NULL,
  `ocr_raw_text` text NOT NULL,
  `ocr_status` varchar(20) NOT NULL,
  `ocr_analysis_result` json NOT NULL,
  `uploaded_at` datetime NOT NULL,
  `registration_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `registration_id` (`registration_id`),
  CONSTRAINT `registrations_document_ibfk_1` FOREIGN KEY (`registration_id`) REFERENCES `registrations_registration` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------
-- Tablas de resultados
-- -----------------------------------------------------

-- Tabla results_raceresult
CREATE TABLE IF NOT EXISTS `results_raceresult` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `start_time` datetime DEFAULT NULL,
  `finish_time` datetime DEFAULT NULL,
  `base_time` time DEFAULT NULL,
  `official_time` time DEFAULT NULL,
  `status` varchar(20) NOT NULL,
  `overall_rank` int(11) UNSIGNED DEFAULT NULL,
  `modality_rank` int(11) UNSIGNED DEFAULT NULL,
  `category_rank` int(11) UNSIGNED DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `registration_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `registration_id` (`registration_id`),
  CONSTRAINT `results_raceresult_ibfk_1` FOREIGN KEY (`registration_id`) REFERENCES `registrations_registration` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------
-- Re-activar verificación de llaves foráneas
-- -----------------------------------------------------

SET FOREIGN_KEY_CHECKS = 1;

-- -----------------------------------------------------
-- Insertar datos para las migraciones de Django
-- -----------------------------------------------------

-- Crear entradas en la tabla de migraciones para evitar que Django intente migrar de nuevo
INSERT INTO django_migrations (app, name, applied) VALUES 
('contenttypes', '0001_initial', NOW()),
('contenttypes', '0002_remove_content_type_name', NOW()),
('auth', '0001_initial', NOW()),
('auth', '0002_alter_permission_name_max_length', NOW()),
('auth', '0003_alter_user_email_max_length', NOW()),
('auth', '0004_alter_user_username_opts', NOW()),
('auth', '0005_alter_user_last_login_null', NOW()),
('auth', '0006_require_contenttypes_0002', NOW()),
('auth', '0007_alter_validators_add_error_messages', NOW()),
('auth', '0008_alter_user_username_max_length', NOW()),
('auth', '0009_alter_user_last_name_max_length', NOW()),
('auth', '0010_alter_group_name_max_length', NOW()),
('auth', '0011_update_proxy_permissions', NOW()),
('auth', '0012_alter_user_first_name_max_length', NOW()),
('accounts', '0001_initial', NOW()),
('admin', '0001_initial', NOW()),
('admin', '0002_logentry_remove_auto_add', NOW()),
('admin', '0003_logentry_add_action_flag_choices', NOW()),
('events', '0001_initial', NOW()),
('participants', '0001_initial', NOW()),
('registrations', '0001_initial', NOW()),
('results', '0001_initial', NOW()),
('sessions', '0001_initial', NOW());

-- -----------------------------------------------------
-- Insertar datos iniciales para el funcionamiento básico
-- -----------------------------------------------------

-- Insertar modalidades de competición
INSERT INTO events_modality (name, description) VALUES 
('Canicross', 'Carrera a pie junto a un perro'),
('Bikejoring', 'Bicicleta tirada por uno o dos perros'),
('Scooter', 'Patinete tirado por uno o dos perros'),
('Skijoring', 'Esquí tirado por uno o dos perros');

-- Insertar categorías básicas
INSERT INTO events_category (name, gender, min_age, max_age, description) VALUES 
('Junior Masculino', 'M', 15, 17, 'Categoría para jóvenes masculinos'),
('Junior Femenino', 'F', 15, 17, 'Categoría para jóvenes femeninas'),
('Senior Masculino', 'M', 18, 39, 'Categoría para adultos masculinos'),
('Senior Femenino', 'F', 18, 39, 'Categoría para adultas femeninas'),
('Veterano Masculino', 'M', 40, 99, 'Categoría para veteranos masculinos'),
('Veterana Femenina', 'F', 40, 99, 'Categoría para veteranas femeninas');

-- Insertar tipos de penalización
INSERT INTO events_penaltytype (name, description, time_penalty, is_disqualification) VALUES 
('Conducción Peligrosa', 'Conducción que pone en peligro a otros participantes', '00:01:30', 0),
('Maltrato Animal', 'Cualquier acción que se considere maltrato animal', NULL, 1),
('Salida Anticipada', 'Salir antes de la señal oficial', '00:00:30', 0),
('Acortar Recorrido', 'No seguir el recorrido oficial', NULL, 1),
('Ayuda Externa', 'Recibir ayuda no permitida durante la carrera', '00:01:00', 0);