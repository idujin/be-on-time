import gradio as gr
import altair as alt
from csv_editor import CSVEditor

ceditor = CSVEditor()

def display_dataframe(user):
    if user:
        return gr.DataFrame(value= ceditor.get_display_csv(user))
    return gr.DataFrame([])
    
def make_plot(users, except_user = None):
    scores_df = ceditor.get_current_score_dataframe(users,except_user)

    bar = alt.Chart(scores_df).mark_bar().encode(
    y='User',
    x='Score').properties(width = 500)

    return bar