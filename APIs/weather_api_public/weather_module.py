import argparse
import logging
import csv
import os
from datetime import datetime
from WeatherApiClient import WeatherAPIClient, RelevantLocationData, RelevantCurrentData, TemperatureAPIFields


class FetchWeather:

    def __init__(self):
        self.args = self.args_parser()
        self.csv_path = self.args.INPUT_PATH
        self.output_path = self.args.SAVE_FILE_BASE_PATH
        self.api_key = self.args.API_KEY
        self.api_client = WeatherAPIClient(self.api_key)
        self.temp_unit = self.args.temperature_unit
        self.logger = self._setup_logger()
        self.RelevantLocationData = RelevantLocationData()
        self.RelevantCurrentData = RelevantCurrentData()
        self.TemperatureAPIFieldsMapping = TemperatureAPIFields.temperature_mapping
        self.csv_columns = self.RelevantLocationData.ALLLOCATIONKEYS + self.RelevantCurrentData.ALLCURRENTCSVCOLS # keeps order
        self.temperature_unit_column()
        self.cache = {}

    def main(self):
        '''
        Main function to process csv.
        Use DictReader rather than pd.read_csv as we want an iterator to iterate through each row in the csv
        in case of large files to preserve memory (scalable).
        '''
        now = datetime.now().strftime("%Y_%m_%dT%H_%M_%S")
        output_path = os.path.join(self.output_path,f'output_weather_file_{now}.csv')
        with open(output_path, mode='w', newline='') as output_csv_file:
            writer = csv.DictWriter(output_csv_file, fieldnames=self.csv_columns)

            # Write the header row first
            writer.writeheader()
            with open(self.csv_path, mode='r', newline='') as csv_file:
                reader = csv.DictReader(csv_file)
                for row in reader:
                    raw_data, original_data, query = self.fetch_data(row)
                    if query in self.cache:
                        parsed = self.cache[query]
                        self.logger.info(f'Repeated Location, take data from cache {parsed}')
                    elif query is None: # invalid csv row or API response
                        writer.writerow(original_data)
                        continue
                    else:
                        parsed = self.parse_raw_data(raw_data, original_data, query)
                    writer.writerow(parsed)


    def fetch_data(self, csv_row):
        '''
        Use client to fetch raw data from API.
        '''
        query, original_data = self.api_client.build_query(csv_row)
        if query is None or query in self.cache: # invalid csv data or in cache
            return None, original_data, query

        raw_data, query = self.api_client.fetch_weather(query)
        if query is None: # failed API response
            return None, original_data, query
        return raw_data, original_data, query

    def temperature_unit_column(self):
        '''
        Identify from CLI arguments what temperature unit is required.
        '''
        self.temp_unit_lower = self.temp_unit.lower()
        if self.temp_unit_lower  == "f":
            self.temp_col = "Temperature (F)"
        elif self.temp_unit_lower  == "k":
            self.temp_col = "Temperature (K)"
        else: # C default
            self.temp_col = "Temperature (C)"
        self.csv_columns.append(self.temp_col)

    def parse_raw_data(self, raw_data, original_data, query):
        '''
        Parse the raw data from the API call to return what is relevant.
        Return location data if not in csv
        original_data: data in csv
        '''
        parsed_data = {}
        for location in original_data:
            if original_data[location]:
                parsed_data[location] = original_data[location]
            elif location == self.RelevantLocationData.COUNTRY:
                parsed_data[location] = raw_data['location'][location]
            elif location == self.RelevantLocationData.CITY:
                parsed_data[location] = raw_data['location']['name']
            elif location == self.RelevantLocationData.STATE:
                parsed_data[location] = raw_data['location']['region']
        # zipcode not provided in API response

        parsed_data[self.RelevantLocationData.LOCALTIME] = raw_data['location'][self.RelevantLocationData.LOCALTIME]

        if self.temp_unit_lower == 'k':
            parsed_data[self.temp_col] = raw_data['current'][self.TemperatureAPIFieldsMapping['c']] + 273.15
        else:
            parsed_data[self.temp_col] = raw_data['current'][self.TemperatureAPIFieldsMapping[self.temp_unit_lower]]

        for current, csv_col in zip(self.RelevantCurrentData.ALLCURRENTKEYS,self.RelevantCurrentData.ALLCURRENTCSVCOLS):
            parsed_data[csv_col] = raw_data['current'][current]

        # ensure variations of same query will be identified if repeated
        self.cache[query] = parsed_data
        self.logger.info(f'Successfully parsed data')

        return parsed_data

    def _setup_logger(self):
        '''
        Initialize and configure logger for FetchWeather.
        '''
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger('FetchWeather')


    def args_parser(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("-ip", "--input-path",
                            dest="INPUT_PATH",
                            help="Full path to input csv",
                            default=r'C:\Users\samfi\OneDrive\Documents\Interviews_2025\Solid_data_team8\weather_data\example_input.csv')
                            #required=True)
        parser.add_argument("-sp", "--save-path",
                            dest="SAVE_FILE_BASE_PATH",
                            help="parent folder that will hold output files",
                            default=r'C:\Users\samfi\OneDrive\Documents\Interviews_2025\Solid_data_team8\weather_data')
                            #required=True)
        parser.add_argument("-apik", "--api-key",
                            dest="API_KEY",
                            help="Personal API Key for Weather API",
                            default=r'8919aa67c51d4f48a1882658252011')
                            #required=True)
        parser.add_argument("-tu", "--temp-unit",
                            dest="temperature_unit",
                            help="Decide which temperature unit to use",
                            choices=['C','c', 'F', 'f', 'K', 'k'],
                            default='C')

        return parser.parse_args()



if __name__ == '__main__':
    Weather = FetchWeather()
    Weather.main()