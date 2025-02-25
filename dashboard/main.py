import panel as pn
from crp_form import get_form_submission_layout
from llama3_interface import get_database_query_layout

pn.extension(theme="dark")

# Create tabs for each app
form_submission_tab = get_form_submission_layout()
database_query_tab = get_database_query_layout()

tabs = pn.Tabs(
    ("Form Submission", form_submission_tab),
    ("Database Query", database_query_tab)
)

# Assemble the main layout
layout = pn.Column(
    pn.pane.Markdown("# Change Request Dashboard"),
    tabs
)

# Serve the application
if __name__ == "__main__":
    layout.show()