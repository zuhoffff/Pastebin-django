import boto3
import logging
from os import environ
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError

# set up the logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
LOGGER = logging.getLogger(__name__)

key_id = environ.get('aws_access_key_id')
secret_key = environ.get('aws_secret_access_key')
BUCKET_NAME=environ.get('BUCKET_NAME')

s3=boto3.client('s3',
                aws_access_key_id=key_id,
                aws_secret_access_key=secret_key)

# Check if the S3 connection is successful
try:
    s3.list_buckets()
    LOGGER.info('Connected to S3 successfully.')
except Exception as e:
    LOGGER.error('Failed to connect to S3:', exc_info=True)

# Constants for error messages
ERROR_HASH_SERVER = 'Hash-server error'
ERROR_CREDENTIALS = 'Credentials error'
ERROR_CLIENT = 'Client error'
ERROR_GENERIC = 'An error occurred'
ERROR_MISSING_DATA = 'Missing data'
ERROR_INVALID_METHOD = 'Invalid request method'

def upload_to_s3(s3_key, text_input):
    try:
        s3.put_object(Bucket=BUCKET_NAME, Key=str(s3_key), Body=str(text_input))
        LOGGER.info('Object uploaded to S3')
    except (NoCredentialsError, PartialCredentialsError) as e:
        LOGGER.error(f'{ERROR_CREDENTIALS}: {e}')
        raise
    except ClientError as e:
        LOGGER.error(f'{ERROR_CLIENT}: {e}')
        raise
    except Exception as e:
        LOGGER.error(f'{ERROR_GENERIC}: {e}')
        raise

def retrieve_from_s3(s3_key):
    s3_object = s3.get_object(Bucket=BUCKET_NAME, Key=s3_key)
    return s3_object['Body'].read().decode('utf-8')

def delete_from_s3(s3_key):
    s3.delete_object(Bucket=BUCKET_NAME, Key=s3_key)
    LOGGER.info('Object deleted')
    return 0