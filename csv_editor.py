'''
'''
import os
from datetime import datetime, timedelta
import pandas as pd
import logging
import numpy as np

import constants
from dateman import DateManager


logging.basicConfig(
    level=logging.INFO
)

logger = logging.getLogger(__name__)

class CSVEditor():
    def __init__(self):
        self.dateman = DateManager()

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
        last_month= int(today.replace(day = 1) - timedelta(days=1))
        last_month_data = df[df['month']==last_month]
        if len(last_month_data) > 0:
            mean_score = np.round(np.mean(last_month_data.values))
        else:
            mean_score = 0
        
        return mean_score

    def _update_csv(self, today: datetime, user:str, time:str, excuse:str, score:int):
        df = self._get_csv(user)
        file_name = user +'.csv'

        time = today.time().strftime("%H:%M:%S")
        new_log = [today.year, today.month, today.day, time, excuse, score]

        if len(df) == 0 or datetime(df.iloc[-1]['year'],df.iloc[-1]['month'],df.iloc[-1]['day']).date() != today.date():
            pd.DataFrame([new_log]).to_csv(file_name, header =False, mode='a')
        else: # rewrite today's log
            df.iloc[-1] = new_log
            df.to_csv(file_name, header =True, mode='w')
            

    def check_in(self, user, option = "없음", is_custom = False, custom_hh=0, custom_mm=0):
        '''
        '''

        current_time = datetime.now()
 
        if(is_custom):
            current_time = current_time.replace(hour=int(custom_hh),minute=int(custom_mm),second=0)
        check_in_time = current_time.time().strftime("%H:%M:%S")

        holiday_name = self.dateman.get_holiday_name_kr()
        weekday = current_time.date().weekday()
        is_working_day = weekday < 5 and not holiday_name

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
        elif(holiday_name):
            msg = f"오늘은 {holiday_name}입니다. 집으로 돌아가세요!"

        logger.info(msg)
        return msg
    
