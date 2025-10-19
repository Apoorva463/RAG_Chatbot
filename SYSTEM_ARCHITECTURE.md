# 🏗️ RAG Chatbot System Architecture

## System Overview

The RAG Chatbot System is built with a modular, layered architecture that separates concerns and enables scalability. Here's how the components interact:

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE LAYER                     │
├─────────────────────────────────────────────────────────────────┤
│  🌐 Streamlit Web UI  │  🔗 FastAPI REST API  │  💻 CLI Demo     │
│  • Interactive Chat   │  • Favorites Mgmt  │  • System Test    │
│  • Analytics Dashboard│  • User Management │  • Development     │
│  • Real-time Metrics │  • Data Export     │  • Debugging      │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      APPLICATION LAYER                          │
├─────────────────────────────────────────────────────────────────┤
│  🤖 Main Chatbot     │  🧠 Intent Parser   │  📝 Response Gen  │
│  • Query Processing  │  • Pattern Matching │  • Context Assembly│
│  • Session Management│  • Intent Detection │  • Citation System│
│  • Error Handling    │  • Query Analysis   │  • Formatting     │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      CORE SERVICES LAYER                        │
├─────────────────────────────────────────────────────────────────┤
│  🔍 RAG System       │  📊 Evaluation     │  👁️ Observability  │
│  • Vector Embeddings│  • Quality Metrics │  • Trace Logging   │
│  • Semantic Search   │  • Hallucination   │  • Performance     │
│  • Document Retrieval│  • Factuality Check│  • Analytics       │
│                     │                     │                    │
│  🎯 Recommendations │  💾 Favorites API   │  📈 Analytics      │
│  • Mood-based       │  • CRUD Operations │  • Reporting       │
│  • User Preferences │  • Data Validation │  • Visualization   │
│  • Hybrid Approach  │  • User Management │  • Export          │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATA & STORAGE LAYER                       │
├─────────────────────────────────────────────────────────────────┤
│  🗃️ Vector Database  │  🗄️ SQLite DB      │  📄 CSV Dataset   │
│  • Embeddings Cache  │  • Favorites Store │  • Song Metadata  │
│  • Similarity Index  │  • User Data       │  • Static Data    │
│  • Fast Retrieval    │  • Session State   │  • Configuration  │
│                     │                     │                    │
│  ☁️ Langfuse Cloud   │  📁 Local Storage  │  🔄 Data Pipeline │
│  • Trace Storage    │  • Log Files       │  • ETL Process    │
│  • Analytics        │  • Cache Files     │  • Data Sync      │
│  • Monitoring       │  • Temp Files       │  • Validation     │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow Architecture

### 1. Query Processing Flow

```
User Query
    │
    ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Intent        │───▶│   RAG           │───▶│   Response      │
│   Recognition   │    │   Retrieval     │    │   Generation    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
    │                         │                         │
    ▼                         ▼                         ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Query         │    │   Vector        │    │   Context       │
│   Analysis      │    │   Similarity    │    │   Assembly      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                    ┌─────────────────┐
                    │   Document      │
                    │   Retrieval     │
                    └─────────────────┘
```

### 2. Evaluation Pipeline

```
Response
    │
    ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Tone          │    │   Factuality    │    │   Hallucination │
│   Analysis      │    │   Scoring       │    │   Detection     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
    │                         │                         │
    ▼                         ▼                         ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   RAG           │    │   Citation      │    │   Quality       │
│   Metrics       │    │   Check         │    │   Assessment    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                    ┌─────────────────┐
                    │   Final         │
                    │   Evaluation    │
                    └─────────────────┘
```

### 3. Observability Flow

```
System Activity
    │
    ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Trace        │    │   Span          │    │   Metadata      │
│   Creation     │    │   Logging       │    │   Collection    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
    │                         │                         │
    ▼                         ▼                         ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Langfuse      │    │   Local         │    │   Export        │
│   Cloud         │    │   Storage       │    │   Analytics     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Component Interaction Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                           USER INTERFACE                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │ Streamlit   │  │ FastAPI    │  │ CLI Demo    │              │
│  │ Web UI      │  │ REST API   │  │ Script      │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
           │                │                │
           ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        MAIN CHATBOT                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │ Intent      │  │ Query       │  │ Response    │              │
│  │ Parser      │  │ Processor   │  │ Generator   │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
           │                │                │
           ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        CORE SERVICES                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │ RAG        │  │ Evaluation  │  │ Observability│              │
│  │ System     │  │ System      │  │ System      │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │ Recommendation│ │ Favorites  │  │ Analytics   │              │
│  │ System      │  │ API         │  │ Engine      │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
           │                │                │
           ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        DATA LAYER                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │ Vector      │  │ SQLite      │  │ CSV         │              │
│  │ Embeddings  │  │ Database    │  │ Dataset     │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │ Langfuse    │  │ Local       │  │ Data        │              │
│  │ Cloud       │  │ Storage     │  │ Pipeline    │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
```

## Technology Stack Details

### Frontend Technologies
```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND LAYER                           │
├─────────────────────────────────────────────────────────────────┤
│  🌐 Streamlit Framework                                         │
│  • Python-based web framework                                  │
│  • Real-time updates and interactivity                         │
│  • Built-in components for data visualization                  │
│                                                                 │
│  📊 Visualization Libraries                                     │
│  • Plotly: Interactive charts and graphs                       │
│  • Altair: Statistical visualizations                          │
│  • Custom CSS: Styling and layout                              │
└─────────────────────────────────────────────────────────────────┘
```

### Backend Technologies
```
┌─────────────────────────────────────────────────────────────────┐
│                        BACKEND LAYER                            │
├─────────────────────────────────────────────────────────────────┤
│  🚀 FastAPI Framework                                          │
│  • High-performance async web framework                        │
│  • Automatic API documentation (OpenAPI/Swagger)               │
│  • Type hints and validation with Pydantic                     │
│                                                                 │
│  🔧 Core Libraries                                             │
│  • Uvicorn: ASGI server for FastAPI                           │
│  • SQLite: Lightweight database                               │
│  • Pydantic: Data validation and serialization                │
└─────────────────────────────────────────────────────────────────┘
```

### Machine Learning Stack
```
┌─────────────────────────────────────────────────────────────────┐
│                    MACHINE LEARNING LAYER                      │
├─────────────────────────────────────────────────────────────────┤
│  🧠 NLP & Embeddings                                          │
│  • Sentence Transformers: Vector embeddings                   │
│  • scikit-learn: Similarity calculations                      │
│  • NumPy: Numerical computations                              │
│                                                                 │
│  🔗 LangChain Ecosystem                                       │
│  • LangChain: LLM framework and utilities                     │
│  • LangChain Community: Community integrations               │
│  • LangChain Core: Core functionality                         │
└─────────────────────────────────────────────────────────────────┘
```

### Observability Stack
```
┌─────────────────────────────────────────────────────────────────┐
│                    OBSERVABILITY LAYER                         │
├─────────────────────────────────────────────────────────────────┤
│  👁️ Monitoring & Tracing                                      │
│  • Langfuse: LLM observability platform                       │
│  • OpenTelemetry: Distributed tracing                         │
│  • Custom logging: Local trace storage                        │
│                                                                 │
│  📊 Analytics & Reporting                                     │
│  • Real-time metrics collection                               │
│  • Performance monitoring                                     │
│  • User behavior analytics                                     │
└─────────────────────────────────────────────────────────────────┘
```

## Database Schema

### SQLite Database Structure
```
┌─────────────────────────────────────────────────────────────────┐
│                        DATABASE SCHEMA                         │
├─────────────────────────────────────────────────────────────────┤
│  📋 Favorites Table                                           │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ favorites                                               │   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │ id (INTEGER PRIMARY KEY)                               │   │
│  │ user_id (TEXT NOT NULL)                                │   │
│  │ song_title (TEXT NOT NULL)                             │   │
│  │ song_author (TEXT NOT NULL)                            │   │
│  │ song_genre (TEXT NOT NULL)                             │   │
│  │ song_mood (TEXT NOT NULL)                              │   │
│  │ song_year (INTEGER NOT NULL)                           │   │
│  │ created_at (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)       │   │
│  │ UNIQUE(user_id, song_title, song_author)               │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### Vector Storage
```
┌─────────────────────────────────────────────────────────────────┐
│                        VECTOR STORAGE                          │
├─────────────────────────────────────────────────────────────────┤
│  🧮 Embeddings Matrix                                         │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Shape: (30, 384) - 30 songs, 384-dimensional vectors   │   │
│  │ Type: float32 numpy array                               │   │
│  │ Model: all-MiniLM-L6-v2                                 │   │
│  │ Storage: In-memory for fast retrieval                   │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## API Endpoints Architecture

### FastAPI REST API Structure
```
┌─────────────────────────────────────────────────────────────────┐
│                        API ENDPOINTS                          │
├─────────────────────────────────────────────────────────────────┤
│  📝 Favorites Management                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ POST   /favorites/{user_id}     - Add favorite         │   │
│  │ GET    /favorites/{user_id}     - Get favorites        │   │
│  │ DELETE /favorites/{user_id}     - Remove favorite      │   │
│  │ DELETE /favorites/{user_id}/clear - Clear favorites    │   │
│  │ GET    /favorites/{user_id}/count - Count favorites    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  📊 Analytics & Health                                         │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ GET    /favorites/analytics/all - All user analytics   │   │
│  │ GET    /health                  - Health check         │   │
│  │ GET    /docs                    - API documentation    │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Performance Architecture

### Caching Strategy
```
┌─────────────────────────────────────────────────────────────────┐
│                        CACHING LAYER                           │
├─────────────────────────────────────────────────────────────────┤
│  🚀 In-Memory Cache                                           │
│  • Vector embeddings (pre-computed)                           │
│  • Session state management                                   │
│  • Response caching for common queries                        │
│                                                                 │
│  💾 Persistent Cache                                          │
│  • SQLite database for favorites                              │
│  • Local file storage for traces                              │
│  • Configuration caching                                       │
└─────────────────────────────────────────────────────────────────┘
```

### Scalability Considerations
```
┌─────────────────────────────────────────────────────────────────┐
│                      SCALABILITY DESIGN                        │
├─────────────────────────────────────────────────────────────────┤
│  🔄 Horizontal Scaling                                        │
│  • Stateless API design                                       │
│  • Load balancer ready                                        │
│  • Database connection pooling                                 │
│                                                                 │
│  📈 Performance Optimization                                  │
│  • Efficient vector operations                                │
│  • Optimized database queries                                 │
│  • Minimal memory footprint                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Security Architecture

### Data Protection
```
┌─────────────────────────────────────────────────────────────────┐
│                        SECURITY LAYER                          │
├─────────────────────────────────────────────────────────────────┤
│  🔒 Data Security                                             │
│  • Input validation with Pydantic                             │
│  • SQL injection prevention                                   │
│  • XSS protection in web interface                            │
│                                                                 │
│  🛡️ Access Control                                           │
│  • User ID-based data isolation                               │
│  • API rate limiting                                           │
│  • Secure environment variable handling                        │
└─────────────────────────────────────────────────────────────────┘
```

## Deployment Architecture

### Local Development
```
┌─────────────────────────────────────────────────────────────────┐
│                    LOCAL DEVELOPMENT                          │
├─────────────────────────────────────────────────────────────────┤
│  💻 Development Environment                                   │
│  • Python virtual environment                                 │
│  • Local SQLite database                                      │
│  • Streamlit development server                               │
│  • FastAPI development server                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Production Deployment
```
┌─────────────────────────────────────────────────────────────────┐
│                    PRODUCTION DEPLOYMENT                       │
├─────────────────────────────────────────────────────────────────┤
│  🐳 Container Deployment                                      │
│  • Docker containerization                                    │
│  • Environment variable configuration                         │
│  • Health checks and monitoring                               │
│                                                                 │
│  ☁️ Cloud Deployment                                          │
│  • Langfuse cloud integration                                 │
│  • Scalable infrastructure                                    │
│  • Monitoring and alerting                                    │
└─────────────────────────────────────────────────────────────────┘
```

This architecture provides a robust, scalable, and maintainable foundation for the RAG chatbot system, with clear separation of concerns and modular design principles.
