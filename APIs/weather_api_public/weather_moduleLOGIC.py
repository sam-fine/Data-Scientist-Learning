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
        Interviewer Notes – main():

        1. Why DictReader instead of pandas? SCALABLE
           - DictReader streams the CSV row-by-row without loading the entire file into memory, which is more efficient and SCALABLE for large datasets.

        2. Why iterate using the CSV iterator?
           - It enables constant-memory processing and avoids building intermediate data structures; each row is processed independently.

        3. Why use context managers for both input and output?
           - They guarantee clean file handling, automatic resource cleanup, and prevent file descriptor leaks
           (too many files open at same time as it closes them), which is critical in batch processing (many open files).

        4. Why separate the reader and writer contexts?
           - It keeps responsibilities clear: one handles input iteration, while the other cleanly manages CSV output and header initialization.

        5. Why use DictWriter for output?
           - DictWriter preserves explicit column ordering, ensures every row has consistent keys, and integrates cleanly with the merged dictionaries produced by the parser.

        6. How does main() orchestrate the pipeline?
           - main() coordinates reading each row, invoking fetch_data(), enriching it through parse_raw_data(), and writing unified rows to the output file.

        7. Why write rows immediately rather than buffering?
           - Streaming each row to disk avoids memory overhead and supports long-running jobs without storing partial results in memory.

        8. Why derive the output filename dynamically?
           - Including timestamps prevents accidental overwrites, improves reproducibility, and makes output files easier to identify.

        9. Why log progress inside main()?
           - To give the user visibility into processing, especially for larger CSVs where silent execution may appear stalled.
        '''



    def fetch_data(self, csv_row):
        '''
        Interviewer Notes – fetch_data():

        1. What does fetch_data do?
           - It takes a CSV row, builds a query using build_query(), and decides whether an API call is needed.

        2. Why check if the query is None?
           - If the row does not contain enough information to form a valid location, the function skips the API call and returns the row unchanged.

        3. Why check the cache before calling the API?
           - To avoid repeated API calls for the same location, reduce latency, and improve efficiency when many rows refer to identical locations.

        5. Why separate query building from data fetching?
           - Query construction and API access have different responsibilities; separating them improves readability and testability.

        6. What happens if the query is valid and not cached?
           - The function calls the WeatherApiClient to retrieve fresh data and stores the successful result in the cache.

        7. Why store API results in the cache only after a successful call?
           - To avoid populating the cache with invalid or incomplete data if the API request fails.

        8. What does the function return?
           - The raw API response (or None), the cleaned CSV row, and the final query string so downstream functions can parse or write the row appropriately.
        '''

    def temperature_unit_column(self):
        '''
        Interviewer Notes – temperature_unit_column():

        1. What does the function do?
           - It determines which temperature unit the user requested and maps that unit to the correct WeatherAPI field (C, F, or derived K).

        2. Why is this needed?
           - WeatherAPI returns separate fields for Celsius and Fahrenheit, and Kelvin must be computed manually. This function provides a consistent way to choose the correct data source.

        3. How does it choose the correct column?
           - It checks the user-supplied unit flag, validates it, and returns the corresponding API field name (e.g., 'temp_c' or 'temp_f'), or indicates that Kelvin must be calculated.

        4. Why separate this logic into its own function?
           - Keeping unit-selection isolated improves readability, avoids scattering conditional checks, and makes it easier to extend with more units later.

        5. What happens for invalid or unsupported units?
           - The function logs the issue and falls back to a default (typically Celsius), ensuring the pipeline remains robust.

        6. How is it used downstream?
           - parse_raw_data() uses the returned field key to extract the correct temperature from the API response before writing the final CSV output.
        '''

    def parse_raw_data(self, raw_data, original_data, query):
        '''
        Interviewer Notes – parse_raw_data():

        1. Purpose of the function:
           - This function merges the original CSV row with the weather data returned by the API, producing a unified output dictionary ready to be written to the final CSV.

        2. Handling original input fields:
           - Original CSV fields are preserved to maintain a clear and traceable mapping from input to output.
           - If a CSV field is missing or empty, the function fills it using the corresponding API field (e.g., city → name, state → region).
           - This ensures the output is complete and consistent even when user input is partially missing.

        3. API-to-CSV mapping:
           - City and state are mapped manually from the API response (city → 'name', state → 'region').
           - This approach works but could be refactored and generalized into a lookup table for cleaner extensibility.

        4. Temperature and local time:
           - Local time and temperature are inserted separately because temperature depends on the user-selected unit, and Kelvin must be computed manually.
           - In hindsight, these could be unified into a more generic “field mapping” mechanism for consistency.

        5. Parsing current weather fields:
           - For current weather metrics (e.g., cloud, wind, humidity), I used zip() to pair API field names with their human-readable CSV column labels.
           - This reduces duplication and makes it easy to add or remove fields by editing a single source of truth.

        6. Using the cache:
           - If the result comes from cache, parse_raw_data() reuses the cached API structure to avoid reprocessing.
           - This keeps the function stateless and ensures consistent results for repeated queries.

        7. Output structure:
           - The final dictionary always contains: original CSV fields, enriched location fields from the API, temperature in the requested unit, local time, and the selected weather metrics.
           - This guarantees predictable ordering and completeness for the output CSV.
        '''

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
                            help="Full path to input csv example: r'C:/Users/example_input.csv'",
                            required=True)
        parser.add_argument("-sp", "--save-path",
                            dest="SAVE_FILE_BASE_PATH",
                            help="parent folder that will hold output files example: r'C:/Users/weather_data'",
                            required=True)
        parser.add_argument("-apik", "--api-key",
                            dest="API_KEY",
                            help="Personal API Key for Weather API",
                            required=True)
        parser.add_argument("-tu", "--temp-unit",
                            dest="temperature_unit",
                            help="Decide which temperature unit to use",
                            choices=['C','c', 'F', 'f', 'K', 'k'],
                            default='C')

        return parser.parse_args()

# command line example
# python weather_module.py -ip "C:\Users\example_input.csv" -sp "C:\Users\weather_data" -apik "abcde" -tu "k"



if __name__ == '__main__':
    Weather = FetchWeather()
    Weather.main()

'''
✔ “What were the main design principles you followed?”

I focused on modularity, separation of concerns, robustness against bad data, and efficient streaming to handle large CSVs safely.

✔ “Why did you choose this structure instead of a more compact script?”

Splitting logic into dedicated components makes the code easier to test, extend, and maintain, especially as requirements grow.

✔ “Why wrap requests in try/except?”

To prevent network or HTTP errors from terminating the pipeline and to handle failures gracefully on a per-row basis.

✔ “How would you add retry logic or backoff?”

I’d wrap the request in a retry loop with exponential backoff using time.sleep or a library like tenacity to handle transient failures.

✔ “How do you ensure your program doesn’t crash on one bad API response?”

By catching exceptions, logging the issue, returning None, and allowing the caller to continue writing the row unchanged.

✔ “How would you scale the cache for a huge file?”

I’d use a disk-backed cache or an LRU cache to avoid unbounded memory growth while still preventing duplicate calls.

✔ “Why manually map ‘name’ → city and ‘region’ → state?”

WeatherAPI uses different field names than the CSV, so explicit mapping ensures the output matches the expected schema.

✔ “Why not just use print statements?”

Logging provides structured, timestamped, level-controlled output, which is essential for debugging batch processes and production use.

✔ “How would you improve the logging for production?”

I’d add rotating file handlers, JSON-structured logs, and environment-based log levels to integrate with monitoring systems.

✔ “What would you change if the CSV had 5 million rows?”

I’d stream the file exactly as now but also consider batching writes, using multiprocessing, and implementing persistent caching.

✔ “How would you parallelize API calls?”

I’d use a worker pool (multiprocessing, asyncio, or ThreadPoolExecutor) while ensuring rate-limit safety and consolidating results.

✔ “How would you handle API rate limits?”

I’d track call frequency and throttle requests or queue them, incorporating sleep intervals or backoff when limits are approached.

✔ “How would you design this as a microservice?”

I’d expose an endpoint that accepts location data, validates it, fetches weather via a service layer, caches results, and returns structured JSON, with clear separation between API, business logic, and data access layers.
'''