from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import shutil, os, uuid

from schema import extract_schema
from llm import generate_sql, generate_insight
from executor import run_query
from viz import auto_chart

load_dotenv()
app = FastAPI(title="QueryMind API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Simple in-memory session store
sessions = {}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(400, "Only CSV files are supported")
    
    session_id = str(uuid.uuid4())
    path = f"/tmp/{session_id}.csv"
    
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    schema, df = extract_schema(path)
    sessions[session_id] = {"df": df, "schema": schema}
    
    return {
        "session_id": session_id,
        "columns": [c["name"] for c in schema["columns"]],
        "row_count": schema["row_count"]
    }

class QueryRequest(BaseModel):
    session_id: str
    question: str

@app.post("/query")
async def query(req: QueryRequest):
    if req.session_id not in sessions:
        raise HTTPException(404, "Session not found. Please upload a file first.")
    
    session = sessions[req.session_id]
    df = session["df"]
    schema = session["schema"]
    
    # First attempt
    sql = generate_sql(req.question, schema)
    result_df, error = run_query(df, sql)
    
    # Retry once with error feedback — this is the industry-level part
    if error:
        sql = generate_sql(req.question, schema, error=error)
        result_df, error = run_query(df, sql)
    
    if error:
        return {"sql": sql, "error": error, "data": [], "columns": [], "insight": None, "chart": None}
    
    preview = result_df.head(10).to_string(index=False)
    insight = generate_insight(req.question, preview)
    chart = auto_chart(result_df)
    
    return {
        "sql": sql,
        "error": None,
        "data": result_df.head(100).to_dict(orient="records"),
        "columns": list(result_df.columns),
        "insight": insight,
        "chart": chart
    }
