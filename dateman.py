from datetime import datetime
import json
import logging

import numpy as np
import requests
from pandas import json_normalize

import private

logging.basicConfig(
    level=logging.INFO
)

logger = logging.getLogger(__name__)

DATE_TO_KEY = private.DATE_TO_KEY
DATE_URL = 'http://apis.data.go.kr/B090041/openapi/service/SpcdeInfoService/getRestDeInfo?_type=json&numOfRows=50&solYear='

class DateManager():
    """
    Manages date-related information in Korean
    """
    def __init__(self):
        self.key = DATE_TO_KEY
        self.url_base = DATE_URL
        self.holidays_frame = None
        self.last_updated ="2023-01-01"

    def _update_holidays(self):
        if self.last_updated == datetime.today().strftime('%Y-%m-%d'):
            return

        today_year = datetime.today().year

        date_url = self.url_base + str(today_year) + '&ServiceKey=' + str(self.key)
        response = requests.get(date_url)
        if response.status_code == 200:
            json_ob = json.loads(response.text)
            holidays_data = json_ob['response']['body']['items']['item']
            data_frame = json_normalize(holidays_data)
            self.holidays_frame = data_frame
            self.last_updated = datetime.today().strftime('%Y-%m-%d')

        else:
            msg = f"Requests was failed with code {response.status_code}"
            logging.error(msg)

    def get_holiday_name_kr(self):
        """
        Returns the holiday name.
        If today is not a public holiday, returns an empty string.
        """
        self._update_holidays()

        today = datetime.today().strftime('%Y%m%d')
        data_frame = self.holidays_frame.loc[self.holidays_frame['locdate'] == int(today), 'dateName']
        return data_frame.values

    def get_order_busday(self):
        """
        Calculate the "n-th" business day from the first day of this month
        """
        self._update_holidays()

        today = datetime.today()

        start_date = today.strftime('%Y-%m-01')
        hol_kr = [np.datetime64(str(x)) for x in self.holidays_frame['locdate']]
        return np.busday_count(start_date,today.date(), holidays= hol_kr)
