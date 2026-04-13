import anthropic
import os

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def generate_sql(question: str, schema: dict) -> str:
    schema_text = "\n".join(
        [f"- {col['name']} ({col['type']}, e.g. {col['sample']})"
         for col in schema["columns"]]
    )
   
    
    prompt = f"""You are a SQL expert. The user has a table called `uploaded_data` with these columns:
{schema_text}

Total rows: {schema["row_count"]}

The user asks: "{question}"

Write a single SQL SELECT query to answer this. Use DuckDB SQL syntax.
Return ONLY the SQL query, nothing else. No explanation, no markdown, just the raw SQL."""

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text.strip()


def generate_insight(question: str, result_preview: str) -> str:
    prompt = f"""The user asked: "{question}"
The query returned this data:
{result_preview}

Write exactly 2 sentences explaining what this result means for the business. Be specific, not generic."""
    
    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=150,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text.strip()

