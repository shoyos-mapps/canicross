-- Script para eliminar todas las tablas existentes y recrear la base de datos
-- ADVERTENCIA: Este script eliminará TODOS los datos existentes en la base de datos canicross

-- Desactivar verificación de llaves foráneas para permitir eliminar tablas con dependencias
SET FOREIGN_KEY_CHECKS = 0;

-- Eliminar base de datos existente y recrearla
DROP DATABASE IF EXISTS canicross;
CREATE DATABASE canicross CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE canicross;

-- Asegurar que el usuario existe y tiene los permisos adecuados
-- (Si el usuario ya existe, estas sentencias no harán nada malo)
CREATE USER IF NOT EXISTS 'canicross'@'localhost' IDENTIFIED BY 'L8934-!thgurebvHGRTtnbhg*32';
GRANT ALL PRIVILEGES ON canicross.* TO 'canicross'@'localhost';

-- Soporte para conexiones desde IPv6 si es necesario
CREATE USER IF NOT EXISTS 'canicross'@'::1' IDENTIFIED BY 'L8934-!thgurebvHGRTtnbhg*32';
GRANT ALL PRIVILEGES ON canicross.* TO 'canicross'@'::1';

-- Permitir conexiones desde otros hosts si se necesita acceso remoto
-- CREATE USER IF NOT EXISTS 'canicross'@'%' IDENTIFIED BY 'L8934-!thgurebvHGRTtnbhg*32';
-- GRANT ALL PRIVILEGES ON canicross.* TO 'canicross'@'%';

FLUSH PRIVILEGES;

-- Activar nuevamente la verificación de llaves foráneas
SET FOREIGN_KEY_CHECKS = 1;

-- Mostrar confirmación
SELECT 'La base de datos canicross ha sido reiniciada correctamente.' as Mensaje;

-- NOTA: Después de ejecutar este script, se debe importar la estructura de tablas:
-- mysql -ucanicross -p'L8934-!thgurebvHGRTtnbhg*32' canicross < mysql_structure_fixed.sql