import panel as pn
import pandas as pd
import requests
from io import BytesIO

pn.extension(theme="dark")

database_api_url = "http://localhost:8000/api/change_requests/"

def scrape_pdf(file):
    # FIXME: Placeholder for PDF scraping. Simulates extracting data from PDF.
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

# Define widgets
project_name = pn.widgets.TextInput(name="Project Name", placeholder="Enter project name")
change_number = pn.widgets.TextInput(name="Change Number", placeholder="Enter change number")
requested_by = pn.widgets.TextInput(name="Requested By", placeholder="Enter requester name")
date_of_request = pn.widgets.DatePicker(name="Date of Request")
presented_to = pn.widgets.TextInput(name="Presented To", placeholder="Enter presented to")
change_name = pn.widgets.TextInput(name="Change Name", placeholder="Enter change name")
description = pn.widgets.TextAreaInput(name="Description of Change", placeholder="Enter description", height=100)
reason = pn.widgets.TextAreaInput(name="Reason for Change", placeholder="Enter reason", height=100)

cost_items_column = pn.Column()

def add_cost_item():
    item_description = pn.widgets.TextInput(name="Item Description", placeholder="Enter item description")
    hours_reduction = pn.widgets.IntInput(name="Hours Reduction", value=0, start=0, width=100)
    hours_increase = pn.widgets.IntInput(name="Hours Increase", value=0, start=0, width=100)
    dollars_reduction = pn.widgets.FloatInput(name="Dollars Reduction", value=0.0, start=0.0, width=100)
    dollars_increase = pn.widgets.FloatInput(name="Dollars Increase", value=0.0, start=0.0, width=100)
    cost_item_row = pn.Row(item_description, hours_reduction, hours_increase, dollars_reduction, dollars_increase)
    cost_items_column.append(cost_item_row)

add_cost_item_button = pn.widgets.Button(name="Add Cost Item", button_type="primary")
add_cost_item_button.on_click(lambda event: add_cost_item())
add_cost_item()  # Initialize with one cost item

file_input = pn.widgets.FileInput(accept=".pdf")
scrape_button = pn.widgets.Button(name="Scrape PDF", button_type="primary")
message_pane = pn.pane.Markdown("", width=500)

def on_scrape_click(event):
    if file_input.value:
        file = BytesIO(file_input.value)
        data = scrape_pdf(file)
        project_name.value = data.get('project_name', '')
        change_number.value = data.get('change_number', '')
        requested_by.value = data.get('requested_by', '')
        date_of_request.value = pd.to_datetime(data.get('date_of_request', None)).date() if data.get('date_of_request') else None
        presented_to.value = data.get('presented_to', '')
        change_name.value = data.get('change_name', '')
        description.value = data.get('description', '')
        reason.value = data.get('reason', '')
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

# Assemble the layout
form = pn.Column(
    project_name,
    change_number,
    requested_by,
    date_of_request,
    presented_to,
    change_name,
    description,
    reason,
    add_cost_item_button,
    cost_items_column,
    submit_button
)

upload_section = pn.Row(
    file_input,
    scrape_button
)

data_entry_section = pn.Row(
    pn.Column(
        pn.pane.Markdown("### Enter Manually"),
        form
    ),
    pn.Spacer(width=5),
    pn.Column(
        pn.pane.Markdown("### Upload Change Request Document"),
        upload_section
    ),
)

layout = pn.Column(
    pn.pane.Markdown("# Change Request Form Submission"),
    data_entry_section,
    message_pane,
)

def get_form_submission_layout():
    return layout