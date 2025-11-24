import requests
import logging


class WeatherAPIURL:
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
    CLOUD = 'cloud'
    WINDSPEED = 'wind_mph'
    HUMIDITY = 'humidity'
    PRESSURE = 'pressure_mb'
    ALLCURRENTKEYS = [LASTUPDATED, CLOUD, WINDSPEED, HUMIDITY, PRESSURE]
    ALLCURRENTCSVCOLS = ['Last Updated', 'Clouds (%)', 'Wind Speed (mph)', 'Humidity (%)', 'Pressure (mb)']

class TemperatureAPIFields:
    temperature_mapping = {'c':'temp_c', 'f':'temp_f'}


class WeatherAPIClient:
    '''
    API client wrapper for Weather API
    '''
    def __init__(self, api_key):
        self.api_key = api_key
        api_url = WeatherAPIURL()
        self.url = api_url.URL
        self.logger = self._setup_logger()
        self.RelevantLocationData = RelevantLocationData()
        self.RelevantCurrentData = RelevantCurrentData()

    def build_query(self, csv_row):
        '''
        Defines the location string for the 'q' parameter in the API query.
        All components must be separated by a comma (,).
        The order listed is recommended for clarity, but the API's geocoding engine can often process valid components in any order.
        WeatherAPI normalises internally, so format of string is irrelevant (e.g. capitalisation).
        Query Structure: https://www.weatherapi.com/docs/
        Region field is equivalent to state if available.
        Data will be fetched only if the recommended location data has been provided.
        NOTE: Threshold for input data can be altered.
        NOTE: Returned data needs to be checked to ensure correct location has been fetched. eg Paris, FR does not return Paris

        The following are RECOMMENDED/ALLOWED combinations for an unambiguous query and will return fetched data:
            - Zip Code + Country - Best for international codes.
            - City + Country
            - City + State + Country

        The following are AMBIGUOUS/NOT RECOMMENDED combinations and will not return fetched data:
            - Zip Code alone - Generally works for common systems like US/UK but not specific enough for other countries.
            - City alone - Likely returns an incorrect location due to multiple matches.
            - City + State - Better, but lacks the necessary specificity of a country code.

        The following are NOT ALLOWED combinations (Insufficient data for a specific point) and will not return fetched data:
            - Country only
            - State only
            - State + Country without city/zip
        """
        '''
        # strip whitespaces at end/ beginning for consistent query format
        original_data = {loc: csv_row[loc].strip() for loc in self.RelevantLocationData.ALLORIGINALLOCATIONKEYS}

        if (original_data[self.RelevantLocationData.COUNTRY] and (original_data[self.RelevantLocationData.ZIPCODE] or
                                                                  original_data[self.RelevantLocationData.CITY])):
            self.logger.info(f'Valid CSV input row: {original_data}')
            parts = [val for key, val in original_data.items() if val]
            query =  ", ".join(parts).lower() # so same location but different cases are identified
            self.logger.info(f'Query: {query}')
            return query, original_data

        else:
            self.logger.info(f'Insufficient data in csv row {original_data}. \n Required: Country and (zipcode or city).')
            return None, original_data


    def fetch_weather(self, query):
        '''
        Use WeatherAPI to fetch weather data.
        '''
        params = {
            'q': query,
            'key': self.api_key
        }

        try:
            response = requests.get(self.url, params=params)
            response.raise_for_status()
        except Exception as e:
            self.logger.error(f"API error for query '{query}': {e}")
            return None, None  # signals failure and row remains unchanged
        self.logger.info('Successful API response')

        return response.json(), query

    def _setup_logger(self):
        '''
        Initialize and configure logger for API client.
        '''
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger('WeatherAPIClient')
