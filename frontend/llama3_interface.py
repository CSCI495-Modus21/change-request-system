import panel as pn
from panel.chat import ChatInterface
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import re
import requests


matplotlib.use('agg')
pn.extension(theme="dark")

last_df = None

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


def parse_query(message):
    """Parse the user's natural language query using a cloud-based Llama 3 API."""
    external_api_url = "https://api.example.com/llama3/generate"  # Replace with actual API URL
    payload = {
        "prompt": f"Extract query parameters from this: '{message}'. Return a JSON with fields like project_name, requested_by, date_of_request__gte, date_of_request__lte.",
        "max_tokens": 100
    }
    try:
        response = requests.post(external_api_url, json=payload, headers={"Authorization": "Bearer 4a44a1a6-98a1-4c2c-b010-068703951eed"})
        if response.status_code == 200:
            params = response.json().get("response", {})
            return params if isinstance(params, dict) else {}
        else:
            print(f"API Error: {response.text}")
            return {}
    except Exception as e:
        print(f"Error calling Llama 3 API: {str(e)}")
        return {}

def filter_simulated_data(params):
    """Filter the simulated data based on query parameters."""
    df = pd.DataFrame(SIMULATED_DATA)
    
    if 'project_name' in params:
        df = df[df['project_name'].str.lower() == params['project_name']]
    if 'requested_by' in params:
        df = df[df['requested_by'].str.lower() == params['requested_by']]
    if 'date_of_request__gte' in params:
        df = df[df['date_of_request'] >= params['date_of_request__gte']]
    if 'date_of_request__lte' in params:
        df = df[df['date_of_request'] <= params['date_of_request__lte']]
    
    return df

def extract_plot_type(message):
    """Determine the type of plot the user wants from their message."""
    message = message.lower()
    if 'per project' in message:
        return 'Change Requests per Project'
    elif 'total cost increase' in message:
        return 'Total Cost Increase'
    return None

def generate_plot(df, plot_type):
    """Generate a Matplotlib plot based on the dataframe and requested plot type."""
    plt.style.use('dark_background')
    
    if plot_type == 'Change Requests per Project':
        plot_df = df['project_name'].value_counts()
        fig, ax = plt.subplots()
        plot_df.plot(kind='bar', ax=ax)
        ax.set_title("Change Requests per Project")
        ax.set_xlabel("Project Name")
        ax.set_ylabel("Number of Requests")
        return fig
    
    elif plot_type == 'Total Cost Increase':
        df['total_cost_increase'] = df['cost_items'].apply(
            lambda items: sum(item['dollars_increase'] - item['dollars_reduction'] for item in items)
        )
        fig, ax = plt.subplots()
        df.plot(x='change_number', y='total_cost_increase', kind='bar', ax=ax)
        ax.set_title("Total Cost Increase per Change Request")
        ax.set_xlabel("Change Number")
        ax.set_ylabel("Total Cost Increase ($)")
        return fig
    
    return None

def query_callback(contents, user, instance):
    """Handle user messages: process queries, return results, and manage plot requests."""
    global last_df
    message = contents.strip().lower()
    
    if message == "test me!":
        df = pd.DataFrame(SIMULATED_DATA)
        last_df = df
        instance.send("Here's some simulated test data:")
        instance.send(df)
        fig = generate_plot(df, 'Change Requests per Project')
        instance.send(fig)
        return
    
    if re.search(r'\b(show|list|find|get)\b', message) and 'change request' in message:
        params = parse_query(message)
        df = filter_simulated_data(params)
        if not df.empty:
            last_df = df
            instance.send(df)
            instance.send("Would you like to see a plot of this data? (e.g., 'plot change requests per project')")
        else:
            instance.send("No matching change requests found in the simulated data.")
        return
    
    elif re.search(r'\b(plot|chart|graph|yes)\b', message):
        if last_df is not None:
            df = last_df
            plot_type = extract_plot_type(message)
            if plot_type:
                fig = generate_plot(df, plot_type)
                if fig:
                    instance.send(fig)
                else:
                    instance.send("Sorry, I couldn’t generate that plot type.")
            else:
                fig = generate_plot(df, 'Change Requests per Project')
                instance.send(fig)
        else:
            instance.send("Please run a query first so I have some data to plot!")
        return
    
    else:
        instance.send("I didn’t understand that. Try asking for change requests (e.g., 'Show me change requests for project Alpha') or a plot.")

chat_interface = ChatInterface(callback=query_callback)

chat_interface.placeholder = "Type your query here (e.g., 'Show me change requests for project Alpha' or 'Test me!')"

chat_interface.send(
    "Hi! I’m here to help you query change requests. Type 'Test me!' for a demo with simulated data and a plot, or use a natural language query like 'Show me all change requests for project Alpha' or 'List change requests by John Doe after 2023-01-01'. Once you see results, you can request a plot, like 'plot change requests per project'. What would you like to do?",
    user="System",
    respond=False
)

layout = pn.Column(
    pn.pane.Markdown("# Change Request Database Query"),
    chat_interface
)

def get_database_query_layout():
    """Return the layout for use in the main application."""
    return layout