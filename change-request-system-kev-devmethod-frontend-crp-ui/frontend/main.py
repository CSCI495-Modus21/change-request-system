import panel as pn
from crp_form import get_form_submission_layout
from llama3_interface import get_database_query_layout

# Initialize Panel with material design
pn.extension('material')

# Set up the template first so we can reference it
template = pn.template.MaterialTemplate(
    title="Change Request Dashboard",
    header_background="#1976D2",
)

# Create a theme toggle button
theme_toggle = pn.widgets.Switch(name='Dark Mode', value=True, width=100)

def toggle_theme(event):
    template.theme = "dark" if event.new else "light"
    # Force refresh all components
    if hasattr(pn.state, 'cache'):
        pn.state.cache.clear()

theme_toggle.param.watch(toggle_theme, 'value')

form_submission_tab = get_form_submission_layout()
database_query_tab = get_database_query_layout()

tabs = pn.Tabs(
    ("Form Submission", form_submission_tab),
    ("Database Query", database_query_tab)
)

# Add components to template
template.header.append(theme_toggle)
template.main.append(tabs)

# Set initial theme
template.theme = "dark"

if __name__ == "__main__":
    template.show()