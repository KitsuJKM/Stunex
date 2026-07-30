# Reglas de Negocio — Stunex

## Propósito del documento

El presente documento define las reglas de negocio (RN) de Stunex, correspondientes a los módulos de **Autenticación** y **Perfil**, ya documentados mediante RF-001 a RF-017, RNF-001 a RNF-024, HU-001 a HU-008 y CU-001 a CU-007.

A diferencia de los requisitos funcionales, las reglas de negocio representan restricciones, condiciones y políticas que el sistema debe respetar independientemente de la interfaz utilizada (aplicación móvil, API, o cualquier cliente futuro).

---

# 1. Gestión de cuentas

## RN-001

**Nombre:** Unicidad de correo electrónico

**Descripción:** Un correo electrónico solo puede estar asociado a una única cuenta en todo el sistema.

**Módulo:** Gestión de cuentas

**Prioridad:** Alta

**RF relacionados:** RF-002

**RNF relacionados:** RNF-018

**CU relacionados:** CU-001

**Regla/condición concreta:** El sistema rechaza cualquier intento de asociar un segundo registro al mismo correo, tanto a nivel de aplicación como mediante restricción de unicidad en la base de datos.

---

## RN-002

**Nombre:** Validez de formato de correo

**Descripción:** Ningún correo con formato inválido puede ser aceptado por el sistema, independientemente del punto de entrada.

**Módulo:** Gestión de cuentas

**Prioridad:** Alta

**RF relacionados:** RF-003

**RNF relacionados:** —

**CU relacionados:** CU-001

**Regla/condición concreta:** Se aplica una validación de formato de correo antes de cualquier persistencia o consulta a la base de datos.

---

## RN-003

**Nombre:** Rango de longitud de contraseña

**Descripción:** Toda contraseña del sistema, sea en registro o en restablecimiento, debe tener entre 8 y 128 caracteres.

**Módulo:** Gestión de cuentas

**Prioridad:** Alta

**RF relacionados:** RF-004

**RNF relacionados:** RNF-006

**CU relacionados:** CU-001, CU-004

**Regla/condición concreta:** Contraseñas fuera de ese rango se rechazan en cualquier flujo que las reciba.

---

## RN-004

**Nombre:** Sin exigencia de complejidad adicional

**Descripción:** El sistema no exige mayúsculas, números ni símbolos obligatorios en la contraseña, más allá del rango de longitud definido en RN-003.

**Módulo:** Gestión de cuentas

**Prioridad:** Media

**RF relacionados:** RF-004

**RNF relacionados:** RNF-006

**CU relacionados:** CU-001, CU-004

**Regla/condición concreta:** Ninguna validación de complejidad adicional debe implementarse salvo un cambio explícito de alcance aprobado por el equipo.

---

# 2. Autenticación

## RN-005

**Nombre:** Algoritmo de firma del JWT

**Descripción:** Todo token JWT emitido por el sistema debe firmarse con el algoritmo HS256.

**Módulo:** Autenticación

**Prioridad:** Media

**RF relacionados:** RF-007

**RNF relacionados:** RNF-005

**CU relacionados:** CU-002

**Regla/condición concreta:** Ningún otro algoritmo de firma es válido en el MVP.

---

## RN-006

**Nombre:** Vigencia del access token

**Descripción:** El access token JWT es válido durante 7 días desde su emisión.

**Módulo:** Autenticación

**Prioridad:** Alta

**RF relacionados:** RF-011

**RNF relacionados:** RNF-004

**CU relacionados:** CU-002, CU-005

**Regla/condición concreta:** Transcurrido ese periodo, el token deja de ser aceptado por cualquier endpoint protegido.

---

## RN-007

**Nombre:** Ausencia de refresh tokens

**Descripción:** El MVP no implementa mecanismo de refresh token; solo existen access tokens.

**Módulo:** Autenticación

**Prioridad:** Alta

**RF relacionados:** RF-011

**RNF relacionados:** RNF-004

**CU relacionados:** CU-002

**Regla/condición concreta:** Al expirar el access token, el único camino disponible es un nuevo inicio de sesión completo; los refresh tokens quedan documentados como posible funcionalidad futura.

---

## RN-008

**Nombre:** Cierre de sesión mediante eliminación local del token

**Descripción:** El cierre de sesión se resuelve eliminando el token en el cliente; no existe invalidación del lado del servidor.

**Módulo:** Autenticación

**Prioridad:** Media

**RF relacionados:** RF-009

**RNF relacionados:** —

**CU relacionados:** CU-003

**Regla/condición concreta:** El servidor no mantiene ninguna lista de tokens revocados ni verifica el estado de "sesión cerrada" del lado del backend.

---

## RN-009

**Nombre:** Gestión stateless de la sesión

**Descripción:** El backend no mantiene sesiones ni mecanismos de revocación de tokens del lado del servidor; toda la autenticación se resuelve validando la firma y vigencia del JWT en cada solicitud.

**Módulo:** Autenticación

**Prioridad:** Alta

**RF relacionados:** RF-009, RF-010, RF-011

**RNF relacionados:** RNF-015

**CU relacionados:** CU-003, CU-005

**Regla/condición concreta:** Un token robado o filtrado permanece técnicamente válido hasta su expiración natural (7 días); no existe forma de invalidarlo anticipadamente en el MVP. Esta limitación de seguridad se acepta explícitamente dado el alcance académico del proyecto.

---

## RN-010

**Nombre:** Límite de intentos de inicio de sesión

**Descripción:** El sistema limita a 5 los intentos fallidos de inicio de sesión por cuenta/IP en una ventana de 15 minutos, sin bloqueo permanente.

**Módulo:** Autenticación

**Prioridad:** Media

**RF relacionados:** RF-017

**RNF relacionados:** RNF-008

**CU relacionados:** CU-002

**Regla/condición concreta:** Al superar el límite, las solicitudes adicionales se rechazan temporalmente; en ningún caso se bloquea la cuenta de forma permanente.

---

# 3. Seguridad

## RN-011

**Nombre:** Prohibición de contraseñas en texto plano

**Descripción:** Ninguna contraseña se almacena, transmite en logs, ni se expone en texto plano bajo ninguna circunstancia.

**Módulo:** Seguridad

**Prioridad:** Alta

**RF relacionados:** RF-005

**RNF relacionados:** RNF-012

**CU relacionados:** CU-001, CU-004

**Regla/condición concreta:** Toda ruta de código que maneje contraseñas debe hashearlas antes de cualquier persistencia o registro en logs.

---

## RN-012

**Nombre:** Hashing de contraseñas mediante bcrypt

**Descripción:** El algoritmo de hash utilizado para contraseñas es bcrypt, con un factor de costo de 12 rounds.

**Módulo:** Seguridad

**Prioridad:** Alta

**RF relacionados:** RF-005

**RNF relacionados:** RNF-007

**CU relacionados:** CU-001, CU-004

**Regla/condición concreta:** Ningún otro algoritmo de hashing (MD5, SHA sin salt, etc.) es válido para contraseñas en el sistema.

---

## RN-013

**Nombre:** Protección obligatoria de endpoints privados

**Descripción:** Todo endpoint que exponga información privada del estudiante exige un JWT válido.

**Módulo:** Seguridad

**Prioridad:** Alta

**RF relacionados:** RF-010

**RNF relacionados:** —

**CU relacionados:** CU-005, CU-006, CU-007

**Regla/condición concreta:** No puede existir un endpoint de datos privados sin que la validación descrita en CU-005 se ejecute como precondición.

---

## RN-014

**Nombre:** No revelación de existencia de cuenta

**Descripción:** Ante credenciales inválidas en el inicio de sesión o ante una solicitud de recuperación de contraseña, el sistema nunca revela si el correo ingresado corresponde a una cuenta existente.

**Módulo:** Seguridad

**Prioridad:** Alta

**RF relacionados:** RF-008, RF-012

**RNF relacionados:** —

**CU relacionados:** CU-002, CU-004

**Regla/condición concreta:** La respuesta del sistema es idéntica en forma y contenido, exista o no la cuenta, tanto en el flujo de login como en el de recuperación.

---

# 4. Recuperación de cuentas

## RN-015

**Nombre:** Uso único del token de recuperación

**Descripción:** Un token de restablecimiento de contraseña solo puede utilizarse una vez.

**Módulo:** Recuperación de cuentas

**Prioridad:** Alta

**RF relacionados:** RF-013

**RNF relacionados:** —

**CU relacionados:** CU-004

**Regla/condición concreta:** Tras un restablecimiento exitoso, el token queda invalidado de forma permanente, incluso si aún no ha expirado.

---

## RN-016

**Nombre:** Vigencia del token de recuperación

**Descripción:** El token de restablecimiento expira 15 minutos después de su emisión.

**Módulo:** Recuperación de cuentas

**Prioridad:** Alta

**RF relacionados:** RF-013

**RNF relacionados:** RNF-009

**CU relacionados:** CU-004

**Regla/condición concreta:** Un token usado después de ese periodo se rechaza, sin importar que no haya sido utilizado previamente.

---

## RN-017

**Nombre:** Límite de solicitudes de recuperación

**Descripción:** No se permite más de una solicitud de recuperación de contraseña por correo en una ventana de 5 minutos.

**Módulo:** Recuperación de cuentas

**Prioridad:** Media

**RF relacionados:** —

**RNF relacionados:** RNF-010

**CU relacionados:** CU-004

**Regla/condición concreta:** Solicitudes adicionales dentro de la ventana de tiempo se rechazan temporalmente, independientemente de si el correo existe o no (consistente con RN-014).

---

# 5. Perfil

## RN-018

**Nombre:** Acceso exclusivo al propio perfil

**Descripción:** Un estudiante solo puede consultar o modificar su propio perfil; nunca el de otro usuario.

**Módulo:** Perfil

**Prioridad:** Alta

**RF relacionados:** RF-015, RF-016

**RNF relacionados:** —

**CU relacionados:** CU-005, CU-006, CU-007

**Regla/condición concreta:** La identidad del perfil consultado o editado se determina exclusivamente a partir del token JWT de la sesión, nunca de un parámetro enviado por el cliente.

---

## RN-019

**Nombre:** Alcance limitado de edición de perfil

**Descripción:** En el MVP, el único campo editable del perfil es el nombre. No se incluye foto de perfil, ni edición de correo electrónico ni de contraseña desde la pantalla de perfil; el cambio de contraseña ocurre únicamente mediante el flujo de recuperación (CU-004).

**Módulo:** Perfil

**Prioridad:** Media

**RF relacionados:** RF-016

**RNF relacionados:** —

**CU relacionados:** CU-007

**Regla/condición concreta:** Cualquier intento de modificar correo o contraseña desde el endpoint de edición de perfil debe rechazarse o simplemente no exponerse en el MVP.

---

## RN-020

**Nombre:** Minimización de datos personales

**Descripción:** El sistema no recolecta ni almacena datos personales adicionales a nombre y correo en los módulos de Autenticación y Perfil.

**Módulo:** Perfil

**Prioridad:** Media

**RF relacionados:** —

**RNF relacionados:** RNF-011

**CU relacionados:** CU-001, CU-006

**Regla/condición concreta:** Ningún flujo actual del MVP debe solicitar datos personales no contemplados (teléfono, dirección, documento de identidad, etc.).

---

# 6. Datos y almacenamiento — Pendiente

Las reglas de negocio relacionadas con almacenamiento de archivos (tamaño máximo de archivo y tipos de archivo permitidos, ya anticipados en RNF-020 y RNF-021) **no se incluyen todavía** en este documento.

Aunque esos valores ya están definidos a nivel de requisito no funcional, el módulo de **Documentos/Recursos** aún no cuenta con requisitos funcionales (RF), historias de usuario (HU) ni casos de uso (CU) propios. Documentar sus reglas de negocio ahora rompería la trazabilidad RN → RF → HU → CU exigida para este proyecto.

Estas reglas se incorporarán en una futura actualización de este documento, una vez se documente formalmente el módulo de Documentos/Recursos siguiendo la misma metodología incremental aplicada a Autenticación y Perfil.

---

# Matriz de trazabilidad RN → RF → HU → CU

| RN | RF | HU | CU |
|----|----|----|----|
| RN-001 | RF-002 | HU-001 | CU-001 |
| RN-002 | RF-003 | HU-001 | CU-001 |
| RN-003 | RF-004 | HU-001, HU-005 | CU-001, CU-004 |
| RN-004 | RF-004 | HU-001, HU-005 | CU-001, CU-004 |
| RN-005 | RF-007 | HU-002 | CU-002 |
| RN-006 | RF-011 | HU-002 | CU-002, CU-005 |
| RN-007 | RF-011 | HU-002 | CU-002 |
| RN-008 | RF-009 | HU-003 | CU-003 |
| RN-009 | RF-009, RF-010, RF-011 | HU-002, HU-003, HU-006 | CU-003, CU-005 |
| RN-010 | RF-017 | HU-002 | CU-002 |
| RN-011 | RF-005 | HU-001, HU-005 | CU-001, CU-004 |
| RN-012 | RF-005 | HU-001, HU-005 | CU-001, CU-004 |
| RN-013 | RF-010 | HU-006 | CU-005, CU-006, CU-007 |
| RN-014 | RF-008, RF-012 | HU-002, HU-004 | CU-002, CU-004 |
| RN-015 | RF-013 | HU-004 | CU-004 |
| RN-016 | RF-013 | HU-004 | CU-004 |
| RN-017 | — | HU-004 | CU-004 |
| RN-018 | RF-015, RF-016 | HU-007, HU-008 | CU-005, CU-006, CU-007 |
| RN-019 | RF-016 | HU-008 | CU-007 |
| RN-020 | — | — | CU-001, CU-006 |

Las 20 reglas de negocio (RN-001 a RN-020) cubren de forma coherente los 17 requisitos funcionales (RF-001 a RF-017), las 8 historias de usuario (HU-001 a HU-008) y los 7 casos de uso (CU-001 a CU-007) ya documentados. Las reglas de almacenamiento de archivos (asociadas a RNF-020 y RNF-021) quedan pendientes hasta documentar el módulo de Documentos/Recursos.
