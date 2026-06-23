# CI/CD Agents Security Observability

A Python-based observability and guardrail agent project for detecting prompt injection attacks, retrieving knowledge-base answers, and streaming security telemetry to a live dashboard.

## Project Overview

This repository implements a security-focused AI agent pipeline using a state graph architecture. The core system evaluates user inputs for safety, retrieves answers from a knowledge base, and falls back to a safe default when no matching answer is found.

A companion Streamlit dashboard displays event metrics from a Google Sheets CSV stream, making it easier to monitor injection events, latency, and cost in real time.

## Key Features

- Prompt injection detection via a guardrail agent
- Knowledge base retrieval with a simple JSON-backed Q&A store
- Safe fallback handling when no knowledge answer matches
- Execution orchestration through a LangGraph state graph
- Observability and cost telemetry logged to Google Sheets
- Streamlit dashboard for live security metrics and alerts

## Repository Structure

- `main.py` - Entry point for the observability agent runtime. It invokes the LangGraph app, computes latency/cost, and syncs telemetry to Google Sheets.
- `agents.py` - Defines the three agent functions: `guardrail_agent`, `knowledge_agent`, and `fallback_agent`.
- `graph.py` - Builds and compiles the LangGraph state graph, sets routers, and connects nodes.
- `Dashboard.py` - Streamlit app that reads a published Google Sheet CSV and visualizes security metrics.
- `state.py` - Typed `AgentState` definition used by the graph nodes.
- `knowledge.json` - Static knowledge base used by the `knowledge_agent`.
- `test_agent.py` - Example pytest tests for agent robustness and prompt injection handling.
- `requirements.txt` - Python package dependencies.

## Requirements

- Python 3.10+ (recommended)
- `pip` package manager
- Optional: Google service account credentials for Google Sheets integration

## Installation

1. Clone the repository:

```bash
git clone https://github.com/<your-org>/ci-cd-Agents.git
cd ci-cd-Agents
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
.\.venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

### Environment variables

The project uses `python-dotenv` to load environment variables from a `.env` file. Create a `.env` file at the repository root with any required values, such as:

```text
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langchain_api_key
```

### Google Sheets telemetry

- `main.py` is configured to post telemetry to a Google Apps Script web app URL stored in the `GOOGLE_SHEETS_WEBAPP_URL` constant.
- `agents.py` uses `credentials.json` and a Google Sheets spreadsheet name to write audit logs directly.
- `Dashboard.py` reads from a published Google Sheet CSV URL in `CSV_URL`.

Update these values to match your Google Sheets deployment.

## Running the Agent

Start the observability agent runtime:

```bash
python main.py
```

You will be prompted to enter a user question. The pipeline evaluates the input, checks for injection, retrieves knowledge results, and logs telemetry.

## Running the Dashboard

Start the Streamlit dashboard with:

```bash
streamlit run Dashboard.py
```

The dashboard will read the live CSV feed from the configured Google Sheet and display metrics including request volume, injection rate, latency, cost, and raw event logs.

## Knowledge Base

The knowledge center is stored in `knowledge.json`. Add or update entries using the following schema:

```json
{
  "id": "KB004",
  "question": "example question",
  "answer": "example answer"
}
```

The `knowledge_agent` attempts to match user input against the stored questions and returns the corresponding answer if found.

## Testing

Run the example test suite with pytest:

```bash
pytest test_agent.py
```

The current tests cover:

- Handling of empty input without crashing
- Resilience against prompt injection-style input

## Notes

- The current dashboard expects the Google Sheet to publish a CSV view of telemetry data.
- The `guardrail_agent` marks malicious inputs as `INJECTION` and prevents further graph execution.
- The `knowledge_agent` returns a database answer if the user question matches exactly; otherwise, the fallback agent provides a safe default.

## Extending the Project

To extend this project, you can:

- Add more robust natural language matching for the knowledge base
- Replace the static JSON store with vector search or database-backed retrieval
- Add additional security or observability nodes to the graph
- Add support for multiple dashboard data sources or visualization panels

## License

This repository does not include a license file by default. Add one if you plan to share the project publicly.
