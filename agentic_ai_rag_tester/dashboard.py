import streamlit as st
import pandas as pd
import os

st.title("🧪 Agentic AI RAG Tester - Generated Cases")

file_path = "generated_test_cases.xlsx"

if os.path.exists(file_path):
    df = pd.read_excel(file_path)
    
    st.markdown("### Preview (First 5 Rows)")
    st.dataframe(df.head(5))
    
    st.markdown("### Download")
    with open(file_path, "rb") as f:
        st.download_button(
            label="📥 Download Excel File",
            data=f,
            file_name="generated_test_cases.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
else:
    st.warning(f"No test cases found. Please run the workflow first to generate `{file_path}`")
