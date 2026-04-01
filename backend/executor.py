import duckdb
import pandas as pd

def run_query(df: pd.DataFrame, sql: str):
    try:
        conn = duckdb.connect(database=":memory:")
        conn.register("uploaded_data", df)
        result = conn.execute(sql).df()
        conn.close()
        return result, None
    except Exception as e:
        return None, str(e)