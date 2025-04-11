from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
from sqlite3 import Error
import json
from dotenv import load_dotenv
import os
import requests

load_dotenv()
app = FastAPI()
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

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
                          cost_items TEXT,
                          category TEXT,
                          timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
            conn.commit()
        except Error as e:
            print(f"Table creation error: {e}")
        finally:
            conn.close()

create_table()

def categorize_description(description: str) -> str:
    """Categorize the description using Together AI API."""
    categories = ["hardware issue", "software issue", "personnel issue", "other"]
    prompt = (
        f"Classify the following description the best that you can. Here are some example categories: "
        f"hardware issue, software issue, personnel issue, other. "
        f"You are not limited to the list. "
        f"Description: {description} Category:"
    )
    
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
                "max_tokens": 10,
                "temperature": 0.0,
                "stop": ["\n"]
            }
        )
        response.raise_for_status()
        result = response.json()
        generated_text = result.get("choices", [{}])[0].get("text", "").strip().lower()
        
        for category in categories:
            if category in generated_text:
                print(f"Description: '{description}'")
                print(f"Predicted Category: '{category}'")
                return category
        print(f"Description: '{description}'")
        print(f"Predicted Category: 'other' (no match found)")
        return "other"
    except requests.RequestException as e:
        print(f"API error: {e}")
        print(f"Description: '{description}'")
        print(f"Predicted Category: 'other' (API error)")
        return "other"

@app.post("/change_requests")
def create_change_request(change_request: ChangeRequest):
    """Create a new change request with automated categorization."""
    category = categorize_description(change_request.description)
    cost_items_json = json.dumps(change_request.cost_items)

    conn = create_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection error")
    try:
        c = conn.cursor()
        c.execute(
            "INSERT INTO change_requests (project_name, change_number, requested_by, date_of_request, presented_to, change_name, description, reason, cost_items, category) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (change_request.project_name, change_request.change_number, change_request.requested_by, change_request.date_of_request, change_request.presented_to, change_request.change_name, change_request.description, change_request.reason, cost_items_json, category)
        )
        conn.commit()
        return {"message": "Change request created", "id": c.lastrowid, "category": category}
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        conn.close()