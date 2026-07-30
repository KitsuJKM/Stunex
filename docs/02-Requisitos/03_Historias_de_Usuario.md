# Historias de Usuario — Stunex

## Propósito del documento

El presente documento define las historias de usuario (HU) derivadas de los requisitos funcionales RF-001 a RF-017, correspondientes a los módulos de **Autenticación** y **Perfil**.

Cada historia representa una funcionalidad real que utilizará el estudiante, y puede estar relacionada con uno o varios requisitos funcionales. Los requisitos no funcionales (RNF) no se documentan como historias independientes, pero influyen en los criterios de aceptación cuando corresponde.

Los módulos restantes del alcance de Stunex (Materias, Tareas, Calendario, Horario, Recursos, Documentos, Dashboard, Herramientas) aún no cuentan con requisitos funcionales documentados, por lo que sus historias de usuario se definirán progresivamente cuando se documente cada módulo.

---

# 1. Autenticación

## HU-001

**Nombre:** Crear una cuenta

**Actor:** Estudiante nuevo

**Historia:** Como estudiante nuevo, quiero crear una cuenta con mi nombre, correo y contraseña, para poder acceder a Stunex y empezar a organizar mi vida académica.

**Requisitos funcionales relacionados:** RF-001, RF-002, RF-003, RF-004, RF-005

**Prioridad:** Alta

**Criterios de aceptación:**
- El correo debe ser único en el sistema; si ya existe, se rechaza el registro.
- El formato del correo se valida antes de crear la cuenta.
- La contraseña debe tener entre 8 y 128 caracteres, sin exigir mayúsculas, números o símbolos obligatorios.
- La contraseña se almacena hasheada con bcrypt, nunca en texto plano.
- Al completarse el registro, el estudiante puede iniciar sesión inmediatamente.

---

## HU-002

**Nombre:** Iniciar sesión

**Actor:** Estudiante registrado

**Historia:** Como estudiante registrado, quiero iniciar sesión con mi correo y contraseña, para acceder a mis materias, tareas y demás información académica.

**Requisitos funcionales relacionados:** RF-006, RF-007, RF-008, RF-011, RF-017

**Prioridad:** Alta

**Criterios de aceptación:**
- Credenciales correctas devuelven un token JWT válido, con expiración de 7 días.
- Credenciales incorrectas muestran un mensaje genérico, sin indicar si falló el correo o la contraseña.
- Tras 5 intentos fallidos en 15 minutos (misma cuenta/IP), las solicitudes adicionales se rechazan temporalmente, sin bloqueo permanente de la cuenta.

---

## HU-003

**Nombre:** Cerrar sesión

**Actor:** Estudiante autenticado

**Historia:** Como estudiante autenticado, quiero cerrar sesión en la aplicación, para proteger el acceso a mi cuenta cuando no la estoy usando, especialmente en dispositivos compartidos.

**Requisitos funcionales relacionados:** RF-009

**Prioridad:** Media

**Criterios de aceptación:**
- Al cerrar sesión, el token almacenado en el dispositivo se elimina.
- Tras cerrar sesión, no se puede acceder a pantallas ni datos protegidos sin volver a iniciar sesión.

---

## HU-004

**Nombre:** Solicitar recuperación de contraseña

**Actor:** Estudiante que olvidó su contraseña

**Historia:** Como estudiante que olvidó su contraseña, quiero solicitar su recuperación ingresando mi correo, para poder recuperar el acceso a mi cuenta sin depender de soporte manual.

**Requisitos funcionales relacionados:** RF-012, RF-013

**Prioridad:** Alta

**Criterios de aceptación:**
- La respuesta es siempre un mensaje genérico, exista o no una cuenta con ese correo.
- Si el correo corresponde a una cuenta real, se genera un token de restablecimiento de un solo uso, válido por 15 minutos.
- No se pueden enviar más de 1 solicitud por correo cada 5 minutos.

---

## HU-005

**Nombre:** Restablecer contraseña con token

**Actor:** Estudiante que solicitó recuperación

**Historia:** Como estudiante que solicitó recuperar mi contraseña, quiero definir una nueva contraseña usando el token recibido, para volver a acceder a mi cuenta de forma segura.

**Requisitos funcionales relacionados:** RF-014

**Prioridad:** Alta

**Criterios de aceptación:**
- Un token expirado, ya usado o inválido es rechazado.
- La nueva contraseña cumple las mismas reglas de longitud (8–128 caracteres) que en el registro.
- La nueva contraseña se almacena hasheada con bcrypt.

---

## HU-006

**Nombre:** Protección de mi información académica

**Actor:** Estudiante autenticado

**Historia:** Como estudiante autenticado, quiero que mi información personal y académica solo sea accesible mediante mi sesión válida, para evitar que otras personas accedan o modifiquen mis datos sin autorización.

**Requisitos funcionales relacionados:** RF-010

**Prioridad:** Alta

**Criterios de aceptación:**
- Cualquier solicitud a endpoints privados sin token, o con token inválido o expirado, es rechazada.
- Solo el usuario dueño del token puede acceder a su propia información.

---

# 2. Perfil

## HU-007

**Nombre:** Consultar mi perfil

**Actor:** Estudiante autenticado

**Historia:** Como estudiante autenticado, quiero consultar los datos de mi perfil, para verificar que mi información esté correcta.

**Requisitos funcionales relacionados:** RF-015

**Prioridad:** Media

**Criterios de aceptación:**
- Solo el propio usuario, mediante su sesión activa, puede ver su perfil.
- Se muestran los datos básicos registrados (nombre, correo).

---

## HU-008

**Nombre:** Editar mi nombre en el perfil

**Actor:** Estudiante autenticado

**Historia:** Como estudiante autenticado, quiero editar mi nombre en mi perfil, para mantener mi información actualizada.

**Requisitos funcionales relacionados:** RF-016

**Prioridad:** Media

**Criterios de aceptación:**
- Solo el campo nombre es editable en esta versión.
- El cambio se valida y persiste correctamente.
- No existe opción de foto de perfil en el MVP.

---

# Matriz de trazabilidad RF → HU

| RF | Descripción breve | HU que lo cubre |
|----|--------------------|--------------------|
| RF-001 | Registrar usuario | HU-001 |
| RF-002 | Validar unicidad de correo | HU-001 |
| RF-003 | Validar formato de correo | HU-001 |
| RF-004 | Reglas mínimas de contraseña | HU-001, HU-005 |
| RF-005 | Hashear contraseña con bcrypt | HU-001, HU-005 |
| RF-006 | Iniciar sesión | HU-002 |
| RF-007 | Generar token JWT | HU-002 |
| RF-008 | Rechazar credenciales inválidas | HU-002 |
| RF-009 | Cerrar sesión | HU-003 |
| RF-010 | Proteger endpoints mediante JWT | HU-006 |
| RF-011 | Expiración del token JWT | HU-002 |
| RF-012 | Solicitar recuperación de contraseña | HU-004 |
| RF-013 | Generar token temporal de restablecimiento | HU-004 |
| RF-014 | Restablecer contraseña mediante token | HU-005 |
| RF-015 | Consultar perfil | HU-007 |
| RF-016 | Editar datos básicos del perfil | HU-008 |
| RF-017 | Rate limiting en login | HU-002 |

Los 17 requisitos funcionales (RF-001 a RF-017) quedan cubiertos por al menos una historia de usuario.
