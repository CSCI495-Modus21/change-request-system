import panel as pn
import pandas as pd
import requests
from io import BytesIO
import random
from theme_manager import theme_manager

# Initialize Panel
pn.extension()

database_api_url = "http://localhost:8000/api/change_requests/"

def generate_cr_num():
    cr_num = random.randint(1000,2000)
    return cr_num

# Create widgets with styling that works in both themes
project_name = pn.widgets.TextInput(name="Project Name", placeholder="Enter project name", stylesheets=['body { margin: 5px; }'])
change_number = pn.widgets.TextInput(name="Change Number", placeholder="Enter change number", value=f"CR-{generate_cr_num()}", disabled=True, stylesheets=['body { margin: 5px; }'])
requested_by = pn.widgets.TextInput(name="Requested By", placeholder="Enter requester name", stylesheets=['body { margin: 5px; }'])
date_of_request = pn.widgets.DatePicker(name="Date of Request", stylesheets=['body { margin: 5px; }'])
presented_to = pn.widgets.TextInput(name="Presented To", placeholder="Enter presented to", stylesheets=['body { margin: 5px; }'])
change_name = pn.widgets.TextInput(name="Change Name", placeholder="Enter change name", stylesheets=['body { margin: 5px; }'])
description = pn.widgets.TextAreaInput(name="Description of Change", placeholder="Enter description", height=100, stylesheets=['body { margin: 5px; }'])
reason = pn.widgets.TextAreaInput(name="Reason for Change", placeholder="Enter reason", height=100, stylesheets=['body { margin: 5px; }'])

cost_items_column = pn.Column()

def add_cost_item():
    item_description = pn.widgets.TextInput(name="Item Description", placeholder="Enter item description")
    hours_reduction = pn.widgets.IntInput(name="Hours Reduction", value=0, start=0, width=100)
    hours_increase = pn.widgets.IntInput(name="Hours Increase", value=0, start=0, width=100)
    dollars_reduction = pn.widgets.FloatInput(name="Dollars Reduction", value=0.0, start=0.0, width=100)
    dollars_increase = pn.widgets.FloatInput(name="Dollars Increase", value=0.0, start=0.0, width=100)
    cost_item_row = pn.Column(
        item_description, 
        pn.Row(hours_reduction, hours_increase, dollars_reduction, dollars_increase),
        pn.Spacer(height=25)
    )
    cost_items_column.append(cost_item_row)

add_cost_item_button = pn.widgets.Button(name="Add Cost Item", button_type="primary")
add_cost_item_button.on_click(lambda event: add_cost_item())

cost_items_area = pn.Column(
    pn.pane.Markdown("### Item Costs"),
    add_cost_item_button,
    pn.Spacer(height=50), 
    cost_items_column
)

add_cost_item()  # Initialize with one cost item

message_pane = pn.pane.Markdown("", width=500)

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
form = pn.Row(
    pn.Column(
        project_name,
        change_number,
        requested_by,
        date_of_request,
        presented_to,
        change_name,
        description,
        reason,
        submit_button
    ),
    pn.Spacer(width=50),
    cost_items_area,
)

data_entry_section = pn.Column(
    pn.pane.Markdown("### Change Request Form"),
    form
)

layout = pn.Column(
    pn.pane.Markdown("# Change Request Form Submission"),
    data_entry_section,
    message_pane,
)

def get_form_submission_layout():
    return layout

def toggle_theme(event):
    print(f"Current theme before toggle: {pn.state.theme}")  # Debug print
    new_theme = 'dark' if pn.state.theme == 'light' else 'light'
    pn.state.theme = new_theme
    print(f"New theme after toggle: {pn.state.theme}")  # Debug print

# Create the toggle theme button
button = pn.widgets.Button(
    name="🌓 Toggle Theme",
    button_type='primary'
)
button.on_click(toggle_theme)

# Adding some test widgets to better see the theme change
text = pn.widgets.TextInput(value="Test input field")
slider = pn.widgets.FloatSlider(start=0, end=10, value=5)
info = pn.pane.Markdown("## Test Theme Toggle\nThis is a test of the theme toggle functionality")

# Create layout with test components
layout = pn.Column(
    info,
    button,
    text,
    slider
)

# Show the layout
layout.servable()