# BDA Analytics Pipeline

A production-grade Big Data Processing & API layer with a React dashboard for large-scale AI Prompt and Response analysis.

## Architecture

```
JSONL DATASET -> INGESTION & PREPROCESSING -> PYTHON/PANDAS + LOCAL MAPREDUCE-STYLE AGGREGATION
-> PYSPARK DATAFRAME + SPARK SQL (LOCAL MODE) -> RECONCILIATION -> FASTAPI -> REACT DASHBOARD
                                      \-> OPTIONAL MONGODB ANALYTICS CACHE
```

## Features

### Backend
- **Dynamic Engine Detection**: Automatically probes installed binaries and reports honest status
- **Analytics paths demonstrated**: Python/pandas, local MapReduce-style processing, PySpark DataFrames, and Spark SQL in Spark local mode
- **Reconciliation Engine**: Cross-engine comparison with mathematical parity calculations
- **Optional MongoDB cache**: Best-effort analytics persistence; the local dataset and analytics work without MongoDB
- **Deterministic Prompt Analyzer**: Rule-based parsing without LLM dependencies
- **Zero Hardcoding**: All metrics computed dynamically from source data

### Frontend
- **Executive Overview**: Key dataset metrics with KPI cards and visualizations
- **Category & Model Intelligence**: Multi-dimensional breakdown with interactive charts
- **BDA Ecosystem Monitor**: Live status matrix of processing engines
- **Data Reconciliation View**: Side-by-side verification table with delta highlighting
- **Prompt Inspector**: Interactive interface for deterministic prompt analysis
- **Graceful Degradation**: Explicit fallback states for unavailable data or engines

## Prerequisites

- Python 3.9+
- Node.js 18+
- Java runtime (required for PySpark local mode)
- PySpark (installed from `requirements.txt`)
- (Optional) MongoDB (analytics cache; not required to run the demo)
- (Optional extensions, not used by the active analytics path): Hadoop/Hive/Pig/Sqoop

## Installation

### Backend Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install backend dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with your settings
```

4. (Optional) Start MongoDB if you want cached analytics to persist:
```bash
# On Windows
mongod --dbpath C:\data\db

# On Linux/Mac
mongod
```

### Frontend Setup

1. Install frontend dependencies:
```bash
cd frontend
npm install
```

2. Configure environment (frontend/.env):
```bash
VITE_API_BASE_URL=/api
```

## Running the Application

### Quick Start (Using Python Scripts)

```bash
# Terminal 1: Start Backend
python start_backend.py

# Terminal 2: Start Frontend
python start_frontend.py
```

### Manual Start

**Backend:**
```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Frontend:**
```bash
cd frontend
npm run dev
```

The dashboard will be available at `http://localhost:3000`

## API Endpoints

- `GET /api/v1/health-ecosystem` - System health and engine status
- `GET /api/v1/analytics/overview` - Executive overview statistics
- `GET /api/v1/analytics/categories` - Category-level analytics
- `GET /api/v1/analytics/models` - Model-level analytics
- `GET /api/v1/analytics/reconciliation` - Cross-engine reconciliation reports
- `POST /api/v1/prompt/inspect` - Deterministic prompt analysis

## Dashboard Views

### Executive Overview
- Total records, tokens, and averages
- Unique categories and models
- Success rate and quality score metrics
- Visual distribution charts

### Category Intelligence
- Token consumption by category
- Record count breakdown
- Success rate and quality score comparisons
- Detailed category analytics table

### Model Intelligence
- Token consumption by model
- Record count breakdown
- Success rate and quality score comparisons
- Detailed model analytics table

### BDA Ecosystem Monitor
- System health status
- MongoDB connection status
- Dataset loading status
- Active processing status (Python, local MapReduce-style code, PySpark, and Spark SQL)
- Optional MongoDB cache status and ecosystem readiness (Hadoop, Hive, Pig, Sqoop)

### Data Reconciliation
- Cross-engine comparison results
- Match rate statistics
- Mismatch highlighting
- Absolute and percentage delta calculations

### Prompt Inspector
- Word and character count
- Code block detection
- Constraint extraction
- Specificity scoring
- Rule-based improvement hints

## Dataset Format

The system expects JSONL format with the following schema. The included generated demo dataset has 100,000 distinct synthetic records and uses the same seven model labels as before. Model-level outcome and token differences are deliberately varied to make group-by visualizations easier to discuss; they are not real model benchmarks.
```json
{
  "prompt": "string",
  "response": "string",
  "model": "string",
  "category": "string",
  "timestamp": "ISO 8601 string",
  "token_count": "integer (optional)",
  "success": "boolean (optional)"
}
```

A 100,000-record synthetic dataset is generated on first run if missing. The backend reads JSONL directly; Sqoop is not used. Generate or replace the dataset with:

```bash
python generate_dataset.py
```

## Engine Status Enums

- `AVAILABLE` - Engine installed and functional
- `NOT_INSTALLED` - Binary/package not found
- `NOT_CONFIGURED` - Installed but not configured
- `CONFIGURED_BUT_OFFLINE` - Configured but not responding
- `EXECUTION_FAILED` - Execution attempt failed
- `VALIDATED_LOCALLY` - Local implementation available

## Design System

### Color Palette
- Background: Slate 50 (#F8FAFC)
- Primary: Slate 900 (#0F172A)
- Secondary: Slate 600 (#475569)
- Border: Slate 200 (#E2E8F0)
- Accent: Blue 600 (#2563EB)

### Components
- Lucide React for icons
- Recharts for data visualizations
- Tailwind CSS for styling

## Zero-Hardcoding Guarantee

All numerical responses are computed dynamically from source files or runtime operations. No static demo numbers or fabricated JSON in production code. If data is unavailable, the UI displays explicit fallback states: "Data Unavailable", "Not Configured", "Execution Failed", or "Engine Offline".
