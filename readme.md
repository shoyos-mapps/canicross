# Aplicación de Gestión de Eventos de Canicross

Una aplicación web para gestionar eventos de canicross y modalidades relacionadas (Bikejoring, Scooter, etc.) con funcionalidades para configuración de eventos, inscripciones, aprobación veterinaria, entrega de kits, check-in, cronometraje de carreras y publicación de resultados.

> **IMPORTANTE**: Esta aplicación debe estar completamente en español, incluyendo todos los textos, etiquetas, mensajes y documentación.

## Funcionalidades

- **Gestión de Eventos**: Creación y configuración de eventos con múltiples modalidades y distancias
- **Inscripciones**: Gestión de inscripciones de participantes y perros para diferentes carreras y categorías
- **Verificación Veterinaria**: Verificación de documentos asistida por IA y aprobación veterinaria presencial
- **Entrega de Kits**: Seguimiento de entrega de kits a participantes inscritos
- **Gestión del Día de Carrera**: Check-in, cronometraje de inicio/fin de carrera, y gestión de penalizaciones
- **Publicación de Resultados**: Cálculo y publicación de resultados de carreras con clasificaciones

## Stack Tecnológico

- **Backend**: Django, Python 3.12
- **API REST**: Django REST Framework
- **Frontend**: Bootstrap 5 (actualmente templates renderizados en servidor)
- **Base de Datos**: SQLite (desarrollo), MySQL (producción)
- **Tareas Asíncronas**: Celery
- **Procesamiento de Documentos**: Integración con OCR e IA (opcional)
- **Sistema de Logs**: Sistema completo de registro de actividad con panel de administración

## Instalación y Configuración

### Requisitos Previos

- Python 3.12+
- pip
- (Opcional para producción) MySQL, Redis

### Instalación

1. Clonar el repositorio:
   ```bash
   git clone <repository-url>
   cd canicross
   ```

2. Crear un entorno virtual y activarlo:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Configurar variables de entorno:
   ```bash
   cp .env.example .env
   # Editar el archivo .env con tu configuración
   ```

5. Aplicar migraciones de base de datos:
   ```bash
   python manage.py migrate
   ```

6. Crear un superusuario:
   ```bash
   python manage.py createsuperuser
   ```

7. Ejecutar el servidor de desarrollo:
   ```bash
   python manage.py runserver
   ```

8. Acceder a la interfaz de administración en:
   ```
   http://192.168.193.200:7080/admin/
   ```

## Estructura del Proyecto

- `accounts`: Autenticación y perfiles de usuarios
- `events`: Gestión de eventos, carreras y categorías
- `participants`: Perfiles de participantes (corredores) y perros
- `registrations`: Gestión de inscripciones y documentos
- `veterinary`: Flujo de aprobación veterinaria
- `kits`: Gestión de entrega de kits
- `checkin`: Check-in del día de carrera
- `race_management`: Cronometraje y gestión de carreras
- `results`: Cálculo y visualización de resultados
- `api`: Endpoints de la API REST
- `utils`: Funciones de utilidad, incluyendo sistema de logs
- `logs`: Directorio que contiene los logs de la aplicación (creado automáticamente)

## Sistema de Logs

La aplicación incluye un sistema completo de logs con las siguientes características:

- Archivos de log separados para diferentes tipos de información (info, errores, API, etc.)
- Rotación automática de logs
- Panel de administración para visualización y análisis de logs
- Utilidad de línea de comandos para análisis de logs

Para información detallada, consulte [README-LOGS.md](README-LOGS.md).

## Documentación de la API

La documentación de la API está disponible en:
```
http://192.168.193.200:7080/api/docs/
```

## Variables de Entorno

Consulte `.env.example` para las variables de entorno requeridas.

## Acceso de Administrador

Credenciales de administrador por defecto (solo para desarrollo):
- Usuario: admin
- Contraseña: admin

## Datos de Prueba

Para cargar datos de prueba para desarrollo:
```bash
python manage.py loaddata test_data.json
```

## Licencia

[Información de licencia]

## Colaboradores

[Información de colaboradores]

## Nota de Idioma

Esta aplicación está completamente en español, incluyendo:
- Interfaz de usuario
- Mensajes de error y notificaciones
- Panel de administración
- Documentación
- Código fuente (comentarios y nombres de variables)

Cualquier contribución debe mantener esta convención y garantizar que todo el contenido visible por el usuario esté en español.
