import pandas as pd

def extract_schema(filepath: str) -> dict:
    df = pd.read_csv(filepath)
    schema = {
        "columns": [
            {"name": col, "type": str(df[col].dtype), "sample": str(df[col].dropna().iloc[0])}
            for col in df.columns
        ],
        "row_count": len(df),
        "table_name": "uploaded_data"
    }
    return schema, df