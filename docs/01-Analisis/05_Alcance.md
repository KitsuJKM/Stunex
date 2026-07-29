# Alcance del Proyecto

## Propósito del documento

El presente documento define el alcance funcional y técnico de la primera versión de **Stunex** (MVP - Minimum Viable Product), estableciendo claramente qué funcionalidades serán desarrolladas durante el proyecto y cuáles quedarán previstas para futuras versiones.

Su objetivo es mantener el enfoque del desarrollo, facilitar la planificación del trabajo y evitar la incorporación de funcionalidades no contempladas durante la etapa inicial del proyecto.

---

# Alcance General

Stunex será una aplicación móvil diseñada para apoyar la organización académica de estudiantes de educación superior mediante una plataforma que centraliza la gestión de materias, tareas, horarios, eventos, documentos y recursos de estudio.

La primera versión del sistema estará enfocada en ofrecer una experiencia estable, intuitiva y funcional que cubra las necesidades esenciales de organización académica.

---

# Funcionalidades Incluidas (MVP)

La versión 1.0 de Stunex incluirá los siguientes módulos:

## Gestión de usuarios

- Registro de usuarios.
- Inicio de sesión.
- Recuperación de contraseña.
- Cierre de sesión.
- Edición del perfil.

---

## Gestión de materias

- Crear materias.
- Editar materias.
- Eliminar materias.
- Visualizar listado de materias.

---

## Gestión de tareas

- Crear tareas.
- Editar tareas.
- Eliminar tareas.
- Marcar tareas como completadas.
- Filtrar tareas por materia y estado.

---

## Calendario académico

- Registrar eventos.
- Consultar eventos.
- Editar eventos.
- Eliminar eventos.
- Visualización mensual.

---

## Horario de clases

- Registrar horarios.
- Modificar horarios.
- Eliminar horarios.
- Consulta semanal del horario.

---

## Biblioteca de recursos

- Registrar enlaces de estudio.
- Registrar documentos.
- Organizar recursos por materia.

---

## Almacenamiento de documentos

- Subir archivos.
- Descargar archivos.
- Eliminar archivos.
- Organización por materia.

---

## Dashboard

Visualización general de:

- Materias activas.
- Tareas pendientes.
- Próximos eventos.
- Actividad reciente.

---

## Herramientas académicas

- Calculadora de notas.
- Temporizador Pomodoro.

---

# Funcionalidades Excluidas del MVP

Las siguientes funcionalidades no harán parte de la versión inicial:

- Chat entre usuarios.
- Videollamadas.
- Mensajería en tiempo real.
- Inteligencia Artificial.
- Integración con Google Calendar.
- Integración con Microsoft Outlook.
- Sincronización con plataformas educativas.
- Sistema de foros.
- Publicación de apuntes públicos.
- Modo offline.
- Notificaciones Push.
- Aplicación para iOS (si el tiempo no lo permite).
- Panel administrativo.

Estas funcionalidades podrán desarrollarse en versiones posteriores.

---

# Alcance Técnico

La aplicación será desarrollada utilizando la siguiente arquitectura:

## Cliente

- Flutter
- Dart

---

## Backend

- Python
- FastAPI

---

## Base de datos

- MySQL

---

## ORM

- SQLAlchemy

---

## Autenticación

- JWT

---

## Almacenamiento

- Bucket Storage compatible con Dropbox.

---

## Control de versiones

- Git
- GitHub

---

# Alcance de los Usuarios

La versión inicial estará dirigida exclusivamente a estudiantes.

No se desarrollarán perfiles para:

- Docentes.
- Administradores.
- Instituciones educativas.

---

# Restricciones del Proyecto

El desarrollo estará sujeto a las siguientes restricciones:

- Tiempo estimado de desarrollo: un mes y medio.
- Equipo de desarrollo conformado por dos integrantes.
- Desarrollo con fines académicos.
- Implementación enfocada en Android.
- Funcionalidades limitadas al MVP definido.

---

# Criterios de Finalización

El proyecto se considerará finalizado cuando:

- Todas las funcionalidades del MVP se encuentren implementadas.
- La aplicación permita registrar e iniciar sesión de usuarios.
- Todos los módulos funcionen correctamente.
- La API REST responda correctamente a las solicitudes.
- La información se almacene correctamente en la base de datos.
- Los documentos puedan cargarse y consultarse desde el Bucket Storage.
- Se hayan realizado pruebas funcionales del sistema.
- La documentación técnica esté actualizada.

---

# Riesgos Relacionados con el Alcance

Durante el desarrollo podrán presentarse riesgos como:

- Cambios en los requisitos.
- Limitaciones de tiempo.
- Problemas de integración entre frontend y backend.
- Dificultades en la configuración del almacenamiento de archivos.
- Curva de aprendizaje de nuevas tecnologías.

Estos riesgos serán mitigados mediante un desarrollo incremental, control de versiones y documentación continua.

---

# Conclusión

El alcance definido para la versión 1.0 de Stunex establece una base sólida para construir una aplicación funcional y escalable, priorizando las necesidades esenciales de los estudiantes y permitiendo futuras ampliaciones sin afectar la arquitectura del sistema.