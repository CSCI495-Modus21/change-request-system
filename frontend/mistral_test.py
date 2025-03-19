import panel as pn
from panel.chat import ChatInterface
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import re
import subprocess

# Set Matplotlib backend to 'agg' before any plotting
matplotlib.use('agg')

# Initialize Panel extension with dark theme
pn.extension(theme="dark")

# Global variable to store the last DataFrame
last_df = None

# Simulated database of change requests
SIMULATED_DATA = [
    {
        "project_name": "Alpha",
        "change_number": "CR-001",
        "requested_by": "Alice Smith",
        "date_of_request": "2023-01-01",
        "cost_items": [
            {"item_description": "Development", "hours_reduction": 0, "hours_increase": 10, "dollars_reduction": 0, "dollars_increase": 500}
        ]
    },
    {
        "project_name": "Alpha",
        "change_number": "CR-002",
        "requested_by": "Bob Jones",
        "date_of_request": "2023-02-01",
        "cost_items": [
            {"item_description": "Testing", "hours_reduction": 0, "hours_increase": 5, "dollars_reduction": 0, "dollars_increase": 250}
        ]
    },
    {
        "project_name": "Beta",
        "change_number": "CR-003",
        "requested_by": "Charlie Brown",
        "date_of_request": "2023-03-01",
        "cost_items": [
            {"item_description": "Design", "hours_reduction": 0, "hours_increase": 8, "dollars_reduction": 0, "dollars_increase": 400}
        ]
    }
]

def query_mistral(message):
    """Send user input to Mistral via Ollama and return the response."""
    try:
        process = subprocess.run(
            ["ollama", "run", "mistral", message],
            capture_output=True,
            text=True
        )
        return process.stdout.strip()
    except Exception as e:
        return f"Error: {str(e)}"

def query_callback(contents, user, instance):
    """Handle user messages with Mistral AI."""
    global last_df
    message = contents.strip().lower()
    
    if message == "test me!":
        df = pd.DataFrame(SIMULATED_DATA)
        last_df = df
        instance.send("Here's some simulated test data:")
        instance.send(df)
        return
    
    if re.search(r'\b(show|list|find|get)\b', message) and 'change request' in message:
        df = pd.DataFrame(SIMULATED_DATA)
        last_df = df
        instance.send(df)
        return
    
    response = query_mistral(message)
    instance.send(response)

# Create the chat interface
chat_interface = ChatInterface(callback=query_callback)

# Customize the input widget's placeholder
chat_interface.placeholder = "Ask anything about change requests or AI!"

# Add a welcome message
chat_interface.send(
    "Hi! I’m an AI-powered assistant using Mistral. You can ask about change requests, project data, or general AI questions!", 
    user="System",
    respond=False
)

# Define the layout
layout = pn.Column(
    pn.pane.Markdown("# AI-Powered Change Request Chatbot"),
    chat_interface
)

def get_database_query_layout():
    """Return the chatbot layout."""
    return layout

layout.servable()
