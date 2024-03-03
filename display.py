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


class DisplayManger():
    def __init__(self, users= None, inactive_users = None):
        self.dateman = DateManager(DATE_TO_KEY)
        self.ceditor = CSVEditor(self.dateman)
        self.display_year = self.dateman.get_current_year()
        self.display_month = self.dateman.get_current_month()
        self.users = users
        self.inactive_users = inactive_users

    def display_dataframe(self,user):
        if user:
            return gr.DataFrame(value= self.ceditor.get_display_csv(user))
        return gr.DataFrame([])
    def make_plot_search(self, direction, users = None):
        if users is None:
            users = self.users
        if direction == "<":
            self.display_month -= 1
            if self.display_month == 0:
                self.display_month = 12
                self.display_year -= 1
        elif direction == ">":
            self.display_month += 1
            if self.display_month == 13:
                self.display_month = 1
                self.display_year += 1
        return self.make_plot(users), gr.Markdown(""" ###  {}/{} """.format(self.display_year,self.display_month))

    def make_plot(self, users):
        scores_df = self.ceditor.get_current_score_dataframe(users,self.inactive_users, self.display_year, self.display_month)

        bar = alt.Chart(scores_df).mark_bar().encode(
        y='User',
        x='Score').properties(width = 500)

        return bar
