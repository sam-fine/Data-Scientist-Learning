import requests
import pandas as pd
import numpy as np
import csv

from WeatherApiClient import WeatherAPIClient


class WeatherModule:

    def __init__(self, api_key, csv_path):
        self.api_client = WeatherAPIClient(api_key)
        self.csv_path = csv_path

    def main(self):
        '''
        Main function to process csv.
        Use DictReader rather than pd.read_csv so an #
        '''
        with open(self.csv_path, mode='r', newline='') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                raw_data = self.fetch_data(row)

    def fetch_data(self, csv_row):
        '''
        Use client to fetch raw data from API.
        '''
        query = self.api_client.build_query(csv_row)
        raw_data = self.api_client.fetch_weather(query)
        return raw_data

    def process_raw_data(self, raw_data):
        '''
        Take the raw data from the API call and return what is relevant.
        '''


if __name__ == '__main__':
    WeatherApi = WeatherAPIClient(API_KEY)
    # user open() and csv rather than pandas read_csv() as we want an iterator for each csv row incase of large csvs so memory is better
    with open(r'weather_data/example_input.csv', mode='r', newline='') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            query = WeatherApi.build_query(row)
            data = WeatherApi.fetch_weather(query)