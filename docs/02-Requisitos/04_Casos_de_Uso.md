# Casos de Uso — Stunex

## Propósito del documento

El presente documento define los casos de uso (CU) derivados de las historias de usuario HU-001 a HU-008, correspondientes a los módulos de **Autenticación** y **Perfil**.

Cada caso de uso detalla el flujo de interacción entre el actor y el sistema, incluyendo flujos alternativos y de excepción. Un caso de uso puede estar relacionado con una o varias historias de usuario cuando estas representan pasos de un mismo objetivo (como ocurre con la recuperación de contraseña).

Los módulos restantes del alcance de Stunex (Materias, Tareas, Calendario, Horario, Recursos, Documentos, Dashboard, Herramientas) aún no cuentan con historias de usuario documentadas, por lo que sus casos de uso se definirán progresivamente cuando se documente cada módulo.

---

# CU-001 — Registrar cuenta

**Actor principal:** Estudiante (no autenticado)

**Objetivo:** Crear una cuenta nueva en Stunex.

**Historias de usuario relacionadas:** HU-001

**Requisitos funcionales relacionados:** RF-001, RF-002, RF-003, RF-004, RF-005

**Precondiciones:** El estudiante no posee una cuenta previa asociada al correo que va a registrar.

**Flujo principal:**
1. El estudiante abre la pantalla de registro.
2. Ingresa nombre, correo y contraseña.
3. El sistema valida el formato del correo.
4. El sistema valida la unicidad del correo.
5. El sistema valida la longitud de la contraseña (8–128 caracteres).
6. El sistema hashea la contraseña con bcrypt.
7. El sistema crea la cuenta y confirma el registro exitoso.

**Flujos alternativos:**
- A1: El estudiante corrige un dato inválido y reenvía el formulario (regresa al paso 2).

**Flujos de excepción:**
- E1: El correo ya está registrado; el sistema rechaza el registro.
- E2: El formato de correo es inválido; el sistema rechaza el registro.
- E3: La contraseña está fuera del rango permitido (menos de 8 o más de 128 caracteres); el sistema rechaza el registro.

**Postcondiciones:** La cuenta queda creada con la contraseña almacenada en forma hasheada; el estudiante puede iniciar sesión.

**Prioridad:** Alta

---

# CU-002 — Iniciar sesión

**Actor principal:** Estudiante registrado

**Objetivo:** Autenticarse en el sistema para acceder a su información académica.

**Historias de usuario relacionadas:** HU-002

**Requisitos funcionales relacionados:** RF-006, RF-007, RF-008, RF-011, RF-017

**Precondiciones:** El estudiante posee una cuenta registrada.

**Flujo principal:**
1. El estudiante ingresa su correo y contraseña.
2. El sistema valida las credenciales.
3. El sistema genera un token JWT con expiración de 7 días.
4. El sistema entrega el token a la aplicación móvil.
5. El estudiante queda autenticado.

**Flujos alternativos:**
- Ninguno identificado en el MVP.

**Flujos de excepción:**
- E1: Las credenciales son incorrectas; el sistema responde con un mensaje genérico sin indicar qué campo falló.
- E2: Se superan 5 intentos fallidos en 15 minutos para la misma cuenta/IP; el sistema rechaza temporalmente nuevas solicitudes.
- E3: Ocurre un error interno al generar el token; el sistema responde con un mensaje genérico sin exponer detalles internos.

**Postcondiciones:** El estudiante queda autenticado con un token JWT válido almacenado en el cliente.

**Prioridad:** Alta

---

# CU-003 — Cerrar sesión

**Actor principal:** Estudiante autenticado

**Objetivo:** Finalizar la sesión activa en el dispositivo.

**Historias de usuario relacionadas:** HU-003

**Requisitos funcionales relacionados:** RF-009

**Precondiciones:** Existe una sesión activa (token JWT almacenado en el cliente).

**Flujo principal:**
1. El estudiante selecciona la opción de cerrar sesión.
2. La aplicación elimina el token almacenado localmente.
3. La aplicación redirige a la pantalla de inicio de sesión.

**Flujos alternativos:**
- Ninguno identificado.

**Flujos de excepción:**
- E1: Ocurre un error al eliminar el token localmente; la aplicación reintenta la operación o fuerza la limpieza del almacenamiento local.

**Postcondiciones:** El cliente ya no posee un token válido; el estudiante debe autenticarse nuevamente para acceder a funcionalidades protegidas.

**Prioridad:** Media

---

# CU-004 — Recuperar contraseña

**Actor principal:** Estudiante (no autenticado)

**Objetivo:** Recuperar el acceso a la cuenta cuando se olvida la contraseña.

**Historias de usuario relacionadas:** HU-004, HU-005

**Requisitos funcionales relacionados:** RF-004, RF-005, RF-012, RF-013, RF-014

*Nota: RF-004 y RF-005 se incluyen porque el restablecimiento de contraseña aplica las mismas reglas de longitud (RF-004) y hashing con bcrypt (RF-005) definidas para el registro (CU-001).*

**Precondiciones:** El estudiante conoce el correo asociado a su cuenta.

**Flujo principal:**
1. El estudiante ingresa su correo en la pantalla de recuperación.
2. El sistema responde con un mensaje genérico de confirmación, exista o no una cuenta asociada a ese correo.
3. Si el correo corresponde a una cuenta real, el sistema genera internamente un token de restablecimiento de un solo uso, válido durante 15 minutos.
4. El estudiante accede a la pantalla de restablecimiento con el token recibido.
5. El estudiante ingresa el token y la nueva contraseña.
6. El sistema valida que el token esté vigente y no haya sido usado.
7. El sistema valida la nueva contraseña según las mismas reglas de longitud del registro (RF-004).
8. El sistema hashea y almacena la nueva contraseña con bcrypt (RF-005), e invalida el token utilizado.
9. El sistema confirma el restablecimiento exitoso.

**Flujos alternativos:**
- A1: Si el token expiró, el estudiante puede solicitar uno nuevo únicamente si se cumple el límite de rate limiting definido: máximo 1 solicitud por correo cada 5 minutos. Si el límite no se cumple, la nueva solicitud es rechazada temporalmente.

**Flujos de excepción:**
- E1: El correo no está registrado; el sistema responde con el mismo mensaje genérico del paso 2, sin generar un token real.
- E2: El token está expirado, ya fue usado o es inválido; el sistema rechaza el restablecimiento.
- E3: La nueva contraseña está fuera del rango permitido (RF-004); el sistema rechaza el restablecimiento y el token no se invalida.

**Postcondiciones:** La contraseña queda actualizada y almacenada de forma hasheada; el token de restablecimiento queda invalidado tras su uso.

**Prioridad:** Alta

---

# CU-005 — Validar acceso a recursos protegidos

**Tipo:** Caso de uso transversal de seguridad. No representa una funcionalidad que el estudiante ejecute directamente, sino una validación que el sistema aplica en cada solicitud a un endpoint protegido, como condición previa para los demás casos de uso que operan sobre datos privados (CU-006, CU-007, y los módulos futuros que expongan información del estudiante).

**Actor principal:** Estudiante autenticado (de forma indirecta, a través de las solicitudes que realiza su sesión)

**Objetivo:** Garantizar que únicamente el dueño legítimo de una sesión válida pueda acceder a su información.

**Historias de usuario relacionadas:** HU-006

**Requisitos funcionales relacionados:** RF-010, RF-011

**Precondiciones:** Existe un endpoint que expone información privada del estudiante.

**Flujo principal:**
1. El cliente envía una solicitud a un endpoint protegido incluyendo el token JWT.
2. El sistema valida la firma y la vigencia del token.
3. El sistema identifica al usuario dueño del token.
4. El sistema procesa la solicitud y devuelve únicamente los datos correspondientes a ese usuario.

**Flujos alternativos:**
- Ninguno identificado.

**Flujos de excepción:**
- E1: La solicitud no incluye token; el sistema la rechaza con código 401.
- E2: El token es inválido o está expirado; el sistema la rechaza con código 401.

**Postcondiciones:** Solo se entrega información al usuario legítimo dueño de la sesión.

**Prioridad:** Alta

---

# CU-006 — Consultar perfil

**Actor principal:** Estudiante autenticado

**Objetivo:** Ver los datos básicos del perfil propio.

**Historias de usuario relacionadas:** HU-007

**Requisitos funcionales relacionados:** RF-015

**Precondiciones:** El estudiante tiene una sesión activa y válida (CU-005).

**Flujo principal:**
1. El estudiante accede a la pantalla de perfil.
2. La aplicación solicita los datos del perfil al backend, incluyendo el token JWT.
3. El sistema valida el token (CU-005) y retorna los datos del usuario dueño de la sesión.
4. La aplicación muestra el nombre y el correo del estudiante.

**Flujos alternativos:**
- Ninguno identificado.

**Flujos de excepción:**
- E1: El token es inválido o está expirado; ver CU-005 (E1/E2).

**Postcondiciones:** El estudiante visualiza correctamente su información de perfil.

**Prioridad:** Media

---

# CU-007 — Editar nombre de perfil

**Actor principal:** Estudiante autenticado

**Objetivo:** Actualizar el nombre asociado al perfil propio.

**Historias de usuario relacionadas:** HU-008

**Requisitos funcionales relacionados:** RF-016

**Precondiciones:** El estudiante tiene una sesión activa y válida (CU-005).

**Flujo principal:**
1. El estudiante accede a la opción de editar perfil.
2. Ingresa el nuevo nombre.
3. El sistema valida el campo (no vacío, longitud razonable).
4. El sistema actualiza el nombre en la base de datos.
5. El sistema confirma la actualización exitosa.

**Flujos alternativos:**
- Ninguno identificado.

**Flujos de excepción:**
- E1: El nombre es vacío o inválido; el sistema rechaza el cambio y no lo persiste.
- E2: El token es inválido o está expirado; ver CU-005 (E1/E2).

**Postcondiciones:** El nombre del perfil queda actualizado.

**Prioridad:** Media

---

# Matriz de trazabilidad RF → HU → CU

| RF | HU | CU |
|----|----|----|
| RF-001 | HU-001 | CU-001 |
| RF-002 | HU-001 | CU-001 |
| RF-003 | HU-001 | CU-001 |
| RF-004 | HU-001, HU-005 | CU-001, CU-004 |
| RF-005 | HU-001, HU-005 | CU-001, CU-004 |
| RF-006 | HU-002 | CU-002 |
| RF-007 | HU-002 | CU-002 |
| RF-008 | HU-002 | CU-002 |
| RF-009 | HU-003 | CU-003 |
| RF-010 | HU-006 | CU-005 |
| RF-011 | HU-002 | CU-002, CU-005 |
| RF-012 | HU-004 | CU-004 |
| RF-013 | HU-004 | CU-004 |
| RF-014 | HU-005 | CU-004 |
| RF-015 | HU-007 | CU-006 |
| RF-016 | HU-008 | CU-007 |
| RF-017 | HU-002 | CU-002 |

Los 17 requisitos funcionales (RF-001 a RF-017) y las 8 historias de usuario (HU-001 a HU-008) quedan cubiertos por los 7 casos de uso (CU-001 a CU-007).
