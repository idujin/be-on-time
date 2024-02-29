import os
import logging

import gradio as gr
import altair as alt

from csv_editor import CSVEditor
from dateman import DateManager

logger = logging.getLogger(__name__)

DATE_TO_KEY = os.getenv("DATE_TO_KEY")
if DATE_TO_KEY is None:
    logger.error("DATE_TO_KEY must be set as environment variable.")
    exit(1)

dateman = DateManager(DATE_TO_KEY)
ceditor = CSVEditor(dateman)

def display_dataframe(user):
    if user:
        return gr.DataFrame(value= ceditor.get_display_csv(user))
    return gr.DataFrame([])

def make_plot(users, inactive_user = None):
    scores_df = ceditor.get_current_score_dataframe(users,inactive_user)

    bar = alt.Chart(scores_df).mark_bar().encode(
    y='User',
    x='Score').properties(width = 500)

    return bar
