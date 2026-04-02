import streamlit as st
import requests, json
import plotly.io as pio

BACKEND = "http://localhost:8000"

st.set_page_config(page_title="QueryMind", page_icon="🔍", layout="wide")
st.title("🔍 QueryMind — Talk to Your Data")
st.caption("Upload a CSV, ask questions in plain English, get answers + SQL")

with st.sidebar:
    st.header("Upload your data")
    file = st.file_uploader("CSV file", type=["csv"])
    if file:
        res = requests.post(f"{BACKEND}/upload", files={"file": file})
        info = res.json()
        st.success(f"Loaded {info['rows']} rows, {len(info['columns'])} columns")
        st.write("**Columns:**", ", ".join(info["columns"]))

question = st.chat_input("Ask anything about your data...")

if "history" not in st.session_state:
    st.session_state.history = []

if question:
    st.session_state.history.append({"role": "user", "content": question})
    
    with st.spinner("Thinking..."):
        res = requests.post(f"{BACKEND}/query", json={"question": question})
        data = res.json()
    
    st.session_state.history.append({"role": "assistant", "data": data})

for msg in st.session_state.history:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.write(msg["content"])
    else:
        with st.chat_message("assistant"):
            d = msg["data"]
            if "error" in d:
                st.error(d["error"])
            else:
                st.info(d["insight"])
                
                # Show chart
                if d.get("chart"):
                    fig = pio.from_json(d["chart"])
                    st.plotly_chart(fig, use_container_width=True)
                
                # Show data table
                with st.expander("📋 Raw results"):
                    st.dataframe(d["data"])
                
                # Show SQL — this is your standout feature
                with st.expander("🔍 SQL query generated"):
                    st.code(d["sql"], language="sql")