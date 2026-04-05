import os
import yaml
import json
import uuid
from datetime import datetime
import pandas as pd
from loguru import logger
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# Optional document parsers
try:
    from docx import Document
except ImportError:
    Document = None

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "configs", "test_suite.yaml")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "knowledge_base")
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

def init_kb_dir():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        logger.info(f"Created knowledge base directory at ./{OUTPUT_DIR}")

def load_config():
    if not os.path.exists(CONFIG_PATH):
        logger.error(f"Config file not found at {CONFIG_PATH}")
        return {}
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config.get("kb_sources", {})

def scrape_url(url):
    logger.info(f"Scraping URL: {url}")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            })
            page.goto(url, wait_until="domcontentloaded", timeout=45000)
            html = page.content()
            browser.close()
            
        soup = BeautifulSoup(html, "html.parser")
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.extract()
        text = soup.get_text(separator="\n\n")
        lines = (line.strip() for line in text.splitlines())
        clean_text = '\n'.join(chunk for chunk in lines if chunk)
        return clean_text
    except Exception as e:
        logger.error(f"Failed to scrape URL {url}: {e}")
        return ""

def process_excel(fp):
    if not os.path.exists(fp):
        logger.warning(f"File not found: {fp}")
        return ""
    try:
        df = pd.read_excel(fp)
        return df.to_json(orient="records", indent=4)
    except Exception as e:
        logger.error(f"Failed to read Excel {fp}: {e}")
        return ""

def process_document(fp):
    if not os.path.exists(fp):
        logger.warning(f"File not found: {fp}")
        return ""
    ext = os.path.splitext(fp)[1].lower()
    content = ""
    try:
        if ext == ".pdf":
            if PdfReader:
                reader = PdfReader(fp)
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        content += text + "\n\n"
        elif ext == ".docx":
            if Document:
                doc = Document(fp)
                for para in doc.paragraphs:
                    content += para.text + "\n"
        elif ext == ".txt":
            with open(fp, "r", encoding="utf-8") as f:
                content = f.read()
    except Exception as e:
        logger.error(f"Failed to process document {fp}: {e}")
    return content

def main():
    logger.info("Initializing Vector Knowledge Base Pipeline...")
    init_kb_dir()
    
    sources = load_config()
    if not sources:
        logger.warning("No 'kb_sources' block found in test_suite.yaml")
        return
        
    urls = sources.get("urls", [])
    excel_files = sources.get("excel_files", [])
    documents = sources.get("documents", [])
    
    all_chunks = []
    
    # 1. Scrape and Chunk
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    
    for url in urls:
        text = scrape_url(url)
        if text:
            chunks = text_splitter.split_text(text)
            for c in chunks:
                all_chunks.append({"source": url, "text": c})
                
    for fp in excel_files:
        abs_fp = fp if os.path.isabs(fp) else os.path.join(SCRIPT_DIR, fp)
        text = process_excel(abs_fp)
        if text:
            chunks = text_splitter.split_text(text)
            for c in chunks:
                all_chunks.append({"source": fp, "text": c})
                
    for fp in documents:
        abs_fp = fp if os.path.isabs(fp) else os.path.join(SCRIPT_DIR, fp)
        text = process_document(abs_fp)
        if text:
            chunks = text_splitter.split_text(text)
            for c in chunks:
                all_chunks.append({"source": fp, "text": c})
                
    if not all_chunks:
        logger.warning("No valid data was scraped. Exiting.")
        return
        
    logger.info(f"Generated {len(all_chunks)} text chunks. Loading embedding model: {EMBEDDING_MODEL_NAME}...")
    
    # 2. Embed
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    texts = [chunk["text"] for chunk in all_chunks]
    embeddings = model.encode(texts, show_progress_bar=True)
    embeddings = np.array(embeddings).astype('float32')
    
    # 3. Create FAISS Index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    
    # 4. Save to disk
    faiss.write_index(index, os.path.join(OUTPUT_DIR, "vector_store.index"))
    
    with open(os.path.join(OUTPUT_DIR, "chunks.json"), "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=4)
    
    # 5. Save metadata for the dashboard
    unique_sources = list(set(chunk["source"] for chunk in all_chunks))
    metadata = {
        "scraped_at": datetime.now().isoformat(),
        "total_chunks": len(all_chunks),
        "total_sources": len(unique_sources),
        "sources": unique_sources,
        "embedding_model": EMBEDDING_MODEL_NAME,
        "embedding_dimension": int(dimension)
    }
    
    # Load existing history or create new
    history_path = os.path.join(OUTPUT_DIR, "scrape_history.json")
    history = []
    if os.path.exists(history_path):
        with open(history_path, "r", encoding="utf-8") as f:
            history = json.load(f)
    history.append(metadata)
    
    with open(history_path, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4)
    
    with open(os.path.join(OUTPUT_DIR, "metadata.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)
        
    logger.success(f"Knowledge Base securely vectorized & saved to {OUTPUT_DIR}!")

if __name__ == "__main__":
    main()
