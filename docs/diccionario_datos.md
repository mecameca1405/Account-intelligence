# Diccionario de Datos — AI for Account Intelligence

## Tabla: `users`

| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| `id` | INTEGER | PK, AUTO | Identificador único |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL | Email corporativo del usuario |
| `full_name` | VARCHAR(255) | NOT NULL | Nombre completo del vendedor |
| `hashed_password` | VARCHAR(255) | NOT NULL | Password hasheado (bcrypt) |
| `role` | VARCHAR(50) | DEFAULT 'seller' | Rol: `admin`, `seller`, `manager` |
| `is_active` | BOOLEAN | DEFAULT TRUE | Estado de la cuenta |
| `created_at` | DATETIME | DEFAULT NOW() | Fecha de creación |

---

## Tabla: `accounts`

| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| `id` | INTEGER | PK, AUTO | Identificador único |
| `company_name` | VARCHAR(255) | NOT NULL | Nombre de la empresa |
| `company_url` | VARCHAR(500) | NOT NULL | URL pública de la empresa |
| `industry` | VARCHAR(100) | NULLABLE | Sector / industria |
| `company_size` | VARCHAR(50) | NULLABLE | Tamaño: `startup`, `midmarket`, `enterprise` |
| `country` | VARCHAR(100) | NULLABLE | País de operación |
| `technologies_detected` | TEXT | JSON | Lista de tecnologías detectadas (NER) |
| `last_analyzed_at` | DATETIME | NULLABLE | Última vez que fue analizada |
| `created_at` | DATETIME | DEFAULT NOW() | Fecha de creación del registro |
| `created_by` | INTEGER | FK → users.id | Usuario que creó la cuenta |

---

## Tabla: `signals`

| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| `id` | INTEGER | PK, AUTO | Identificador único |
| `account_id` | INTEGER | FK → accounts.id | Cuenta relacionada |
| `signal_type` | VARCHAR(100) | NOT NULL | Tipo: `hiring`, `expansion`, `funding`, `tech_change`, `pain_point` |
| `signal_source` | VARCHAR(255) | NULLABLE | URL o fuente de la señal |
| `signal_text` | TEXT | NOT NULL | Texto de la señal detectada |
| `confidence_score` | FLOAT | 0.0-1.0 | Confianza del modelo en la señal |
| `detected_at` | DATETIME | DEFAULT NOW() | Fecha de detección |

---

## Tabla: `propensity_scores`

| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| `id` | INTEGER | PK, AUTO | Identificador único |
| `account_id` | INTEGER | FK → accounts.id | Cuenta evaluada |
| `score` | FLOAT | 0.0-100.0 | Puntuación de propensión a comprar |
| `score_breakdown` | TEXT | JSON | Desglose por dimensiones (señales, fit, timing) |
| `model_version` | VARCHAR(50) | NOT NULL | Versión del modelo usado |
| `calculated_at` | DATETIME | DEFAULT NOW() | Fecha del cálculo |

---

## Tabla: `recommendations`

| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| `id` | INTEGER | PK, AUTO | Identificador único |
| `account_id` | INTEGER | FK → accounts.id | Cuenta relacionada |
| `product_name` | VARCHAR(255) | NOT NULL | Nombre del producto HPE recomendado |
| `product_family` | VARCHAR(100) | NULLABLE | Familia/portafolio |
| `relevance_score` | FLOAT | 0.0-1.0 | Relevancia de la recomendación |
| `rationale` | TEXT | NOT NULL | Justificación generada por IA |
| `created_at` | DATETIME | DEFAULT NOW() | Fecha de creación |

---

## Tabla: `speeches`

| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| `id` | INTEGER | PK, AUTO | Identificador único |
| `account_id` | INTEGER | FK → accounts.id | Cuenta objetivo |
| `speech_text` | TEXT | NOT NULL | Texto del speech comercial generado |
| `tone` | VARCHAR(50) | DEFAULT 'consultivo' | Tono: `consultivo`, `urgente`, `relacional` |
| `word_count` | INTEGER | NULLABLE | Longitud del speech |
| `model_used` | VARCHAR(100) | NULLABLE | Modelo LLM que generó el speech |
| `created_at` | DATETIME | DEFAULT NOW() | Fecha de generación |

---

## Tabla: `top5_history`

| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| `id` | INTEGER | PK, AUTO | Identificador único |
| `date` | DATE | NOT NULL | Fecha del top 5 |
| `rank` | INTEGER | 1-5 | Posición en el ranking |
| `account_id` | INTEGER | FK → accounts.id | Cuenta |
| `score_snapshot` | FLOAT | NOT NULL | Puntuación al momento del ranking |
| `created_at` | DATETIME | DEFAULT NOW() | Timestamp de generación |

---

## Tabla: `feedbacks`

| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| `id` | INTEGER | PK, AUTO | Identificador único |
| `user_id` | INTEGER | FK → users.id | Vendedor que da feedback |
| `account_id` | INTEGER | FK → accounts.id | Cuenta evaluada |
| `feedback_type` | VARCHAR(50) | NOT NULL | `speech`, `recommendation`, `score` |
| `rating` | INTEGER | 1-5 | Calificación del 1 al 5 |
| `comment` | TEXT | NULLABLE | Comentario libre |
| `created_at` | DATETIME | DEFAULT NOW() | Fecha del feedback |
