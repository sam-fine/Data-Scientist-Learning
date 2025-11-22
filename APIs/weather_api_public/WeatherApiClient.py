import requests
import csv
import logging
import pandas as pd
# import numpy as np

API_KEY = '8919aa67c51d4f48a1882658252011'
URL = 'http://api.weatherapi.com/v1/current.json'

ZIPCODE = 'zip code'
COUNTRY = 'country'
STATE = 'state'
CITY = 'city'


class WeatherAPIClient:
    '''
    API client wrapper for Weather API
    '''
    def __init__(self, api_key):
        self.api_key = api_key
        self.url = URL
        self.logger = self.api_client_logger()

    def build_query(self, csv_row):
        '''
        WeatherAPI normalises internally, so no need for consistent format in csv (e.g. capitalisation).
        WeatherAPI expects at least city or state.
        The following are allowed combinations (in the order stated):
            - Zip code alone
            - City + Country
            - City + State + Country
            - City + State
            - City alone
        The following are not allowed combinations:
            - Country only
            - State only
            - State + Country without city
        '''
        zipcode = csv_row[ZIPCODE]
        if zipcode:
            self.logger.info(f'Zipcode {zipcode} provided')
            return zipcode

        city = csv_row[CITY]# # do we need to strip
        if not city:
            self.logger.info('Invalid csv row: No zipcode or city')
            return None

        state = csv_row[STATE]
        country = csv_row[COUNTRY]
        parts = [x for x in (city, state, country) if x]
        self.logger.info(f'CSV row data {parts}')
        return ", ".join(parts)

    def fetch_weather(self, query):
        '''
        Use WeatherAPI to fetch weather data.
        '''
        params = {
            'q': query,
            'key': self.api_key
        }

        try:
            response = requests.get(URL, params=params)
            response.raise_for_status() # raises errors for 4xx (client error) or 5xx (server error)
        except requests.exceptions.RequestException as e:
            raise SystemExit(f'Error in API call {e}')
        return response.json()

    def api_client_logger(self):
        '''
        Initiate logger for API.
        '''
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        logger = logging.getLogger('WeatherAPIClient')
        return logger
