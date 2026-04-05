import streamlit as st
import pandas as pd
import os
import glob
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="RAG Quality Dashboard", layout="wide")
st.title("RAG Tester Dashboard")

# Determine data source
data_source = st.sidebar.radio("Data Source", ["CSV Results", "Neon DB"])

if data_source == "CSV Results":
    st.sidebar.subheader("Select Execution Result")
    result_files = glob.glob("reports/execution_results/*.csv")
    if result_files:
        selected_file = st.sidebar.selectbox("File", sorted(result_files, reverse=True))
        df = pd.read_csv(selected_file)
    else:
        st.warning("No CSV files found in reports/execution_results/")
        df = pd.DataFrame()
else:
    db_url = os.getenv("NEON_DB_URL")
    if db_url:
        st.sidebar.success("Found Neon DB Connection")
        if db_url.startswith("postgresql://"):
            db_url = db_url.replace("postgresql://", "postgresql+psycopg2://", 1)
        engine = create_engine(db_url)
        try:
            df = pd.read_sql_table("test_results", engine)
        except Exception as e:
            st.error(f"Failed to load from DB: {e}. Provide correct Neon credentials.")
            df = pd.DataFrame()
    else:
        st.warning("NEON_DB_URL not found in environment.")
        df = pd.DataFrame()

if not df.empty:
    st.subheader("Global Metrics")
    col1, col2, col3, col4 = st.columns(4)
    total = len(df)
    correct = len(df[df["verdict"] == "CORRECT"])
    accuracy = (correct / total) * 100 if total else 0
    
    col1.metric("Total Tests", total)
    col2.metric("Accuracy", f"{accuracy:.1f}%")
    col3.metric("Avg Confidence", f'{df["confidence_score"].mean():.2f}')
    
    st.subheader("Failure Analysis")
    if "failure_category" in df.columns:
        failures = df[df["verdict"] != "CORRECT"]
        if not failures.empty:
            st.bar_chart(failures["failure_category"].value_counts())
        else:
            st.success("No failures!")

    st.subheader("Detailed Results")
    st.dataframe(df, use_container_width=True)
