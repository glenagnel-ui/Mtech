# Agentic AI RAG Tester

An intelligent, autonomous testing suite for validating Retrieval-Augmented Generation (RAG) chatbots using a multi-agent AI architecture powered by **Llama 3** (via Groq API), **FAISS** vector search, and **Playwright** browser automation.

> **M.Tech Project** — Automated Quality Assurance for RAG-Based Conversational AI Systems

---

## Table of Contents

- [Features](#-features)
- [Architecture Overview](#-architecture-overview)
- [Project Structure](#-project-structure)
- [Technology Stack](#-technology-stack)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage Workflow](#-usage-workflow)
- [Dashboards](#-dashboards)
- [Database Schema](#-database-schema)
- [API Reference](#-api-reference)
- [Troubleshooting](#-troubleshooting)
- [License](#-license)

---

## 🌟 Features

| Feature | Description |
|---------|-------------|
| **Vector Knowledge Base** | Ingests web pages (via headless Playwright), Excel spreadsheets, PDFs, DOCX, and TXT files to build a local FAISS vector index using `all-MiniLM-L6-v2` embeddings |
| **BDD Acceptance Criteria** | Test generation is governed by explicitly defined Given/When/Then acceptance criteria from YAML configuration |
| **Multi-Agent Pipeline** | Three specialized LLM agents (Generator, Judge, Classifier) collaborate autonomously to create, evaluate, and diagnose test results |
| **Playwright UI Automation** | Automatically navigates to the target chatbot's web UI, sends questions, and extracts responses — zero human intervention |
| **Neon Cloud Postgres** | Persists all execution metrics, verdicts, and failure analyses to a serverless Neon PostgreSQL database |
| **Streamlit Dashboards** | Two interactive dashboards for visualizing test execution metrics, failure categories, and downloading generated test cases |
| **Workflow Runner** | Standalone RAG-powered test case generator that queries the FAISS index to produce context-aware acceptance-criteria-bound test prompts |

---

## 🏗 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        CONFIGURATION LAYER                      │
│   test_suite.yaml  ·  system_config.yaml  ·  .env              │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                     KNOWLEDGE BASE PIPELINE                     │
│                        (scrape_kb.py)                           │
│                                                                 │
│  Web URLs ──► Playwright Scraper ──► BeautifulSoup Parser       │
│  Excel    ──► Pandas Reader         │                           │
│  PDF/DOCX ──► PyPDF / python-docx   ▼                           │
│                              Text Chunks (LangChain Splitter)   │
│                                     │                           │
│                                     ▼                           │
│                         SentenceTransformer Encoding             │
│                                     │                           │
│                                     ▼                           │
│                           FAISS Vector Index                    │
│                     (knowledge_base/vector_store.index)          │
└─────────────────────────────────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                     ORCHESTRATOR (executor.py)                   │
│                                                                 │
│  Step 1: Scrape target URLs ──► Extract raw context             │
│  Step 2: GeneratorAgent ──► Synthesize Q&A test cases           │
│  Step 3: PlaywrightRunner ──► Ask chatbot each question         │
│  Step 4: JudgeAgent ──► Grade: CORRECT / PARTIAL / INCORRECT    │
│  Step 5: ClassifierAgent ──► Diagnose failure mode              │
│  Step 6: Save ──► CSV + Neon PostgreSQL                         │
└─────────────────────────────────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                       REPORTING LAYER                           │
│                                                                 │
│  📊 app.py (Streamlit)       — Execution results dashboard      │
│  📋 dashboard.py (Streamlit) — Generated test case viewer       │
│  📁 reports/execution_results/ — CSV result archives            │
│  🗄️ Neon PostgreSQL          — Persistent cloud storage         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
agentic_ai_rag_tester/
├── configs/
│   ├── system_config.yaml        # LLM model selection, browser settings, log level
│   └── test_suite.yaml           # Target URLs, topics, acceptance criteria, KB sources
├── src/
│   ├── agents/
│   │   ├── base_agent.py         # Abstract base class for all agents
│   │   ├── generator_agent.py    # Generates synthetic Q&A test cases via LLM
│   │   ├── judge_agent.py        # Grades chatbot answers (CORRECT/PARTIAL/INCORRECT)
│   │   └── classifier_agent.py   # Classifies failure modes (hallucination, missing info, etc.)
│   ├── core/
│   │   ├── config_loader.py      # YAML + env config parsing with Pydantic validation
│   │   └── llm_client.py         # OpenAI-compatible LLM client (Groq/OpenAI/Local)
│   ├── orchestrator/
│   │   └── executor.py           # End-to-end pipeline orchestration
│   ├── tools/
│   │   ├── playwright_runner.py  # Browser automation for chatbot interaction
│   │   └── web_scraper.py        # Lightweight text extraction from URLs
│   └── utils/
│       ├── db_utils.py           # Neon PostgreSQL ORM models and handler
│       ├── file_utils.py         # CSV I/O with timestamped filenames
│       └── logger.py             # Loguru-based structured logging (console + file)
├── knowledge_base/               # Generated FAISS index + chunk metadata (gitignored)
├── data/
│   ├── synthetic_data/           # Generated test prompts and cases (gitignored)
│   └── test_notes.txt            # Manual testing notes
├── reports/                      # Execution results and logs (gitignored)
├── .env                          # API keys and chatbot selectors (gitignored)
├── .gitignore
├── app.py                        # Streamlit dashboard — execution results viewer
├── dashboard.py                  # Streamlit dashboard — generated test case viewer
├── generate_test_suite.py        # CLI entry point — offline test generation only
├── main.py                       # CLI entry point — full end-to-end pipeline
├── scrape_kb.py                  # CLI entry point — standalone KB vector builder
├── workflow_runner.py            # CLI entry point — RAG-powered AC-driven test generator
├── requirements.txt              # Python dependencies
└── vercel.json                   # Deployment configuration
```

---

## 🔧 Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **LLM Backend** | Groq API (Llama 3.1 8B / Llama 3.3 70B) | Test generation, answer grading, failure classification |
| **Embeddings** | SentenceTransformers (`all-MiniLM-L6-v2`) | CPU-based semantic embeddings for the knowledge base |
| **Vector Store** | FAISS (`faiss-cpu`) | Similarity search over knowledge base chunks |
| **Text Splitting** | LangChain `RecursiveCharacterTextSplitter` | Chunking documents into 1000-char segments with 100-char overlap |
| **Browser Automation** | Playwright (Chromium) | Headless interaction with target chatbot UIs |
| **Web Scraping** | BeautifulSoup4 | HTML content extraction and cleaning |
| **Document Parsing** | PyPDF, python-docx | PDF and Word document ingestion |
| **Data Processing** | Pandas, openpyxl, xlrd | Excel and CSV data handling |
| **Configuration** | PyYAML, Pydantic, python-dotenv | Type-safe config loading with validation |
| **Database** | Neon PostgreSQL via SQLAlchemy + psycopg2 | Cloud-persistent test result storage |
| **Dashboard** | Streamlit | Interactive web UI for result analysis |
| **Logging** | Loguru | Structured, colorized console + rotating file logs |
| **API** | FastAPI + Uvicorn | REST API endpoints (optional) |

---

## 📋 Prerequisites

- **Python**: 3.10 or higher
- **OS**: Windows 10/11 (tested), Linux, macOS
- **Git**: Installed (verify with `git --version`)
- **Groq API Key**: Free tier available at [console.groq.com](https://console.groq.com)
- **Neon DB** (optional): Free tier at [neon.tech](https://neon.tech) for cloud persistence

---

## 🚀 Installation

### 1. Clone the Repository

```powershell
git clone https://github.com/glenagnel-ui/Mtech.git
cd Mtech/agentic_ai_rag_tester
```

### 2. Create a Virtual Environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 4. Install Playwright Browsers

```powershell
playwright install chromium
```

---

## ⚙ Configuration

### Environment Variables (`.env`)

Create a `.env` file in the `agentic_ai_rag_tester/` directory:

```env
# LLM Configuration (Groq)
OPENAI_API_KEY="gsk_your_groq_api_key_here"
LLM_BASE_URL="https://api.groq.com/openai/v1"

# Target Chatbot UI Selectors
CHATBOT_URL="https://your-chatbot-url.com"
CHATBOT_INPUT_SELECTOR="textarea[placeholder='Ask a question...']"
CHATBOT_SEND_SELECTOR="button[type='submit']"
CHATBOT_ANSWER_SELECTOR="div.markdown"

# Neon PostgreSQL (Optional)
NEON_DB_URL="postgresql://user:password@ep-xxx.region.aws.neon.tech/dbname?sslmode=require"
```

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | ✅ | Your Groq API key (format: `gsk_...`) |
| `LLM_BASE_URL` | ✅ | Groq endpoint: `https://api.groq.com/openai/v1` |
| `CHATBOT_URL` | ✅ | Full URL of the target chatbot web interface |
| `CHATBOT_INPUT_SELECTOR` | ✅ | CSS selector for the chatbot's text input field |
| `CHATBOT_SEND_SELECTOR` | ✅ | CSS selector for the chatbot's send/submit button |
| `CHATBOT_ANSWER_SELECTOR` | ⬚ | CSS selector for extracting the chatbot's response (defaults to `body`) |
| `NEON_DB_URL` | ⬚ | Neon PostgreSQL connection string for cloud persistence |

### System Configuration (`configs/system_config.yaml`)

Controls LLM model selection, browser behavior, and logging:

```yaml
llm:
  generator_model: "llama-3.1-8b-instant"     # Fast model for test generation
  judge_model: "llama-3.3-70b-versatile"       # Powerful model for grading
  classifier_model: "llama-3.3-70b-versatile"  # Powerful model for failure analysis

browser:
  headless: true        # Set to false to watch the browser interact
  timeout_ms: 30000     # Max wait time per page action
  slow_mo: 50           # Milliseconds delay between actions

logging:
  level: "INFO"         # Options: DEBUG, INFO, WARNING, ERROR
```

### Test Suite Configuration (`configs/test_suite.yaml`)

Defines what to test, what to scrape, and acceptance criteria:

```yaml
targets:
  - url: "https://your-chatbot-url.com/feature-page"
    topics:
      - "Feature Overview"
      - "Pricing"
    tests_per_topic: 3
    acceptance_criteria:
      - "Given a user asks about pricing, they should receive accurate fee information"
      - "Given a user asks about discounts, they should be told about available reductions"

personas:
  - "Student"
  - "Expert"
  - "Skeptic"

kb_sources:
  urls:
    - "https://your-documentation-site.com/page1"
    - "https://your-documentation-site.com/page2"
  excel_files:
    - "data/sample_data.xlsx"
  documents:
    - "data/docs/guide.pdf"
    - "data/docs/faq.docx"
```

---

## 🛠 Usage Workflow

The system operates in four sequential steps. Each step can be run independently.

### Step 1: Build the Vector Knowledge Base

Scrape configured sources and build the FAISS vector index. **Re-run only when source documentation changes.**

```powershell
python scrape_kb.py
```

**What it does:**
1. Reads `kb_sources` from `configs/test_suite.yaml`
2. Scrapes web URLs with headless Playwright + BeautifulSoup
3. Parses Excel files with Pandas
4. Reads PDF/DOCX/TXT documents
5. Splits all text into 1000-character chunks (100-char overlap)
6. Generates embeddings using `all-MiniLM-L6-v2`
7. Builds and saves a FAISS `IndexFlatL2` to `knowledge_base/`

**Output:**
```
knowledge_base/
├── vector_store.index   # FAISS binary index
└── chunks.json          # Source metadata + chunk text
```

### Step 2: Generate Synthetic Test Cases (Offline)

Generate test prompts using the LLM Generator Agent, bound by your acceptance criteria:

```powershell
python generate_test_suite.py
```

**Output:** Timestamped CSV files in `data/synthetic_data/prompt/`

### Step 3: Run the Full End-to-End Pipeline

Execute the complete testing workflow — generate tests, interact with the chatbot via browser, grade responses, classify failures:

```powershell
python main.py
```

Or provide a pre-generated test file:

```powershell
python main.py --test-file "data/synthetic_data/prompt/generated_tests_20260405_220000.csv"
```

**Pipeline Flow:**
1. **Generate** → LLM creates Q&A test cases from scraped context + acceptance criteria
2. **Execute** → Playwright opens the chatbot, sends each question, captures the response
3. **Judge** → LLM evaluates each response: `CORRECT`, `PARTIAL`, or `INCORRECT`
4. **Classify** → For failures, LLM diagnoses the error mode (hallucination, missing info, etc.)
5. **Save** → Results exported to CSV + Neon PostgreSQL

**Output:** Timestamped CSV in `reports/execution_results/`

### Step 4 (Alternative): RAG-Powered Test Generation

Use the workflow runner to generate test cases that are explicitly grounded in KB context:

```powershell
python workflow_runner.py
```

**Output:** `generated_test_cases.xlsx` with columns: Test Case ID, Acceptance Criteria, Prompts

---

## 📊 Dashboards

### Execution Results Dashboard (`app.py`)

Interactive dashboard for analyzing test execution outcomes:

```powershell
streamlit run app.py
```

**Features:**
- Toggle between **CSV Results** and **Neon DB** as data source
- Global metrics: Total Tests, Accuracy %, Average Confidence Score
- Failure analysis bar chart by category
- Full detailed results table with filtering

### Generated Test Cases Viewer (`dashboard.py`)

Preview and download generated test cases:

```powershell
streamlit run dashboard.py
```

**Features:**
- Preview first 5 generated test cases
- Download the complete Excel file

---

## 🗄 Database Schema

The `test_results` table is auto-created in Neon PostgreSQL on first run:

| Column | Type | Description |
|--------|------|-------------|
| `id` | `INTEGER` (PK, auto) | Unique record identifier |
| `topic` | `VARCHAR(255)` | Test topic category |
| `persona` | `VARCHAR(255)` | Simulated user persona |
| `question` | `TEXT` | Generated test question |
| `expected_answer` | `TEXT` | Ground truth expected answer |
| `chatbot_answer` | `TEXT` | Actual chatbot response |
| `verdict` | `VARCHAR(50)` | `CORRECT`, `PARTIAL`, or `INCORRECT` |
| `confidence_score` | `FLOAT` | Judge's confidence (0.0 – 1.0) |
| `failure_category` | `VARCHAR(100)` | `hallucination`, `missing_info`, `contradiction`, `off_topic`, `other` |
| `severity` | `INTEGER` | Failure severity (1–5, where 5 = critical) |
| `created_at` | `DATETIME` | Timestamp of test execution |

---

## 📡 API Reference

### Agent Classes

#### `GeneratorAgent.run()`
```python
run(context_text: str, topics: List[str], personas: List[str],
    num_tests: int, acceptance_criteria: List[str] = None) -> List[Dict]
```
Returns a list of `{"question", "expected_answer", "topic", "persona"}` dictionaries.

#### `JudgeAgent.run()`
```python
run(question: str, chatbot_answer: str, expected_answer: str) -> Dict
```
Returns `{"verdict": str, "confidence_score": float, "reason": str}`.

#### `ClassifierAgent.run()`
```python
run(question: str, chatbot_answer: str, expected_answer: str, judge_reason: str) -> Dict
```
Returns `{"failure_category": str, "explanation": str, "severity": int}`.

#### `LLMClient`
```python
generate(prompt, system_prompt, model, json_mode) -> str
generate_json(prompt, system_prompt, model) -> dict
```
OpenAI-compatible client supporting Groq, OpenAI, and local LLM endpoints.

---

## 🔍 Troubleshooting

| Issue | Solution |
|-------|----------|
| `OPENAI_API_KEY is missing` | Ensure `.env` file exists and contains your Groq API key |
| `playwright._impl._errors.Error` | Run `playwright install chromium` to install browser binaries |
| `Knowledge base not found` | Run `python scrape_kb.py` before using `workflow_runner.py` |
| `git is not recognized` | Git is installed at `C:\Program Files\Git\bin\git.exe` but not in PATH. Add it to your system PATH or use the full path |
| `Failed to load from DB` | Verify your `NEON_DB_URL` connection string includes `?sslmode=require` |
| `JSONDecodeError` from LLM | The LLM returned malformed JSON. The client has automatic cleanup fallback — if persistent, try a larger model |
| `Timeout during chatbot interaction` | Increase `timeout_ms` in `system_config.yaml` or check if `CHATBOT_URL` is accessible |
| No test cases generated | Verify `test_suite.yaml` has valid `targets` with `topics` and `tests_per_topic` |

---

## 📄 License

This project is developed as part of an M.Tech academic research project.

---

## 👤 Author

**Glen Agnel**
- GitHub: [github.com/glenagnel-ui](https://github.com/glenagnel-ui)
- Email: gllenagnel@gmail.com
