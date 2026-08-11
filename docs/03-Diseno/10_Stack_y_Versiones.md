# Stack Tecnológico y Versiones — Stunex

## Propósito del documento

El presente documento fija las versiones concretas del stack tecnológico de Stunex, tanto en backend como en la aplicación móvil, y documenta un hallazgo detectado durante la investigación de versiones que requiere una decisión de diseño explícita: el conflicto entre el límite de 72 bytes de `bcrypt` y las contraseñas de hasta 128 caracteres ya definidas en RNF-006 y RN-003.

Este documento no modifica ningún requisito ya aprobado: RNF-006 y RN-003 siguen vigentes tal como están documentados en `docs/02-Requisitos/`. La solución aquí descrita (sección 4) resuelve el conflicto técnico sin tocar esos requisitos.

---

# 1. Alcance de este documento

Este documento fija las versiones de los componentes ya decididos en documentos anteriores (`01_Arquitectura.md`, sección 6; `03_Arquitectura_Backend.md`; `02_Arquitectura_Movil.md`), sin introducir componentes nuevos. No define versiones para dependencias de módulos futuros (Materias, Tareas, Calendario, Horario, Recursos, Documentos, Dashboard, Herramientas), por no contar aún con RF, RNF ni RN propios.

---

# 2. Versiones del backend

| Componente | Versión fijada | Respalda |
|---|---|---|
| Python | **3.13.x** | Runtime base |
| FastAPI | **0.141.1** | RNF-019 |
| SQLAlchemy | **2.0.51** | `04_Modelo_Base_de_Datos.md` |
| Alembic | **1.19.1** | `04_Modelo_Base_de_Datos.md`, sección 7 |
| Pydantic | **2.13.4** | RNF-019 (esquemas de `schemas.py`, `03_Arquitectura_Backend.md` sección 3.4) |
| PyJWT | **2.13.0** | RF-007, RNF-005 (HS256) |
| bcrypt | **5.0.0** | RF-005, RF-014, RNF-007, RN-011, RN-012 |
| resend | **2.35.0** | RF-012, `01_Arquitectura.md` sección 6.6 |
| PyMySQL | **1.2.0** | `04_Modelo_Base_de_Datos.md` |
| slowapi | **0.1.10** | RF-017, RNF-008, RN-010 (ver sección 6) |

**Justificación de las elecciones no obvias:**

- **Python 3.13.x, no 3.14:** aunque FastAPI, Alembic, Pydantic, PyJWT y bcrypt ya soportan 3.14, SQLAlchemy 2.0.51, slowapi y resend no lo declaran oficialmente. 3.13 es la versión donde los diez componentes del backend coinciden sin zona gris de compatibilidad, priorizando estabilidad sobre disponer de la versión más reciente.
- **PyJWT, no python-jose:** python-jose está prácticamente sin mantenimiento (último release con más de un año de antigüedad respecto a la fecha de esta investigación) y las propias guías de FastAPI migraron su recomendación de python-jose a PyJWT. Para HS256 (RNF-005), PyJWT es autosuficiente y no requiere la dependencia adicional `cryptography` que sí necesitan los algoritmos asimétricos.
- **PyMySQL, no mysqlclient ni mysql-connector-python:** `mysqlclient` exige un toolchain de compilación en C y headers de `libmysqlclient` en el sistema, lo que introduce fricción de instalación distinta entre los dos entornos de desarrollo del equipo (RF-006 a RF-016 no dependen de rendimiento de driver que justifique esa complejidad). `mysql-connector-python` es más pesado y su integración con SQLAlchemy está menos probada en la práctica. PyMySQL es Python puro, se instala sin dependencias nativas, y es suficiente para el volumen de un MVP académico.
- **SQLAlchemy 2.0.x, no 2.1:** la serie 2.1 solo tiene versiones beta a la fecha de esta investigación (última: `2.1.0b3`). Se fija 2.0.51 por ser la última versión estable de la serie 2.x, consistente con SQLAlchemy como ORM ya establecido en `01_Arquitectura.md` (sección 3.3) y con priorizar estabilidad sobre lo más reciente.

---

# 3. Versiones de la aplicación móvil

| Componente | Versión fijada | Respalda |
|---|---|---|
| Flutter (canal stable) | **3.44.9** | RNF-014 (Material Design 3) |
| Dart (incluido en Flutter 3.44.9) | **3.12.2** | — |
| dio | **5.11.0** | `01_Arquitectura.md` sección 6.3, `02_Arquitectura_Movil.md` sección 4 |
| provider | **6.1.5+1** | `01_Arquitectura.md` sección 6.4, `02_Arquitectura_Movil.md` sección 6 |
| flutter_secure_storage | **11.0.0** | `01_Arquitectura.md` sección 6.5, `02_Arquitectura_Movil.md` sección 7 |

**Verificación explícita — `flutter_secure_storage` 11.0.0 y RNF-024:** la versión 11.0.0 eleva su requisito mínimo a `minSdkVersion 24` (Android 7.0) en el proyecto Android generado por Flutter. RNF-024 ya fija **Android API 26** (Android 8.0) como versión mínima soportada por Stunex. Dado que 26 > 24, **no existe conflicto**: el requisito mínimo de `flutter_secure_storage` queda cubierto holgadamente por el mínimo ya exigido por el proyecto.

---

# 4. Conflicto `bcrypt` / 72 bytes y solución aprobada

## 4.1 El problema

`bcrypt` procesa únicamente los **primeros 72 bytes** de la contraseña que recibe; cualquier byte adicional se ignora en versiones anteriores, o produce un error en versiones recientes. Este límite es una característica del algoritmo Blowfish subyacente, no un defecto de la librería.

Dos factores agravan este límite en el contexto de Stunex:

1. **El límite es en bytes, no en caracteres.** En codificación UTF-8, los caracteres propios del español con tilde (á, é, í, ó, ú) y la letra ñ ocupan **2 bytes** cada uno, no 1. Dado que el público objetivo de Stunex es hispanohablante (`docs/00-General/02_Informacion_del_Proyecto.md`), es razonable esperar contraseñas con estos caracteres. Una contraseña de 75 caracteres con varias tildes puede superar los 72 bytes sin acercarse siquiera al límite de 128 caracteres permitido.
2. **`bcrypt` 5.0.0 cambió su comportamiento ante ese límite:** en versiones anteriores, una contraseña de más de 72 bytes se truncaba en silencio; desde la 5.0.0, `bcrypt.hashpw()` **lanza `ValueError`** ante una contraseña que supere los 72 bytes.

## 4.2 Por qué contradice RNF-006 y RN-003 si no se maneja

RNF-006 fija la longitud de contraseña permitida entre **8 y 128 caracteres**, y RN-003 exige que esa misma regla se aplique de forma consistente en registro y restablecimiento. Sin una solución, una contraseña válida según esos requisitos (por ejemplo, 80 caracteres con tildes, superando los 72 bytes en UTF-8) haría que `bcrypt.hashpw()` lance una excepción no controlada durante el registro (RF-005) o el restablecimiento (RF-014), en contradicción directa con requisitos ya aprobados.

## 4.3 Solución aprobada: pre-hash con SHA-256

Antes de pasar la contraseña a `bcrypt`, se calcula su hash **SHA-256** y es ese digest (de longitud fija, muy por debajo de 72 bytes) el que se entrega a `bcrypt.hashpw()`:

```text
contraseña (8-128 caracteres, UTF-8)
    → SHA-256 → digest de longitud fija (32 bytes)
    → bcrypt (12 rounds, RNF-007) → password_hash almacenado
```

**Esto no modifica RNF-006 ni RN-003:** el rango de 8 a 128 caracteres se sigue validando exactamente igual que antes, sobre la contraseña original ingresada por el usuario. El pre-hash es un paso técnico interno entre esa validación y el almacenamiento, no un cambio en las reglas de longitud ya aprobadas.

**Tampoco modifica el esquema de base de datos:** el resultado final que se almacena en `users.password_hash` sigue siendo un hash `bcrypt` estándar de longitud fija, consistente con `VARCHAR(60)` ya definido en `04_Modelo_Base_de_Datos.md` (sección 2.3).

Esta lógica se ubicaría en las funciones de hashing y verificación de `core/security.py`, ya descritas en `03_Arquitectura_Backend.md` (sección 4.3).

> **⚠️ Advertencia — consistencia obligatoria:** el pre-hash SHA-256 + `bcrypt` debe aplicarse de forma **idéntica** en los tres puntos donde se maneja una contraseña:
> - **Registro** (RF-005, `03_Arquitectura_Backend.md` sección 7.3): al crear el hash almacenado.
> - **Restablecimiento de contraseña** (RF-014, `03_Arquitectura_Backend.md` sección 7.5): al crear el nuevo hash almacenado.
> - **Verificación en login** (RF-006, `03_Arquitectura_Backend.md` sección 7.1): al comparar la contraseña ingresada contra el hash almacenado.
>
> Si alguno de estos tres puntos aplicara el pre-hash de forma distinta a los otros dos (por ejemplo, olvidándolo en la verificación de login), el usuario **quedaría sin poder iniciar sesión** con una contraseña que sí se registró o restableció correctamente, ya que el hash resultante no coincidiría.

## 4.4 El pre-hash no reemplaza ni debilita a `bcrypt`

`bcrypt` con factor de costo 12 (RNF-007, RN-012) sigue siendo el mecanismo real de resistencia a ataques de fuerza bruta y de diccionario: es el paso computacionalmente costoso e intencionalmente lento. SHA-256 no aporta esa propiedad (es, al contrario, deliberadamente rápido) y no sustituye a `bcrypt` en ningún sentido de seguridad; su único propósito aquí es **normalizar la longitud de entrada** para que quede dentro del límite que `bcrypt` acepta, sin alterar el rango de contraseñas válidas ya definido por RNF-006.

---

# 5. Por qué se descarta `passlib`

`passlib` fue considerada como capa de abstracción sobre `bcrypt`, pero se descarta por dos razones:

1. **Sin mantenimiento activo:** su última versión (1.7.4) fue publicada en 2020. No ha recibido actualizaciones desde entonces.
2. **Incompatibilidad con `bcrypt` 5.0.0:** `passlib` detecta la versión de `bcrypt` instalada leyendo un atributo interno (`bcrypt.__about__`) que `bcrypt` 5.0.0 eliminó. Esto provoca que `passlib` falle al calcular o verificar hashes, incluso con contraseñas muy por debajo de cualquier límite de longitud.

Se usa la librería `bcrypt` **directamente** (`bcrypt.hashpw()` / `bcrypt.checkpw()`), sin capa de abstracción intermedia, consistente con el principio de simplicidad sobre sobre-ingeniería ya establecido en `01_Arquitectura.md` (sección 4.3).

---

# 6. Rate limiting: dos mecanismos distintos

Como ya anticipó `04_Modelo_Base_de_Datos.md` (sección 5), el rate limiting de Stunex se implementa mediante **dos mecanismos distintos**, cada uno adecuado al caso que cubre. Este documento no redefine su diseño, ya detallado en `03_Arquitectura_Backend.md` (secciones 4.4 y 7.6) y en `04_Modelo_Base_de_Datos.md` (sección 5); aquí solo se fija la librería concreta para uno de los dos casos:

- **Login (RF-017, RNF-008, RN-010):** límite de 5 intentos fallidos por cuenta/IP cada 15 minutos, implementado mediante la dependencia reutilizable `core/rate_limit.py` (`03_Arquitectura_Backend.md`, sección 4.4), para la cual se fija la librería **slowapi 0.1.10**, sin el extra `slowapi[redis]` (que fijaría una versión obsoleta de `redis` y añadiría infraestructura no justificada para la instancia única del MVP).
- **Solicitud de recuperación de contraseña (RNF-010, RN-017):** límite de 1 solicitud por correo cada 5 minutos. Este caso **no** se resuelve con `slowapi`, ya que el límite es por el valor del campo `email` del cuerpo de la solicitud, no por IP/cuenta de sesión. Se resuelve mediante la consulta a la tabla `password_reset_tokens` ya diseñada en `04_Modelo_Base_de_Datos.md` (sección 5), filtrando por `user_id` y `created_at`, tal como ese documento ya especifica.

---

# 7. Trazabilidad de este documento

| Decisión | RF | RNF | RN | HU/CU |
|---|---|---|---|---|
| Versión de Python (3.13.x) | — | — | — | — |
| PyJWT como librería de JWT | RF-007 | RNF-005 | — | HU-002, CU-002 |
| PyMySQL como driver de MySQL | — | — | — | — |
| SQLAlchemy 2.0.x (no 2.1 beta) | — | — | — | — |
| `flutter_secure_storage` 11.0.0, minSdk 24 compatible con RNF-024 | — | RNF-024 | — | — |
| Pre-hash SHA-256 antes de `bcrypt` | RF-005, RF-006, RF-014 | RNF-006, RNF-007 | RN-003, RN-011, RN-012 | HU-001, HU-002, HU-005, CU-001, CU-002, CU-004 |
| Consistencia del pre-hash en registro/login/restablecimiento | RF-005, RF-006, RF-014 | — | RN-003 | CU-001, CU-002, CU-004 |
| Descarte de `passlib`, uso directo de `bcrypt` | RF-005 | RNF-007 | RN-011, RN-012 | CU-001, CU-004 |
| slowapi para rate limiting en login | RF-017 | RNF-008 | RN-010 | HU-002, CU-002 |
| Consulta en BD para rate limiting en recuperación | — | RNF-010 | RN-017 | CU-004 |

---

# 8. Nota final

Las versiones fijadas en este documento se materializarán en `backend/requirements.txt` y `mobile/pubspec.yaml` durante la fase de Implementación, en las ubicaciones ya definidas en `08_Estructura_Proyecto.md` (secciones 4 y 5). Este documento no crea esos archivos ni instala ninguna dependencia: su alcance es exclusivamente fijar y justificar las versiones antes de que comience esa fase.
