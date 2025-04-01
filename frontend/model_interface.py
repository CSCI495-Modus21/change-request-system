import sqlite3
import pandas as pd
from transformers import TapasTokenizer, TapasForQuestionAnswering
from dotenv import load_dotenv
import os
import panel as pn

pn.extension(theme="dark", notifications=True)

load_dotenv()
HF_TOKEN = os.getenv("HUGGING_FACE_TOKEN")

model_name = "google/tapas-base-finetuned-wtq"
tokenizer = TapasTokenizer.from_pretrained(model_name)                     
model = TapasForQuestionAnswering.from_pretrained(model_name)

conn = sqlite3.connect('../backend/database/change_requests.db')
table = pd.read_sql_query("SELECT * FROM change_requests", conn)
print(table)  
conn.close()

def query_database(natural_language_query, table):
    table = table.astype(str).fillna('')
    inputs = tokenizer(table=table, queries=natural_language_query, padding="max_length", return_tensors="pt")
    outputs = model(**inputs)
    answer_coordinates, aggregation_labels = tokenizer.convert_logits_to_predictions(
        inputs, outputs.logits.detach(), outputs.logits_aggregation.detach()
    )
    return format_answer(natural_language_query, answer_coordinates, aggregation_labels, table)

def format_answer(query, answer_coordinates, aggregation_labels, table):
    if not answer_coordinates:
        return "No answer found."
    
    coordinates = answer_coordinates[0]  # e.g., [(0, 2), (1, 2)]  
    agg_label = aggregation_labels[0]    # e.g., 3
    
    if "how many" in query.lower():
        unique_rows = set(row for row, _ in coordinates)
        return f"There are {len(unique_rows)} items."
    elif agg_label == 0:  
        values = [table.iloc[row, col] for row, col in coordinates]
        return ", ".join(values)
    elif agg_label == 1:  
        values = [float(table.iloc[row, col]) for row, col in coordinates]
        return str(sum(values))
    elif agg_label == 2:
        unique_rows = set(row for row, _ in coordinates)
        return str(len(unique_rows))
    elif agg_label == 3:  
        values = [float(table.iloc[row, col]) for row, col in coordinates]
        return str(sum(values) / len(values) if values else 0)
    else:
        return "Unknown aggregation"

def chat_callback(contents, user, instance):
    response = query_database(contents, table)
    return response

chat_interface = pn.chat.ChatInterface(
    callback=chat_callback,
    user="You",
    show_clear=False,
    show_undo=False,
    width=600,
    height=400,
    placeholder_text="Ask a question (e.g., 'How many hardware-related issues are there?')",
    name="Database Query Chat"
)

layout = pn.Column(
    "# Database Query",
    chat_interface,
    sizing_mode="stretch_width"
)

def get_layout():
    return layout