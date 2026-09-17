# ⚡ QueryAI — Natural Language to SQL Analytics Platform

[![Live Demo](https://img.shields.io/badge/🚀_Live_Demo-Streamlit_Community_Cloud-FF4B4B?style=for-the-badge&logo=streamlit)](https://nl2sql-analytics.streamlit.app)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Groq](https://img.shields.io/badge/LLM_Inference-Groq_Cloud-F55036?style=for-the-badge)](https://groq.com/)
[![LangChain](https://img.shields.io/badge/Orchestration-LangChain-1C3C3C?style=for-the-badge)](https://www.langchain.com/)
[![Plotly](https://img.shields.io/badge/Visualization-Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)](https://plotly.com/)

**QueryAI** is a modern, ChatGPT-style conversational analytics copilot that translates plain English (and spoken voice queries) into executable SQL, queries relational databases or custom CSVs, and automatically renders interactive data visualizations.

---

## 🌟 Key Features

- 🗣️ **Conversational Text-to-SQL**: Ask complex data questions in plain English—no SQL expertise required.
- 🎙️ **Voice Dictation (Groq Whisper)**: Speak your query directly into the chatbar via speech-to-text powered by `whisper-large-v3-turbo`.
- 📦 **Hybrid Data Ingestion**:
  - **🌟 Instant Demo**: Pre-bundled SQLite datasets (`student_db` and `clothing`) with zero setup needed.
  - **📁 Custom CSV / SQLite Upload**: Drag-and-drop any spreadsheet to automatically generate in-memory relational schemas.
  - **🔌 Remote MySQL Connector**: Connect live production or cloud MySQL servers.
- 📊 **Automatic Plotly Visualizations**: Generates interactive dark-mode bar and pie charts when visualization keywords are detected.
- ⚡ **Two-Stage Chain Architecture**: Separates SQL code generation from natural-language result summarization for accuracy.
- 🛡️ **SQL Sanitization & Safety**: Cleans Markdown wrappers, removes non-SQL text, and safely executes queries with transactional support.
- 💬 **Session History & New Chat**: Manage previous conversations and start fresh sessions with 1 click.

---

## 🏗️ System Architecture

```
                       ┌───────────────────────────────┐
                       │    User Input (Text / Voice)   │
                       └──────────────┬────────────────┘
                                      │
                         [🎙️ Voice Dictation]
                                      ▼
                        Groq Whisper-large-v3-turbo
                                      │
                                      ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                           STAGE 1: SQL GENERATION                          │
│                                                                           │
│  Schema Introspection  +  Few-Shot Examples  +  Conversation Context      │
│                                    │                                      │
│                                    ▼                                      │
│                  Groq LLM (openai/gpt-oss-20b, 120b)                      │
│                                    │                                      │
│                                    ▼                                      │
│                          Regex SQL Sanitizer                              │
└────────────────────────────────────┬──────────────────────────────────────┘
                                     │
                                     ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                          DATABASE EXECUTION LAYER                         │
│                                                                           │
│    🌟 Bundled SQLite Demo  │  📁 Uploaded CSV  │  🔌 Remote MySQL         │
└────────────────────────────────────┬──────────────────────────────────────┘
                                     │
                                     ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                      STAGE 2: NATURAL LANGUAGE SYNTHESIS                  │
│                                                                           │
│         SQL Query  +  Execution Results  +  Original Question             │
│                                    │                                      │
│                                    ▼                                      │
│                 Conversational Explanation & Plotly Chart                 │
└───────────────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Frontend UI** | Streamlit | Responsive dark-mode interface inspired by ChatGPT & Claude |
| **LLM Inference** | Groq Cloud | Ultra-low latency inference (`openai/gpt-oss-20b`, `120b`, `qwen3.8-27b`) |
| **Speech-to-Text** | Groq Whisper | Real-time speech transcription (`whisper-large-v3-turbo`) |
| **Orchestration** | LangChain | LCEL chains, prompt templates, and schema bindings |
| **Database Engines** | SQLite & MySQL | Dual support for local embedded DBs and live relational servers |
| **Data & Viz** | Pandas & Plotly | In-memory data transformation and interactive chart rendering |

---

## 📁 Project Structure

```text
Natural-Language-to-SQL-Converter/
├── data/
│   └── demo.db             # Bundled SQLite database (student_db & clothing)
├── src/
│   ├── app.py              # Main Streamlit application & modern UI
│   ├── database.py         # Multi-database manager, Groq chains, Whisper
│   ├── k_shot_examples.py  # Domain-specific few-shot SQL prompts
│   ├── logging_utils.py    # Rotating session log manager
│   ├── test_app.py         # Test harness UI entry point
│   ├── test_database.py    # Automated test execution helpers
│   ├── test_examples.py    # Benchmark test suites
│   └── testing_utils.py    # Evaluation dashboard
├── .env                    # Environment variables (GROQ_API_KEY)
├── .gitignore              # Git ignore rules protecting keys & venv
├── README.md               # Project documentation
├── requirements.txt        # Python package dependencies
└── setup_databases.py      # MySQL schema initialization and seed script
```

---

## 🚀 Quickstart (Local Setup)

### 1. Clone the Repository
```bash
git clone https://github.com/rahul-1909/Natural-Language-to-SQL-Converter.git
cd Natural-Language-to-SQL-Converter
```

### 2. Create and Activate Virtual Environment
```bash
python -m venv venv
# On Windows:
.\venv\Scripts\Activate.ps1
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure API Keys
Create a `.env` file in the project root:
```env
GROQ_API_KEY=gsk_your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-20b
```
*(Get your free API key at [console.groq.com/keys](https://console.groq.com/keys))*

### 5. Run the Application
```bash
streamlit run src/app.py
```
Open **`http://localhost:8501`** in your browser.

---

## 🌐 Deploying to Streamlit Cloud

1. Fork or push this repository to your GitHub account.
2. Go to **[share.streamlit.io](https://share.streamlit.io)** and click **New App**.
3. Select your repository and set Main file path to **`src/app.py`**.
4. In **Advanced settings $\rightarrow$ Secrets**, paste:
   ```toml
   GROQ_API_KEY = "gsk_your_actual_key_here"
   GROQ_MODEL = "openai/gpt-oss-20b"
   ```
5. Click **Deploy**!

---

## 📜 License
This project is open-source and available under the [MIT License](LICENSE).
