import requests
import csv
import logging
import pandas as pd
# import numpy as np

API_KEY = '8919aa67c51d4f48a1882658252011'
URL = 'http://api.weatherapi.com/v1/current.json'

class RelevantLocationData:
    '''
    Hard coded csv columns, with the assumption that they match the API response fields (can change if needed).
    '''
    ZIPCODE = 'zip code'
    COUNTRY = 'country'
    STATE = 'state'
    CITY = 'city'
    LOCALTIME = 'localtime'
    ALLORIGINALLOCATIONKEYS = [COUNTRY, STATE, CITY, ZIPCODE]
    ALLLOCATIONKEYS = [COUNTRY, STATE, CITY, ZIPCODE, LOCALTIME]

class RelevantCurrentData:
    LASTUPDATED = 'last_updated'
    TEMPC = 'temp_c'
    TEMPF = 'temp_f'
    CLOUD = 'cloud'
    WINDSPEED = 'wind_mph'
    HUMIDITY = 'humidity'
    PRESSURE = 'pressure_mb'
    ALLCURRENTKEYS = [LASTUPDATED, TEMPC, TEMPF, CLOUD, WINDSPEED, HUMIDITY, PRESSURE]


class WeatherAPIClient:
    '''
    API client wrapper for Weather API
    '''
    def __init__(self, api_key):
        self.api_key = api_key
        self.url = URL
        self.logger = self.api_client_logger()
        self.RelevantLocationData = RelevantLocationData()
        self.RelevantCurrentData = RelevantCurrentData()

    def build_query(self, csv_row):
        '''
        WeatherAPI normalises internally, so no need for consistent format in csv (e.g. capitalisation).
        WeatherAPI expects at least city or zipcode.
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
        original_data = {loc: csv_row[loc] for loc in self.RelevantLocationData.ALLORIGINALLOCATIONKEYS}

        if original_data[self.RelevantLocationData.ZIPCODE]:
            #self.logger.info(f'Zipcode {original_data[self.RelevantLocationData.ZIPCODE]} provided')
            self.logger.info(f'CSV row data {original_data}')
            return original_data[self.RelevantLocationData.ZIPCODE], original_data
        if not original_data[self.RelevantLocationData.CITY]:
            self.logger.info(f'Invalid csv row {original_data}: No zipcode or city')
            return None, original_data

        parts = [x for x in (original_data[self.RelevantLocationData.CITY], original_data[self.RelevantLocationData.STATE], original_data[self.RelevantLocationData.COUNTRY]) if x]
        self.logger.info(f'CSV row data {original_data}')
        return ", ".join(parts), original_data

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
        return response.json(), query

    def api_client_logger(self):
        '''
        Initiate logger for API.
        '''
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        logger = logging.getLogger('WeatherAPIClient')
        return logger
