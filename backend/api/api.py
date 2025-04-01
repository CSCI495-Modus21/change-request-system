from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
from sqlite3 import Error
import json
from dotenv import load_dotenv
import os
from transformers import pipeline

load_dotenv()
app = FastAPI()
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli", token=os.getenv("HUGGING_FACE_TOKEN"))

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
    """Categorize the description using BART-MNLI for zero-shot classification."""
    categories = ["hardware issue", "software issue", "personnel issue", "other"]
    result = classifier(description, candidate_labels=categories)
    category = result["labels"][0]  # The highest-scoring label
    score = result["scores"][0]     # Confidence score for the top label
    
    print(f"Description: '{description}'")
    print(f"Predicted Category: '{category}' with score: {score}")
    
    return category

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