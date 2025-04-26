-- -----------------------------------------------------
-- MySQL Script para Canicross Application
-- -----------------------------------------------------

-- 1. CREAR LA BASE DE DATOS (si no existe)
CREATE DATABASE IF NOT EXISTS canicross CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 2. CREAR USUARIO (si no existe)
CREATE USER IF NOT EXISTS 'canicross'@'localhost' IDENTIFIED BY 'L8934-!thgurebvHGRTtnbhg*32';
GRANT ALL PRIVILEGES ON canicross.* TO 'canicross'@'localhost';
FLUSH PRIVILEGES;

-- 3. PERMITIR CONEXIONES IPv6 (si necesario)
CREATE USER IF NOT EXISTS 'canicross'@'::1' IDENTIFIED BY 'L8934-!thgurebvHGRTtnbhg*32';
GRANT ALL PRIVILEGES ON canicross.* TO 'canicross'@'::1';

-- 3.1 PERMITIR CONEXIONES REMOTAS (descomente si necesita acceso desde otra máquina)
-- CREATE USER IF NOT EXISTS 'canicross'@'%' IDENTIFIED BY 'L8934-!thgurebvHGRTtnbhg*32';
-- GRANT ALL PRIVILEGES ON canicross.* TO 'canicross'@'%';

FLUSH PRIVILEGES;

-- 4. USAR LA BASE DE DATOS
USE canicross;

-- -----------------------------------------------------
-- IMPORTANTE: Para crear las tablas de la base de datos,
-- existen dos opciones:
-- -----------------------------------------------------

-- OPCIÓN 1 (RECOMENDADA): Usar Django Migrations
-- Ejecuta el siguiente comando desde la línea de comandos:
-- python manage.py migrate

-- OPCIÓN 2: Si prefieres crear las tablas manualmente, 
-- puedes usar el archivo mysql_structure.sql que contiene toda 
-- la estructura de tablas generada por Django.
-- mysql -u canicross -p canicross < mysql_structure.sql

-- -----------------------------------------------------
-- CREACIÓN DE DATOS INICIALES
-- -----------------------------------------------------

-- Datos de ejemplo para la tabla de Modalidades
INSERT INTO events_modality (name, description) VALUES 
('Canicross', 'Carrera a pie junto a un perro'),
('Bikejoring', 'Bicicleta tirada por uno o dos perros'),
('Scooter', 'Patinete tirado por uno o dos perros'),
('Skijoring', 'Esquí tirado por uno o dos perros');

-- Datos de ejemplo para la tabla de Categorías
INSERT INTO events_category (name, gender, min_age, max_age, description) VALUES 
('Junior Masculino', 'M', 15, 17, 'Categoría para jóvenes masculinos'),
('Junior Femenino', 'F', 15, 17, 'Categoría para jóvenes femeninas'),
('Senior Masculino', 'M', 18, 39, 'Categoría para adultos masculinos'),
('Senior Femenino', 'F', 18, 39, 'Categoría para adultas femeninas'),
('Veterano Masculino', 'M', 40, 99, 'Categoría para veteranos masculinos'),
('Veterana Femenina', 'F', 40, 99, 'Categoría para veteranas femeninas');

-- Datos de ejemplo para la tabla de Tipos de Penalización
INSERT INTO events_penaltytype (name, description, time_penalty, is_disqualification) VALUES 
('Conducción Peligrosa', 'Conducción que pone en peligro a otros participantes', '00:01:30', 0),
('Maltrato Animal', 'Cualquier acción que se considere maltrato animal', NULL, 1),
('Salida Anticipada', 'Salir antes de la señal oficial', '00:00:30', 0),
('Acortar Recorrido', 'No seguir el recorrido oficial', NULL, 1),
('Ayuda Externa', 'Recibir ayuda no permitida durante la carrera', '00:01:00', 0);

-- -----------------------------------------------------
-- IMPORTANTE: Para crear un superusuario (administrador),
-- ejecuta el siguiente comando desde la línea de comandos:
-- python manage.py createsuperuser
-- -----------------------------------------------------