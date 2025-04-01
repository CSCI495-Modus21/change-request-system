import panel as pn
import os
import sqlite3
from dotenv import load_dotenv
from transformers import T5Tokenizer, T5ForConditionalGeneration
import torch
import re

# Load environment variables
load_dotenv()
HF_TOKEN = os.getenv("HUGGING_FACE_TOKEN")
print("HF_TOKEN:", HF_TOKEN)
if not HF_TOKEN:
    raise ValueError("HF_TOKEN not found in .env file")

# Define model name
model_name = "mrm8488/t5-base-finetuned-wikiSQL"

# Load tokenizer and model
try:
    tokenizer = T5Tokenizer.from_pretrained(model_name, token=HF_TOKEN)
    model = T5ForConditionalGeneration.from_pretrained(model_name, token=HF_TOKEN)
except Exception as e:
    print(f"Error loading model: {e}")
    raise

# Set device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)

# Define valid columns and text columns based on the database schema
valid_columns = ["id", "category", "description"]
text_columns = ["category", "description"]

# Function to post-process the generated SQL
def post_process_sql(sql):
    # Replace 'table' with 'change_requests'
    sql = sql.replace("table", "change_requests")
    
    # Fix COUNT syntax
    sql = re.sub(r"COUNT\s+\w+", "COUNT(*)", sql, flags=re.IGNORECASE)
    
    # Quote unquoted values in WHERE clause (non-numeric)
    sql = re.sub(r"(\w+)\s*=\s*([a-zA-Z_]\w*)", r"\1 = '\2'", sql)
    
    # Use LIKE for Category column
    sql = re.sub(r"Category\s*=\s*'([^']+)'", r"Category LIKE '%\1%'", sql, flags=re.IGNORECASE)
    
    return sql

# Function to execute SQL query on the database
def execute_query(sql):
    try:
        conn = sqlite3.connect('../backend/database/change_requests.db')
        cursor = conn.cursor()
        cursor.execute(sql)
        results = cursor.fetchall()
        conn.close()
        return results
    except Exception as e:
        return f"Error executing query: {str(e)}"

# Define response generation function
def get_response(contents, user, instance):
    # Convert input to string
    prompt = contents if isinstance(contents, str) else " ".join(str(msg) for msg in contents)
    
    # Define the schema for the model (relevant columns)
    sql_prompt = f"translate to SQL: {prompt} | id, category, description"
    inputs = tokenizer(sql_prompt, return_tensors="pt", max_length=512, truncation=True)
    inputs = inputs.to(device)
    
    # Generate SQL
    outputs = model.generate(
        **inputs,
        max_new_tokens=200,
        do_sample=False,
        temperature=0.1,
        pad_token_id=tokenizer.eos_token_id
    )
    
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print("Generated SQL (raw):", response)
    
    # Post-process the SQL
    processed_sql = post_process_sql(response)
    print("Generated SQL (processed):", processed_sql)
    
    # Execute the query and format results
    results = execute_query(processed_sql)
    if isinstance(results, str):  # Error occurred
        return results
    
    # Check if it's a COUNT query or a SELECT query
    if "SELECT COUNT(*)" in processed_sql.upper():
        count = results[0][0]  # First row, first column
        return f"The count is {count}"
    else:
        # For SELECT queries, format the rows
        if not results:
            return "No results found."
        output = "Results:\n"
        for row in results:
            output += f"- ID: {row[0]}, Category: {row[1]}, Description: {row[2]}\n"
        return output

# Set up chat interface
chat_interface = pn.chat.ChatInterface(
    callback=get_response,
    user="You",
    show_clear=False,
    show_undo=False,
    width=600,
    height=400,
    placeholder_text="Enter a natural language query (e.g., 'Count all software related issues')",
    name="SQLCoder Chat"
)

# Define app layout
app = pn.Column(
    "# Natural Language to SQL Chat Interface",
    chat_interface,
    sizing_mode="stretch_width"
)

# Initialize Panel extension and serve the app
pn.extension()
app.servable()