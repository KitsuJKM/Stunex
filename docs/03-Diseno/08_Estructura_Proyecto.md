# Estructura del Proyecto — Stunex

## Propósito del documento

El presente documento define la estructura de directorios del repositorio de Stunex: la organización monorepo, la ubicación de `backend/` y `mobile/`, sus archivos de configuración, la gestión de variables de entorno y las convenciones de nomenclatura.

Este documento **resuelve explícitamente** la definición que quedó delegada en dos documentos ya mergeados:
- `03_Arquitectura_Backend.md` (sección 2): "El nombre y la ubicación de la carpeta raíz del backend dentro del repositorio (junto con la aplicación móvil) aún no están definidos; eso corresponde a `08_Estructura_Proyecto.md`."
- `02_Arquitectura_Movil.md` (sección 3): "El nombre y la ubicación de la carpeta de la aplicación móvil dentro del repositorio (junto con el backend) aún no están definidos; eso corresponde a `08_Estructura_Proyecto.md`."

Este documento no introduce nuevos requisitos ni redefine contenido ya documentado: para la responsabilidad de cada archivo dentro de un dominio del backend, ver `03_Arquitectura_Backend.md` (secciones 3 y 4); para las capas internas de la aplicación móvil, ver `02_Arquitectura_Movil.md` (secciones 2 y 4). Aquí solo se ubican esas estructuras ya definidas dentro del repositorio.

---

# 1. Alcance de este documento

Al igual que los documentos de diseño ya mergeados, este documento ubica en el repositorio únicamente las carpetas correspondientes a los dominios ya aprobados: `auth/`, `profile/` y `core/` en `backend/`, y su equivalente en `mobile/lib/`. No se crea ninguna carpeta para Materias, Tareas, Calendario, Horario, Recursos, Documentos, Dashboard ni Herramientas, por no contar aún con RF, RNF ni RN propios (ver sección 10).

---

# 2. Monorepo: justificación

Stunex se organiza como un **monorepo**: un único repositorio Git que contiene `backend/`, `mobile/` y `docs/` como carpetas hermanas en la raíz, en lugar de repositorios separados por componente.

**Justificación:**

- **Equipo de dos personas:** con un equipo tan pequeño (`docs/00-General/02_Informacion_del_Proyecto.md`: Juan Martínez en backend/base de datos/API, Ana en Flutter/UI), coordinar múltiples repositorios (versiones, permisos, sincronización de ramas) añade sobrecarga operativa sin un beneficio real a esta escala.
- **Cambios de contrato de API afectan a ambos lados a la vez:** cuando cambia un endpoint documentado en `05_Diseno_API.md`, ese cambio típicamente requiere modificar `backend/` (implementación) y `mobile/` (consumo) de forma coordinada. Un monorepo permite que ambos cambios viajen en el mismo commit o la misma rama, sin depender de versionar y sincronizar paquetes entre repositorios independientes.
- **Documentación centralizada:** `docs/` ya existe en la raíz del repositorio desde el inicio del proyecto (fase de Análisis y Requisitos) y referencia decisiones que abarcan tanto al backend como a la aplicación móvil (por ejemplo, `01_Arquitectura.md`). Mantener `docs/`, `backend/` y `mobile/` en el mismo repositorio evita que la documentación quede desincronizada del código que describe.
- **Consistente con simplicidad sobre sobre-ingeniería:** esta decisión sigue el mismo principio ya establecido en `01_Arquitectura.md` (sección 4.3): para un MVP académico de este tamaño, una arquitectura de múltiples repositorios sería complejidad sin beneficio concreto todavía.

---

# 3. Árbol de directorios de la raíz

```text
Stunex/
│
├── .gitignore
├── README.md
│
├── docs/
│   ├── 00-General/
│   ├── 01-Analisis/
│   ├── 02-Requisitos/
│   └── 03-Diseno/
│
├── backend/
│   └── (ver sección 4)
│
└── mobile/
    └── (ver sección 5)
```

`docs/` permanece en la ubicación que ya tenía antes de este documento, sin cambios. `backend/` y `mobile/` son las dos carpetas nuevas que este documento define como hermanas entre sí y respecto a `docs/`, en la raíz del repositorio.

---

# 4. Estructura interna de `backend/`

La organización por dominio (`auth/`, `profile/`, `core/`) ya definida en `03_Arquitectura_Backend.md` (sección 2) se ubica ahora bajo `backend/`, sin modificaciones a su contenido interno:

```text
backend/
│
├── requirements.txt
├── .env.example
├── alembic.ini
├── main.py
│
├── migrations/
│   └── versions/
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

**Archivos de configuración de `backend/`:**
- `requirements.txt`: dependencias de Python del proyecto.
- `.env.example`: documenta las variables de entorno requeridas, sin valores reales (ver sección 6).
- `alembic.ini`: configuración de Alembic para el versionado del esquema de base de datos, ya mencionado en `04_Modelo_Base_de_Datos.md` (sección 7).
- `migrations/versions/`: carpeta donde Alembic almacena los scripts de migración generados.
- `main.py`: punto de entrada de la aplicación FastAPI.

Para la responsabilidad de cada archivo dentro de `auth/`, `profile/` y `core/` (qué contiene y qué NO contiene cada uno), ver `03_Arquitectura_Backend.md` (secciones 3 y 4). Este documento no redefine ese contenido.

---

# 5. Estructura interna de `mobile/`

La estructura de `lib/` ya definida en `02_Arquitectura_Movil.md` (sección 3) se ubica ahora bajo `mobile/`, sin modificaciones a su contenido interno:

```text
mobile/
│
├── pubspec.yaml
├── android/
├── ios/
├── test/
│
└── lib/
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

**Archivos y carpetas propios de un proyecto Flutter:**
- `pubspec.yaml`: dependencias y metadatos del proyecto Flutter.
- `android/`: proyecto nativo Android generado por el tooling de Flutter, necesario para la compatibilidad mínima ya definida (RNF-024, Android API 26).
- `ios/`: proyecto nativo iOS generado por el tooling de Flutter. Su mantenimiento activo queda supeditado a lo ya definido en RNF-024: iOS permanece fuera del alcance del MVP salvo que el tiempo del proyecto lo permita.
- `test/`: pruebas automatizadas de la aplicación móvil.

Para las capas internas (presentación, estado, servicios, modelos) y la responsabilidad de cada carpeta dentro de `lib/`, ver `02_Arquitectura_Movil.md` (secciones 2 y 3). Este documento no redefine ese contenido.

---

# 6. Gestión de variables de entorno

Consistente con la configuración por carpeta (no global) y con RNF-002, cada componente documenta sus propias variables de entorno mediante un archivo de ejemplo versionado, sin valores reales:

| Variable | Ubicación | Propósito |
|---|---|---|
| Secreto de firma JWT | `backend/.env.example` | Firma y verificación de tokens JWT (HS256), ya definida en `03_Arquitectura_Backend.md` (sección 4.3) |
| Credenciales de MySQL | `backend/.env.example` | Conexión a la base de datos definida en `04_Modelo_Base_de_Datos.md` |
| API key de Resend | `backend/.env.example` | Servicio de envío de correo para recuperación de contraseña, ya decidido en `01_Arquitectura.md` (sección 6.6) |
| `baseUrl` de la API | Configuración de compilación de `mobile/` | Consumida por el cliente `dio`, ya definida como variable de entorno de compilación en `02_Arquitectura_Movil.md` (sección 4.1); este documento no redefine el mecanismo concreto de esa variable, solo señala que tampoco se hardcodea ni se versiona con un valor real |

**`.env.example` se versiona en el repositorio**, documentando qué variables existen (sus nombres) sin contener ningún valor real ni secreto. El archivo `.env` real de cada componente **nunca se versiona**: queda excluido mediante el `.gitignore` de la raíz del repositorio, que a la fecha de este documento ya incluye una entrada `.env`, conforme a RNF-002 ("las credenciales de base de datos, el secreto de firma JWT y las claves del Bucket Storage se gestionan mediante variables de entorno, nunca embebidas en el código fuente ni en el repositorio").

## 6.1 Contenido mínimo esperado del `.gitignore` de la raíz

Este documento no crea el `.gitignore` (su creación corresponde a la fase de implementación); documenta el contenido mínimo que debe cubrir, dado que es compartido por `backend/` y `mobile/` en la estructura monorepo (sección 2):

```gitignore
# Variables de entorno (RNF-002)
.env

# Python (backend/)
__pycache__/
*.pyc
venv/
.venv/

# Flutter/Dart (mobile/)
build/
.dart_tool/
.packages
```

---

# 7. Convenciones de nomenclatura

- **Carpetas y archivos de código:** en inglés (`auth/`, `profile/`, `router.py`, `dio_client.dart`), siguiendo la convención ya aplicada en `03_Arquitectura_Backend.md` y `02_Arquitectura_Movil.md`.
- **Documentación:** en español, como el resto de `docs/`.
- **Sin tildes ni eñes en nombres de archivo**, tanto en código como en documentación (por ejemplo, este mismo directorio es `docs/03-Diseno/`, no `docs/03-Diseño/`, y el documento de diseño de API es `05_Diseno_API.md`, no `05_Diseño_API.md`). Esto evita fricción en comandos de terminal, rutas de importación y URLs, que pueden comportarse de forma inconsistente entre sistemas operativos y herramientas ante caracteres no ASCII.

---

# 8. Estrategia de ramas

La estrategia de ramas (`main`, `develop`, `feature/*`, integración vía Pull Request hacia `develop`) ya está vigente y definida en las instrucciones operativas del proyecto; este documento no la redefine.

Su relación con esta estructura monorepo: al ser un único repositorio, una misma rama `feature/*` puede abarcar cambios en `backend/`, `mobile/` y `docs/` simultáneamente cuando el cambio lo requiere (por ejemplo, una modificación de contrato de API que afecte a ambos lados, ver sección 2), sin necesidad de coordinar ramas equivalentes en repositorios distintos ni de versionar dependencias cruzadas entre ellos.

---

# 9. Trazabilidad de este documento

| Decisión de diseño | RF | RNF | RN | HU/CU |
|---|---|---|---|---|
| Monorepo (`backend/`, `mobile/`, `docs/` en un único repositorio) | — | — | — | — |
| Configuración por carpeta (`requirements.txt`, `.env.example`, `alembic.ini`, `pubspec.yaml`) | — | — | — | — |
| Ubicación de `backend/` (resuelve delegación de `03_Arquitectura_Backend.md`, sección 2) | — | — | — | — |
| Ubicación de `mobile/` (resuelve delegación de `02_Arquitectura_Movil.md`, sección 3) | — | — | — | — |
| `.env.example` versionado, `.env` real excluido vía `.gitignore` | — | RNF-002 | — | — |
| Convenciones de nomenclatura sin tildes/eñes | — | — | — | — |
| Estrategia de ramas ya vigente, aplicada a la estructura monorepo | — | — | — | — |

La mayoría de las decisiones de este documento son puramente estructurales/organizativas y no derivan de un RF, RNF o RN específico; se marcan con guion en lugar de forzar una relación inexistente. La única excepción es la gestión de `.env.example`/`.env`, que sí respalda directamente RNF-002.

---

# 10. Estructura de módulos futuros

Los módulos restantes del alcance del MVP (Materias, Tareas, Calendario, Horario, Recursos, Documentos, Dashboard, Herramientas) no tienen carpetas definidas todavía en `backend/` ni en `mobile/lib/`, por no contar aún con RF, RNF ni RN aprobados.

Cuando cada módulo complete su fase de requisitos, su incorporación seguirá el mismo patrón ya establecido: una carpeta de dominio propia bajo `backend/` (siguiendo el ejemplo conceptual de `materias/` ya ilustrado en `03_Arquitectura_Backend.md`, sección 6) y una carpeta equivalente bajo `mobile/lib/` (siguiendo la misma organización por dominio ya aplicada a `auth/` y `profile/` en `02_Arquitectura_Movil.md`, sección 3), sin requerir cambios a la estructura de `auth/`, `profile/` ni `core/` aquí definida.
