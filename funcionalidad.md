# Documentación de Funcionalidades - Canicross

Este documento mantiene un registro histórico de las funcionalidades implementadas en la aplicación Canicross, así como los cambios significativos realizados durante el desarrollo.

## Tabla de Contenidos

- [Sistema de Autenticación y Autorización](#sistema-de-autenticación-y-autorización)
- [Gestión de Participantes](#gestión-de-participantes)
- [Gestión de Eventos](#gestión-de-eventos)
- [Control Veterinario](#control-veterinario)
- [Gestión de Resultados](#gestión-de-resultados)

---

## Sistema de Autenticación y Autorización

### Modelo de Usuarios (2025-04-26)

La aplicación utiliza un modelo de usuario personalizado (`User`) que extiende de `AbstractUser` de Django, incluyendo los siguientes roles:

- **Administrador (`admin`)**: Acceso completo al sistema
- **Personal/Voluntario (`staff`)**: Soporte en eventos y tareas administrativas
- **Juez (`judge`)**: Gestión de resultados y cumplimiento del reglamento
- **Veterinario (`veterinary`)**: Revisión y aprobación de perros participantes
- **Participante (`participant`)**: Usuario estándar que se inscribe en eventos

Cada tipo de usuario tiene métodos auxiliares para verificar su rol:
- `is_admin()`
- `is_staff_member()`
- `is_judge()`
- `is_veterinary()`
- `is_participant()`

### Permisos basados en Roles (2025-04-26)

Se ha implementado un sistema completo de 8 roles con permisos específicos siguiendo el principio de menor privilegio:

1. **Administradores**: Control total del sistema
   - Todos los permisos disponibles

2. **Organizadores**: Gestión de eventos
   - Permisos completos: Event, Race, Modality, Category, RaceCategory, PenaltyType
   - Lectura/escritura: Registration, Document, Result, User 
   - Solo lectura: Dog, Participant, VeterinaryCheck

3. **Gestores de Inscripciones**: Manejo del proceso de registro
   - Lectura/escritura: Registration, Document, Participant, Dog
   - Solo lectura: Event, Race, RaceCategory, Category, Modality

4. **Veterinarios**: Control veterinario
   - Permisos completos: VeterinaryCheck, VaccinationRecord, MedicalAlert
   - Lectura/escritura: Registration, Document (para actualizar estado veterinario)
   - Solo lectura: Dog, Participant, Event, Race

5. **Jueces**: Resultados y reglamento
   - Permisos completos: Result, TimeRecord, Penalty, ParticipantAnnotation
   - Lectura/escritura: Registration (actualizar estado)
   - Solo lectura: Dog, Participant, Event, Race, RaceCategory, PenaltyType, VeterinaryCheck

6. **Cronometradores**: Tiempos y resultados
   - Lectura/escritura: Result, TimeRecord (gestión de tiempos)
   - Solo lectura: Registration, Participant, Dog, Event, Race, RaceCategory, Penalty

7. **Participantes**: Usuarios finales
   - Lectura/escritura: Dog (propios), Participant (propio perfil), Registration (propias)
   - Gestión completa: Document (propios)
   - Solo lectura: Event, Race, RaceCategory, Result

8. **Voluntarios**: Personal de apoyo
   - Lectura/escritura: Registration (para check-in y entregas)
   - Solo lectura: Dog, Participant, Event, Race

### Decoradores de Permisos (2025-04-26)

Se han implementado decoradores para proteger las vistas según el tipo de usuario:

- `@veterinary_required`: Restringe acceso solo a veterinarios
- `@judge_required`: Restringe acceso solo a jueces
- `@admin_required`: Restringe acceso solo a administradores
- `@staff_required`: Restringe acceso solo a staff

Estos decoradores complementan el sistema de grupos de permisos de Django.

---

## Control Veterinario

### Módulo de Gestión Veterinaria (2025-04-26)

Se ha implementado un sistema completo para que los veterinarios puedan revisar y aprobar perros participantes:

#### Modelos:

1. **VeterinaryCheck**: Revisión veterinaria completa
   - Datos del perro y participante
   - Signos vitales (temperatura, peso, frecuencia cardíaca)
   - Evaluación física y estado de salud
   - Estado de aprobación (pendiente, en_revisión, aprobado, condicional, rechazado)
   - Verificación de vacunas
   - Notas y recomendaciones

2. **VaccinationRecord**: Registro de vacunas verificadas
   - Nombre de la vacuna
   - Fecha de administración y expiración
   - Número de lote
   - Estado de verificación

3. **MedicalAlert**: Sistema de alertas médicas
   - Niveles de prioridad (baja, media, alta, crítica)
   - Seguimiento requerido
   - Estado de la alerta (activa, monitoreo, resuelta, descartada)

#### Vistas:

1. **Dashboard Veterinario**: Panel principal con estadísticas y pendientes
2. **Lista de Inscripciones**: Filtrable por evento y estado
3. **Formulario de Revisión**: Interfaz completa para evaluación veterinaria
4. **Gestión de Vacunas**: Registro y verificación de vacunaciones
5. **Sistema de Alertas**: Creación y seguimiento de problemas médicos
6. **Historial Médico**: Registro histórico por perro
7. **Revisión de Documentos**: Análisis de certificados de vacunación

---

## Gestión de Resultados

### Sistema de Resultados (2025-04-26)

Se ha implementado un módulo completo para la gestión de resultados de carreras:

#### Modelos:

1. **Result**: Resultado principal de un participante
   - Tiempo oficial (en segundos para facilitar cálculos)
   - Posición en clasificación
   - Estado (borrador, pendiente, verificado, descalificado, no_finalizó, no_inició)
   - Seguimiento de quién registró y verificó el resultado

2. **TimeRecord**: Registros de tiempo intermedios
   - Puntos de control con tiempos parciales
   - Sistema de conversión entre formatos de tiempo

3. **Penalty**: Gestión de penalizaciones
   - Enlace a tipos de penalización configurables
   - Descripción y justificación

#### Vistas para Jueces:

1. **Dashboard**: Panel de control con estadísticas y próximas carreras
2. **Lista de Carreras**: Para seleccionar qué carrera gestionar
3. **Lista de Participantes**: Filtrable por estado de resultado
4. **Registro de Resultados**: Interfaz para tiempos y posiciones
5. **Gestión de Penalizaciones**: Aplicación de reglas
6. **Anotaciones**: Sistema para registrar incidencias

#### Vistas Públicas:

1. **Resultados por Evento**: Clasificación general
2. **Resultados por Carrera**: Desglose detallado

---

## [Próximas secciones serán documentadas a medida que se implementen nuevas funcionalidades]