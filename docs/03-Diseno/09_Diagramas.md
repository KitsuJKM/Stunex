# Diagramas del Sistema — Stunex

## Propósito del documento

El presente documento consolida visualmente, mediante diagramas Mermaid, las decisiones ya tomadas y aprobadas en los documentos de diseño anteriores. **Este documento no toma decisiones nuevas**: cada diagrama es una representación gráfica de contenido ya documentado, y bajo cada uno se referencia el documento y la sección exacta que lo respalda.

Si algún diagrama de este documento no coincidiera con lo ya documentado en un archivo anterior de `docs/03-Diseno/`, el error está en el diagrama, no en el documento previo. Ante cualquier discrepancia, prevalece siempre el documento textual ya aprobado.

---

# 1. Alcance de este documento

Este documento incluye exactamente **cuatro diagramas**:

1. Arquitectura general del sistema.
2. Entidad-relación de la base de datos.
3. Secuencia de autenticación (login y acceso a endpoint protegido).
4. Secuencia de recuperación de contraseña.

Al igual que los documentos anteriores, estos diagramas cubren únicamente lo ya diseñado para **Autenticación** y **Perfil**. Ningún diagrama incluye elementos, tablas, endpoints ni flujos de los módulos restantes del alcance del MVP (Materias, Tareas, Calendario, Horario, Recursos, Documentos, Dashboard, Herramientas), por no contar aún con RF, RNF ni RN aprobados (ver sección 8).

**No se incluye un diagrama de casos de uso UML.** Esa información ya está documentada en `docs/02-Requisitos/04_Casos_de_Uso.md` (CU-001 a CU-007); representarla nuevamente en un diagrama UML crearía dos fuentes de verdad para el mismo contenido, con el riesgo de que ambas versiones diverjan con el tiempo. Los diagramas de secuencia de este documento (secciones 5 y 6) ilustran esos mismos casos de uso desde una perspectiva técnica de interacción entre componentes, sin duplicar su descripción funcional.

---

# 2. Formato de los diagramas: Mermaid

Todos los diagramas de este documento se expresan en **Mermaid**, embebido directamente en bloques de código Markdown. Razones:

- **Renderizado nativo en GitHub:** GitHub interpreta los bloques ` ```mermaid ` y los muestra como diagramas reales en la interfaz web del repositorio, no como bloques de texto plano.
- **Editable sin herramientas externas:** cualquier persona con acceso al repositorio puede modificar un diagrama editando texto, sin depender de un editor gráfico propietario ni de archivos binarios.
- **Versionado como texto:** al ser texto plano, los diagramas se versionan en Git de la misma forma que el resto de la documentación, permitiendo ver diffs legibles entre revisiones.

---

# 3. Diagrama 1 — Arquitectura general

```mermaid
flowchart LR
    A["Aplicación Flutter<br/>(cliente móvil)"] -->|"HTTPS/TLS (RNF-001)"| B["Backend FastAPI<br/>(API REST)"]
    B -->|"SQLAlchemy"| C[("MySQL<br/>(datos relacionales)")]
    B -.->|"Sin uso en Autenticación/Perfil (previsto para módulos futuros)"| D[("Bucket Storage<br/>(archivos)")]
```

**Descripción:** la aplicación Flutter se comunica con el backend FastAPI exclusivamente sobre HTTPS/TLS. El backend persiste los datos de usuarios y perfiles en MySQL mediante SQLAlchemy. La conexión hacia Bucket Storage se representa con línea punteada porque, en el alcance actual (Autenticación y Perfil), **no existe interacción real** con ese componente: ningún RF vigente la requiere; está previsto únicamente para los futuros módulos de Documentos y Recursos.

**Referencia:** `01_Arquitectura.md`, sección 2 (flujo general del sistema) y secciones 3.3–3.4 (responsabilidad de MySQL y Bucket Storage).

---

# 4. Diagrama 2 — Entidad-relación

```mermaid
erDiagram
    users ||--o{ password_reset_tokens : "tiene"

    users {
        int id PK
        varchar(100) name
        varchar(255) email UK
        varchar(60) password_hash
        timestamp created_at
        timestamp updated_at
    }

    password_reset_tokens {
        int id PK
        int user_id FK
        char(64) token_hash UK
        timestamp expires_at
        timestamp used_at "NULL = no usado"
        timestamp created_at
    }
```

**Descripción:** un usuario (`users`) puede tener cero o varios tokens de restablecimiento (`password_reset_tokens`) a lo largo del tiempo (relación 1:N). No existe una tabla "perfil" separada: `users` respalda tanto al dominio `auth/` como al dominio `profile/`.

**Referencia:** `04_Modelo_Base_de_Datos.md`, secciones 2 (tabla `users`), 3 (tabla `password_reset_tokens`) y 4 (diagrama entidad-relación en texto que este diagrama traduce a Mermaid).

---

# 5. Diagrama 3 — Secuencia de autenticación

## 5.1 Login exitoso

```mermaid
sequenceDiagram
    actor U as Estudiante
    participant App as App Flutter
    participant API as Backend FastAPI
    participant DB as MySQL
    participant SS as flutter_secure_storage

    U->>App: Ingresa correo y contraseña
    App->>API: POST /api/v1/auth/login
    API->>API: Verifica rate limiting (RF-017, RNF-008, RN-010)
    alt Limite de intentos superado
        API-->>App: 429 Too Many Requests
    else Limite no superado
        API->>DB: Consulta password_hash por email
        DB-->>API: password_hash
        API->>API: Verifica bcrypt (RF-005, RN-012)
        alt Credenciales válidas
            API->>API: Genera JWT (HS256, expira en 7 días)
            API-->>App: 200 OK (access_token)
            App->>SS: Almacena access_token
        else Credenciales inválidas
            API-->>App: 401 Unauthorized (mensaje genérico)
        end
    end
```

## 5.2 Acceso a endpoint protegido

```mermaid
sequenceDiagram
    actor U as Estudiante
    participant App as App Flutter
    participant SS as flutter_secure_storage
    participant DIO as Interceptor dio
    participant API as Backend FastAPI

    U->>App: Abre pantalla de Perfil
    App->>DIO: GET /api/v1/profile/me
    DIO->>SS: Lee token almacenado
    SS-->>DIO: access_token
    DIO->>API: GET /api/v1/profile/me (Authorization: Bearer access_token)
    API->>API: Depends(get_current_user) valida el JWT (RF-010, RN-013)
    alt Token válido
        API-->>DIO: 200 OK (id, name, email)
        DIO-->>App: Datos del perfil
    else Token ausente, inválido o expirado
        API-->>DIO: 401 Unauthorized
        DIO->>SS: Elimina token almacenado
        DIO-->>App: Redirige a Inicio de sesión
    end
```

**Descripción:** el primer diagrama (5.1) cubre, antes de procesar las credenciales, la verificación del límite de intentos de inicio de sesión (rate limiting: máximo 5 intentos fallidos en 15 minutos por cuenta/IP, respondiendo 429 si se supera); si el límite no se supera, continúa con la generación del token: verificación de credenciales contra el hash bcrypt almacenado, generación del JWT firmado con HS256 con expiración de 7 días, y su almacenamiento en `flutter_secure_storage`. El segundo diagrama (5.2) cubre el acceso a un endpoint protegido: el interceptor de `dio` inyecta el token almacenado, `Depends(get_current_user)` lo valida en el backend, y ante un 401 el interceptor elimina el token y redirige al inicio de sesión.

**Referencia:** `03_Arquitectura_Backend.md`, sección 7.1 (generación del JWT) y 7.2 (validación mediante `Depends()`); `05_Diseno_API.md`, secciones 4.2 (`POST /auth/login`) y 4.5 (`GET /profile/me`); `02_Arquitectura_Movil.md`, sección 5 (comportamiento concreto ante una respuesta 401) y sección 7 (almacenamiento seguro del token).

---

# 6. Diagrama 4 — Secuencia de recuperación de contraseña

```mermaid
sequenceDiagram
    actor U as Estudiante
    participant App as App Flutter
    participant API as Backend FastAPI
    participant DB as MySQL
    participant R as Resend

    U->>App: Solicita recuperación (ingresa correo)
    App->>API: POST /api/v1/auth/forgot-password
    API->>API: Verifica rate limiting por correo (RNF-010, RN-017)
    alt Limite de solicitudes superado
        API-->>App: 429 Too Many Requests
    else Limite no superado
        API->>DB: Busca usuario por email
        alt Correo corresponde a una cuenta
            API->>API: Genera token y calcula su hash SHA-256
            API->>DB: INSERT password_reset_tokens (expires_at +15 min, used_at NULL)
            API->>R: Envía correo con el token
        else Correo no existe
            Note over API: No se genera ningún token
        end
        API-->>App: 200 OK (mensaje genérico, idéntico en ambos casos)
    end

    U->>App: Ingresa token y nueva contraseña
    App->>API: POST /api/v1/auth/reset-password
    API->>DB: Busca password_reset_tokens por token_hash
    API->>API: Valida expires_at y used_at = NULL (RN-015, RN-016)
    alt Token válido y vigente
        API->>API: Hashea new_password con bcrypt
        API->>DB: UPDATE users.password_hash
        API->>DB: UPDATE password_reset_tokens SET used_at = NOW()
        API-->>App: 200 OK
    else Token inválido, expirado o ya usado
        API-->>App: 401 Unauthorized
    end
```

**Descripción:** antes de procesar la solicitud de recuperación, se verifica el límite de solicitudes por correo (rate limiting: máximo 1 solicitud cada 5 minutos, respondiendo 429 si se supera). Si el límite no se supera, `forgot-password` responde siempre con el mismo mensaje genérico, exista o no una cuenta asociada al correo; internamente, solo si la cuenta existe se genera un token (almacenado como hash SHA-256, con vigencia de 15 minutos) y se envía por correo mediante Resend. El restablecimiento (`reset-password`) valida que el token exista, esté vigente y no haya sido usado antes de actualizar la contraseña, y marca el token como usado mediante `used_at` para impedir su reutilización.

**Referencia:** `03_Arquitectura_Backend.md`, sección 7.5 (recuperación de contraseña); `04_Modelo_Base_de_Datos.md`, secciones 3.1 (almacenamiento hasheado del token) y 3.2 (uso único mediante `used_at`); `05_Diseno_API.md`, secciones 4.3 (`POST /auth/forgot-password`) y 4.4 (`POST /auth/reset-password`); `01_Arquitectura.md`, sección 6.6 (Resend como servicio de correo).

---

# 7. Trazabilidad de este documento

| Diagrama | RF | RNF | RN | HU/CU |
|---|---|---|---|---|
| 1 — Arquitectura general | — | RNF-001 | — | — |
| 2 — Entidad-relación | RF-001, RF-002, RF-005, RF-013 | RNF-007, RNF-018 | RN-001, RN-011, RN-012, RN-015, RN-016 | CU-001, CU-004 |
| 3.1 — Login exitoso | RF-005 a RF-008, RF-011, RF-017 | RNF-004, RNF-005, RNF-008 | RN-010, RN-012, RN-014 | HU-002, CU-002 |
| 3.2 — Acceso a endpoint protegido | RF-010, RF-011 | — | RN-013 | HU-006, CU-005, CU-006 |
| 4 — Recuperación de contraseña | RF-012, RF-013, RF-014 | RNF-009, RNF-010 | RN-014, RN-015, RN-016, RN-017 | HU-004, HU-005, CU-004 |

---

# 8. Diagramas pendientes para módulos futuros

Los siguientes módulos del alcance del MVP no cuentan con diagramas en este documento, por no tener aún RF, RNF ni RN aprobados: Materias, Tareas, Calendario, Horario, Recursos, Documentos, Dashboard y Herramientas (Calculadora de notas, Temporizador Pomodoro).

Ningún diagrama de arquitectura, entidad-relación ni secuencia de esos módulos se documenta ni se infiere aquí. Se agregarán a este documento en actualizaciones futuras, una vez cada módulo complete su fase de requisitos y su diseño correspondiente, siguiendo la misma metodología incremental aplicada a Autenticación y Perfil. El Diagrama 1 (arquitectura general) se actualizaría en ese momento para mostrar la interacción real con Bucket Storage, actualmente representada como prevista pero sin uso (sección 3).
