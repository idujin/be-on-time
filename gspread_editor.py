'''
'''
from datetime import datetime
import logging

import gspread
from gspread.exceptions import WorksheetNotFound

import constants
from dateman import DateManager


logging.basicConfig(
    level=logging.INFO
)

logger = logging.getLogger(__name__)

class GSpreadEditor():
    def __init__(self):
        gc, authorized_user = gspread.oauth_from_dict(constants.GSPREAD_CREDENTIAL, constants.GSPREAD_AUTH_USER)

        self.sh = gc.open_by_url(constants.GSPREAD_URL)
        self.worksheet = self.sh.sheet1
        self.dateman = DateManager()
        self.excuse = {"재택": 1, "운동": 2, "연차": 3}
        self.user_start_col = {"유진": "B", "애리": "F", "지은": "J"}

    def _update_data(self, cell, data):

        sheet_name = datetime.today().strftime('%Y-%m')
        try:
            self.worksheet = self.sh.worksheet(sheet_name)
        except WorksheetNotFound:
            logger.info("Worksheet %s not found. Creating a new one.", sheet_name)
            templete = self.sh.worksheet("Template v3 (Do not edit!!)")
            templete.duplicate(new_sheet_name = sheet_name)

        self.worksheet.update(cell, [data])
        return

    def _clear_options(self, start_row, start_col):
        '''
        '''
        start_option = chr(ord(start_col)+1)+str(start_row)
        end_option = chr(ord(start_col)+len(self.excuse))+str(start_row)
        clear_val = [False for i in range(len(self.excuse))]
        self._update_data(start_option +":" + end_option, clear_val)

    def check_in(self, user, option = "없음", is_custom = False, custom_hh=0, custom_mm=0):
        '''
        '''
        start_col = self.user_start_col[user]
        current_time = datetime.now()
        today = str(current_time.date())
        check_in_time = current_time.time().strftime("%H:%M:%S")
        if(is_custom):
            check_in_time =str(int(custom_hh))+":"+str(int(custom_mm))+":00"
        holiday_name = self.dateman.get_holiday_name_kr()
        weekday = current_time.date().weekday()
        is_working_day = weekday < 5 and not holiday_name

        msg = f"{user}님, 오늘은 주말입니다. 집으로 돌아가세요!"
        if(is_working_day):
            start_row = 23 + self.dateman.get_order_busday()

            self._update_data("A"+str(start_row),[today])
            self._update_data(start_col +str(start_row),[check_in_time])

            self._clear_options(start_row, start_col)

            msg = f"{user}님은 {check_in_time}시에 출근완료."
            if option != "없음" and option != None:
                self._clear_options(start_row, start_col)
                self._update_data(chr(ord(start_col)+self.excuse[option])+str(start_row),[True])

                if(option !="운동"):
                    msg = f"{user}님은 오늘 {option}!"
                else:
                    msg += f" {option} 점수가 추가되었어요."
        elif(holiday_name):
            msg = f"오늘은 {holiday_name}입니다. 집으로 돌아가세요!"

        logger.info(msg)
        return msg
