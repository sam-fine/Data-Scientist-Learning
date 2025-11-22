import requests
import pandas as pd
import numpy as np
import csv
import os

from WeatherApiClient import WeatherAPIClient, RelevantLocationData, RelevantCurrentData

API_KEY = '8919aa67c51d4f48a1882658252011'

class WeatherModule:

    def __init__(self, api_key, csv_path, output_path):
        self.api_client = WeatherAPIClient(api_key)
        self.logger = self.api_client.logger
        self.csv_path = csv_path
        self.output_path = output_path
        self.RelevantLocationData = RelevantLocationData()
        self.RelevantCurrentData = RelevantCurrentData()
        self.csv_columns = self.RelevantLocationData.ALLLOCATIONKEYS + self.RelevantCurrentData.ALLCURRENTKEYS # keeps order
        self.cache = {}

    def main(self):
        '''
        Main function to process csv.
        Use DictReader rather than pd.read_csv as we want an iterator to iterate through each row in the csv
        in case of large files to preserve memory (scalable).
        '''
        output_path = os.path.join(self.output_path,'output_weather_file.csv')
        with open(output_path, mode='w', newline='') as output_csv_file:
            writer = csv.DictWriter(output_csv_file, fieldnames=self.csv_columns)

            # Write the header row first
            writer.writeheader()
            with open(self.csv_path, mode='r', newline='') as csv_file:
                reader = csv.DictReader(csv_file)
                for row in reader:
                    raw_data, original_data, query = self.fetch_data(row)
                    if raw_data is None:
                        writer.writerow(original_data)
                        continue
                    if raw_data is True:
                        parsed = self.cache[query]
                        self.logger.info(f'Repeated Location, take data from cache {parsed}')
                    else:
                        parsed = self.parse_raw_data(raw_data, original_data, query)
                    writer.writerow(parsed)


    def fetch_data(self, csv_row):
        '''
        Use client to fetch raw data from API.
        '''
        query, original_data = self.api_client.build_query(csv_row)
        if query is None: # invalid csv data
            return None, original_data, query
        if query in self.cache:
            return True, original_data, query

        raw_data, query = self.api_client.fetch_weather(query)
        return raw_data, original_data, query

    def parse_raw_data(self, raw_data, original_data, query):
        '''
        Parse the raw data from the API call to return what is relevant.
        Return location data if not in csv
        original_data: data in csv
        '''
        parsed_data = {}
        for location in original_data:
            if location:
                parsed_data[location] = original_data[location]
            elif location == self.RelevantLocationData.COUNTRY:
                parsed_data[location] = raw_data['location'][location]
            elif location == self.RelevantLocationData.CITY:
                parsed_data[location] = raw_data['location']['name']
            elif location == self.RelevantLocationData.STATE:
                parsed_data[location] = raw_data['location']['region']

        parsed_data[self.RelevantLocationData.LOCALTIME] = raw_data['location'][self.RelevantLocationData.LOCALTIME]

        for current in self.RelevantCurrentData.ALLCURRENTKEYS:
            parsed_data[current] = raw_data['current'][current]

        self.cache[query] = parsed_data

        return parsed_data

    # def reformat_result_headers(self):
    #     '''
    #     Current column headers are based off csv headers and API fields, change them to include units.
    #     '''
    #     self.csv_columns.rename({})


if __name__ == '__main__':
    Weather = WeatherModule(API_KEY,r'C:\Users\samfi\OneDrive\Documents\Interviews_2025\Solid_data_team8\weather_data/example_input.csv', r'C:\Users\samfi\OneDrive\Documents\Interviews_2025\Solid_data_team8\weather_data')
    Weather.main()