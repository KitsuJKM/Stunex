# Modelo de Base de Datos — Stunex

## Propósito del documento

El presente documento define el modelo de datos de Stunex: las tablas de la base de datos MySQL, sus campos, tipos y restricciones, la relación entre ellas, y los datos que deliberadamente no se almacenan.

Este documento complementa a `docs/03-Diseno/03_Arquitectura_Backend.md`, que ya estableció que `profile/` no posee tabla propia y opera sobre el modelo `User` de `auth/` (sección 5). Aquí se detalla el esquema concreto de esa y las demás tablas ya aprobadas.

Este documento no introduce nuevos requisitos: cada campo y restricción aquí descrita referencia el RF, RNF o RN que la respalda, o se documenta explícitamente como una decisión técnica sin requisito específico asociado.

---

# 1. Alcance de este documento

Al igual que los documentos de diseño ya mergeados, este documento modela únicamente las tablas necesarias para **Autenticación** y **Perfil**: `users` y `password_reset_tokens`.

Los módulos restantes del alcance del MVP (Materias, Tareas, Calendario, Horario, Recursos, Documentos, Dashboard, Herramientas) **no tienen modelo de datos todavía**, por no contar con RF, RNF ni RN propios. Ninguna tabla, campo ni relación de esos módulos se infiere ni se anticipa en este documento (ver sección 9).

---

# 2. Tabla `users`

Como ya estableció `03_Arquitectura_Backend.md` (sección 5), **no existe una tabla "perfil" separada**: los endpoints de consulta y edición de perfil (RF-015, RF-016) operan sobre el mismo registro creado durante el registro (RF-001). `users` es, por lo tanto, la única tabla que respalda tanto al dominio `auth/` como al dominio `profile/`.

| Campo | Tipo | Restricciones | Respalda |
|---|---|---|---|
| `id` | `INT` | `AUTO_INCREMENT`, `PRIMARY KEY` | Decisión técnica (ver sección 2.1) |
| `name` | `VARCHAR(100)` | `NOT NULL` | RF-001 (registro), RF-016 (edición de nombre) |
| `email` | `VARCHAR(255)` | `NOT NULL`, `UNIQUE` | RF-001, RF-002 (unicidad), RNF-018, RN-001 |
| `password_hash` | `VARCHAR(60)` | `NOT NULL` | RF-005 (hash bcrypt), RNF-007, RN-011, RN-012 |
| `created_at` | `TIMESTAMP` | `NOT NULL`, `DEFAULT CURRENT_TIMESTAMP` | Auditoría (ver sección 2.2) |
| `updated_at` | `TIMESTAMP` | `NOT NULL`, `DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP` | Auditoría (ver sección 2.2) |

## 2.1 Clave primaria: `INT AUTO_INCREMENT`

Se utiliza `INT AUTO_INCREMENT` como clave primaria en lugar de UUID. Esta es una decisión técnica sin un RF/RNF específico que la exija: para un backend único (no distribuido, ver `01_Arquitectura.md`, sección 4.4, backend stateless pero de instancia única en el MVP), un entero autoincremental es más eficiente en MySQL (índices más pequeños, mejor rendimiento en joins) que un UUID, y no se requiere generación distribuida de identificadores.

## 2.2 Campos de auditoría: solo `created_at` y `updated_at`

La tabla incluye únicamente marcas de tiempo de creación y última modificación. No se implementa soft delete (no existe campo `deleted_at`), porque ningún RF aprobado contempla la eliminación de cuentas. Si en el futuro se aprobara un requisito de eliminación de cuenta, este documento se actualizaría en consecuencia.

## 2.3 Longitud de `password_hash`

`VARCHAR(60)` corresponde a la longitud exacta que produce un hash bcrypt (algoritmo, factor de costo, salt y hash concatenados), consistente con el factor de costo de 12 rounds ya definido en RNF-007 y documentado en `03_Arquitectura_Backend.md` (sección 7.3).

---

# 3. Tabla `password_reset_tokens`

Almacena los tokens de restablecimiento de contraseña (RF-013), en el dominio `auth/`, conforme a lo ya establecido en `03_Arquitectura_Backend.md` (sección 7.7).

| Campo | Tipo | Restricciones | Respalda |
|---|---|---|---|
| `id` | `INT` | `AUTO_INCREMENT`, `PRIMARY KEY` | Decisión técnica (ver sección 2.1) |
| `user_id` | `INT` | `NOT NULL`, `FOREIGN KEY → users(id)` | RF-013, RNF-018 (ver sección 5) |
| `token_hash` | `CHAR(64)` | `NOT NULL`, `UNIQUE` | RF-013 (ver sección 3.1) |
| `expires_at` | `TIMESTAMP` | `NOT NULL` | RF-013, RNF-009, RN-016 (15 minutos) |
| `used_at` | `TIMESTAMP` | `NULL` (NULL = no usado) | RN-015 (uso único, ver sección 3.2) |
| `created_at` | `TIMESTAMP` | `NOT NULL`, `DEFAULT CURRENT_TIMESTAMP` | Auditoría |

## 3.1 El token se almacena hasheado (SHA-256), no en texto plano

`token_hash` almacena el hash SHA-256 del token de restablecimiento (representado como `CHAR(64)`, la longitud de un digest SHA-256 en hexadecimal), nunca el token en texto plano.

**Justificación:** el token de restablecimiento es, funcionalmente, una credencial temporal equivalente a una contraseña de un solo uso (RF-013, RF-014): quien lo posee puede definir una nueva contraseña para la cuenta. Una filtración de la base de datos que expusiera el token en texto plano permitiría a un atacante usarlo directamente, sin necesidad de conocer ningún otro dato. Esto es consistente con el principio de seguridad desde el diseño ya establecido en `01_Arquitectura.md` (sección 4.2).

No se utiliza bcrypt para este campo, a diferencia de `password_hash`: el token ya es generado aleatoriamente con alta entropía (a diferencia de una contraseña elegida por un humano), por lo que no es susceptible a ataques de diccionario ni de fuerza bruta por adivinación, y un hash rápido como SHA-256 es suficiente para el propósito de que su valor no quede expuesto en texto plano ante una filtración de la base de datos.

## 3.2 Uso único mediante `used_at`

RN-015 exige que un token de restablecimiento solo pueda utilizarse una vez. Esto se implementa mediante el campo `used_at`: `NULL` indica que el token no ha sido utilizado; al usarse exitosamente, se registra la fecha/hora de uso, y cualquier intento posterior de reutilizarlo se rechaza porque `used_at` ya no es `NULL`.

No se elimina el registro tras su uso: se conserva como evidencia de auditoría del restablecimiento, consistente con la ausencia de soft delete/borrado físico ya establecida para `users` (sección 2.2).

---

# 4. Diagrama entidad-relación

```text
┌────────────────────────────────┐
│              users              │
├────────────────────────────────┤
│ PK  id               INT        │
│     name             VARCHAR(100)│
│ UQ  email             VARCHAR(255)│
│     password_hash     VARCHAR(60)│
│     created_at        TIMESTAMP │
│     updated_at        TIMESTAMP │
└────────────────┬─────────────────┘
                  │ 1
                  │
                  │ N
┌────────────────┴─────────────────┐
│      password_reset_tokens        │
├────────────────────────────────┤
│ PK  id               INT        │
│ FK  user_id           INT       │  ──> users.id
│ UQ  token_hash         CHAR(64)  │
│     expires_at         TIMESTAMP │
│     used_at            TIMESTAMP NULL │
│     created_at         TIMESTAMP │
└────────────────────────────────┘
```

Un usuario (`users`) puede tener cero o varios tokens de restablecimiento (`password_reset_tokens`) a lo largo del tiempo (relación 1:N), correspondientes a distintas solicitudes de recuperación (RF-012) realizadas en momentos diferentes.

---

# 5. Restricciones de integridad e índices

- **Unicidad de `email`:** índice `UNIQUE` sobre `users.email`, aplicado a nivel de esquema de base de datos y no solo en la capa de aplicación (RNF-018, RN-001). Esto garantiza la unicidad incluso ante condiciones de carrera que la validación de aplicación por sí sola no podría prevenir.
- **Clave foránea `password_reset_tokens.user_id → users.id`:** protege la relación entre ambas tablas (RNF-018). Su comportamiento ante eliminación es `ON DELETE CASCADE`: si un registro de `users` fuera eliminado, sus tokens de restablecimiento asociados se eliminarían junto con él, ya que no tiene sentido conservar tokens de recuperación de una cuenta que ya no existe. En el MVP actual esta cláusula no se ejecuta en la práctica, dado que ningún RF contempla eliminación de cuentas (sección 2.2), pero se define como comportamiento correcto del esquema.
- **Unicidad de `token_hash`:** índice `UNIQUE` sobre `password_reset_tokens.token_hash`, evitando colisiones y permitiendo una búsqueda directa y eficiente del token al validarlo (RF-014).
- **Índice sobre `user_id`:** además de servir como clave foránea, permite consultar eficientemente los tokens asociados a un usuario.

---

# 6. Datos que deliberadamente no se almacenan

- **Contraseñas en texto plano:** en ningún caso se almacena la contraseña original del usuario; únicamente su hash bcrypt en `password_hash` (RN-011, RN-012).
- **Tokens JWT:** el backend no persiste los tokens JWT emitidos en el login. Al ser el sistema stateless (RN-009), la validez de un token se determina exclusivamente verificando su firma y expiración en cada solicitud, sin necesidad de consultarlo contra la base de datos.
- **Datos personales adicionales:** más allá de `name` y `email`, no se almacena ningún otro dato personal del estudiante (teléfono, dirección, documento de identidad, foto de perfil, etc.), conforme a la minimización de datos personales exigida por RNF-011 y RN-020.

---

# 7. Migraciones

El versionado del esquema de base de datos se gestiona mediante **Alembic**, conforme al stack tecnológico ya definido en `docs/00-General/02_Informacion_del_Proyecto.md`. Cada cambio a las tablas descritas en este documento (creación, modificación de columnas, índices) se implementa como una migración de Alembic versionada, evitando modificaciones manuales directas al esquema de la base de datos.

---

# 8. Trazabilidad de este documento

| Decisión de diseño | RF | RNF | RN | HU/CU |
|---|---|---|---|---|
| Tabla `users` única (sin tabla "perfil" separada) | RF-015, RF-016 | — | RN-018, RN-019 | HU-007, HU-008, CU-006, CU-007 |
| Clave primaria `INT AUTO_INCREMENT` | — | — | — | — |
| Campo `email` con índice `UNIQUE` | RF-001, RF-002 | RNF-018 | RN-001 | HU-001, CU-001 |
| Campo `password_hash VARCHAR(60)` (bcrypt) | RF-005 | RNF-007 | RN-011, RN-012 | HU-001, HU-005, CU-001, CU-004 |
| Solo `created_at`/`updated_at`, sin soft delete | — | — | — | — |
| Tabla `password_reset_tokens` | RF-013 | — | — | HU-004, CU-004 |
| Clave foránea `user_id → users.id` (`ON DELETE CASCADE`) | RF-013 | RNF-018 | — | CU-004 |
| `token_hash` almacenado con SHA-256, no en texto plano | RF-013, RF-014 | — | — | CU-004 |
| `expires_at` (vigencia de 15 minutos) | RF-013 | RNF-009 | RN-016 | HU-004, CU-004 |
| `used_at` para uso único del token | RF-013, RF-014 | — | RN-015 | HU-004, HU-005, CU-004 |
| No persistencia de tokens JWT (backend stateless) | RF-009 | RNF-015 | RN-009 | CU-003, CU-005 |
| No almacenamiento de datos personales adicionales | — | RNF-011 | RN-020 | CU-001, CU-006 |
| Migraciones versionadas con Alembic | — | — | — | — |

---

# 9. Tablas pendientes de modelar

Los siguientes módulos del alcance del MVP no cuentan con modelo de datos en este documento, por no tener aún RF, RNF ni RN aprobados: Materias, Tareas, Calendario, Horario, Recursos, Documentos, Dashboard y Herramientas (Calculadora de notas, Temporizador Pomodoro).

Ninguna tabla, campo ni relación de esos módulos se documenta ni se infiere aquí. Su modelo de datos se definirá en actualizaciones futuras de `docs/03-Diseno/`, una vez completen su fase de requisitos siguiendo la misma metodología incremental aplicada a Autenticación y Perfil. Cuando esos módulos se incorporen, sus tablas se relacionarán con `users` mediante clave foránea (como ya se ilustró conceptualmente en `03_Arquitectura_Backend.md`, sección 6), sin requerir modificaciones a las tablas `users` ni `password_reset_tokens` aquí definidas.
