# Arquitectura General del Sistema — Stunex

## Propósito del documento

El presente documento define la arquitectura general de Stunex: los componentes que conforman el sistema, el flujo de comunicación entre ellos, los principios arquitectónicos adoptados y las decisiones técnicas de alto nivel ya aprobadas para los módulos de **Autenticación** y **Perfil**.

Este documento no introduce nuevos requisitos: cada decisión aquí descrita referencia el RF, RNF o RN que la respalda, documentados previamente en `docs/02-Requisitos/`.

---

# 1. Alcance de este documento

Únicamente los módulos de **Autenticación** y **Perfil** cuentan con requisitos funcionales, no funcionales, historias de usuario, casos de uso y reglas de negocio aprobados (RF-001 a RF-017, RNF-001 a RNF-024, RN-001 a RN-020). Por lo tanto, este documento describe con detalle la arquitectura de esos dos módulos únicamente.

Los módulos restantes contemplados en el alcance del proyecto —Materias, Tareas, Calendario, Horario, Recursos, Documentos, Dashboard y Herramientas (Calculadora de notas, Pomodoro)— **no tienen diseño de arquitectura todavía**. Su diseño se documentará una vez existan sus propios RF, HU, CU y RN, siguiendo la misma metodología incremental aplicada hasta ahora. Este documento no infiere ni anticipa decisiones técnicas para esos módulos.

---

# 2. Flujo general del sistema

El sistema se compone de cuatro elementos principales, comunicados de forma lineal:

```text
Aplicación Flutter (cliente móvil)

↓  HTTPS/TLS (RNF-001)

Backend FastAPI (API REST)

↓                              ↓

MySQL                    Bucket Storage
(datos relacionales)     (archivos)
```

**Descripción del flujo:**

1. La aplicación Flutter realiza solicitudes HTTP hacia la API mediante conexiones cifradas HTTPS/TLS, sin excepción (RNF-001).
2. El backend FastAPI recibe la solicitud, valida el JWT cuando el endpoint lo requiere (RF-010), aplica la lógica de negocio correspondiente y responde en formato JSON.
3. Para operaciones sobre datos relacionales (usuarios, perfiles, y en el futuro materias, tareas, etc.), el backend se comunica con **MySQL** mediante SQLAlchemy.
4. Para operaciones sobre archivos (aplicable a futuros módulos de Documentos y Recursos), el backend se comunicará con el **Bucket Storage**. En la fase actual (Autenticación y Perfil) no existe interacción con Bucket Storage, ya que ninguno de los RF vigentes la requiere.

---

# 3. Responsabilidad de cada componente

## 3.1 Aplicación Flutter (cliente móvil)

- Presenta la interfaz de usuario siguiendo Material Design 3 (RNF-014).
- Envía credenciales y datos del usuario a la API, nunca procesa lógica de autenticación ni de negocio localmente.
- Almacena el access token JWT de forma segura en el dispositivo mediante `flutter_secure_storage` (Keystore en Android, Keychain en iOS), evitando su exposición en almacenamiento no cifrado.
- Adjunta automáticamente el JWT almacenado en cada solicitud a endpoints protegidos, mediante interceptores del cliente HTTP `dio`.
- Gestiona el estado de la aplicación (por ejemplo, sesión del usuario autenticado) mediante `Provider`.
- Ante una respuesta 401 del backend, el interceptor de `dio` intercepta el error de forma centralizada y dirige al usuario nuevamente al flujo de inicio de sesión, sin necesidad de manejar el caso en cada pantalla individualmente.

## 3.2 Backend FastAPI (API REST)

- Expone los endpoints REST documentados automáticamente mediante Swagger/OpenAPI (RNF-019).
- Valida el JWT recibido en cada endpoint protegido mediante `Depends()` de FastAPI, de forma explícita por ruta (ver sección 5).
- Aplica las reglas de negocio (RN-001 a RN-020): unicidad de correo, hashing de contraseñas con bcrypt, expiración y vigencia de tokens, límites de intentos, no revelación de existencia de cuentas, entre otras.
- No mantiene sesiones en memoria ni en disco: es completamente **stateless** (RNF-015), ver sección 4.4.
- Se organiza internamente por dominio de negocio, no por capas técnicas (ver sección 4.1).

## 3.3 MySQL (base de datos relacional)

- Persiste los datos de usuarios y perfiles (nombre, correo, hash de contraseña).
- Garantiza integridad de datos mediante restricciones a nivel de esquema: unicidad de correo electrónico y claves foráneas entre tablas relacionadas (RNF-018).
- El acceso se realiza exclusivamente mediante SQLAlchemy con consultas parametrizadas, sin concatenación de strings SQL (RNF-003).

## 3.4 Bucket Storage

- Componente destinado al almacenamiento de archivos (documentos, recursos) para módulos futuros (Documentos, Recursos), compatible con Dropbox.
- No participa en el flujo de los módulos de Autenticación y Perfil, ya que estos no manejan archivos.
- Su diseño detallado (estructura de carpetas, políticas de acceso, validación de tipo MIME) queda pendiente hasta que el módulo de Documentos/Recursos cuente con RF, HU, CU y RN propios, conforme a RNF-020 y RNF-021.

---

# 4. Principios arquitectónicos del proyecto

## 4.1 Modularidad por dominio

El backend se organiza por **dominio de negocio** (`auth/`, `profile/`, `core/`), en lugar de por capas técnicas horizontales (por ejemplo, un único directorio `controllers/` o `models/` para todo el sistema).

Cada dominio agrupa sus propios controladores, servicios, modelos y esquemas relacionados. El módulo `core/` contiene elementos compartidos y transversales (configuración, conexión a base de datos, utilidades comunes), pero no lógica de negocio de ningún dominio específico.

Esta decisión respalda directamente **RNF-016** (ver sección 5) y es coherente con **RNF-017**, que exige separación por responsabilidades dentro del backend.

## 4.2 Seguridad desde el diseño

La seguridad no se añade posteriormente, sino que forma parte de las decisiones estructurales del sistema desde su diseño inicial:

- Toda comunicación cliente-servidor ocurre sobre HTTPS/TLS (RNF-001).
- Las contraseñas se hashean con bcrypt (factor de costo 12) antes de almacenarse; nunca se guardan ni se registran en texto plano (RF-005, RNF-007, RN-011, RN-012).
- Los endpoints privados exigen JWT válido, verificado explícitamente por ruta (RF-010, RN-013).
- Las variables sensibles (secreto de firma JWT, credenciales de base de datos, claves de Bucket Storage) se gestionan mediante variables de entorno, nunca embebidas en el código (RNF-002).
- El sistema nunca revela si un correo electrónico está o no registrado, ni en el inicio de sesión ni en la recuperación de contraseña (RN-014).

## 4.3 Simplicidad sobre sobre-ingeniería

Dado el carácter de MVP académico del proyecto, las decisiones arquitectónicas priorizan la simplicidad y lo estrictamente necesario para cumplir los requisitos aprobados, evitando mecanismos no solicitados:

- No se implementan refresh tokens; el MVP funciona únicamente con access tokens de vigencia de 7 días (RF-011, RNF-004, RN-007).
- No existe revocación de tokens del lado del servidor ni lista de tokens invalidados; el cierre de sesión se resuelve eliminando el token en el cliente (RF-009, RN-008, RN-009).
- No se valida el JWT mediante middleware global, sino de forma explícita por ruta (ver sección 5), evitando lógica implícita difícil de rastrear.

## 4.4 Backend stateless

El backend no mantiene sesiones de servidor ni estado de autenticación en memoria o disco entre solicitudes. Toda la información necesaria para identificar al usuario autenticado viaja en el propio JWT, validado en cada solicitud (RNF-015, RN-009).

Esto permite que el backend pueda reiniciarse o escalar horizontalmente (en un escenario futuro) sin perder ni invalidar las sesiones activas de los clientes, ya que ninguna sesión vive del lado del servidor.

---

# 5. Cumplimiento de RNF-016 (arquitectura extensible por módulos)

**RNF-016** exige que la incorporación de nuevos módulos (materias, tareas, calendario, horario, recursos, documentos, dashboard, herramientas) no requiera modificar el núcleo de autenticación.

La arquitectura elegida cumple este requisito mediante dos decisiones combinadas:

1. **Organización por dominio (sección 4.1):** al estar el backend dividido en `auth/`, `profile/` y futuros dominios independientes (`subjects/`, `tasks/`, etc.), un nuevo módulo se agrega como un nuevo dominio autocontenido, sin tocar los archivos de `auth/`.

2. **Validación de JWT mediante `Depends()` por ruta, sin middleware global:** cada endpoint nuevo que requiera protección simplemente declara la dependencia de autenticación existente (`Depends(get_current_user)` o equivalente) al definirse, en lugar de depender de un middleware global que intercepte todas las rutas del sistema.

   Esta decisión cumple explícitamente **RF-010** (protección de endpoints privados) y **RN-013** (protección obligatoria de endpoints privados) de forma **tipada y explícita**: cada ruta declara si requiere autenticación o no directamente en su firma, sin lógica implícita ni condicionales dispersos que deban modificarse al añadir un módulo nuevo.

En conjunto, un módulo nuevo (por ejemplo, Materias) se construye como un dominio propio que reutiliza la dependencia de autenticación ya existente, sin necesidad de leer, modificar ni entender el código interno de `auth/`.

---

# 6. Decisiones técnicas por componente

## 6.1 Backend — Organización por dominio

**Decisión:** estructura de carpetas por dominio de negocio (`auth/`, `profile/`, `core/`), no por capas técnicas globales.

**Respalda:** RNF-016, RNF-017.

## 6.2 Backend — Validación de JWT

**Decisión:** validación mediante `Depends()` de FastAPI, aplicada explícitamente por ruta protegida. Sin middleware global de autenticación.

**Respalda:** RF-010, RN-013, RNF-016 (ver sección 5).

## 6.3 Aplicación móvil — Cliente HTTP

**Decisión:** `dio` como cliente HTTP en Flutter, aprovechando sus interceptores nativos para:
- Inyección automática del JWT almacenado en cada solicitud a endpoints protegidos.
- Manejo centralizado de respuestas 401 (token inválido o expirado).

**Respalda:** RF-010, RF-011.

## 6.4 Aplicación móvil — Gestión de estado

**Decisión:** `Provider` como solución de gestión de estado en Flutter.

**Respalda:** no corresponde a un RF/RNF específico; es una decisión de arquitectura de la aplicación móvil necesaria para soportar los flujos de autenticación y perfil ya definidos (RF-006 a RF-016).

## 6.5 Aplicación móvil — Almacenamiento del token

**Decisión:** `flutter_secure_storage` (Keystore en Android, Keychain en iOS) para almacenar el access token JWT en el dispositivo. No se utiliza `SharedPreferences` sin cifrar.

**Respalda:** RNF-002 (gestión segura de credenciales/tokens), RNF-012 (no exposición de datos sensibles).

## 6.6 Recuperación de contraseña — Servicio de correo

**Decisión:** **Resend** como servicio de envío de correo para la recuperación de contraseña.

**Respalda:** RF-012, que dejaba explícitamente pendiente de definición técnica el proveedor de envío de correo.

---

# 7. Trazabilidad de esta arquitectura

| Decisión arquitectónica | RF relacionados | RNF relacionados | RN relacionados |
|---|---|---|---|
| Organización backend por dominio | — | RNF-016, RNF-017 | — |
| Validación JWT vía `Depends()` por ruta | RF-010 | RNF-016 | RN-013 |
| Cliente HTTP `dio` con interceptores | RF-010, RF-011 | — | — |
| Gestión de estado con `Provider` | RF-006 a RF-016 | — | — |
| Almacenamiento seguro del token (`flutter_secure_storage`) | — | RNF-002, RNF-012 | — |
| Comunicación exclusivamente HTTPS | — | RNF-001 | — |
| Hashing de contraseñas con bcrypt | RF-005 | RNF-007 | RN-011, RN-012 |
| Backend stateless | RF-009 | RNF-015 | RN-009 |
| Servicio de correo (Resend) para recuperación | RF-012 | — | — |

---

# 8. Módulos pendientes de diseño

Los siguientes módulos, contemplados en el alcance del MVP (`docs/01-Analisis/05_Alcance.md`), **no cuentan con diseño de arquitectura** en este documento por no tener aún RF, HU, CU ni RN aprobados:

- Materias
- Tareas
- Calendario
- Horario
- Recursos
- Documentos
- Dashboard
- Herramientas (Calculadora de notas, Temporizador Pomodoro)

Su arquitectura se documentará en actualizaciones futuras de `docs/03-Diseno/`, una vez se complete su fase de requisitos siguiendo la misma metodología incremental aplicada a Autenticación y Perfil. Mientras tanto, la organización por dominio descrita en la sección 4.1 y 5 garantiza que su incorporación futura no requiera modificar el núcleo de autenticación ya diseñado.
