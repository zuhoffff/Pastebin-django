from django.http import JsonResponse
from .models import Metadata
from django.views.decorators.csrf import csrf_exempt
import logging
from pastebin_main_app.setup_s3 import s3, BUCKET_NAME
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
import requests
from os import environ

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
LOGGER = logging.getLogger(__name__)

HASH_SERVER_URI = environ.get('HASH_SERVER_URI')

# Constants for error messages
ERROR_HASH_SERVER = 'Hash-server error'
ERROR_CREDENTIALS = 'Credentials error'
ERROR_CLIENT = 'Client error'
ERROR_GENERIC = 'An error occurred'
ERROR_MISSING_DATA = 'Missing data'
ERROR_INVALID_METHOD = 'Invalid request method'

def get_hash_from_server():
    try:
        response = requests.get(HASH_SERVER_URI)
        response.raise_for_status()
        return response.json().get('hash')
    except requests.RequestException as e:
        LOGGER.error(f'Error getting hash from hash-server: {e}')
        raise

def save_metadata(timestamp, user_agent, s3_key, author):
    new_entry = Metadata.objects.create(
        timestamp=timestamp,
        user_agent=user_agent,
        s3_key=s3_key,
        author=author
    )
    new_entry.save()
    LOGGER.info('Database entry added')
    return new_entry

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

@csrf_exempt
def submit_text(request):
    if request.method != 'POST':
        return JsonResponse({'error': ERROR_INVALID_METHOD}, status=405)
    
    text_input = request.POST.get('text')
    timestamp = request.POST.get('timestamp')
    user_agent = request.POST.get('userAgent')
    author = request.POST.get('author')
    #TODO: MAKE SURE TIME FORMAT OF EXPIERY DATA CORRESPONDS TO TIMESTAMP TIME FORMAT. and delete temporary logger
    expirationTime = request.POST.get('expirationTime')
    LOGGER.info(expirationTime)
    LOGGER.info(timestamp)

    if not author:  author='Anonymous' # make sure the variable is not empty string or None

    if not (text_input and timestamp and user_agent and expirationTime):
        return JsonResponse({'error': ERROR_MISSING_DATA}, status=400)

    LOGGER.info('Data received')

    try:
        s3_key = get_hash_from_server()
        LOGGER.info(f'Obtained hash: {s3_key}')

        new_entry = save_metadata(timestamp, user_agent, s3_key, author)
        
        upload_to_s3(s3_key, text_input)

        curr_url = f'/block/{new_entry.id}/'
        return JsonResponse({'message': 'Text saved successfully', 'url': curr_url})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)