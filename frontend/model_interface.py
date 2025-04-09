# import sqlite3
# import pandas as pd
# from transformers import TapasTokenizer, TapasForQuestionAnswering
# from dotenv import load_dotenv
# import os
# import panel as pn

# pn.extension(theme="dark", notifications=True)

# load_dotenv()
# HF_TOKEN = os.getenv("HUGGING_FACE_TOKEN")

# model_name = "google/tapas-base-finetuned-wtq"
# tokenizer = TapasTokenizer.from_pretrained(model_name)                     
# model = TapasForQuestionAnswering.from_pretrained(model_name)

# conn = sqlite3.connect('../backend/database/change_requests.db')
# table = pd.read_sql_query("SELECT * FROM change_requests", conn)
# conn.close()

# def query_database(natural_language_query, table):
#     table = table.astype(str).fillna('')
#     inputs = tokenizer(table=table, queries=natural_language_query, padding="max_length", return_tensors="pt")
#     outputs = model(**inputs)
#     answer_coordinates, aggregation_labels = tokenizer.convert_logits_to_predictions(
#         inputs, outputs.logits.detach(), outputs.logits_aggregation.detach()
#     )
#     return format_answer(natural_language_query, answer_coordinates, aggregation_labels, table)

# def format_answer(query, answer_coordinates, aggregation_labels, table):
#     if not answer_coordinates:
#         return "No answer found."
    
#     coordinates = answer_coordinates[0]  # e.g., [(0, 2), (1, 2)]  
#     agg_label = aggregation_labels[0]    # e.g., 3
    
#     if "how many" in query.lower():
#         unique_rows = set(row for row, _ in coordinates)
#         return f"There are {len(unique_rows)} items."
#     elif agg_label == 0:  
#         values = [table.iloc[row, col] for row, col in coordinates]
#         return ", ".join(values)
#     elif agg_label == 1:  
#         values = [float(table.iloc[row, col]) for row, col in coordinates]
#         return str(sum(values))
#     elif agg_label == 2:
#         unique_rows = set(row for row, _ in coordinates)
#         return str(len(unique_rows))
#     elif agg_label == 3:  
#         values = [float(table.iloc[row, col]) for row, col in coordinates]
#         return str(sum(values) / len(values) if values else 0)
#     else:
#         return "Unknown aggregation"

# def chat_callback(contents, user, instance):
#     response = query_database(contents, table)
#     return response

# chat_interface = pn.chat.ChatInterface(
#     callback=chat_callback,
#     user="You",
#     show_clear=False,
#     show_undo=False,
#     width=600,
#     height=400,
#     placeholder_text="Ask a question (e.g., 'How many hardware-related issues are there?')",
#     name="Database Query Chat"
# )

# layout = pn.Column(
#     "# Database Query",
#     chat_interface,
#     sizing_mode="stretch_width"
# )

# def get_layout():
#     return layout



import sqlite3
import pandas as pd
import panel as pn
import matplotlib.pyplot as plt
import seaborn as sns
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
from datetime import datetime

# Initialize Panel extension
pn.extension()

# Step 1: Connect to the SQL database
conn = sqlite3.connect("../backend/database/change_requests.db")  # Replace with your database path
cursor = conn.cursor()

# Step 2: Load the Text-to-SQL Model
# Using defog/sqlcoder (you may need to adjust based on the specific model variant)
model_name = "defog/sqlcoder-7b"  # Replace with the exact model name if different
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)
sql_generator = pipeline("text2text-generation", model=model, tokenizer=tokenizer)

# Database schema for the model to understand the structure
schema = """
Table: change_requests
Columns:
- id (integer)
- project_name (text)
- change_number (integer)
- requested_by (text)
- date_of_request (text)
- presented_to (text)
- change_name (text)
- description (text)
- reason (text)
- cost_items (text)
- category (text)
- timestamp (text)
"""

# Step 3: Query Processor
def process_query(user_input):
    # Step 3.1: Generate SQL query using the text-to-SQL model
    prompt = f"""
    ### Database Schema
    {schema}

    ### Question
    {user_input}

    ### Task
    Generate a SQL query to answer the question based on the schema.
    """
    generated_sql = sql_generator(prompt, max_length=200)[0]["generated_text"]

    # Step 3.2: Execute the SQL query
    try:
        df = pd.read_sql_query(generated_sql, conn)
    except Exception as e:
        return f"Error executing SQL query: {str(e)}", None

    # Step 3.3: Determine the intent (text response or visualization)
    response = ""
    plot = None

    # Check for visualization requests
    if "bar plot" in user_input.lower():
        # Assume the SQL query returns columns suitable for a bar plot (e.g., category and count)
        if len(df.columns) >= 2:
            plt.figure(figsize=(8, 6))
            sns.barplot(x=df.columns[1], y=df.columns[0], data=df)
            plt.title("Bar Plot")
            plt.xlabel(df.columns[1])
            plt.ylabel(df.columns[0])
            plot = plt.gcf()
            plt.close()
        response = "Here’s the bar plot you requested."
    elif "line plot" in user_input.lower():
        # Assume the SQL query returns columns suitable for a line plot (e.g., date and count)
        if len(df.columns) >= 2:
            plt.figure(figsize=(8, 6))
            df[df.columns[0]] = pd.to_datetime(df[df.columns[0]])
            plt.plot(df[df.columns[0]], df[df.columns[1]], marker="o")
            plt.title("Line Plot")
            plt.xlabel(df.columns[0])
            plt.ylabel(df.columns[1])
            plt.xticks(rotation=45)
            plot = plt.gcf()
            plt.close()
        response = "Here’s the line plot you requested."
    else:
        # For non-visualization queries, return the result as text
        if not df.empty:
            response = df.to_string(index=False)
        else:
            response = "No results found."

    return response, plot

# Step 4: Panel Frontend
chat_input = pn.widgets.TextInput(placeholder="Ask about your change requests...")
chat_output = pn.Column()

def update_chat(event):
    user_input = chat_input.value
    if user_input:
        response, plot = process_query(user_input)
        chat_output.append(f"**You:** {user_input}")
        chat_output.append(f"**Bot:** {response}")
        if plot:
            chat_output.append(pn.pane.Matplotlib(plot, tight=True))
        chat_input.value = ""

chat_input.param.watch(update_chat, "value")

# Layout
app = pn.Column(
    pn.pane.Markdown("# Change Request Chatbot"),
    pn.pane.Markdown("Ask questions about your database, like 'how many requests made by John?' or 'make me a bar plot representing the distribution of each type of change request'."),
    chat_input,
    chat_output
)

# Serve the app
app.servable()

# Step 5: Clean up
# conn.close()  # Uncomment when done