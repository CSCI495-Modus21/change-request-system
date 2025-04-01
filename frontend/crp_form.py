import panel as pn
import requests
import random

pn.extension(theme="dark", notifications=True)

change_request_api_url = "http://127.0.0.1:8000/change_requests"

def generate_cr_num():
    return f"CR-{random.randint(1000, 2000)}"

project_name = pn.widgets.TextInput(name="Project Name", placeholder="Enter project name")
change_number = pn.widgets.TextInput(name="Change Number", value=generate_cr_num(), disabled=True)
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
    cost_item_row = pn.Column(
        item_description,
        pn.Row(hours_reduction, hours_increase, dollars_reduction, dollars_increase),
        pn.Spacer(height=25)
    )
    cost_items_column.append(cost_item_row)
    return cost_item_row  # Return for initial setup

add_cost_item_button = pn.widgets.Button(name="Add Cost Item", button_type="primary")
add_cost_item_button.on_click(lambda event: add_cost_item())

cost_items_area = pn.Column(
    pn.pane.Markdown("### Item Costs"),
    add_cost_item_button,
    pn.Spacer(height=50),
    cost_items_column
)

add_cost_item()

submit_button = pn.widgets.Button(name="Submit Change Request", button_type="success")

def reset_form():
    """Reset all form fields and regenerate change_number."""
    project_name.value = ""
    change_number.value = generate_cr_num()
    requested_by.value = ""
    date_of_request.value = None
    presented_to.value = ""
    change_name.value = ""
    description.value = ""
    reason.value = ""
    cost_items_column.clear()  # Clear all cost items
    add_cost_item()  # Add one fresh cost item row

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

        for cost_item_column in cost_items_column:
            item_description = cost_item_column[0].value
            cost_row = cost_item_column[1]
            hours_reduction = cost_row[0].value
            hours_increase = cost_row[1].value
            dollars_reduction = cost_row[2].value
            dollars_increase = cost_row[3].value

            cost_item = {
                "item_description": item_description,
                "hours_reduction": hours_reduction,
                "hours_increase": hours_increase,
                "dollars_reduction": dollars_reduction,
                "dollars_increase": dollars_increase,
            }
            change_request_data["cost_items"].append(cost_item)

        response = requests.post(change_request_api_url, json=change_request_data)
        response.raise_for_status()
        response_data = response.json()
        
        category = response_data.get("category", "unknown")
        pn.state.notifications.success(f"Change request submitted successfully. Category: {category}")
        
        reset_form()
    except requests.exceptions.RequestException as e:
        pn.state.notifications.error(f"Error submitting change request: {e.response.text if e.response else str(e)}")
    except Exception as e:
        pn.state.notifications.error(f"Error: {str(e)}")
    finally:
        submit_button.loading = False

submit_button.on_click(on_submit_click)

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
)

def get_layout():
    return layout