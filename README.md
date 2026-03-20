# SQL Database Chat Assistant

A Streamlit-based AI assistant that converts natural language questions into SQL queries, executes them on a MySQL database, and returns human-readable answers. It also supports simple chart visualizations and includes a built-in testing interface for SQL generation quality checks.

## Features

- Natural language to SQL conversion using LangChain + Groq LLM
- MySQL database connectivity with selectable databases
- Chat UI with persistent chat history (`chat_history.json`)
- Optional data visualization (bar/pie charts) for query results
- Session logging to daily log files in `logs/`
- Test harness UI for running SQL generation test cases

## Project Structure

```text
sqlproj_nogit/
├─ src/
│  ├─ app.py               # Main Streamlit chat application
│  ├─ database.py          # SQL chain, sanitization, and response pipeline
│  ├─ k_shot_examples.py   # Few-shot examples per database
│  ├─ logging_utils.py     # Logging setup
│  ├─ testing_utils.py     # Streamlit-based test dashboard
│  ├─ test_app.py          # Test app entrypoint
│  ├─ test_database.py     # Test execution helpers
│  └─ test_examples.py     # Test case definitions
├─ chat_history.json
├─ logs/
├─ requirements.txt
└─ start.txt
```

## Requirements

- Python 3.10+
- Access to a MySQL server
- A Groq API key

## Installation

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root with your API key:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Database connection settings are entered from the Streamlit sidebar at runtime (host, port, user, password, and database).

## Run the App

From project root:

```bash
streamlit run src/app.py
```

Windows shortcut command (as in `start.txt`):

```bash
venv\Scripts\python.exe -m streamlit run src/app.py
```

## Run the Test Interface

```bash
streamlit run src/test_app.py
```

The test interface:

- Connects to your selected MySQL database
- Runs predefined test cases from `src/test_examples.py`
- Compares expected and generated SQL behavior
- Displays summary metrics and detailed results

## Notes

- Query sanitization is handled in `src/database.py` before execution.
- Non-SELECT SQL statements are committed automatically.
- Logs are written to `logs/session_YYYYMMDD.log`.

## Troubleshooting

- **Connection errors**: Verify MySQL host/port/credentials and selected database.
- **LLM/auth errors**: Confirm `GROQ_API_KEY` is set in `.env`.
- **Import/module errors**: Ensure dependencies are installed in the active environment.
