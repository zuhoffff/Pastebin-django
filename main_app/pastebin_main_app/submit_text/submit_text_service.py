import dateutil.parser as dp
import logging
import requests
from os import environ
import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
LOGGER = logging.getLogger(__name__)

HASH_SERVER_URI = environ.get('HASH_SERVER_URI')

class SubmitTextService():
        # Constants for error messages
    ERROR_HASH_SERVER = 'Hash-server error'
    ERROR_CREDENTIALS = 'Credentials error'
    ERROR_CLIENT = 'Client error'
    ERROR_GENERIC = 'An error occurred'
    ERROR_MISSING_DATA = 'Missing frontend data'
    ERROR_INVALID_METHOD = 'Invalid request method'

    def __init__(self, hash_server_uri) -> None:
        self.hash_server_uri = hash_server_uri

    def get_hash_from_server(self):
        try:
            response = requests.get(self.hash_server_uri)
            response.raise_for_status()
            return response.json().get('hash')
        except Exception:
            raise Exception(self.ERROR_HASH_SERVER)
    
    @staticmethod
    def convert_string_to_unix_time(time_str) -> float:
        ''' Converts {days}.{hours}.{minutes} to unix time'''
        # Parse the expiry string
        days, hours, minutes = map(int, time_str.split('.'))
        time_til_expiry = datetime.timedelta(days=days, hours=hours, minutes=minutes)
        return float(time_til_expiry.timestamp())
    
    @staticmethod
    def convert_iso_to_unix(time_iso8601):
        parsed_t = dp.parse(time_iso8601)
        t_in_seconds = parsed_t.timestamp()
        return float(t_in_seconds)