"""
Scraped Knowledge Base Dashboard
Interactive Streamlit dashboard for exploring the FAISS vector knowledge base.
"""
import streamlit as st
import json
import os
import numpy as np
from datetime import datetime

# Resolve paths relative to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
KB_DIR = os.path.join(SCRIPT_DIR, "knowledge_base")

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Scraped Knowledge Base Dashboard",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1a1a2e;
        padding-bottom: 0.3rem;
        border-bottom: 3px solid #3b82f6;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        font-size: 1rem;
        color: #6b7280;
        margin-bottom: 1.5rem;
    }
    
    /* Stat cards */
    .stat-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
    }
    .stat-label {
        font-size: 0.85rem;
        color: #64748b;
        font-weight: 500;
    }
    .stat-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1e293b;
        text-align: right;
    }
    .stat-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.3rem 0;
    }
    
    /* Scrape status dot */
    .status-dot {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
        vertical-align: middle;
    }
    .status-green { background: #22c55e; }
    .status-yellow { background: #eab308; }
    .status-red { background: #ef4444; }
    
    /* Source URL links */
    .source-link {
        display: block;
        color: #3b82f6;
        text-decoration: none;
        font-size: 0.9rem;
        padding: 0.25rem 0;
        word-break: break-all;
    }
    .source-link:hover {
        text-decoration: underline;
        color: #2563eb;
    }
    
    /* Result cards */
    .result-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .result-header {
        font-weight: 600;
        font-size: 0.95rem;
        color: #1e293b;
        margin-bottom: 0.4rem;
    }
    .result-score {
        display: inline-block;
        background: #f1f5f9;
        border: 1px solid #cbd5e1;
        border-radius: 20px;
        padding: 0.1rem 0.6rem;
        font-size: 0.75rem;
        color: #475569;
        margin-left: 0.5rem;
        font-weight: 500;
    }
    .result-text {
        color: #475569;
        font-size: 0.9rem;
        line-height: 1.5;
    }
    
    /* History cards */
    .history-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .history-time {
        font-weight: 600;
        font-size: 0.9rem;
        color: #1e293b;
    }
    .history-ago {
        font-size: 0.8rem;
        color: #94a3b8;
    }
    
    /* Section headers */
    .section-header {
        font-size: 1rem;
        font-weight: 600;
        color: #1e293b;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }

    div[data-testid="stHorizontalBlock"] > div {
        padding: 0 0.3rem;
    }
</style>
""", unsafe_allow_html=True)


# ── Utility Functions ────────────────────────────────────────────────────────

def load_kb_data():
    """Load chunks.json and metadata.json from the knowledge base directory."""
    chunks, metadata, history = [], {}, []
    
    chunks_path = os.path.join(KB_DIR, "chunks.json")
    if os.path.exists(chunks_path):
        with open(chunks_path, "r", encoding="utf-8") as f:
            chunks = json.load(f)
    
    meta_path = os.path.join(KB_DIR, "metadata.json")
    if os.path.exists(meta_path):
        with open(meta_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)
    
    hist_path = os.path.join(KB_DIR, "scrape_history.json")
    if os.path.exists(hist_path):
        with open(hist_path, "r", encoding="utf-8") as f:
            history = json.load(f)
    
    return chunks, metadata, history


@st.cache_resource
def load_faiss_and_model():
    """Load FAISS index and SentenceTransformer model (cached)."""
    index_path = os.path.join(KB_DIR, "vector_store.index")
    if not os.path.exists(index_path):
        return None, None
    
    import faiss
    from sentence_transformers import SentenceTransformer
    
    index = faiss.read_index(index_path)
    model = SentenceTransformer("all-MiniLM-L6-v2")
    return index, model


def time_ago(iso_str):
    """Return a human-readable 'X ago' string from an ISO timestamp."""
    try:
        dt = datetime.fromisoformat(iso_str)
        delta = datetime.now() - dt
        
        if delta.days > 0:
            return f"({delta.days} day{'s' if delta.days != 1 else ''} ago)"
        hours = delta.seconds // 3600
        if hours > 0:
            return f"({hours} hour{'s' if hours != 1 else ''} ago)"
        minutes = delta.seconds // 60
        if minutes > 0:
            return f"({minutes} minute{'s' if minutes != 1 else ''} ago)"
        return "(just now)"
    except Exception:
        return ""


def get_status_color(iso_str):
    """Green if <24h, yellow if <7d, red otherwise."""
    try:
        dt = datetime.fromisoformat(iso_str)
        delta = datetime.now() - dt
        if delta.days < 1:
            return "green"
        elif delta.days < 7:
            return "yellow"
        else:
            return "red"
    except Exception:
        return "red"


def format_timestamp(iso_str):
    """Format ISO string to readable date."""
    try:
        dt = datetime.fromisoformat(iso_str)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return iso_str


# ── Load Data ────────────────────────────────────────────────────────────────
chunks, metadata, history = load_kb_data()

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">📚 Scraped Knowledge Base Dashboard</div>', unsafe_allow_html=True)

if metadata:
    source_urls = [s for s in metadata.get("sources", []) if s.startswith("http")]
    domains = set()
    for url in source_urls:
        try:
            from urllib.parse import urlparse
            domains.add(urlparse(url).netloc)
        except Exception:
            pass
    domain_str = ", ".join(domains) if domains else "configured sources"
    st.markdown(f'<div class="subtitle">Content from {domain_str}</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="subtitle">No knowledge base found. Run <code>python scrape_kb.py</code> first.</div>', unsafe_allow_html=True)

# ── Check if KB exists ───────────────────────────────────────────────────────
if not chunks:
    st.warning("⚠️ No knowledge base data found. Please run `python scrape_kb.py` to build the vector index first.")
    st.stop()

# ── Main Layout ──────────────────────────────────────────────────────────────
left_col, right_col = st.columns([1, 2.5], gap="large")

# ── LEFT COLUMN: Stats + Sources ─────────────────────────────────────────────
with left_col:
    # Knowledge Base Stats
    st.markdown('<div class="section-header">📊 Knowledge Base Stats</div>', unsafe_allow_html=True)
    
    total_chunks = metadata.get("total_chunks", len(chunks))
    unique_sources = list(set(c.get("source", "") for c in chunks))
    source_urls = [s for s in unique_sources if s.startswith("http")]

    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-row">
            <span class="stat-label">Total Text Chunks:</span>
            <span class="stat-value">{total_chunks}</span>
        </div>
        <div class="stat-row">
            <span class="stat-label">Scraped URLs:</span>
            <span class="stat-value">{len(source_urls)}</span>
        </div>
        <div class="stat-row">
            <span class="stat-label">Total Sources:</span>
            <span class="stat-value">{len(unique_sources)}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Last Scrape
    if metadata.get("scraped_at"):
        scraped_at = metadata["scraped_at"]
        color = get_status_color(scraped_at)
        ts_display = format_timestamp(scraped_at)
        ago = time_ago(scraped_at)
        
        st.markdown(f"""
        <div class="stat-card">
            <div class="section-header">Last Scrape:</div>
            <div>
                <span class="status-dot status-{color}"></span>
                <strong>{ts_display}</strong><br>
                <span style="margin-left: 20px; color: #94a3b8; font-size: 0.85rem;">{ago}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Source URLs
    st.markdown('<div class="section-header">🔗 Source URLs</div>', unsafe_allow_html=True)
    
    source_links_html = ""
    for src in unique_sources:
        if src.startswith("http"):
            source_links_html += f'<a class="source-link" href="{src}" target="_blank">• {src}</a>'
        else:
            source_links_html += f'<div class="source-link" style="color: #64748b;">📄 {src}</div>'
    
    st.markdown(f'<div class="stat-card">{source_links_html}</div>', unsafe_allow_html=True)


# ── RIGHT COLUMN: Search + Results ───────────────────────────────────────────
with right_col:
    # Search box
    search_col, btn_col = st.columns([5, 1])
    with search_col:
        query = st.text_input(
            "Search the Knowledge Base",
            placeholder="What is tuition reduction?",
            label_visibility="collapsed",
            key="kb_search_input"
        )
    with btn_col:
        search_clicked = st.button("🔍 Go", use_container_width=True, type="primary")
    
    # Perform search
    if query and search_clicked:
        index, model = load_faiss_and_model()
        
        if index is None or model is None:
            st.error("FAISS index or embedding model could not be loaded.")
        else:
            query_vec = model.encode([query]).astype('float32')
            k = min(5, index.ntotal)
            distances, indices = index.search(query_vec, k=k)
            
            st.markdown('<div class="section-header">Results</div>', unsafe_allow_html=True)
            
            for rank, (dist, idx) in enumerate(zip(distances[0], indices[0]), 1):
                if idx < len(chunks):
                    chunk = chunks[idx]
                    # Convert L2 distance to a similarity score (lower distance = higher similarity)
                    score = 1.0 / (1.0 + float(dist))
                    text_preview = chunk["text"][:300] + ("..." if len(chunk["text"]) > 300 else "")
                    source = chunk.get("source", "Unknown")
                    
                    st.markdown(f"""
                    <div class="result-card">
                        <div class="result-header">
                            🔎 Result {rank} <span class="result-score">score {score:.3f}</span>
                        </div>
                        <div class="result-text">{text_preview}</div>
                        <div style="margin-top: 0.5rem; font-size: 0.8rem; color: #94a3b8;">
                            Source: <a href="{source}" target="_blank" style="color: #3b82f6;">{source}</a>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    
    # All Chunks Preview (Expandable)
    with st.expander("≡ All Chunks (Preview)", expanded=False):
        import pandas as pd
        chunk_data = []
        for i, chunk in enumerate(chunks):
            chunk_data.append({
                "ID": i + 1,
                "Source": chunk.get("source", ""),
                "Text Preview": chunk["text"][:150] + "..." if len(chunk["text"]) > 150 else chunk["text"]
            })
        df = pd.DataFrame(chunk_data)
        st.dataframe(df, use_container_width=True, height=400)


# ── BOTTOM: Scrape History Timeline ──────────────────────────────────────────
if history and len(history) > 0:
    st.markdown("---")
    st.markdown('<div class="section-header">📅 Scrape History</div>', unsafe_allow_html=True)
    
    # Show last 5 entries, most recent first
    recent = list(reversed(history[-5:]))
    cols = st.columns(min(len(recent), 5))
    
    for i, entry in enumerate(recent):
        with cols[i]:
            scraped_at = entry.get("scraped_at", "")
            color = get_status_color(scraped_at)
            ts = format_timestamp(scraped_at)
            ago = time_ago(scraped_at)
            total = entry.get("total_chunks", "?")
            
            st.markdown(f"""
            <div class="history-card">
                <div>
                    <span class="status-dot status-{color}"></span>
                    <span class="history-time">{ts}</span>
                </div>
                <div class="history-ago">{ago}</div>
                <div style="margin-top: 0.4rem; font-size: 0.8rem; color: #64748b;">
                    {total} chunks
                </div>
            </div>
            """, unsafe_allow_html=True)
