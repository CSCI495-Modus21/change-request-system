import panel as pn
import pandas as pd
import matplotlib.pyplot as plt
import pdfplumber
import requests
import os
from io import BytesIO

pn.extension()

database_api_url = "http://localhost:8000/api/change_requests/"

def call_llama_api(prompt): # FIXME: Placeholder for Llama 3 API call
    return f"Summary based on prompt: {prompt}"

def scrape_pdf(file): # FIXME: # Placeholder for PDF scraping. Simulate extracting data from PDF.
    data = {
        "project_name": "Sample Project",
        "change_number": "CR-001",
        "requested_by": "John Doe",
        "date_of_request": "2023-10-01",
        "presented_to": "Jane Smith",
        "change_name": "Update API",
        "description": "Update API endpoints",
        "reason": "Customer request",
        "effect_on_deliverables": "Will delay deliverable A",
        "effect_on_organization": "Requires training",
        "effect_on_schedule": "Adds 2 weeks",
        "effect_of_not_approving": "Customer dissatisfaction",
        "reason_for_rejection": "",
        "cost_items": [
            {"item_description": "Analysis", "hours_reduction": 0, "hours_increase": 10, "dollars_reduction": 0.00, "dollars_increase": 500.00},
            {"item_description": "Development", "hours_reduction": 0, "hours_increase": 20, "dollars_reduction": 0.00, "dollars_increase": 1000.00}
        ]
    }
    return data


# Main change request fields
project_name = pn.widgets.TextInput(name="Project Name", placeholder="Enter project name")
change_number = pn.widgets.TextInput(name="Change Number", placeholder="Enter change number")
requested_by = pn.widgets.TextInput(name="Requested By", placeholder="Enter requester name")
date_of_request = pn.widgets.DatePicker(name="Date of Request")
presented_to = pn.widgets.TextInput(name="Presented To", placeholder="Enter presented to")
change_name = pn.widgets.TextInput(name="Change Name", placeholder="Enter change name")
description = pn.widgets.TextAreaInput(name="Description of Change", placeholder="Enter description", height=100)
reason = pn.widgets.TextAreaInput(name="Reason for Change", placeholder="Enter reason", height=100)
effect_on_deliverables = pn.widgets.TextAreaInput(name="Effect on Deliverables", placeholder="Enter effect on deliverables", height=100)
effect_on_organization = pn.widgets.TextAreaInput(name="Effect on Organization", placeholder="Enter effect on organization", height=100)
effect_on_schedule = pn.widgets.TextAreaInput(name="Effect on Schedule", placeholder="Enter effect on schedule", height=100)
effect_of_not_approving = pn.widgets.TextAreaInput(name="Effect of NOT Approving", placeholder="Enter effect of not approving", height=100)
reason_for_rejection = pn.widgets.TextAreaInput(name="Reason for Rejection", placeholder="Enter reason for rejection (if applicable)", height=100)

# Cost items management
cost_items_column = pn.Column()

def add_cost_item():
    item_description = pn.widgets.TextInput(name="Item Description", placeholder="Enter item description")
    hours_reduction = pn.widgets.IntInput(name="Hours Reduction", value=0, start=0)
    hours_increase = pn.widgets.IntInput(name="Hours Increase", value=0, start=0)
    dollars_reduction = pn.widgets.FloatInput(name="Dollars Reduction", value=0.0, start=0.0)
    dollars_increase = pn.widgets.FloatInput(name="Dollars Increase", value=0.0, start=0.0)
    cost_item_row = pn.Row(item_description, hours_reduction, hours_increase, dollars_reduction, dollars_increase)
    cost_items_column.append(cost_item_row)

add_cost_item_button = pn.widgets.Button(name="Add Cost Item", button_type="primary")
add_cost_item_button.on_click(lambda event: add_cost_item())

# Initialize with one cost item row
add_cost_item()

file_input = pn.widgets.FileInput(accept=".pdf")
scrape_button = pn.widgets.Button(name="Scrape PDF", button_type="primary")

def on_scrape_click(event):
    if file_input.value:
        file = BytesIO(file_input.value)
        data = scrape_pdf(file)
        project_name.value = data.get('project_name', '')
        change_number.value = data.get('change_number', '')
        requested_by.value = data.get('requested_by', '')
        date_of_request.value = pd.to_datetime(data.get('date_of_request', None))
        presented_to.value = data.get('presented_to', '')
        change_name.value = data.get('change_name', '')
        description.value = data.get('description', '')
        reason.value = data.get('reason', '')
        effect_on_deliverables.value = data.get('effect_on_deliverables', '')
        effect_on_organization.value = data.get('effect_on_organization', '')
        effect_on_schedule.value = data.get('effect_on_schedule', '')
        effect_of_not_approving.value = data.get('effect_of_not_approving', '')
        reason_for_rejection.value = data.get('reason_for_rejection', '')
        # Clear existing cost items and add new ones
        cost_items_column.clear()
        for cost_item in data.get('cost_items', []):
            add_cost_item()
            cost_items_column[-1][0].value = cost_item['item_description']
            cost_items_column[-1][1].value = cost_item['hours_reduction']
            cost_items_column[-1][2].value = cost_item['hours_increase']
            cost_items_column[-1][3].value = cost_item['dollars_reduction']
            cost_items_column[-1][4].value = cost_item['dollars_increase']
        message_pane.object = "PDF scraped successfully. Please review and edit if necessary."

scrape_button.on_click(on_scrape_click)

submit_button = pn.widgets.Button(name="Submit Change Request", button_type="success")
message_pane = pn.pane.Markdown("", width=500)

def on_submit_click(event):
    submit_button.loading = True
    try:
        change_request_data = {
            "project_name": project_name.value,
            "change_number": change_number.value,
            "requested_by": requested_by.value,
            "date_of_request": date_of_request.value.isoformat() if date_of_request.value else None,
            "presented_to": presented_to.value,
            "change_name": change_name.value,
            "description": description.value,
            "reason": reason.value,
            "effect_on_deliverables": effect_on_deliverables.value,
            "effect_on_organization": effect_on_organization.value,
            "effect_on_schedule": effect_on_schedule.value,
            "effect_of_not_approving": effect_of_not_approving.value,
            "reason_for_rejection": reason_for_rejection.value,
            "cost_items": []
        }
        for cost_item_row in cost_items_column:
            cost_item = {
                "item_description": cost_item_row[0].value,
                "hours_reduction": cost_item_row[1].value,
                "hours_increase": cost_item_row[2].value,
                "dollars_reduction": cost_item_row[3].value,
                "dollars_increase": cost_item_row[4].value,
            }
            change_request_data["cost_items"].append(cost_item)
        response = requests.post(database_api_url, json=change_request_data)
        if response.status_code == 201:
            message_pane.object = "Change request submitted successfully."
        else:
            message_pane.object = f"Error submitting change request: {response.text}"
    except Exception as e:
        message_pane.object = f"Error: {str(e)}"
    finally:
        submit_button.loading = False

submit_button.on_click(on_submit_click)

# Query filters
project_filter = pn.widgets.TextInput(name="Project Name Filter", placeholder="Enter project name")
requester_filter = pn.widgets.TextInput(name="Requested By Filter", placeholder="Enter requester name")
date_start = pn.widgets.DatePicker(name="Start Date")
date_end = pn.widgets.DatePicker(name="End Date")
keywords = pn.widgets.TextInput(name="Keywords", placeholder="Enter keywords for description search")
natural_query = pn.widgets.TextAreaInput(name="Natural Language Query", placeholder="Enter query (e.g., 'all change requests involving hardware')", height=100)
query_button = pn.widgets.Button(name="Query Database", button_type="primary")
results_pane = pn.pane.DataFrame()
plot_select = pn.widgets.Select(name="Plot Type", options=["None", "Change Requests per Project", "Total Cost Increase"])
plot_pane = pn.pane.Matplotlib()

def on_query_click(event):
    query_button.loading = True
    try:
        params = {}
        if project_filter.value:
            params['project_name'] = project_filter.value
        if requester_filter.value:
            params['requested_by'] = requester_filter.value
        if date_start.value:
            params['date_of_request__gte'] = date_start.value.isoformat()
        if date_end.value:
            params['date_of_request__lte'] = date_end.value.isoformat()
        if keywords.value:
            params['keywords'] = keywords.value
        response = requests.get(database_api_url, params=params)
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data)
            results_pane.object = df
            # Generate plot if selected
            if plot_select.value != "None":
                plt.clf()  # Clear previous plot
                if plot_select.value == "Change Requests per Project":
                    plot_df = df['project_name'].value_counts()
                    fig, ax = plt.subplots()
                    plot_df.plot(kind='bar', ax=ax)
                    ax.set_title("Change Requests per Project")
                    ax.set_xlabel("Project Name")
                    ax.set_ylabel("Number of Requests")
                    plot_pane.object = fig
                elif plot_select.value == "Total Cost Increase":
                    # Calculate total cost increase per change request
                    df['total_cost_increase'] = df['cost_items'].apply(
                        lambda items: sum(item['dollars_increase'] - item['dollars_reduction'] for item in items)
                    )
                    fig, ax = plt.subplots()
                    df.plot(x='change_number', y='total_cost_increase', kind='bar', ax=ax)
                    ax.set_title("Total Cost Increase per Change Request")
                    ax.set_xlabel("Change Number")
                    ax.set_ylabel("Total Cost Increase ($)")
                    plot_pane.object = fig
            else:
                plot_pane.object = None
        else:
            message_pane.object = f"Error fetching data: {response.text}"
        # Handle natural language query
        if natural_query.value:
            # Use keywords to fetch relevant data, then summarize with Llama 3
            if not keywords.value:
                # Extract keywords from natural query (placeholder)
                keywords.value = ' '.join([word for word in natural_query.value.split() if word.lower() in ['hardware', 'software', 'project', 'season']])
            response = requests.get(database_api_url, params={'keywords': keywords.value})
            if response.status_code == 200:
                data = response.json()
                prompts = f"Summarize the following change requests based on query '{natural_query.value}':\n"
                for item in data:
                    prompts += f"- {item['description']}\n"
                summary = call_llama_api(prompts)
                message_pane.object = summary
            else:
                message_pane.object = f"Error fetching data for natural query: {response.text}"
    except Exception as e:
        message_pane.object = f"Error: {str(e)}"
    finally:
        query_button.loading = False

query_button.on_click(on_query_click)

# Data entry form
form = pn.Column(
    project_name,
    change_number,
    requested_by,
    date_of_request,
    presented_to,
    change_name,
    description,
    reason,
    effect_on_deliverables,
    effect_on_organization,
    effect_on_schedule,
    effect_of_not_approving,
    reason_for_rejection,
    add_cost_item_button,
    cost_items_column,
    submit_button
)

# Upload section
upload_section = pn.Row(
    file_input,
    scrape_button
)

# Data entry section
data_entry_section = pn.Column(
    pn.pane.Markdown("### Upload Document or Enter Data Manually"),
    upload_section,
    form
)

# Query section
query_section = pn.Column(
    pn.pane.Markdown("### Query Change Requests"),
    project_filter,
    requester_filter,
    date_start,
    date_end,
    keywords,
    natural_query,
    query_button
)

# Results section
results_section = pn.Column(
    pn.pane.Markdown("### Query Results"),
    results_pane,
    plot_select,
    plot_pane
)

# Final layout
layout = pn.Column(
    pn.pane.Markdown("# Change Request Dashboard"),
    data_entry_section,
    query_section,
    results_section,
    message_pane,
    align="center"
)

layout.servable()