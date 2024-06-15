from datetime import datetime, timezone
import dateutil.parser as dp
import logging
import requests
from os import environ

logger = logging.getLogger(__name__)

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
            hash = response.json().get('hash')
            logger.info(hash)
            return hash
        except Exception:
            logger.exception('Hash server error!')
            raise Exception(self.ERROR_HASH_SERVER)
    
    @staticmethod
    def convert_timedelta_to_unix(timedelta_obj):
        epoch = datetime.utcfromtimestamp(0)
        return int((epoch + timedelta_obj).timestamp())

    @staticmethod
    def convert_iso_to_unix(time_iso8601):
        parsed_t = dp.parse(time_iso8601)
        t_in_seconds = parsed_t.timestamp()
        return float(t_in_seconds)
    
    @staticmethod
    def convert_datetime_to_utc_timestamp(dt: datetime) -> int:
        """
        make sure that timezone is utc:
        """
        return int(dt.replace(tzinfo=timezone.utc).timestamp())
    
    @staticmethod
    def get_current_int_utc_timestamp() -> int:
        return int(datetime.utcnow().timestamp())

    
submitTextService = SubmitTextService(HASH_SERVER_URI)