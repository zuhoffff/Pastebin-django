import boto3
import logging
from os import environ
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError

# set up the logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
LOGGER = logging.getLogger(__name__)

class S3Service():
    # Constants for error messages
    ERROR_CREDENTIALS = 'Credentials error'
    ERROR_CLIENT = 'Client error'
    ERROR_GENERIC = 'An error occurred'

    def __init__(self, aws_access_key_id, aws_secret_access_key, bucket_name) -> None:
        self.s3 = boto3.client('s3',
                               aws_access_key_id,
                               aws_secret_access_key)
        self.bucket_name = bucket_name
    
    def upload_to_s3(self, s3_key, text_input):
        try:
            self.s3.put_object(Bucket=self.bucket_name, Key=str(s3_key), Body=str(text_input))
            LOGGER.info('Object uploaded to S3')
        except (NoCredentialsError, PartialCredentialsError) as e:
            LOGGER.error(f'{S3Service.ERROR_CREDENTIALS}: {e}')
            raise
        except ClientError as e:
            LOGGER.error(f'{S3Service.ERROR_CLIENT}: {e}')
            raise
        except Exception as e:
            LOGGER.error(f'{S3Service.ERROR_GENERIC}: {e}')
            raise

    def retrieve_from_s3(self, s3_key):
        s3_object = self.s3.get_object(Bucket=self.bucket_name, Key=s3_key)
        return s3_object['Body'].read().decode('utf-8')

    def delete_from_s3(self, s3_key):
        self.s3.delete_object(Bucket=self.bucket_name, Key=s3_key)
        LOGGER.info('Object deleted')

key_id = environ.get('aws_access_key_id')
secret_key = environ.get('aws_secret_access_key')
BUCKET_NAME=environ.get('BUCKET_NAME')

myS3Service = S3Service(key_id, secret_key, BUCKET_NAME)
