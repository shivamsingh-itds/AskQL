import pandas as pd
import plotly.express as px
import json

def auto_chart(df: pd.DataFrame) -> str | None:
    if df is None or df.empty or len(df.columns) < 2:
        return None

    col1 = df.columns[0]
    col2 = df.columns[1]
    is_col2_numeric = pd.api.types.is_numeric_dtype(df[col2])
    n_rows = len(df)

    if is_col2_numeric and n_rows <= 25:
        fig = px.bar(df, x=col1, y=col2)
    elif is_col2_numeric and n_rows > 25:
        fig = px.line(df, x=col1, y=col2)
    elif pd.api.types.is_numeric_dtype(df[col1]) and pd.api.types.is_numeric_dtype(df[col2]):
        fig = px.scatter(df, x=col1, y=col2)
    else:
        return None

    fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=20),
        height=320,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    return fig.to_json()