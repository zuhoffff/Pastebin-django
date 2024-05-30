import boto3
import logging
from os import environ

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