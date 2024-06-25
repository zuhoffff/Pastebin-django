import boto3
import logging
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
from decouple import config

# set up the logs
logger = logging.getLogger(__name__)

class S3Service():
    # Constants for error messages
    ERROR_CREDENTIALS = 'Credentials error'
    ERROR_CLIENT = 'Client error'
    ERROR_GENERIC = 'An error occurred'

    def __init__(self, aws_access_key_id, aws_secret_access_key, bucket_name) -> None:
        self.s3_client=boto3.client('s3',
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key)
        self.bucket_name = bucket_name

    def check_s3_connection(self):
        try:
            self.s3_client.list_buckets()
            logger.info('s3 connected')
        except ClientError:
            logger.error('s3 client error')
            raise
            
    def upload_to_s3(self, s3_key, text_input):
        try:
            self.s3_client.put_object(Bucket=self.bucket_name, Key=str(s3_key), Body=str(text_input))
            logger.info('Object uploaded to S3')
        except (NoCredentialsError, PartialCredentialsError) as e:
            logger.error(f'{self.__class__.ERROR_CREDENTIALS}: {e}')
            raise
        except ClientError as e:
            logger.error(f'{self.__class__.ERROR_CLIENT}: {e}')
            raise
        except Exception as e:
            logger.error(f'{self.__class__.ERROR_GENERIC}: {e}')
            raise

    def retrieve_from_s3(self, s3_key):
        s3_object = self.s3_client.get_object(Bucket=self.bucket_name, Key=s3_key)
        return s3_object['Body'].read().decode('utf-8')

    def delete_from_s3(self, s3_key):
        self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
        logger.info('Object deleted from s3')

key_id = config('aws_access_key_id', default='none')
secret_key = config('aws_secret_access_key', default = 'none')
BUCKET_NAME=config('BUCKET_NAME',default= 'my_pastebin_bucket')

myS3Service = S3Service(key_id, secret_key, BUCKET_NAME)
myS3Service.check_s3_connection()
