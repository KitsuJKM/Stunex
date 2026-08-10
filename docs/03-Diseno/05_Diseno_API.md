# Diseño de la API — Stunex

## Propósito del documento

El presente documento define el diseño de los endpoints REST de Stunex: convenciones generales, el detalle de cada endpoint (método, ruta, autenticación, cuerpo de la solicitud, respuestas y códigos de estado), y las decisiones sobre respuestas genéricas y ausencia intencional de ciertos endpoints.

Este documento complementa a `03_Arquitectura_Backend.md` (que ya definió `router.py`, `service.py` y los flujos de autenticación) y a `04_Modelo_Base_de_Datos.md` (que ya definió las tablas `users` y `password_reset_tokens`), sin contradecirlos. Aquí se documenta específicamente el contrato HTTP expuesto al cliente.

Este documento no introduce nuevos requisitos: cada endpoint, campo y código de estado aquí descrito referencia el RF, RNF o RN que la respalda.

---

# 1. Alcance de este documento

Al igual que los documentos de diseño ya mergeados, este documento define únicamente los endpoints de **Autenticación** y **Perfil**, derivados exclusivamente de los casos de uso CU-001 a CU-007 (`docs/02-Requisitos/04_Casos_de_Uso.md`).

Los módulos restantes del alcance del MVP (Materias, Tareas, Calendario, Horario, Recursos, Documentos, Dashboard, Herramientas) **no tienen diseño de API todavía**, por no contar con RF, RNF ni RN propios. Ningún endpoint de esos módulos se documenta ni se infiere aquí (ver sección 10).

---

# 2. Convenciones generales

- **Prefijo y versionado:** todas las rutas se exponen bajo `/api/v1/`. Un cambio incompatible futuro en el contrato de la API se expondría como una nueva versión (`/api/v2/`), sin romper clientes existentes.
- **Formato:** todas las solicitudes y respuestas usan JSON.
- **Verbos HTTP:** `POST` para acciones y creación de recursos (registro, login, recuperación), `GET` para consultas (RF-015), `PATCH` para actualización parcial (RF-016, ya que solo el campo `name` es editable, no un reemplazo completo del recurso).
- **Documentación automática:** todos los endpoints quedan documentados automáticamente vía Swagger/OpenAPI, generado por FastAPI a partir de los esquemas Pydantic de `schemas.py` (RNF-019), consistente con `03_Arquitectura_Backend.md` (sección 3.4).
- **Transporte:** toda comunicación ocurre exclusivamente sobre HTTPS/TLS (RNF-001), consistente con `01_Arquitectura.md` (sección 2).
- **Rutas de perfil basadas en la identidad del token:** las rutas de perfil son `/profile/me`, nunca `/profile/{id}` ni `/users/{id}`. La identidad del usuario sobre el que opera cada solicitud se determina exclusivamente a partir del JWT validado por `Depends(get_current_user)`, nunca a partir de un parámetro enviado por el cliente, conforme a RN-018 ("la identidad del perfil consultado o editado se determina exclusivamente a partir del token JWT de la sesión, nunca de un parámetro enviado por el cliente").

---

# 3. Tabla resumen de endpoints

Esta tabla sirve como lista de verificación durante la implementación: todo endpoint marcado como **Protegido** debe declarar `Depends(get_current_user)` (`03_Arquitectura_Backend.md`, sección 4.3) en su firma.

| Método | Ruta | Acceso | CU | RF relacionados |
|---|---|---|---|---|
| `POST` | `/api/v1/auth/register` | Público | CU-001 | RF-001 a RF-005 |
| `POST` | `/api/v1/auth/login` | Público | CU-002 | RF-006 a RF-008, RF-011, RF-017 |
| `POST` | `/api/v1/auth/forgot-password` | Público | CU-004 | RF-012 |
| `POST` | `/api/v1/auth/reset-password` | Público | CU-004 | RF-013, RF-014 |
| `GET` | `/api/v1/profile/me` | **Protegido** | CU-006 | RF-015 |
| `PATCH` | `/api/v1/profile/me` | **Protegido** | CU-007 | RF-016 |

No existe un endpoint de cierre de sesión (ver sección 5).

---

# 4. Detalle de endpoints

## 4.1 `POST /api/v1/auth/register`

**Autenticación:** ninguna (endpoint público).

**Cuerpo de la solicitud:**
```json
{
  "name": "string",
  "email": "string (formato de correo válido)",
  "password": "string (8-128 caracteres)"
}
```
Validaciones: `name` requerido; `email` requerido y con formato válido (RF-003); `password` requerido, entre 8 y 128 caracteres (RF-004, RNF-006).

**Respuesta exitosa:** `201 Created`
```json
{
  "id": 1,
  "name": "string",
  "email": "string"
}
```

**Respuestas de error:**
- `409 Conflict`: el correo ya está registrado (RF-002; ver sección 6 sobre por qué este caso es una excepción intencional a RN-014).
- `422 Unprocessable Entity`: error de validación de Pydantic (formato de correo inválido, contraseña fuera de rango, campos faltantes).

**Respalda:** RF-001 a RF-005, RN-001 a RN-004, RN-011, RN-012 (el `password_hash` se genera server-side y nunca se expone, ver sección 8).

## 4.2 `POST /api/v1/auth/login`

**Autenticación:** ninguna (endpoint público).

**Cuerpo de la solicitud:**
```json
{
  "email": "string",
  "password": "string"
}
```

**Respuesta exitosa:** `200 OK`
```json
{
  "access_token": "string (JWT)",
  "token_type": "bearer"
}
```
El token se firma con HS256 y expira en 7 días (RNF-004, RNF-005, RF-007, RF-011).

**Respuestas de error:**
- `401 Unauthorized`: credenciales inválidas, con mensaje genérico que no indica cuál campo falló (RF-008, RN-014; ver sección 6).
- `429 Too Many Requests`: se superaron 5 intentos fallidos en 15 minutos para la misma cuenta/IP (RF-017, RNF-008, RN-010).
- `422 Unprocessable Entity`: error de validación de Pydantic (campos faltantes o con formato inválido).

**Respalda:** RF-006 a RF-008, RF-011, RF-017.

## 4.3 `POST /api/v1/auth/forgot-password`

**Autenticación:** ninguna (endpoint público).

**Cuerpo de la solicitud:**
```json
{
  "email": "string"
}
```

**Respuesta exitosa:** `200 OK`, con un mensaje genérico de confirmación, **idéntico exista o no una cuenta asociada a ese correo** (RF-012, RN-014; ver sección 6):
```json
{
  "message": "Si el correo está registrado, recibirás instrucciones para restablecer tu contraseña."
}
```

**Respuestas de error:**
- `429 Too Many Requests`: se superó el límite de 1 solicitud por correo cada 5 minutos (RNF-010, RN-017).
- `422 Unprocessable Entity`: error de validación de Pydantic (campo `email` faltante o mal formado).

No existe una respuesta que indique "correo no encontrado": ese caso también responde `200 OK` con el mismo mensaje genérico (ver sección 6).

**Respalda:** RF-012, RF-013 (la generación interna del token, cuando el correo corresponde a una cuenta real, ocurre como efecto de este endpoint).

## 4.4 `POST /api/v1/auth/reset-password`

**Autenticación:** ninguna (endpoint público; la validez de la operación depende del token de restablecimiento recibido en el cuerpo, no de un JWT de sesión).

**Cuerpo de la solicitud:**
```json
{
  "token": "string",
  "new_password": "string (8-128 caracteres)"
}
```
Validaciones: `token` requerido; `new_password` requerida, entre 8 y 128 caracteres (RF-004, aplicado también al restablecimiento).

**Respuesta exitosa:** `200 OK`
```json
{
  "message": "Contraseña actualizada correctamente."
}
```

**Respuestas de error:**
- `401 Unauthorized`: el token está ausente, es inválido, ya fue usado, o está expirado (RF-014, RN-015, RN-016).
- `422 Unprocessable Entity`: error de validación de Pydantic (`new_password` fuera del rango permitido, campos faltantes).

**Respalda:** RF-013, RF-014.

## 4.5 `GET /api/v1/profile/me`

**Autenticación:** requerida (`Depends(get_current_user)`).

**Cuerpo de la solicitud:** ninguno.

**Respuesta exitosa:** `200 OK`
```json
{
  "id": 1,
  "name": "string",
  "email": "string"
}
```

**Respuestas de error:**
- `401 Unauthorized`: token ausente, inválido o expirado (RF-010, RN-013).

**Respalda:** RF-015.

## 4.6 `PATCH /api/v1/profile/me`

**Autenticación:** requerida (`Depends(get_current_user)`).

**Cuerpo de la solicitud:**
```json
{
  "name": "string"
}
```
Validaciones: `name` requerido, no vacío (único campo editable del perfil, RN-019).

**Respuesta exitosa:** `200 OK`
```json
{
  "id": 1,
  "name": "string",
  "email": "string"
}
```

**Respuestas de error:**
- `401 Unauthorized`: token ausente, inválido o expirado (RF-010, RN-013).
- `422 Unprocessable Entity`: `name` vacío o con formato inválido.

**Respalda:** RF-016.

---

# 5. Ausencia intencional de un endpoint de cierre de sesión

Deliberadamente **no existe** un endpoint `POST /api/v1/auth/logout`. Esto no es una omisión: RF-009 y RN-008 establecen que el cierre de sesión se resuelve enteramente en el cliente, eliminando el token JWT almacenado localmente, sin que el backend participe en la operación.

El backend permanece stateless (RN-009): no mantiene ninguna lista de tokens revocados ni un registro de sesiones activas, por lo que no existe nada que un endpoint de logout pudiera invalidar del lado del servidor. Este comportamiento ya está documentado en detalle en `02_Arquitectura_Movil.md` (secciones 6.1 y 7), donde `AuthProvider.logout()` elimina el token de `flutter_secure_storage` sin realizar ninguna solicitud HTTP.

---

# 6. Respuestas genéricas y no revelación de existencia de cuenta

RN-014 exige que, ante credenciales inválidas en el inicio de sesión o ante una solicitud de recuperación de contraseña, el sistema nunca revele si un correo corresponde a una cuenta existente:

- **`POST /api/v1/auth/login`:** ante correo inexistente o contraseña incorrecta, responde siempre `401 Unauthorized` con el mismo mensaje genérico, sin indicar cuál de los dos datos falló (RF-008, RN-014).
- **`POST /api/v1/auth/forgot-password`:** responde siempre `200 OK` con el mismo mensaje genérico, exista o no una cuenta asociada al correo ingresado (RF-012, RN-014).

**Importante — excepción intencional en el registro:** `POST /api/v1/auth/register` **sí** responde `409 Conflict` indicando explícitamente que el correo ya está registrado, porque RF-002 lo exige literalmente en sus criterios de aceptación ("se muestra un mensaje indicando que el correo ya se encuentra registrado"). Esto **no contradice RN-014**: el alcance de RN-014, según su propia descripción, se limita explícitamente al inicio de sesión y a la recuperación de contraseña, no al registro. Ambos comportamientos son correctos y deliberadamente distintos entre sí; durante la implementación, ninguno de los dos debe "corregirse" para igualarlo al otro.

---

# 7. Formato consistente de errores

Conforme a RNF-022, todas las respuestas de error siguen una estructura consistente, sin exponer stack traces ni detalles internos de implementación (nombres de excepciones, rutas de archivos, consultas SQL). Los errores de validación de Pydantic (`422`) utilizan el formato estándar que FastAPI genera automáticamente a partir de los esquemas de `schemas.py`, que ya es estructurado y no expone información interna. Los demás errores (`401`, `409`, `429`) responden con una estructura mínima consistente:

```json
{
  "detail": "mensaje de error entendible para el cliente"
}
```

---

# 8. Datos nunca expuestos en las respuestas

Ninguna respuesta de la API, en ningún endpoint, incluye `password_hash` ni el hash del token de restablecimiento (`token_hash`, ver `04_Modelo_Base_de_Datos.md`, sección 3.1). Los esquemas de respuesta (`schemas.py`, `03_Arquitectura_Backend.md` sección 3.4) exponen únicamente los campos necesarios (`id`, `name`, `email`), nunca los modelos de base de datos directamente, conforme a RNF-012 y RN-011.

---

# 9. Trazabilidad de este documento

| Decisión de diseño | RF | RNF | RN | HU/CU |
|---|---|---|---|---|
| Prefijo `/api/v1/` y versionado | — | — | — | — |
| Documentación automática vía Swagger/OpenAPI | — | RNF-019 | — | — |
| Comunicación exclusivamente HTTPS | — | RNF-001 | — | — |
| Rutas de perfil `/profile/me` basadas en el token | RF-015, RF-016 | — | RN-018 | CU-006, CU-007 |
| `POST /auth/register` | RF-001 a RF-005 | — | RN-001 a RN-004, RN-011, RN-012 | HU-001, CU-001 |
| `POST /auth/login` | RF-006 a RF-008, RF-011, RF-017 | RNF-004, RNF-005, RNF-008 | RN-005, RN-006, RN-010, RN-014 | HU-002, CU-002 |
| `POST /auth/forgot-password` | RF-012, RF-013 | RNF-009, RNF-010 | RN-014, RN-016, RN-017 | HU-004, CU-004 |
| `POST /auth/reset-password` | RF-013, RF-014 | RNF-009 | RN-015, RN-016 | HU-005, CU-004 |
| `GET /profile/me` | RF-015 | — | RN-013, RN-018 | HU-007, CU-006 |
| `PATCH /profile/me` | RF-016 | — | RN-013, RN-018, RN-019 | HU-008, CU-007 |
| Ausencia intencional de endpoint de logout | RF-009 | RNF-015 | RN-008, RN-009 | HU-003, CU-003 |
| Respuesta genérica en login | RF-008 | — | RN-014 | CU-002 |
| Respuesta genérica en forgot-password | RF-012 | — | RN-014 | CU-004 |
| Excepción intencional: `409` en registro | RF-002 | — | — | CU-001 |
| Formato consistente de errores | — | RNF-022 | — | — |
| No exposición de `password_hash`/`token_hash` en respuestas | — | RNF-012 | RN-011 | — |

---

# 10. Endpoints pendientes de diseño

Los siguientes módulos del alcance del MVP no cuentan con diseño de API en este documento, por no tener aún RF, RNF ni RN aprobados: Materias, Tareas, Calendario, Horario, Recursos, Documentos, Dashboard y Herramientas (Calculadora de notas, Temporizador Pomodoro).

Ningún endpoint, ruta ni contrato de esos módulos se documenta ni se infiere aquí. Su diseño de API se definirá en actualizaciones futuras de `docs/03-Diseno/`, una vez completen su fase de requisitos siguiendo la misma metodología incremental aplicada a Autenticación y Perfil. Conforme a RNF-016 y a lo ya establecido en `03_Arquitectura_Backend.md` (sección 6), sus rutas se protegerán reutilizando `Depends(get_current_user)` bajo el mismo prefijo `/api/v1/`, sin requerir cambios a los endpoints aquí definidos.
