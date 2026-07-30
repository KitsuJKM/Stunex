# Requisitos No Funcionales — Stunex

## Propósito del documento

El presente documento define los requisitos no funcionales (RNF) de Stunex, cubriendo seguridad, autenticación, rendimiento, usabilidad, disponibilidad, escalabilidad, mantenibilidad, integridad de datos, API REST, almacenamiento de archivos, manejo de errores/logs y compatibilidad móvil.

Cada requisito cuenta con un identificador único, una descripción, una prioridad y, cuando corresponde, el valor o decisión técnica definida para el proyecto.

---

# 1. Seguridad

## RNF-001

**Nombre:** Comunicación exclusivamente mediante HTTPS

**Descripción:** Toda comunicación entre la aplicación móvil y la API debe realizarse sobre HTTPS/TLS.

**Prioridad:** Alta

**Decisión/valor definido:** No aplica valor adicional; requisito no negociable.

---

## RNF-002

**Nombre:** Gestión de variables sensibles mediante variables de entorno

**Descripción:** Las credenciales de base de datos, el secreto de firma JWT y las claves del Bucket Storage se gestionan mediante variables de entorno, nunca embebidas en el código fuente ni en el repositorio.

**Prioridad:** Alta

**Decisión/valor definido:** No aplica valor adicional.

---

## RNF-003

**Nombre:** Prevención de inyección SQL

**Descripción:** Todo acceso a datos se realiza mediante SQLAlchemy con consultas parametrizadas; no se construyen queries SQL por concatenación de strings.

**Prioridad:** Alta

**Decisión/valor definido:** No aplica valor adicional.

---

# 2. Autenticación y JWT

## RNF-004

**Nombre:** Tiempo de expiración del access token JWT

**Descripción:** El access token JWT emitido tras el inicio de sesión (RF-007) debe expirar tras un tiempo definido. Al no existir refresh tokens en el MVP (RF-011), el valor prioriza la experiencia de uso diario del estudiante.

**Prioridad:** Alta

**Decisión/valor definido:** Expiración de **7 días**.

---

## RNF-005

**Nombre:** Algoritmo de firma del JWT

**Descripción:** Se define el algoritmo utilizado para generar y validar la firma de los tokens JWT.

**Prioridad:** Media

**Decisión/valor definido:** **HS256** (secreto simétrico).

---

# 3. Contraseñas y bcrypt

## RNF-006

**Nombre:** Reglas mínimas de contraseña

**Descripción:** Complementa RF-004, definiendo los valores concretos de longitud para la contraseña de los usuarios.

**Prioridad:** Alta

**Decisión/valor definido:** Longitud **mínima de 8 caracteres** y **máxima de 128 caracteres**. No es obligatorio exigir mayúsculas, números ni símbolos específicos.

---

## RNF-007

**Nombre:** Factor de costo (rounds) de bcrypt

**Descripción:** Define el costo computacional aplicado al hash de la contraseña (RF-005), balanceando seguridad y rendimiento.

**Prioridad:** Media

**Decisión/valor definido:** **12 rounds.**

---

# 4. Rate limiting

## RNF-008

**Nombre:** Límite de intentos de inicio de sesión

**Descripción:** Complementa RF-017, definiendo los valores concretos del rate limiting sobre el inicio de sesión.

**Prioridad:** Media

**Decisión/valor definido:** **5 intentos fallidos por cuenta/IP cada 15 minutos**, tras lo cual las solicitudes adicionales se rechazan temporalmente. Sin bloqueo permanente de cuentas.

---

# 5. Recuperación de contraseña

## RNF-009

**Nombre:** Expiración del token de restablecimiento

**Descripción:** Complementa RF-013, definiendo el tiempo de vida del token de recuperación de contraseña.

**Prioridad:** Alta

**Decisión/valor definido:** El token es válido durante **15 minutos** y es de **un solo uso**.

---

## RNF-010

**Nombre:** Límite de solicitudes de recuperación por correo

**Descripción:** Evita el envío masivo o repetido de solicitudes de recuperación de contraseña hacia el mismo correo electrónico.

**Prioridad:** Media

**Decisión/valor definido:** **Máximo 1 solicitud por correo cada 5 minutos.**

---

# 6. Protección de datos

## RNF-011

**Nombre:** Minimización de datos personales

**Descripción:** El sistema solo almacenará los datos personales estrictamente necesarios para el funcionamiento del MVP (nombre, correo), sin recolectar información adicional no utilizada.

**Prioridad:** Media

**Decisión/valor definido:** No aplica valor adicional.

---

## RNF-012

**Nombre:** No exposición de datos sensibles en logs

**Descripción:** Contraseñas (aun hasheadas), tokens JWT completos y tokens de recuperación no deben aparecer en los logs del sistema.

**Prioridad:** Alta

**Decisión/valor definido:** No aplica valor adicional.

---

# 7. Rendimiento

## RNF-013

**Nombre:** Tiempo de respuesta esperado de la API

**Descripción:** Las operaciones CRUD simples deben responder en un tiempo razonable bajo condiciones normales de prueba.

**Prioridad:** Media

**Decisión/valor definido:** Objetivo de **≤ 500 ms en el percentil 95** para operaciones CRUD simples bajo condiciones normales de prueba.

---

# 8. Usabilidad

## RNF-014

**Nombre:** Interfaz simple e intuitiva

**Descripción:** La aplicación debe seguir Material Design 3 y ser utilizable por un estudiante sin necesidad de capacitación previa.

**Prioridad:** Media

**Decisión/valor definido:** No aplica valor adicional (requisito cualitativo).

---

# 9. Disponibilidad

## RNF-015

**Nombre:** Gestión stateless de autenticación

**Descripción:** El backend no mantiene sesiones de servidor; la autenticación se resuelve exclusivamente mediante la validación del JWT en cada solicitud, permitiendo que el backend pueda reiniciarse sin perder las sesiones activas de los clientes.

**Prioridad:** Media

**Decisión/valor definido:** No se establece SLA formal de disponibilidad, por tratarse de un MVP académico.

---

# 10. Escalabilidad

## RNF-016

**Nombre:** Arquitectura extensible por módulos

**Descripción:** La incorporación de nuevos módulos (materias, tareas, calendario, horario, recursos, documentos, dashboard, herramientas) no debe requerir modificar el núcleo de autenticación.

**Prioridad:** Media

**Decisión/valor definido:** No aplica valor adicional (requisito cualitativo).

---

# 11. Mantenibilidad

## RNF-017

**Nombre:** Organización modular del código backend

**Descripción:** El backend debe mantenerse separado por responsabilidades (controllers, services, models, schemas, middlewares), conforme a la estructura ya presente en el repositorio.

**Prioridad:** Media

**Decisión/valor definido:** No aplica valor adicional.

---

# 12. Integridad de datos

## RNF-018

**Nombre:** Restricciones de integridad en base de datos

**Descripción:** El correo electrónico debe tener restricción de unicidad a nivel de base de datos (no solo a nivel de aplicación); las relaciones entre tablas deben protegerse mediante claves foráneas.

**Prioridad:** Alta

**Decisión/valor definido:** No aplica valor adicional.

---

# 13. API REST

## RNF-019

**Nombre:** Convenciones REST y documentación automática

**Descripción:** La API debe utilizar verbos HTTP y códigos de estado correctos, y debe estar documentada automáticamente mediante Swagger/OpenAPI provisto por FastAPI.

**Prioridad:** Media

**Decisión/valor definido:** No aplica valor adicional.

---

# 14. Almacenamiento de archivos

## RNF-020

**Nombre:** Tamaño máximo de archivo permitido

**Descripción:** Define el límite de tamaño por archivo subido al Bucket Storage para los módulos de Documentos y Recursos.

**Prioridad:** Alta

**Decisión/valor definido:** **Máximo 10 MB por archivo.**

---

## RNF-021

**Nombre:** Tipos de archivo permitidos

**Descripción:** Restringe la subida de archivos a tipos seguros y relevantes académicamente.

**Prioridad:** Alta

**Decisión/valor definido:** Se permiten **PDF, DOCX, XLSX, PPTX, JPG y PNG**. La validación no debe depender únicamente de la extensión del archivo; posteriormente deberá contemplarse validación del tipo MIME/contenido real del archivo. No se permiten ejecutables ni scripts.

---

# 15. Manejo de errores y logs

## RNF-022

**Nombre:** Formato consistente de errores

**Descripción:** Los errores de la API deben devolverse en un formato estructurado y consistente (código, mensaje), sin exponer detalles internos como stack traces.

**Prioridad:** Media

**Decisión/valor definido:** No aplica valor adicional.

---

## RNF-023

**Nombre:** Logs sin datos sensibles

**Descripción:** Los logs de la aplicación no deben registrar contraseñas, tokens completos, ni datos personales innecesarios (relacionado con RNF-012).

**Prioridad:** Alta

**Decisión/valor definido:** No aplica valor adicional.

---

# 16. Compatibilidad móvil

## RNF-024

**Nombre:** Versión mínima de Android soportada

**Descripción:** Define la versión mínima de Android compatible con la aplicación móvil.

**Prioridad:** Media

**Decisión/valor definido:** **Android API 26 (Android 8.0)** como versión mínima. iOS permanece fuera del MVP salvo que el tiempo lo permita (definido en el alcance del proyecto).

---

# Resumen de requisitos

| ID | Nombre | Prioridad | Valor definido |
|----|--------|-----------|-----------------|
| RNF-001 | Comunicación exclusivamente mediante HTTPS | Alta | — |
| RNF-002 | Gestión de variables sensibles mediante variables de entorno | Alta | — |
| RNF-003 | Prevención de inyección SQL | Alta | — |
| RNF-004 | Tiempo de expiración del access token JWT | Alta | 7 días |
| RNF-005 | Algoritmo de firma del JWT | Media | HS256 |
| RNF-006 | Reglas mínimas de contraseña | Alta | 8–128 caracteres |
| RNF-007 | Factor de costo (rounds) de bcrypt | Media | 12 rounds |
| RNF-008 | Límite de intentos de inicio de sesión | Media | 5 intentos / 15 min |
| RNF-009 | Expiración del token de restablecimiento | Alta | 15 min, un solo uso |
| RNF-010 | Límite de solicitudes de recuperación por correo | Media | 1 / correo / 5 min |
| RNF-011 | Minimización de datos personales | Media | — |
| RNF-012 | No exposición de datos sensibles en logs | Alta | — |
| RNF-013 | Tiempo de respuesta esperado de la API | Media | ≤500 ms p95 |
| RNF-014 | Interfaz simple e intuitiva | Media | — |
| RNF-015 | Gestión stateless de autenticación | Media | Sin SLA formal |
| RNF-016 | Arquitectura extensible por módulos | Media | — |
| RNF-017 | Organización modular del código backend | Media | — |
| RNF-018 | Restricciones de integridad en base de datos | Alta | — |
| RNF-019 | Convenciones REST y documentación automática | Media | — |
| RNF-020 | Tamaño máximo de archivo permitido | Alta | 10 MB |
| RNF-021 | Tipos de archivo permitidos | Alta | PDF, DOCX, XLSX, PPTX, JPG, PNG |
| RNF-022 | Formato consistente de errores | Media | — |
| RNF-023 | Logs sin datos sensibles | Alta | — |
| RNF-024 | Versión mínima de Android soportada | Media | Android API 26 (8.0) |
