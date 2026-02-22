# Arquitectura del Sistema — AI for Account Intelligence

## 1. Visión General

La plataforma **AI for Account Intelligence** es un sistema de inteligencia comercial que combina IA generativa open-source, análisis de señales públicas y un sistema RAG para ayudar a vendedores a identificar, priorizar y abordar oportunidades de negocio.

---

## 2. Diagrama de Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                     USUARIO (Vendedor)                        │
│                    Dashboard Web (React)                      │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTPS / REST
┌──────────────────────────▼──────────────────────────────────┐
│                   BACKEND (FastAPI)                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │  Auth / JWT  │  │  API Router  │  │  Dependencias    │  │
│  └──────────────┘  └──────┬───────┘  └──────────────────┘  │
│                            │                                  │
│  ┌─────────────────────────▼──────────────────────────────┐ │
│  │                    SERVICES LAYER                        │ │
│  │  ┌─────────────┐  ┌──────────┐  ┌──────────────────┐  │ │
│  │  │  AI Engine  │  │ RAG Svc  │  │  Web Search Svc  │  │ │
│  │  │ (Mistral7B) │  │ (FAISS)  │  │  (BeautifulSoup) │  │ │
│  │  └─────────────┘  └──────────┘  └──────────────────┘  │ │
│  └─────────────────────────────────────────────────────────┘ │
└──────────────────┬──────────────────────┬───────────────────┘
                   │ SQLAlchemy / pyodbc   │ FAISS / Embeddings
┌──────────────────▼───────────┐  ┌───────▼────────────────────┐
│   Microsoft SQL Server 2022  │  │   FAISS Vector Index       │
│   (Azure SQL en producción)  │  │   (SentenceTransformers)   │
└──────────────────────────────┘  └────────────────────────────┘
```

---

## 3. Capas del Sistema

### 3.1 Presentación (Frontend)
- **Framework**: React / Next.js
- **Función**: Dashboard para vendedores no técnicos
- **Componentes clave**: Top5 Widget, Account Card, Signal Timeline, Speech Generator View

### 3.2 API Gateway (FastAPI)
- **Responsabilidad**: Routing, validación de requests, autenticación JWT
- **Patrones**: Routers por dominio, Dependency Injection, Pydantic schemas

### 3.3 Capa de Servicios
| Servicio | Tecnología | Responsabilidad |
|----------|-----------|-----------------|
| `ai_engine.py` | Mistral 7B / LLaMA 3 | Generación de texto, NER, scoring |
| `rag_service.py` | FAISS + SentenceTransformers | Búsqueda semántica en docs internos |
| `web_search.py` | BeautifulSoup + httpx | Extracción de señales públicas |

### 3.4 Persistencia
- **SQL Server**: Datos estructurados (cuentas, scores, usuarios)
- **FAISS Index**: Embeddings para búsqueda semántica

---

## 4. Flujo de Análisis de una Cuenta

```
1. Vendedor ingresa URL de empresa
2. web_search.py extrae contenido público
3. ai_engine.py detecta señales y entidades (NER)
4. rag_service.py busca contexto en docs HPE relevantes
5. ai_engine.py genera PropensityScore híbrido
6. ai_engine.py genera Recommendations y Speech
7. Datos persisten en SQL Server
8. Respuesta entregada al Dashboard
```

---

## 5. Seguridad

- Autenticación JWT (HS256, expiración configurable)
- Contraseñas hasheadas con bcrypt
- Variables sensibles en `.env` (nunca en código)
- CORS configurado por entorno
- Usuario SQL dedicado (sin permisos `sa`)

---

## 6. Escalabilidad

- **Horizontal**: Docker containers en Azure Container Apps con autoescalado
- **Base de datos**: Azure SQL con réplicas de lectura
- **Caché**: Posibilidad de agregar Redis para respuestas frecuentes
- **Modelos IA**: Carga bajo demanda | opción de GPU en Azure (NC instances)
