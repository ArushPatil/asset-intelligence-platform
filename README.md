# Asset Intelligence Platform

An enterprise AI assistant capable of answering natural language inquiries regarding building assets, infrastructure, operational status, telemetry health, and technical documentation by unifying three distinct knowledge tiers.

---

## Architecture Overview

The Asset Intelligence Platform combines three decoupled data sources into a single retrieval & reasoning pipeline:

```
                    User Natural Language Query
                                │
                                ▼
                        LLM Orchestrator
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
   Neo4j Graph           Telemetry Engine        PDF Document Store
(Relationships &      (Historical Time-Series   (Technical Manuals &
  Metadata Layer)           Metrics)                RAG Vector DB)
```

1. **Knowledge Graph (Neo4j)**: Stores semantic topology, facility hierarchies, equipment components, sensor metadata, warranties, contracts, and technicians.
2. **Telemetry Engine (CSV / Pandas)**: Manages high-frequency historical sensor readings (e.g., Supply/Return Air Temperature, Fan RPM, Energy Consumption).
3. **Technical Document Store (RAG)**: Stores unstructured PDF manuals, service records, and engineering schematics for semantic vector search.
4. **LLM Orchestrator**: Fuses context across all three data tiers into a factual, context-aware answer.

---

## Repository Structure

```
AssetIntelligence/
│
├── README.md                 # Project documentation & setup guide
├── requirements.txt          # Python package dependencies
├── .env.example              # Environment variables template
├── main.py                   # Main CLI entry point
├── config.py                 # Centralized configuration management
│
├── graph/                    # Neo4j Knowledge Graph interface module
│   ├── __init__.py
│   ├── neo4j_client.py       # Neo4j connection pool and query execution client
│   └── graph_queries.py      # Cypher query templates and retrieval methods
│
├── telemetry/                # CSV Telemetry processing engine
│   ├── __init__.py
│   ├── telemetry_reader.py   # Historical telemetry loading and filtering
│   └── telemetry_analysis.py # Statistical aggregation and anomaly detection
│
├── documents/                # Technical document loading & RAG module
│   ├── __init__.py
│   └── document_loader.py    # PDF document parsing and text chunking
│
├── llm/                      # Multi-source LLM Orchestration
│   ├── __init__.py
│   └── orchestrator.py       # Context fusion, prompt construction, and response synthesis
│
└── utils/                    # Shared utility modules
    ├── logger.py             # Centralized logging configuration
    └── exceptions.py         # Custom application exception hierarchy
```

---

## Getting Started

1. **Clone & Set Up Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure Environment Variables**:
   Copy `.env.example` to `.env` and populate your database credentials and API keys:
   ```bash
   cp .env.example .env
   ```

3. **Run the web app**:
   ```bash
   streamlit run app.py
   ```
   Opens at http://localhost:8501. Every source is optional: with Neo4j down the graph is
   marked offline, and with no `GEMINI_API_KEY` or `OPENAI_API_KEY` answers come from a
   local template built from the retrieved evidence.

4. **Run the command-line demo** (optional):
   ```bash
   python main.py
   ```
