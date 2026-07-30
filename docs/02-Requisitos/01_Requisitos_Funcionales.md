# Requisitos Funcionales — Módulo de Autenticación

## Propósito del documento

El presente documento define los requisitos funcionales (RF) del módulo de **Autenticación** de Stunex, correspondientes al primer módulo documentado dentro de la fase de requisitos del proyecto.

Cada requisito cuenta con un identificador único, una descripción, una prioridad y sus criterios de aceptación.

---

# 1. Registro

## RF-001

**Nombre:** Registrar usuario

**Descripción:** El sistema permitirá que un estudiante cree una cuenta ingresando nombre, correo electrónico y contraseña.

**Prioridad:** Alta

**Criterios de aceptación:**
- Los campos nombre, correo y contraseña son obligatorios.
- La cuenta solo se crea si se cumplen las validaciones definidas en RF-002, RF-003, RF-004 y RF-005.

---

## RF-002

**Nombre:** Validar unicidad del correo electrónico

**Descripción:** El sistema no permitirá registrar dos cuentas asociadas al mismo correo electrónico.

**Prioridad:** Alta

**Criterios de aceptación:**
- Un intento de registro con un correo ya existente es rechazado.
- Se muestra un mensaje indicando que el correo ya se encuentra registrado.

---

## RF-003

**Nombre:** Validar formato de correo electrónico

**Descripción:** El sistema verificará que el correo ingresado tenga un formato válido antes de procesar el registro.

**Prioridad:** Alta

**Criterios de aceptación:**
- Correos con formato inválido son rechazados.
- La validación ocurre antes de consultar o modificar la base de datos.

---

## RF-004

**Nombre:** Validar reglas mínimas de seguridad de la contraseña

**Descripción:** El sistema exigirá que la contraseña cumpla una longitud y complejidad mínimas definidas para el proyecto.

**Prioridad:** Alta

**Criterios de aceptación:**
- Contraseñas que no cumplan el mínimo definido son rechazadas.
- Se informa al usuario el motivo por el cual la contraseña no es válida.

---

## RF-005

**Nombre:** Hashear la contraseña con bcrypt

**Descripción:** El sistema hasheará la contraseña utilizando bcrypt antes de almacenarla. En ningún caso se almacenará la contraseña en texto plano.

**Prioridad:** Alta

**Criterios de aceptación:**
- La base de datos únicamente contiene el hash bcrypt de la contraseña.
- La contraseña original no puede recuperarse a partir del hash almacenado.
- La contraseña en texto plano no se registra en logs del sistema.

---

# 2. Inicio y cierre de sesión

## RF-006

**Nombre:** Iniciar sesión

**Descripción:** El sistema permitirá autenticar a un usuario registrado mediante su correo electrónico y contraseña.

**Prioridad:** Alta

**Criterios de aceptación:**
- Credenciales correctas permiten el acceso del usuario al sistema.
- El resultado de un inicio de sesión exitoso incluye un token JWT, según RF-007.

---

## RF-007

**Nombre:** Generar token JWT al autenticar

**Descripción:** Tras un inicio de sesión exitoso, el sistema emitirá un access token JWT que identifica al usuario autenticado.

**Prioridad:** Alta

**Criterios de aceptación:**
- El token generado contiene la información mínima necesaria para identificar al usuario.
- El token incluye una fecha de expiración, según lo definido en RF-011.

---

## RF-008

**Nombre:** Rechazar credenciales inválidas

**Descripción:** El sistema rechazará los intentos de inicio de sesión con correo o contraseña incorrectos, sin indicar cuál de los dos datos falló.

**Prioridad:** Alta

**Criterios de aceptación:**
- Ante correo inexistente o contraseña incorrecta se muestra el mismo mensaje genérico ("credenciales inválidas").
- El sistema no revela si el correo ingresado existe o no en la base de datos.

---

## RF-009

**Nombre:** Cerrar sesión

**Descripción:** El cierre de sesión se implementará mediante la eliminación del token de autenticación almacenado en el cliente (aplicación móvil). En el MVP no se implementa revocación del token del lado del servidor.

**Prioridad:** Media

**Criterios de aceptación:**
- Al cerrar sesión, el cliente elimina el token almacenado localmente.
- Tras el cierre de sesión, el cliente no puede acceder a endpoints protegidos sin autenticarse nuevamente.
- El token permanece técnicamente válido del lado del servidor hasta su expiración natural (RF-011); no existe revocación anticipada en el MVP.

---

## RF-010

**Nombre:** Proteger endpoints privados mediante JWT

**Descripción:** Los endpoints que requieren autenticación validarán el token JWT recibido antes de procesar la solicitud.

**Prioridad:** Alta

**Criterios de aceptación:**
- Solicitudes sin token son rechazadas con código de error 401.
- Solicitudes con token inválido o expirado son rechazadas con código de error 401.

---

## RF-011

**Nombre:** Expiración del token JWT

**Descripción:** El access token JWT tendrá un tiempo de vida definido, transcurrido el cual dejará de ser válido. El MVP utiliza únicamente access tokens; no se implementan refresh tokens.

**Prioridad:** Alta

**Criterios de aceptación:**
- Un token utilizado después de su tiempo de expiración es rechazado.
- No existe mecanismo de refresh token en el MVP; queda documentado como posible funcionalidad futura.

---

# 3. Recuperación de contraseña

## RF-012

**Nombre:** Solicitar recuperación de contraseña

**Descripción:** El usuario podrá solicitar la recuperación de su contraseña ingresando su correo electrónico. Ante cualquier solicitud, el sistema responderá con un mensaje genérico, independientemente de si el correo se encuentra registrado o no. Si existe una cuenta asociada al correo, se generará internamente la solicitud de recuperación (token de restablecimiento, según RF-013). El proveedor de envío de correo queda pendiente de definición técnica.

**Prioridad:** Alta

**Criterios de aceptación:**
- La respuesta del sistema es idéntica tanto si el correo existe como si no, evitando revelar si una cuenta está registrada.
- Si el correo corresponde a una cuenta existente, se genera un token de restablecimiento según RF-013.
- El mecanismo concreto de envío de correo (proveedor SMTP/servicio externo) no se define en este documento.

---

## RF-013

**Nombre:** Generar token temporal de restablecimiento

**Descripción:** El sistema generará un token de un solo uso, con expiración corta, destinado exclusivamente al restablecimiento de contraseña.

**Prioridad:** Alta

**Criterios de aceptación:**
- El token es de un solo uso.
- El token expira transcurrido un periodo de tiempo corto definido para el proyecto.
- El token no es válido para ninguna operación distinta al restablecimiento de contraseña.

---

## RF-014

**Nombre:** Restablecer contraseña mediante token

**Descripción:** El usuario podrá definir una nueva contraseña presentando un token de restablecimiento válido y no expirado.

**Prioridad:** Alta

**Criterios de aceptación:**
- Un token expirado, ya utilizado o inválido es rechazado.
- La nueva contraseña debe cumplir las mismas validaciones definidas en RF-004.
- La nueva contraseña se almacena hasheada según lo definido en RF-005.

---

# 4. Perfil

## RF-015

**Nombre:** Consultar perfil del usuario autenticado

**Descripción:** El usuario autenticado podrá consultar los datos básicos de su propio perfil.

**Prioridad:** Media

**Criterios de aceptación:**
- Únicamente el usuario autenticado, mediante su token JWT, puede consultar su propio perfil.
- La consulta requiere que el endpoint esté protegido según RF-010.

---

## RF-016

**Nombre:** Editar datos básicos del perfil

**Descripción:** El usuario autenticado podrá editar el nombre asociado a su perfil. La foto de perfil queda fuera del alcance del MVP.

**Prioridad:** Media

**Criterios de aceptación:**
- Únicamente el campo nombre es editable en esta versión del sistema.
- Los cambios realizados se validan y se persisten correctamente.
- No se implementa edición ni almacenamiento de foto de perfil en el MVP.

---

# 5. Seguridad de autenticación

## RF-017

**Nombre:** Limitar solicitudes excesivas de inicio de sesión

**Descripción:** El sistema limitará la cantidad de intentos de inicio de sesión permitidos en una ventana de tiempo determinada, mediante un mecanismo de rate limiting básico, con el fin de mitigar ataques de fuerza bruta. No se implementa bloqueo permanente de cuentas.

**Prioridad:** Media

**Criterios de aceptación:**
- Al superar el límite de intentos definido dentro de la ventana de tiempo establecida, las solicitudes adicionales son rechazadas temporalmente.
- El límite exacto de intentos y la duración de la ventana de tiempo se definirán en el documento de requisitos no funcionales.
- No se implementa bloqueo permanente de la cuenta bajo ninguna circunstancia en el MVP.

---

# Resumen de requisitos

| ID | Nombre | Prioridad |
|----|--------|-----------|
| RF-001 | Registrar usuario | Alta |
| RF-002 | Validar unicidad del correo electrónico | Alta |
| RF-003 | Validar formato de correo electrónico | Alta |
| RF-004 | Validar reglas mínimas de seguridad de la contraseña | Alta |
| RF-005 | Hashear la contraseña con bcrypt | Alta |
| RF-006 | Iniciar sesión | Alta |
| RF-007 | Generar token JWT al autenticar | Alta |
| RF-008 | Rechazar credenciales inválidas | Alta |
| RF-009 | Cerrar sesión | Media |
| RF-010 | Proteger endpoints privados mediante JWT | Alta |
| RF-011 | Expiración del token JWT | Alta |
| RF-012 | Solicitar recuperación de contraseña | Alta |
| RF-013 | Generar token temporal de restablecimiento | Alta |
| RF-014 | Restablecer contraseña mediante token | Alta |
| RF-015 | Consultar perfil del usuario autenticado | Media |
| RF-016 | Editar datos básicos del perfil | Media |
| RF-017 | Limitar solicitudes excesivas de inicio de sesión | Media |
