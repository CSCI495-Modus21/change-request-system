import panel as pn
from panel.chat import ChatInterface
import pandas as pd
import requests

pn.extension(theme="dark", callback_exception='verbose')

def query_database(query_text):
    """Send a natural language query to the API and return the response."""
    url = "http://127.0.0.1:8000/query"
    try:
        response = requests.post(url, json={"query_text": query_text})
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API error: {response.text}"}
    except requests.RequestException as e:
        return {"error": f"Network error: {str(e)}"}

def query_callback(contents, user, instance):
    """Handle user input and display query results in the chat."""
    if not contents.strip():
        return
    
    result = query_database(contents)
    
    if "error" in result:
        instance.send(f"Error: {result['error']}")
    elif "count" in result:
        instance.send(f"Count: {result['count']}")
    elif "results" in result:
        if result["results"]:
            df = pd.DataFrame(result["results"])
            instance.send(df)
        else:
            instance.send("No results found.")

chat_interface = ChatInterface(callback=query_callback)
chat_interface.placeholder = "Type your query (e.g., 'How many hardware issues?' or 'List change requests for project Alpha')"

chat_interface.send(
    "Hi! I can help you query the change request database. Try something like 'How many hardware issues?' or 'List change requests for project Alpha'. What would you like to know?",
    user="System",
    respond=False
)

layout = pn.Column(
    pn.pane.Markdown("# Change Request Database Query"),
    chat_interface
)

def get_database_query_layout():
    """Return the layout for use in main.py."""
    return layout