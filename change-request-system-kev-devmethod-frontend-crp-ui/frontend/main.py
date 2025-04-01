import panel as pn
from crp_form import get_form_submission_layout
from llama3_interface import get_database_query_layout
from theme_manager import theme_manager

# Initialize Panel
pn.extension()

# Set initial theme
pn.state.theme = theme_manager.get_theme()

# Get the theme toggle from the theme manager
theme_toggle = theme_manager.get_toggle_widget()

# Create the header
header = pn.Row(
    pn.pane.Markdown("# Change Request Dashboard", styles={'color': '#1976D2'}),
    theme_toggle,
    styles={'background': '#f8f9fa', 'padding': '10px'}
)

# Create tabs
form_submission_tab = get_form_submission_layout()
database_query_tab = get_database_query_layout()

tabs = pn.Tabs(
    ("Form Submission", form_submission_tab),
    ("Database Query", database_query_tab)
)

# Create main layout
layout = pn.Column(
    header,
    tabs,
    sizing_mode='stretch_width'
)

# Show the application
if __name__ == "__main__":
    layout.show()