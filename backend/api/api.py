from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
from sqlite3 import Error
import requests
import os
import re
import json
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

HF_API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-base"
HF_API_TOKEN = os.getenv("HUGGING_FACE_TOKEN")
print(f"HF_API_TOKEN: {HF_API_TOKEN}")

if not HF_API_TOKEN:
    raise ValueError("Hugging Face API token not found. Please set the HF_API_TOKEN environment variable.")

class ChangeRequest(BaseModel):
    project_name: str
    change_number: str
    requested_by: str
    date_of_request: str 
    presented_to: str
    change_name: str
    description: str
    reason: str
    cost_items: list  

class Query(BaseModel):
    query_text: str

def create_connection():
    """Create a connection to the SQLite database."""
    try:
        return sqlite3.connect('../database/change_requests.db')
    except Error as e:
        print(f"Database connection error: {e}")
        return None

def create_table():
    """Create the change_requests table if it doesn’t exist."""
    conn = create_connection()
    if conn:
        try:
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS change_requests
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          project_name TEXT,
                          change_number TEXT,
                          requested_by TEXT,
                          date_of_request DATE,
                          presented_to TEXT,
                          change_name TEXT,
                          description TEXT,
                          reason TEXT,
                          cost_items TEXT,  -- Stored as JSON string
                          category TEXT,
                          timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
            conn.commit()
        except Error as e:
            print(f"Table creation error: {e}")
        finally:
            conn.close()

create_table()

def query_hf_api(prompt: str) -> str:
    """Send a prompt to the Hugging Face Inference API and return the response."""
    headers = {
        "Authorization": f"Bearer {HF_API_TOKEN}",  # Ensure HF_API_TOKEN is set
        "Content-Type": "application/json"
    }
    # Format the prompt for categorization
    full_prompt = (
        f"Categorize the following change request description into one of these categories: "
        f"hardware issue, software issue, personnel issue, or other. Return only the category name.\n\n"
        f"Description: {prompt}\n\nCategory:"
    )
    payload = {
        "inputs": full_prompt,
        "parameters": {"max_length": 50}  # Use max_length for T5 models
    }
    response = requests.post(HF_API_URL, headers=headers, json=payload)
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail=f"Hugging Face API error: {response.text}")
    # Extract the generated text (T5 output format)
    return response.json()[0]["generated_text"].strip()

@app.post("/change_requests")
def create_change_request(change_request: ChangeRequest):
    """Create a new change request and categorize it."""
    prompt = (f"Categorize the following change request description into one of these categories: "
              f"hardware issue, software issue, personnel issue, or other. Return only the category name.\n\n"
              f"Description: {change_request.description}\n\nCategory:")
    
    raw_response = query_hf_api(prompt).lower().strip()
    response_lines = raw_response.split('\n')
    category = response_lines[-1].strip()
    
    valid_categories = {"hardware issue", "software issue", "personnel issue", "other"}
    if category not in valid_categories:
        category = "other" 

    cost_items_json = json.dumps(change_request.cost_items)

    conn = create_connection()
    if conn:
        try:
            c = conn.cursor()
            c.execute("INSERT INTO change_requests (project_name, change_number, requested_by, date_of_request, presented_to, change_name, description, reason, cost_items, category) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                      (change_request.project_name, change_request.change_number, change_request.requested_by, change_request.date_of_request, change_request.presented_to, change_request.change_name, change_request.description, change_request.reason, cost_items_json, category))
            conn.commit()
            return {"message": "Change request created", "id": c.lastrowid}
        except Error as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        finally:
            conn.close()
    else:
        raise HTTPException(status_code=500, detail="Database connection error")

@app.post("/query")
def process_query(query: dict):
    prompt = (
        f"Interpret this query and return the query type (count or list) and category (hardware issue, software issue, personnel issue, or other). "
        f"If the query asks for all categories, use 'all'.\n\n"
        f"Example:\n"
        f"Query: List all change requests\n"
        f"Response: query_type: list, category: all\n\n"
        f"Query: {query['query_text']}\n"
        f"Response format: query_type: <type>, category: <category>"
    )
    response_text = query_hf_api(prompt) 

    query_type_match = re.search(r"query_type:\s*(\w+)", response_text, re.IGNORECASE)
    category_match = re.search(r"category:\s*([\w\s]+)", response_text, re.IGNORECASE)

    if not query_type_match or not category_match:
        raise HTTPException(status_code=400, detail="Could not interpret query")

    query_type = query_type_match.group(1).lower()
    category = category_match.group(1).lower().strip()

    conn = create_connection()
    if conn:
        try:
            c = conn.cursor()
            if category == "all":
                if query_type == "count":
                    c.execute("SELECT COUNT(*) FROM change_requests")
                    count = c.fetchone()[0]
                    return {"count": count}
                elif query_type == "list":
                    c.execute("SELECT * FROM change_requests")
                    columns = [col[0] for col in c.description]
                    results = [dict(zip(columns, row)) for row in c.fetchall()]
                    return {"results": results}
            else:
                if query_type == "count":
                    c.execute("SELECT COUNT(*) FROM change_requests WHERE category = ?", (category,))
                    count = c.fetchone()[0]
                    return {"count": count}
                elif query_type == "list":
                    c.execute("SELECT * FROM change_requests WHERE category = ?", (category,))
                    columns = [col[0] for col in c.description]
                    results = [dict(zip(columns, row)) for row in c.fetchall()]
                    return {"results": results}
        finally:
            conn.close()
    else:
        raise HTTPException(status_code=500, detail="Database connection error")