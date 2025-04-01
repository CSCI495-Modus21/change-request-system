import panel as pn
import crp_form
import model_interface

pn.extension(theme="dark")

form_submission_tab = crp_form.get_layout()
database_query_tab = model_interface.get_layout()

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