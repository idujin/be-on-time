import os
import logging

import gradio as gr
import altair as alt
from datetime import datetime

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
        self.display_year = datetime.today().year
        self.display_month = datetime.today().month
        self.display_user = users[0]
        self.users = users
        self.inactive_users = inactive_users

    def display_dataframe(self,user):
        if user:
            self.display_user = user
            return gr.DataFrame(value= self.ceditor.get_display_csv(user, self.display_year, self.display_month))
        return gr.DataFrame([])
    
    def _add_months(self, delta_months: int):
        """
        Increments (or decrements) the month by the integer delta_months
        and automatically adjusts the year as needed.
        """
        new_month = self.display_month + delta_months
        
        self.display_year += (new_month - 1) // 12
        new_month = (new_month - 1) % 12 + 1
        
        self.display_month = new_month

    def make_plot_search(self, direction, users = None):
        score_chart =[]
        if users is None:
            users = self.users
        month_step = 1
        if direction == "<":
            month_step = -1
        elif direction == ">":
            month_step = 1
        
        self._add_months(month_step)
        score_chart = self.make_plot(users)
        if score_chart is None:
            self._add_months(-1*month_step)
            score_chart = self.make_plot(users)

        return score_chart, self.display_dataframe(self.display_user), gr.Markdown(""" ###  {}/{} """.format(self.display_year,self.display_month))

    def make_plot(self, users):
        scores_df = self.ceditor.get_current_score_dataframe(users,self.inactive_users, self.display_year, self.display_month)
        if scores_df is None:
            return None
        bar = alt.Chart(scores_df).mark_bar().encode(
        y='User',
        x='Score').properties(width = 500)

        return bar
