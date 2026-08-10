# Arquitectura de la Aplicación Móvil — Stunex

## Propósito del documento

El presente documento define la arquitectura interna de la aplicación móvil de Stunex: sus capas internas, la estructura de carpetas de `lib/`, la configuración del cliente HTTP (`dio`), la gestión de estado con `Provider`, el almacenamiento seguro del token JWT, la navegación entre pantallas y las pantallas contempladas para los módulos ya aprobados.

Este documento complementa a `docs/03-Diseno/01_Arquitectura.md` (arquitectura general) y a `docs/03-Diseno/03_Arquitectura_Backend.md` (arquitectura del backend), sin contradecirlos. En particular, resuelve la definición que `01_Arquitectura.md` (sección 3.1) delegó explícitamente a este documento: la acción concreta de navegación ante una respuesta 401 (ver sección 5).

Este documento no introduce nuevos requisitos: cada decisión aquí descrita referencia el RF, RNF, HU o CU que la respalda.

---

# 1. Alcance de este documento

Al igual que los documentos de diseño ya mergeados, este documento cubre en detalle únicamente los flujos y pantallas de **Autenticación** y **Perfil**, derivados exclusivamente de los casos de uso CU-001 a CU-007 (`docs/02-Requisitos/04_Casos_de_Uso.md`).

Los módulos restantes del alcance del MVP (Materias, Tareas, Calendario, Horario, Recursos, Documentos, Dashboard, Herramientas) **no tienen diseño de aplicación móvil todavía**, por no contar con RF, HU ni CU propios. Este documento no infiere ni anticipa pantallas, flujos ni decisiones técnicas para esos módulos (ver sección 12).

---

# 2. Capas internas de la aplicación

La aplicación Flutter se organiza en cuatro capas, cada una con una responsabilidad única:

## 2.1 Presentación (pantallas y widgets)

Contiene las pantallas (`screens`) y los widgets reutilizables de la interfaz, siguiendo Material Design 3 (RNF-014). Esta capa **no contiene lógica de negocio ni llamadas directas a la API**: consume el estado expuesto por los Providers (sección 6) y dispara acciones sobre ellos (por ejemplo, `authProvider.login(...)`).

## 2.2 Estado (Providers)

Contiene las clases `ChangeNotifier` (`AuthProvider`, `ProfileProvider`) que exponen el estado de sesión y de perfil a la capa de presentación, y orquestan las llamadas a la capa de servicios. No contiene widgets ni lógica de presentación.

## 2.3 Servicios (comunicación con la API)

Contiene las clases responsables de la comunicación HTTP con el backend a través de `dio` (sección 4): una por dominio (`AuthService`, `ProfileService`), reflejando la misma separación por dominio ya adoptada en el backend (`03_Arquitectura_Backend.md`, sección 2). Esta capa traduce las respuestas HTTP en modelos (sección 2.4) o en errores, pero no mantiene estado ni actualiza la interfaz directamente.

## 2.4 Modelos (representación de datos)

Contiene las clases que representan los datos manejados por la aplicación (por ejemplo, `User`), incluyendo su serialización/deserialización JSON. No contienen lógica de negocio ni llamadas a servicios.

---

# 3. Estructura de carpetas (`lib/`)

```text
lib/
│
├── main.dart
│
├── auth/
│   ├── screens/
│   ├── providers/
│   ├── services/
│   └── models/
│
├── profile/
│   ├── screens/
│   ├── providers/
│   ├── services/
│   └── models/
│
└── core/
    ├── network/
    │   └── dio_client.dart
    ├── storage/
    │   └── secure_storage.dart
    └── config.dart
```

**Notas sobre la estructura:**

- La organización por dominio (`auth/`, `profile/`) dentro de `lib/` es coherente con el enfoque adoptado en el backend (`03_Arquitectura_Backend.md`, sección 2), manteniendo el mismo principio de modularidad ya definido en `01_Arquitectura.md` (sección 4.1) también del lado móvil.
- `core/` agrupa exclusivamente infraestructura compartida por todos los dominios: el cliente `dio` configurado (sección 4), el acceso a `flutter_secure_storage` (sección 7) y la configuración de variables de entorno (`baseUrl`, sección 4.1). No contiene lógica de negocio de ningún dominio.
- El nombre y la ubicación de la carpeta de la aplicación móvil dentro del repositorio (junto con el backend) aún no están definidos; eso corresponde a `08_Estructura_Proyecto.md`. Este documento se enfoca únicamente en la organización interna de la aplicación.

---

# 4. Cliente HTTP: configuración de `dio`

## 4.1 Instancia central y `baseUrl`

La aplicación mantiene una única instancia central de `dio`, configurada en `core/network/dio_client.dart` y reutilizada por todos los servicios de dominio (`AuthService`, `ProfileService`), evitando instancias duplicadas con configuraciones inconsistentes.

La URL base de la API (`baseUrl`) se define mediante variable de entorno de compilación, no hardcodeada en el código fuente, siguiendo el mismo principio de gestión de variables sensibles/configurables ya establecido para el backend (RNF-002).

## 4.2 Interceptor de request: inyección del JWT

Un interceptor de request, registrado en la instancia central de `dio`, lee el token almacenado en `flutter_secure_storage` (sección 7) antes de cada solicitud y, si existe, lo adjunta automáticamente en el header `Authorization` de las solicitudes a endpoints protegidos. Esto evita que cada pantalla o servicio deba manejar manualmente la inyección del token (RF-010, RF-011).

## 4.3 Interceptor de response: manejo centralizado de 401

Un interceptor de response, registrado en la misma instancia central, intercepta cualquier respuesta con código 401 antes de que el error llegue a la pantalla que originó la solicitud. Esto centraliza el manejo del caso "token inválido o expirado" en un único lugar, en vez de duplicar esa lógica en cada pantalla (tal como ya se estableció en `01_Arquitectura.md`, sección 3.1, y se lista como decisión en su sección 6.3).

---

# 5. Comportamiento concreto ante una respuesta 401

`01_Arquitectura.md` (sección 3.1) delegó explícitamente a este documento la definición de la acción de navegación concreta ante un 401. Se define de la siguiente forma:

1. El interceptor de response de `dio` (sección 4.3) detecta el código 401.
2. Se elimina el token almacenado en `flutter_secure_storage` (sección 7), ya que un token rechazado por el backend no debe conservarse localmente.
3. `AuthProvider` (sección 6.1) actualiza su estado a "no autenticado".
4. La aplicación redirige al estudiante a la pantalla de inicio de sesión (CU-002), independientemente de en qué pantalla se encontraba al momento del error.

Este comportamiento aplica a cualquier endpoint protegido, consistente con RF-010 y con el caso de uso transversal CU-005 (validación de acceso a recursos protegidos).

---

# 6. Gestión de estado con `Provider`

Cada Provider expone, como mínimo, tres estados posibles para las operaciones que realiza: **cargando**, **éxito** y **error**, permitiendo que la capa de presentación reaccione de forma consistente (por ejemplo, mostrar un indicador de carga o un mensaje de error).

## 6.1 `AuthProvider`

**Responsabilidad:** gestionar el estado de la sesión del estudiante.

**Expone:**
- Estado de sesión actual (autenticado / no autenticado / verificando).
- `register(...)`: invoca `AuthService` para el registro (CU-001, RF-001 a RF-005).
- `login(...)`: invoca `AuthService` para iniciar sesión, y en caso de éxito almacena el token (CU-002, RF-006 a RF-008, RF-011, RF-017; ver sección 7).
- `logout()`: elimina el token almacenado y limpia el estado de sesión (CU-003, RF-009, RN-008; ver sección 7).
- `requestPasswordReset(...)` y `resetPassword(...)`: invocan `AuthService` para el flujo de recuperación (CU-004, RF-012 a RF-014).
- Verificación de sesión existente al iniciar la aplicación (sección 8).

## 6.2 `ProfileProvider`

**Responsabilidad:** gestionar el estado del perfil del estudiante autenticado.

**Expone:**
- `fetchProfile()`: invoca `ProfileService` para consultar el perfil (CU-006, RF-015).
- `updateName(...)`: invoca `ProfileService` para editar el nombre (CU-007, RF-016).
- Estado del perfil cargado (nombre, correo) para su consumo en la pantalla de perfil.

---

# 7. Almacenamiento seguro del token

El almacenamiento del token JWT se realiza mediante `flutter_secure_storage` (Keystore en Android, Keychain en iOS), tal como se definió en `01_Arquitectura.md` (sección 6.5), evitando `SharedPreferences` sin cifrar (RNF-002, RNF-012).

- **Guardado:** el token se almacena inmediatamente después de un inicio de sesión exitoso, una vez recibido del backend (RF-007).
- **Eliminación:** el token se elimina del almacenamiento en dos casos: al cerrar sesión de forma explícita (RF-009, RN-008, CU-003), y al recibir una respuesta 401 (sección 5).
- El backend no mantiene ninguna lista de tokens revocados (RN-009); por lo tanto, la eliminación local del token es, en el MVP, el único mecanismo que efectivamente termina el acceso desde ese dispositivo.

---

# 8. Navegación

## 8.1 Verificación de sesión al iniciar la aplicación

Al arrancar, la aplicación consulta `flutter_secure_storage` a través de `AuthProvider` para determinar si existe un token almacenado, antes de decidir qué pantalla mostrar. Este documento no valida la vigencia del token localmente (el JWT no se decodifica ni se interpreta en el cliente); la validación real de vigencia y firma ocurre en el backend (RF-010, RN-013) ante la primera solicitud a un endpoint protegido, momento en el cual un token expirado se maneja según el flujo de la sección 5.

- Si existe un token almacenado, la aplicación navega directamente al área autenticada (por ejemplo, la pantalla de Perfil).
- Si no existe token almacenado, la aplicación navega al flujo de autenticación, comenzando por la pantalla de inicio de sesión.

## 8.2 Flujo entre pantallas de autenticación

```text
Inicio de sesión (CU-002)
   │
   ├──> Registro (CU-001) ──> [registro exitoso] ──> Inicio de sesión
   │
   └──> Solicitud de recuperación (CU-004) ──> Restablecimiento con token (CU-004)
                                                        │
                                                        └──> [restablecimiento exitoso] ──> Inicio de sesión
```

## 8.3 Flujo hacia el área autenticada

Un inicio de sesión exitoso (CU-002) navega al área autenticada de la aplicación, donde se encuentra la pantalla de Perfil (CU-006, CU-007). Desde esa área, la acción de cerrar sesión (CU-003) devuelve al estudiante a la pantalla de inicio de sesión (sección 8.2), y una respuesta 401 en cualquier punto del área autenticada aplica el comportamiento ya descrito en la sección 5.

---

# 9. Pantallas contempladas

Las siguientes pantallas se derivan exclusivamente de los casos de uso CU-001 a CU-007. No se contempla ninguna pantalla adicional:

| Pantalla | Caso de uso | RF relacionados |
|---|---|---|
| Registro | CU-001 | RF-001 a RF-005 |
| Inicio de sesión | CU-002 | RF-006 a RF-008, RF-011, RF-017 |
| Solicitud de recuperación de contraseña | CU-004 (pasos 1–2) | RF-012 |
| Restablecimiento de contraseña | CU-004 (pasos 4–9) | RF-013, RF-014 |
| Perfil (consulta y edición de nombre) | CU-006, CU-007 | RF-015, RF-016 |

El cierre de sesión (CU-003) no corresponde a una pantalla propia: es una acción disponible desde el área autenticada (por ejemplo, desde la pantalla de Perfil) que dispara el flujo descrito en la sección 8.3. La validación de acceso a recursos protegidos (CU-005) es transversal y no tiene representación visual propia: se manifiesta en la aplicación únicamente a través del comportamiento ante 401 (sección 5).

---

# 10. Validaciones del lado del cliente

La aplicación aplica validaciones básicas en los formularios de registro, inicio de sesión, recuperación y restablecimiento, coherentes con las reglas ya definidas del lado del servidor:

- **Formato de correo electrónico** (RF-003): se valida el formato antes de enviar la solicitud.
- **Longitud de contraseña** (RF-004, RNF-006): se valida que la contraseña tenga entre 8 y 128 caracteres antes de enviarla, tanto en registro como en restablecimiento.

**Importante:** estas validaciones del lado del cliente existen únicamente para mejorar la experiencia de usuario (retroalimentación inmediata, sin esperar un viaje de red). **No reemplazan ni sustituyen las validaciones del servidor.** El backend valida de forma independiente estas mismas reglas en cada solicitud (RF-002 a RF-005, RN-001 a RN-004), y es la única fuente de verdad: ninguna validación del cliente puede considerarse suficiente por sí sola para garantizar la integridad de los datos.

---

# 11. Trazabilidad de este documento

| Decisión de diseño | RF relacionados | RNF relacionados | RN relacionados | HU/CU relacionados |
|---|---|---|---|---|
| Estructura `lib/` por dominio (`auth/`, `profile/`, `core/`) | — | — | — | — |
| Instancia central de `dio` con `baseUrl` por variable de entorno | — | RNF-002 | — | — |
| Interceptor de request: inyección automática del JWT | RF-010, RF-011 | — | — | HU-006 |
| Interceptor de response: manejo centralizado de 401 | RF-010 | — | RN-013 | CU-005 |
| Redirección a inicio de sesión y eliminación del token ante 401 | RF-010 | — | RN-013 | CU-002, CU-005 |
| `AuthProvider` (registro, login, logout, recuperación) | RF-001 a RF-014, RF-017 | — | RN-008, RN-014 | HU-001 a HU-006, CU-001 a CU-005 |
| `ProfileProvider` (consulta y edición de nombre) | RF-015, RF-016 | — | RN-018, RN-019 | HU-007, HU-008, CU-006, CU-007 |
| Almacenamiento del token con `flutter_secure_storage` | RF-007, RF-009 | RNF-002, RNF-012 | RN-008, RN-009 | CU-002, CU-003 |
| Verificación de sesión existente al iniciar la app | RF-011 | — | — | CU-002 |
| Validación de formato de correo en cliente | RF-003 | — | RN-002 | CU-001 |
| Validación de longitud de contraseña en cliente | RF-004 | RNF-006 | RN-003 | CU-001, CU-004 |
| Interfaz Material Design 3 | — | RNF-014 | — | — |
| Compatibilidad mínima Android API 26 | — | RNF-024 | — | — |

---

# 12. Módulos pendientes de diseño móvil

Los siguientes módulos del alcance del MVP no cuentan con diseño de aplicación móvil en este documento, por no tener aún RF, HU ni CU aprobados: Materias, Tareas, Calendario, Horario, Recursos, Documentos, Dashboard y Herramientas (Calculadora de notas, Temporizador Pomodoro).

Ninguna pantalla, flujo de navegación ni Provider de esos módulos se documenta ni se infiere aquí. Su diseño se realizará en actualizaciones futuras de `docs/03-Diseno/`, una vez completen su fase de requisitos siguiendo la misma metodología incremental aplicada a Autenticación y Perfil. La estructura por dominio descrita en la sección 3 permite incorporar cada nuevo módulo como una carpeta independiente dentro de `lib/`, sin modificar `auth/`, `profile/` ni `core/`.
