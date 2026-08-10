# Arquitectura del Backend — Stunex

## Propósito del documento

El presente documento detalla la arquitectura interna del backend de Stunex: la estructura de carpetas y archivos por dominio, la responsabilidad de cada archivo, el contenido de los elementos compartidos en `core/`, y los flujos de autenticación y autorización.

Este documento profundiza y complementa `docs/03-Diseno/01_Arquitectura.md`, sin contradecirlo. Absorbe además lo que correspondería a un documento separado de autenticación, dado que las reglas de negocio de autenticación ya están definidas en `docs/02-Requisitos/` (RF, RNF, RN) y aquí solo se documenta cómo se implementan arquitectónicamente.

Este documento no introduce nuevos requisitos: cada decisión aquí descrita referencia el RF, RNF o RN que la respalda.

---

# 1. Alcance de este documento

Al igual que `01_Arquitectura.md`, este documento cubre en detalle únicamente los dominios de **Autenticación** (`auth/`) y **Perfil** (`profile/`), por ser los únicos que cuentan con RF, RNF, RN, HU y CU aprobados.

Los módulos restantes del alcance del MVP (Materias, Tareas, Calendario, Horario, Recursos, Documentos, Dashboard, Herramientas) **no tienen diseño de backend todavía**. La sección 7 de este documento ilustra, de forma conceptual y sin definir requisitos, cómo se incorporaría un dominio futuro a esta estructura — sin que eso constituya diseño aprobado de ese módulo.

---

# 2. Estructura de carpetas del backend

```text
backend/
│
├── auth/
│   ├── router.py
│   ├── service.py
│   ├── schemas.py
│   └── models.py
│
├── profile/
│   ├── router.py
│   ├── service.py
│   └── schemas.py
│
└── core/
    ├── config.py
    ├── database.py
    ├── security.py
    └── rate_limit.py
```

**Notas sobre la estructura:**

- Cada dominio (`auth/`, `profile/`) agrupa únicamente los archivos relacionados con su propia responsabilidad de negocio (ver sección 3.1).
- `profile/` **no tiene `models.py` propio**, porque no posee tabla propia: opera sobre el modelo `User`, definido en `auth/models.py` (ver sección 5).
- `core/` no es un dominio de negocio; contiene exclusivamente infraestructura y utilidades compartidas por todos los dominios (ver sección 4).
- Esta estructura es la aplicación concreta del principio de modularidad por dominio ya definido en `01_Arquitectura.md` (sección 4.1) y respalda RNF-016 y RNF-017.
- El nombre y la ubicación de la carpeta raíz del backend dentro del repositorio (junto con la aplicación móvil) aún no están definidos; eso corresponde a `08_Estructura_Proyecto.md`. Este documento se enfoca únicamente en la organización interna del backend.

---

# 3. Responsabilidad de cada archivo dentro de un dominio

## 3.1 `router.py`

**Contiene:**
- Definición de los endpoints REST del dominio (rutas, verbos HTTP, códigos de estado).
- Declaración de las dependencias de FastAPI aplicables a cada ruta: `Depends(get_current_user)` en rutas protegidas (RF-010, RN-013), y la dependencia de rate limiting en las rutas que lo requieran (ver sección 4.4).
- Delegación inmediata de la solicitud hacia las funciones de `service.py`.

**NO contiene:**
- Lógica de negocio (validaciones de reglas, hashing, generación de tokens).
- Acceso directo a la sesión de base de datos ni queries de SQLAlchemy.

## 3.2 `service.py`

**Contiene:**
- La lógica de negocio del dominio: validaciones de reglas de negocio (RN), orquestación de operaciones, interacción directa con la sesión de SQLAlchemy para leer y escribir datos (sin patrón repositorio, ver sección 3.5).
- Llamadas a utilidades de `core/` cuando corresponda (hashing, verificación de JWT).

**NO contiene:**
- Definición de rutas HTTP ni códigos de estado (eso es responsabilidad de `router.py`, que traduce el resultado del servicio a una respuesta HTTP).
- Definición de esquemas de entrada/salida (eso vive en `schemas.py`).

## 3.3 `models.py`

**Contiene:**
- Los modelos de SQLAlchemy (tablas) que pertenecen exclusivamente a ese dominio.
- En `auth/models.py`: el modelo `User` y el modelo de tokens de restablecimiento de contraseña (ver sección 5.2).

**NO contiene:**
- Modelos de otros dominios. `profile/` no define un `models.py` propio porque no tiene tabla propia (ver sección 5).

## 3.4 `schemas.py`

**Contiene:**
- Los esquemas Pydantic de entrada (request) y salida (response) de los endpoints del dominio, usados para validación automática (RNF-019) y para no exponer directamente los modelos de base de datos en las respuestas de la API.

**NO contiene:**
- Lógica de validación de negocio compleja más allá de la validación estructural de tipos/formato que Pydantic resuelve de forma declarativa.

## 3.5 Sin patrón repositorio

El proyecto no implementa una capa de repositorio intermedia entre `service.py` y la base de datos. `service.py` interactúa directamente con la sesión de SQLAlchemy inyectada.

Esta decisión es consistente con el principio de simplicidad sobre sobre-ingeniería ya establecido en `01_Arquitectura.md` (sección 4.3): dado el tamaño del MVP y el número de dominios actuales, una capa de repositorio añadiría indirección sin un beneficio concreto todavía.

---

# 4. Contenido y límites de `core/`

`core/` contiene exclusivamente infraestructura y utilidades transversales, reutilizables por cualquier dominio presente o futuro. **`core/` no contiene lógica de negocio de ningún dominio específico** — ninguna regla de negocio (RN) ni regla propia de un módulo debe implementarse aquí.

## 4.1 `config.py`

**Contiene:** carga y validación de variables de entorno (secreto de firma JWT, credenciales de MySQL, claves de Bucket Storage, configuración del servicio de correo), conforme a RNF-002. Ninguna credencial o secreto se embebe en el código fuente.

## 4.2 `database.py`

**Contiene:** el `engine` de SQLAlchemy y la fábrica de sesiones (`SessionLocal` o equivalente), junto con la dependencia de FastAPI que provee una sesión de base de datos por solicitud. No contiene modelos ni queries de ningún dominio.

## 4.3 `security.py`

**Contiene:**
- `get_current_user`: la dependencia de FastAPI que valida el JWT recibido y resuelve el usuario autenticado (ver sección 5.3). Vive en `core/` — y no en `auth/` — precisamente para que dominios futuros puedan proteger sus rutas importando esta dependencia sin depender del dominio `auth/` completo (ver sección 6).
- Funciones de verificación/decodificación de JWT (HS256, RNF-005).
- Funciones de hashing y verificación de contraseñas con bcrypt (RF-005, RNF-007).

**NO contiene:** los endpoints de login, registro o recuperación (esos viven en `auth/router.py` y `auth/service.py`); `security.py` solo provee las utilidades que esos endpoints consumen.

## 4.4 `rate_limit.py`

**Contiene:** una dependencia de FastAPI reutilizable que implementa el límite de solicitudes por ventana de tiempo (RF-017, RNF-008, RNF-010), parametrizable en número de intentos y duración de la ventana.

Se define en `core/` porque, aunque en el alcance actual solo se aplica a rutas de `auth/` (login y recuperación de contraseña), el mecanismo en sí no es una regla de negocio de autenticación sino una utilidad de infraestructura que otros dominios podrían reutilizar en el futuro. Se aplica explícitamente en `auth/router.py`, no de forma global.

---

# 5. Relación entre `auth/` y `profile/`

## 5.1 El modelo `User` vive en `auth/models.py`

El modelo `User` (creado durante el registro, RF-001) se define en `auth/models.py`, ya que `auth/` es el dominio responsable de la creación y ciclo de vida de la cuenta.

## 5.2 `profile/` no tiene tabla propia

`profile/` no define un `models.py` propio. Los endpoints de consulta y edición de perfil (RF-015, RF-016) operan sobre el mismo registro `User` creado en el registro (RF-001) — no existe una entidad "Perfil" separada en el modelo de datos. Por lo tanto, `profile/service.py` importa el modelo `User` desde `auth/models.py` para leer y actualizar el campo `nombre` (RN-019).

## 5.3 Por qué esto no contradice RNF-016

RNF-016 exige que la incorporación de **nuevos módulos** no requiera modificar el núcleo de autenticación. `profile/` no es un módulo nuevo en el sentido de RNF-016: opera sobre el mismo usuario ya autenticado, no introduce una entidad de negocio independiente ni requiere que `auth/` cambie para que `profile/` funcione.

La importación de `User` desde `auth/models.py` es una lectura de un modelo ya estable, no una dependencia que obligue a modificar `auth/` cada vez que `profile/` (o un futuro dominio) cambie. Un módulo genuinamente nuevo con su propia entidad de negocio (por ejemplo, Materias) no necesita importar ni modificar `auth/models.py` en absoluto — únicamente reutiliza `get_current_user` desde `core/security.py` (ver sección 6), que es precisamente el mecanismo que RNF-016 exige mantener estable.

---

# 6. Cómo se incorporaría un módulo futuro (ejemplo conceptual)

**Nota:** esta sección es un ejemplo ilustrativo del cumplimiento de RNF-016. No constituye diseño aprobado del módulo de Materias, que carece de RF/HU/CU/RN propios.

Si en el futuro se aprobaran los requisitos del módulo de Materias, su incorporación seguiría el mismo patrón estructural ya establecido:

```text
backend/
│
├── auth/          (sin modificaciones)
├── profile/        (sin modificaciones)
├── core/            (sin modificaciones)
│
└── materias/
    ├── router.py
    ├── service.py
    ├── schemas.py
    └── models.py
```

`materias/router.py` protegería sus rutas mediante `Depends(get_current_user)`, importado directamente desde `core/security.py` — el mismo mecanismo que ya usan `auth/` y `profile/`. `materias/models.py` definiría su propia tabla, relacionada con `User` mediante clave foránea (RNF-018), sin que ningún archivo de `auth/` requiera cambios.

Esto demuestra en concreto el cumplimiento de RNF-016 ya argumentado en `01_Arquitectura.md` (sección 5): el núcleo de autenticación (`auth/` y `core/security.py`) permanece estable ante la incorporación de nuevos dominios.

---

# 7. Autenticación y autorización

Esta sección documenta, a nivel de flujo, cómo se implementan las reglas de autenticación ya definidas en `docs/02-Requisitos/`.

## 7.1 Generación del JWT al iniciar sesión

1. El usuario envía correo y contraseña a `auth/router.py` (RF-006).
2. `auth/service.py` verifica las credenciales contra el hash bcrypt almacenado (RF-005, RN-012) y, si son válidas, invoca la función de generación de JWT en `core/security.py`.
3. El token generado se firma con **HS256** (RNF-005) y se le asigna una expiración de **7 días** (RNF-004, RF-011).
4. Si las credenciales son inválidas, se responde con un mensaje genérico, sin indicar cuál dato falló (RF-008, RN-014).

## 7.2 Validación del JWT mediante `Depends()`

Cada ruta protegida declara `Depends(get_current_user)` en su firma (RF-010, RN-013). `get_current_user`, en `core/security.py`:

1. Extrae el token del header `Authorization`.
2. Verifica su firma (HS256) y su vigencia.
3. Si el token es inválido, está expirado o falta, la solicitud se rechaza con código 401 (RF-010), sin llegar a ejecutar la lógica de `service.py`.
4. Si el token es válido, resuelve el usuario autenticado y lo entrega al endpoint (CU-005).

No existe middleware global que intercepte todas las rutas: la protección es explícita por ruta, tal como se argumenta en `01_Arquitectura.md` (sección 5) y se lista como decisión en la sección 6.2 de ese mismo documento.

## 7.3 Hashing de contraseñas

Toda contraseña (en registro, RF-005, y en restablecimiento, RF-014) se hashea con **bcrypt**, factor de costo **12 rounds** (RNF-007), mediante la función correspondiente de `core/security.py`. Ninguna contraseña se almacena, transmite en logs, ni se compara en texto plano (RN-011, RN-012).

## 7.4 Cierre de sesión

El cierre de sesión (RF-009) se resuelve enteramente en el cliente, mediante la eliminación del token almacenado (ver `01_Arquitectura.md`, sección 3.1). El backend no implementa endpoint de revocación ni mantiene lista de tokens invalidados (RN-008); el sistema permanece stateless (RN-009).

## 7.5 Recuperación de contraseña

1. El usuario solicita recuperación mediante `auth/router.py` (RF-012). La respuesta es idéntica exista o no el correo (RN-014).
2. Si el correo corresponde a una cuenta existente, `auth/service.py` genera un token de restablecimiento de un solo uso (RF-013), con **15 minutos** de vigencia (RNF-009, RN-016), y lo persiste en la tabla de tokens de restablecimiento del dominio `auth/` (ver sección 7.7).
3. El usuario presenta el token para definir una nueva contraseña (RF-014). Un token expirado, ya usado o inválido se rechaza. Tras un uso exitoso, el token se invalida de forma permanente aunque no haya expirado (RN-015).
4. La nueva contraseña se valida (RF-004) y se hashea (sección 7.3) antes de persistirse.

## 7.6 Rate limiting

La dependencia reutilizable de `core/rate_limit.py` (sección 4.4) se aplica en dos rutas de `auth/`:

- **Login:** máximo **5 intentos fallidos por cuenta/IP cada 15 minutos** (RF-017, RNF-008, RN-010), sin bloqueo permanente de cuentas.
- **Solicitud de recuperación de contraseña:** máximo **1 solicitud por correo cada 5 minutos** (RNF-010, RN-017).

## 7.7 Tabla de tokens de restablecimiento

La tabla que almacena los tokens de restablecimiento de contraseña (RF-013) pertenece al dominio `auth/`, definida en `auth/models.py`, ya que la recuperación de contraseña es una responsabilidad del ciclo de vida de la cuenta, no del perfil del usuario.

---

# 8. Manejo de errores y logs

## 8.1 Formato consistente de errores

Los errores devueltos por la API siguen un formato estructurado y consistente (código, mensaje), sin exponer detalles internos de implementación como stack traces o nombres de excepciones internas (RNF-022). Este formato se aplica de manera uniforme en todos los dominios, mediante los manejadores de excepciones de FastAPI.

## 8.2 Logs sin datos sensibles

Ningún log del sistema registra contraseñas (ni siquiera hasheadas), tokens JWT completos, tokens de restablecimiento, ni datos personales innecesarios (RNF-012, RNF-023). Esta restricción aplica tanto a `auth/service.py` (donde se manejan credenciales y tokens) como a cualquier utilidad de `core/` que registre actividad.

---

# 9. Trazabilidad de este documento

| Decisión de diseño | RF relacionados | RNF relacionados | RN relacionados |
|---|---|---|---|
| Backend organizado por dominio (`auth/`, `profile/`, `core/`) | — | RNF-016, RNF-017 | — |
| Estructura interna por archivo (router/service/schemas/models) | — | RNF-017 | — |
| Sin patrón repositorio | — | — | — |
| `get_current_user` en `core/security.py` | RF-010 | RNF-016 | RN-013 |
| `User` en `auth/models.py`, importado por `profile/` | RF-015, RF-016 | — | RN-018, RN-019 |
| Generación de JWT en login (HS256, 7 días) | RF-006, RF-007, RF-011 | RNF-004, RNF-005 | RN-005, RN-006 |
| Validación de JWT vía `Depends()` por ruta | RF-010 | RNF-016 | RN-013 |
| Hashing de contraseñas (bcrypt, 12 rounds) | RF-005, RF-014 | RNF-007 | RN-011, RN-012 |
| Cierre de sesión sin revocación en servidor | RF-009 | RNF-015 | RN-008, RN-009 |
| Recuperación de contraseña (token de un solo uso, 15 min) | RF-012, RF-013, RF-014 | RNF-009 | RN-014, RN-015, RN-016 |
| Rate limiting en login | RF-017 | RNF-008 | RN-010 |
| Rate limiting en recuperación de contraseña | — | RNF-010 | RN-017 |
| Tabla de tokens de restablecimiento en `auth/` | RF-013 | — | RN-015, RN-016 |
| Formato consistente de errores | — | RNF-022 | — |
| Logs sin datos sensibles | — | RNF-012, RNF-023 | — |

---

# 10. Módulos pendientes de diseño de backend

Los siguientes módulos del alcance del MVP no cuentan con diseño de backend en este documento, por no tener aún RF, HU, CU ni RN aprobados: Materias, Tareas, Calendario, Horario, Recursos, Documentos, Dashboard y Herramientas (Calculadora de notas, Temporizador Pomodoro).

La sección 6 de este documento ilustra de forma conceptual cómo se incorporarían siguiendo la estructura ya definida, sin que ello constituya diseño aprobado de esos módulos. Su documentación formal se realizará una vez completen su fase de requisitos, siguiendo la misma metodología incremental aplicada a Autenticación y Perfil.
