import panel as pn
from crp_form import get_form_submission_layout
from frontend.model_interface import get_database_query_layout

pn.extension(theme="dark")

form_submission_tab = get_form_submission_layout()
database_query_tab = get_database_query_layout()

tabs = pn.Tabs(
    ("Form Submission", form_submission_tab),
    ("Database Query", database_query_tab)
)

layout = pn.Column(
    pn.pane.Markdown("# Change Request Dashboard"),
    tabs
)

if __name__ == "__main__":
    layout.show()