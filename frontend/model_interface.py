import sqlite3
import pandas as pd
import requests
import os
import time
from dotenv import load_dotenv
import panel as pn

pn.extension(theme="dark", notifications=True)

load_dotenv()
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
if not TOGETHER_API_KEY:
    print("Error: TOGETHER_API_KEY not found.")
    exit(1)

def load_database(db_path="../backend/database/change_requests.db"):
    try:
        with sqlite3.connect(db_path) as conn:
            df = pd.read_sql_query("SELECT * FROM change_requests", conn)
            print(f"Loaded {len(df)} rows from {db_path}")
        return df
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return pd.DataFrame()

table = load_database()
if table.empty:
    print("Failed to load database. Exiting.")
    exit(1)

def convert_df_to_text(df):
    total_rows = len(df)
    columns = ", ".join(df.columns)
    data_text = f"Database: change_requests\nTotal Entries: {total_rows}\nColumns: {columns}\n\n"
    for i, (_, row) in enumerate(df.iterrows(), 1):
        data_text += f"Change Request {i}:\n"
        for col in df.columns:
            data_text += f"  **{col}**: {row[col]}\n"
        data_text += "\n"
    print(f"Generated database text with {total_rows} rows, length: {len(data_text)} characters")
    return data_text

database_text = convert_df_to_text(table)

def create_prompt(database_text, question):
    max_db_length = 26000  # ~7,000 tokens, leaving room for prompt overhead
    if len(database_text) > max_db_length:
        database_text = database_text[:max_db_length] + "... [truncated]"
        print(f"Warning: Database text truncated to {max_db_length} characters. Full length: {len(database_text)}")
    prompt = f"""You are a precise database assistant. Answer the user's question based on the provided database content. Follow these rules:
- Provide clear and concise answers using all available data.
- Use 'Total Entries' for total counts.
- For queries about 'issues', check the '**category**' field unless another field (e.g., '**description**') is specified.
- For lists or detailed responses, provide complete information.

Database content:
{database_text}

Question: {question}

Answer:"""
    return prompt

response_cache = {}
def generate_response(question):
    print(f"Generating response for question: {question}")
    if question in response_cache:
        print("Returning cached response.")
        return response_cache[question]
    
    start_time = time.time()
    prompt = create_prompt(database_text, question)
    print(f"Prompt length: {len(prompt)} characters")
    
    try:
        response = requests.post(
            "https://api.together.xyz/v1/completions",
            headers={
                "Authorization": f"Bearer {TOGETHER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
                "prompt": prompt,
                "max_tokens": 500,
                "temperature": 0.0,
                "top_p": 0.95,
                "stop": ["\n\n"]
            }
        )
        response.raise_for_status()
        result = response.json()
        answer = result.get("choices", [{}])[0].get("text", "").strip()
    except requests.RequestException as e:
        answer = f"API error: {e}"
        if hasattr(e.response, 'text'):
            print(f"Error details: {e.response.text}")
    
    api_time = time.time() - start_time
    print(f"API call: {api_time:.2f}s")
    print(f"Response: {answer}")
    
    response_cache[question] = answer
    return answer

def chat_callback(contents, user, instance):
    instance.placeholder_text = "*(generating response...)*"
    response = generate_response(contents)
    instance.placeholder_text = "*(thinking...)*"
    return response

chat_interface = pn.chat.ChatInterface(
    callback=chat_callback,
    user="You",
    show_clear=False,
    show_undo=False,
    height=600,
    placeholder_text="*(thinking...)*",
    name="Database Query Chat",
    sizing_mode="stretch_width"
)

layout = pn.Column(
    "# Database Query",
    chat_interface,
    sizing_mode="stretch_both"
)

def get_layout():
    return layout

if __name__ == "__main__":
    pn.serve(
        layout,
        show=True,
        title="Database Query Interface",
    )