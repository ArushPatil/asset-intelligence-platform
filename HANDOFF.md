# Hand-off: bug fixes and new frontend

## What changed

**Frontend (all of `ui/`, `app.py`, `.streamlit/config.toml`)**
- Dark theme. The colour tokens live in `ui/styles.py`, and the Streamlit theme lives in `.streamlit/config.toml`.
- The landing page shows live KPI cards (latest value against the 24 h average), a 24 h chart with anomaly markers and a question box with presets.
- An answer shows its sources, the backend that wrote it and the latency, plus evidence tabs: Telemetry, Asset, Manuals and Trace.
- The sidebar shows the real state of each data source: Neo4j, telemetry, the manual index and the LLM.
- No fake or placeholder data. When a source is down, the UI says so.
- `ui/data.py` caches the orchestrator once per server process. The manual index no longer rebuilds on every rerun.
- `ui/execution_view.py` was removed; its content moved into the Trace tab.

**Backend fixes**
- `documents/embedding_service.py` and `documents/vector_store.py` were missing the `typing.Any` import.
- `llm/llm_client.py`:
  - The local fallback answer no longer invents facts.
  - The diagnosis is built from the retrieved context.
  - The client records which backend answered (`last_backend`).
- `llm/models.py` and `llm/orchestrator.py`: the response now carries `llm_backend`.
- `requirements.txt`: added `scikit-learn`, `google-genai`, `streamlit` and `plotly`.
- `.env.example`: removed the fake key.

## Resuming on your machine

```bash
pip install -r requirements.txt   # full set, includes sentence-transformers (pulls torch)
streamlit run app.py              # http://localhost:8501
```

- Start Neo4j at `NEO4J_URI` from `.env`. Without it, the Asset tab and topology questions report that the graph is offline.
- `GEMINI_API_KEY` and `OPENAI_API_KEY` are optional. Without a key, answers come from the local template engine.

## Not tested here

The fixes were tested on a light install without torch, Neo4j or API keys. These paths were not run:
- **sentence-transformers embeddings:** the manuals were searched with the TF-IDF fallback, which returns weak passages.
- **A live Neo4j graph.**
- **Gemini and OpenAI answers:** the Gemini model names in `llm/llm_client.py` were not checked against Google's current list.
