# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# import sqlite3
# from sqlite3 import Error
# import requests
# import json
# from dotenv import load_dotenv
# import os

# load_dotenv()
# app = FastAPI()

# HF_API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-large"
# HF_API_TOKEN = os.getenv("HUGGING_FACE_TOKEN")

# if not HF_API_TOKEN:
#     raise ValueError("Hugging Face API token not found. Please set the HF_API_TOKEN environment variable.")

# class ChangeRequest(BaseModel):
#     project_name: str
#     change_number: str
#     requested_by: str
#     date_of_request: str
#     presented_to: str
#     change_name: str
#     description: str
#     reason: str
#     cost_items: list

# def create_connection():
#     """Create a connection to the SQLite database."""
#     try:
#         return sqlite3.connect('../database/change_requests.db')
#     except Error as e:
#         print(f"Database connection error: {e}")
#         return None

# def create_table():
#     """Create the change_requests table if it doesn’t exist."""
#     conn = create_connection()
#     if conn:
#         try:
#             c = conn.cursor()
#             c.execute('''CREATE TABLE IF NOT EXISTS change_requests
#                          (id INTEGER PRIMARY KEY AUTOINCREMENT,
#                           project_name TEXT,
#                           change_number TEXT,
#                           requested_by TEXT,
#                           date_of_request DATE,
#                           presented_to TEXT,
#                           change_name TEXT,
#                           description TEXT,
#                           reason TEXT,
#                           cost_items TEXT,
#                           category TEXT,
#                           timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
#             conn.commit()
#         except Error as e:
#             print(f"Table creation error: {e}")
#         finally:
#             conn.close()

# create_table()

# def categorize_description(description: str) -> str:
#     """Simple categorization based on description content."""
#     description = description.lower()
#     if "hardware" in description:
#         return "hardware issue"
#     elif "software" in description:
#         return "software issue"
#     elif "personnel" in description or "staff" in description:
#         return "personnel issue"
#     return "other"

# @app.post("/change_requests")
# def create_change_request(change_request: ChangeRequest):
#     """Create a new change request with categorization."""
#     category = categorize_description(change_request.description)
#     cost_items_json = json.dumps(change_request.cost_items)

#     conn = create_connection()
#     if not conn:
#         raise HTTPException(status_code=500, detail="Database connection error")
#     try:
#         c = conn.cursor()
#         c.execute(
#             "INSERT INTO change_requests (project_name, change_number, requested_by, date_of_request, presented_to, change_name, description, reason, cost_items, category) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
#             (change_request.project_name, change_request.change_number, change_request.requested_by, change_request.date_of_request, change_request.presented_to, change_request.change_name, change_request.description, change_request.reason, cost_items_json, category)
#         )
#         conn.commit()
#         return {"message": "Change request created", "id": c.lastrowid}
#     except Error as e:
#         raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
#     finally:
#         conn.close()


from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
from sqlite3 import Error
import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()
app = FastAPI()

HF_API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-large"
HF_API_TOKEN = os.getenv("HUGGING_FACE_TOKEN")

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
    """Categorize the description using Flan-T5 via Hugging Face Inference API."""
    categories = ["hardware issue", "software issue", "personnel issue", "other"]
    prompt = f"Classify the following description into one of these categories: {', '.join(categories)}. Description: {description}"
    
    headers = {
        "Authorization": f"Bearer {HF_API_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "inputs": prompt,
        "parameters": {"max_length": 50}
    }
    
    try:
        response = requests.post(HF_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        
        # Extract the generated text (assuming Flan-T5 returns a single string)
        category = result[0]["generated_text"].strip()
        
        # Ensure the category is valid; fallback to 'other' if not in the list
        if category not in categories:
            return "other"
        return category
    except requests.exceptions.RequestException as e:
        print(f"Error querying Hugging Face API: {e}")
        return "other"  # Fallback in case of API failure

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