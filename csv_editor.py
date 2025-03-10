'''
'''
from datetime import datetime, timedelta
import logging
import os

import numpy as np
import pandas as pd

import constants
from dateman import DateManager


logging.basicConfig(
    level=logging.INFO
)

logger = logging.getLogger(__name__)

class CSVEditor():
    def __init__(self, date_manager : DateManager):
        self.dateman = date_manager

    def _create_new_csv(self, user):
        '''
        Create new csv file. The file is created in same directory with the name of userYYYY.
        Make sure this function should be called when creating a new file. Otherwise, an existed file will be replaced with new empty file.

        '''

        file_name = user + '.csv'
        column_info =[("year"),("month"),("day"),("time"),("excuse"),("score")]
        df = pd.DataFrame(columns=column_info)
        df.to_csv(file_name, header =True, mode='w')

    def _get_csv(self, user):
        file_name = user+'.csv'
        if not os.path.isfile(file_name):
            self._create_new_csv(user)
        return pd.read_csv(file_name, index_col = [0])

    def _get_score(self, user, checkin_datetime: datetime, excuse: str)-> int:
        score = -20
        yy, mm, dd = checkin_datetime.year,checkin_datetime.month,checkin_datetime.day
        if datetime(yy, mm, dd, hour=8,minute=30,second=0) > checkin_datetime:
            score= 5
        elif datetime(yy, mm, dd, hour=9,minute=0,second=0) > checkin_datetime:
            score = 0
        elif datetime(yy, mm, dd, hour=9,minute=30,second=0) > checkin_datetime:
            score = -5
        elif datetime(yy, mm, dd, hour=10,minute=0,second=0) > checkin_datetime:
            score = -10
        elif datetime(yy, mm, dd, hour=10,minute=30,second=0) > checkin_datetime:
            score = -15

        if excuse == '운동':
            score += 5
        elif excuse == '연차':
            score = 0
        elif excuse =='재택':
            score = self._get_last_month_mean(user, checkin_datetime.date())

        return score
    def _get_last_month_mean(self, user, today: datetime.date)->int:
        df = self._get_csv(user)
        last_month= (today.replace(day = 1) - timedelta(days=1)).month
        last_month_data = df[df['month']==last_month]
        
        if len(last_month_data) > 0:
            mean_score = last_month_data['score'].mean().round(0)
        else:
            mean_score = 0

        return mean_score

    def _update_csv(self, today: datetime, user:str, time:str, excuse:str, score:int, is_empty_checker = False):
        df = self._get_csv(user)
        file_name = user +'.csv'

        time = today.time().strftime("%H:%M:%S")
        new_log = [today.year, today.month, today.day, time, excuse, score]

        if len(df) == 0 or datetime(df.iloc[-1]['year'],df.iloc[-1]['month'],df.iloc[-1]['day']).date() != today.date():
            pd.DataFrame([new_log]).to_csv(file_name, header =False, mode='a')
        elif not is_empty_checker: # rewrite today's log
            df.iloc[-1] = new_log
            df.to_csv(file_name, header =True, mode='w')

    def get_display_csv(self, user, year: int = datetime.now().date().year, month: int=datetime.now().date().month):
        df = self._get_csv(user)
        logger.info("Displaying %s's data for %d/%d", user, year, month)
        return df[np.logical_and(df['year']==year, df['month']==month)]

    def get_current_score_dataframe(self, users, inactive_users = None, year: int = datetime.now().date().year, month: int=datetime.now().date().month):
        scores = np.array([])
        for user in users:
            sc = 0
            if inactive_users is None or not user in inactive_users:
                score_ret = self.get_user_month_score(user, year, month)
                if score_ret is not None:
                    sc = np.sum(score_ret)
                else:
                    return None
            scores = np.append(scores, sc)

        if inactive_users is not None:
            mean_score = np.round(np.sum(scores)/(len(users)-len(inactive_users)))
            for i, user in enumerate(users):
                if user in inactive_users:
                    scores[i] = mean_score
        return pd.DataFrame({ 'User': users, 'Score': scores })

    def get_user_month_score(self, user, year: int = datetime.now().date().year, month: int=datetime.now().date().month):
        df = self._get_csv(user)
        min_year = df.loc[:,"year"].min()
        max_year = df.loc[:,"year"].max()
        if year < min_year or year > max_year:
            logger.error("Invalid %d year input", year)
            return [0]
        min_month = df[df['year']==year]['month'].min()
        max_month = df[df['year']==year]['month'].max()

        if month < min_month or month > max_month:
            logger.error("Invalid %d month input", month)
            return [0]
        score = df[np.logical_and(df['year']==year, df['month']==month)]['score'].values
        return score

    def daily_check_in_auto(self, users, inactive_users = None):
        '''
        This function is called every at 11:55 PM.
        If user did not check-in before that time, 23:55:00 would be filled at check-in time and the score also would be -20.
        '''
        current_time = datetime.now()
        holiday_name = self.dateman.get_holiday_name_kr()
        weekday = current_time.date().weekday()
        is_working_day = weekday < 5 and not holiday_name
        if(is_working_day):
            yy, mm, dd = current_time.year,current_time.month,current_time.day
            active_users = users.copy()
            if inactive_users is not None:
                for u in inactive_users:
                    active_users.remove(u)

            for user in active_users:
                latest_time = datetime(yy, mm, dd, hour=23,minute=55,second=0)
                score = self._get_score(user, latest_time, "없음")
                self._update_csv(current_time, user, latest_time, "없음", score, is_empty_checker=True)
        return

    def check_in(self, user, option = "없음", is_custom = False, custom_hh=0, custom_mm=0):
        '''
        '''

        current_time = datetime.now()

        if(is_custom):
            current_time = current_time.replace(hour=int(custom_hh),minute=int(custom_mm),second=0)
        check_in_time = current_time.time().strftime("%H:%M:%S")

        holiday_name = self.dateman.get_holiday_name_kr()
        weekday = current_time.date().weekday()
        is_working_day = weekday < 5 and holiday_name.size == 0

        msg = f"{user}님, 오늘은 주말입니다. 집으로 돌아가세요!"
        if(is_working_day):
            score = self._get_score(user, current_time, option)
            self._update_csv(current_time, user, check_in_time, option, score)
            msg = f"{user}님은 {check_in_time}시에 출근완료."
            if option != "없음" and option != None:
                if(option !="운동"):
                    msg = f"{user}님은 오늘 {option}!"
                else:
                    msg += f" {option} 점수가 추가되었어요."
        elif(holiday_name.size > 0):
            msg = f"오늘은 {holiday_name}입니다. 집으로 돌아가세요!"

        logger.info(msg)
        return msg
if __name__ == "__main__":
    logger.info("daily_check_in_auto is running...")

    DATE_TO_KEY = os.getenv("DATE_TO_KEY")
    if DATE_TO_KEY is None:
        logger.error("DATE_TO_KEY must be set as environment variable.")
        exit(1)

    dateman = DateManager(DATE_TO_KEY)
    ceditor = CSVEditor(dateman)
    ceditor.daily_check_in_auto(constants.USERS, constants.INACTIVE_USERS)

