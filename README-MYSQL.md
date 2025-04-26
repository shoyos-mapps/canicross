# Configuración de MySQL para Canicross

## Archivos SQL Incluidos

Este proyecto incluye los siguientes archivos SQL para la configuración de MySQL:

1. `mysql_instructions.sql` - Script básico con instrucciones para crear la base de datos y credenciales
2. `mysql_structure_fixed.sql` - Script completo con la estructura de todas las tablas optimizada para MySQL

## Migración Rápida a MySQL

Para migrar la aplicación a MySQL:

1. Crea la base de datos y el usuario:
   ```sql
   CREATE DATABASE canicross CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   CREATE USER 'canicross'@'localhost' IDENTIFIED BY 'L8934-!thgurebvHGRTtnbhg*32';
   GRANT ALL PRIVILEGES ON canicross.* TO 'canicross'@'localhost';
   FLUSH PRIVILEGES;
   ```

2. Ejecuta el script de estructura para crear todas las tablas:
   ```bash
   mysql -u canicross -p canicross < mysql_structure_fixed.sql
   ```

3. Edita el archivo `.env` para descomentar las líneas de configuración de MySQL:
   ```
   DB_ENGINE=django.db.backends.mysql
   DB_NAME=canicross
   DB_USER=canicross
   DB_PASSWORD=L8934-!thgurebvHGRTtnbhg*32
   DB_HOST=localhost
   DB_PORT=3306
   ```

4. Crea un superusuario para acceder al panel de administración:
   ```bash
   python manage.py createsuperuser
   ```

## Solución de Problemas

### Error de conexión IPv6

Si recibes un error como `Host '::1' is not allowed to connect to this MySQL server`, prueba una de estas soluciones:

1. Si tienes problemas con IPv6, puedes probar estas opciones:
   ```
   DB_HOST=localhost
   ```

2. Actualiza los permisos de MySQL para permitir conexiones desde IPv6:
   ```sql
   CREATE USER 'canicross'@'::1' IDENTIFIED BY 'L8934-!thgurebvHGRTtnbhg*32';
   GRANT ALL PRIVILEGES ON canicross.* TO 'canicross'@'::1';
   FLUSH PRIVILEGES;
   ```

### Tablas de Autenticación Django

Si encuentras errores al crear las tablas, asegúrate de que el orden de creación sea correcto (las tablas de Django como `django_content_type` deben crearse antes de las tablas que dependen de ellas). En ese caso, puedes usar las migraciones de Django:

```bash
python manage.py migrate auth
python manage.py migrate contenttypes
python manage.py migrate admin
python manage.py migrate sessions
python manage.py migrate accounts
# ... y así con el resto de las aplicaciones
```

## Insertar Datos Iniciales

El archivo `mysql_instructions.sql` incluye ejemplos para insertar datos iniciales:

```sql
-- Insertar modalidades básicas
INSERT INTO events_modality (name, description) VALUES 
('Canicross', 'Carrera a pie junto a un perro'),
('Bikejoring', 'Bicicleta tirada por uno o dos perros');

-- Insertar categorías
INSERT INTO events_category (name, gender, min_age, max_age, description) VALUES 
('Senior Masculino', 'M', 18, 39, 'Categoría para adultos masculinos'),
('Senior Femenino', 'F', 18, 39, 'Categoría para adultas femeninas');
```

## Backup y Restauración

Para hacer respaldo de la base de datos:

```bash
mysqldump -u canicross -p canicross > backup.sql
```

Para restaurar:

```bash
mysql -u canicross -p canicross < backup.sql
```