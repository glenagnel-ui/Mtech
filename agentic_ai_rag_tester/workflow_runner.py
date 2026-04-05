import os
import faiss
import json
import yaml
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from src.core.llm_client import LLMClient
from loguru import logger

KB_DIR = "./knowledge_base"
CONFIG_PATH = "configs/test_suite.yaml"
OUTPUT_FILE = "generated_test_cases.xlsx"

def run_workflow():
    if not os.path.exists(KB_DIR) or not os.path.exists(os.path.join(KB_DIR, "vector_store.index")):
        logger.error("Knowledge base not found. Please run the standalone scraper scrape_kb.py first.")
        return

    # Load FAISS
    index = faiss.read_index(os.path.join(KB_DIR, "vector_store.index"))
    with open(os.path.join(KB_DIR, "chunks.json"), "r") as f:
        chunks = json.load(f)
        
    model = SentenceTransformer("all-MiniLM-L6-v2")

    # Load ACs
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    
    acs = []
    for target in config.get("targets", []):
        for ac in target.get("acceptance_criteria", []):
            acs.append(ac)
            
    if not acs:
        logger.warning("No acceptance criteria found in test_suite.yaml!")
        return

    llm = LLMClient()
    results = []

    for idx, ac in enumerate(acs):
        # Query FAISS
        query_vec = model.encode([ac]).astype('float32')
        D, I = index.search(query_vec, k=3)
        
        retrieved_texts = []
        for i in I[0]:
            if i < len(chunks):
                retrieved_texts.append(chunks[i]["text"])
                
        context = "\n\n".join(retrieved_texts)
        if not context.strip():
            results.append({
                "Test Case ID": f"TC-{idx+1:03d}",
                "Acceptance Criteria": ac,
                "Prompts": "[KB missing - please update scrape_kb.py with additional sources]"
            })
            continue

        prompt = f"""
        Acceptance Criteria: {ac}
        Knowledge Base Context:
        {context}
        
        Create a detailed test prompt with steps and expected results to test the AC against the context.
        Output ONLY the prompt steps and expected result as text, no extra chit chat.
        """
        
        generated = llm.generate(prompt, system_prompt="You are a QA automation engineer.", model="llama-3.1-8b-instant")
        
        results.append({
            "Test Case ID": f"TC-{idx+1:03d}",
            "Acceptance Criteria": ac,
            "Prompts": generated.strip()
        })
        
    df = pd.DataFrame(results)
    df.to_excel(OUTPUT_FILE, index=False)
    print(f"✅ Test cases generated: {len(results)} from {len(acs)} acceptance criteria.")

if __name__ == "__main__":
    run_workflow()
