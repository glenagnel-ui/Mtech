# Agentic AI RAG Tester

An intelligent, autonomous testing suite to validate Retrieval-Augmented Generation (RAG) chatbots using a multi-agent AI architecture powered by **Llama 3** (via Groq API).

## 🌟 Features

- **Vector Knowledge Base Generator (`scrape_kb.py`)**: A standalone script that ingests Web URLs (via headless Playwright), Excel Spreadsheets, and Documents (PDFs, DOCX, TXT) to create a local FAISS vector database using CPU embeddings (`all-MiniLM-L6-v2`).
- **BDD Acceptance Criteria Integration**: Synthetically generated test questions are tightly bound to explicitly defined testing requirements.
- **Agentic Testing Pipeline**:
  - **Generator Agent**: Leverages context from the knowledge base to synthetically generate diverse QA test cases.
  - **Judge Agent**: Evaluates the target chatbot's responses against expected answers.
  - **Classifier Agent**: Analyzes failure modes for incorrect answers.
- **Playwright Web Automation**: Automatically navigates the web UI of your target chatbot to execute test cases without human intervention.
- **Neon Cloud Postgres Integration**: Saves all execution metrics and pipeline data to Neon DB.

---

## 🚀 Setup Instructions

### 1. Install Dependencies
Make sure you are utilizing a python virtual environment, then install requirements:
```powershell
pip install -r requirements.txt
playwright install
```

### 2. Configure Environment Variables
Inside your `.env` file, configure your API keys and UI Targets:
```env
OPENAI_API_KEY="gsk_..." # <--- PASTE YOUR GROQ API KEY HERE
LLM_BASE_URL="https://api.groq.com/openai/v1" # Groq Llama API Endpoint

CHATBOT_URL="https://example.com/chat"
CHATBOT_INPUT_SELECTOR="textarea[placeholder='Ask a question...']"
CHATBOT_SEND_SELECTOR="button[type='submit']"

NEON_DB_URL="postgresql://..." # Your Neon pgSQL Connection String
```

### 3. Configure the Test Suite
Edit `configs/test_suite.yaml` to specify target areas. This file governs both what datastreams are scraped for the local knowledge base, and what topics the AI should test against.

```yaml
targets:
  - url: "https://example.com/important_feature"
    topics:
      - "Feature Description"
    acceptance_criteria:
      - "Given a user asks about X, they should be told Y"
    tests_per_topic: 5

personas:
  - "Student"
  - "Expert"

kb_sources:
  urls:
    - "https://example.com/important_feature"
  excel_files:
    - "data/sample_data.xlsx"
```

---

## 🛠️ Usage Workflow

### Step 1: Scrape & Build the Vector Knowledge Base (On Demand)
Before generating intelligent testing data, you must build the vector index. You only need to re-run this script when documentation/websites update. 
```powershell
python scrape_kb.py
```
> *This will generate vector embeddings for your data and construct a FAISS index inside `./knowledge_base/`*

### Step 2: Generate Synthetic Test Prompts (Offline)
Generate testing prompts explicitly designed around your Acceptance Criteria constraints.
```powershell
python generate_test_suite.py
```
> *Outputs are routed to `./data/synthetic_data/prompt/`*

### Step 3: Full End-to-End Execution (UI Testing)
To dynamically spawn the testing browser, chat with your target RAG app, grade the responses with Llama 3 Judge/Classifier, and publish execution summaries:
```powershell
python main.py
```

### Step 4: Analyze Results with Streamlit
Run the visual web dashboard to review test execution metrics, failure categories, and model responses:
```powershell
streamlit run app.py
```
