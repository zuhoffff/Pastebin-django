from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from .models import Metadata
from django.views.decorators.csrf import csrf_exempt
import logging
from pastebin_main_app.s3_handler import upload_to_s3
import requests
from os import environ
from pastebin_main_app.expiry_controller import add_event
import pastebin_main_app.apps as newExpiryController

# TODO: remake into oop if sufficient

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
LOGGER = logging.getLogger(__name__)

HASH_SERVER_URI = environ.get('HASH_SERVER_URI')

# Constants for error messages
ERROR_HASH_SERVER = 'Hash-server error'
ERROR_CREDENTIALS = 'Credentials error'
ERROR_CLIENT = 'Client error'
ERROR_GENERIC = 'An error occurred'
ERROR_MISSING_DATA = 'Missing frontend data'
ERROR_INVALID_METHOD = 'Invalid request method'

def get_hash_from_server():
    response = requests.get(HASH_SERVER_URI)
    response.raise_for_status()
    return response.json().get('hash')

@csrf_exempt
def submit_text(request):
    if request.method != 'POST':
        return JsonResponse({'error': ERROR_INVALID_METHOD}, status=405)
    
    # Returns None for optional field not specified
    raw_data = request.body.decode('utf-8')
    LOGGER.info("Received form data: %s", raw_data)
        
    # Parse the form data
    form_data = request.POST
    
    # Retrieve individual fields from the form data
    text_input = form_data.get('text')
    timestamp = form_data.get('timestamp')
    user_agent = form_data.get('userAgent')
    author = form_data.get('author')
    password = form_data.get('password')
    # Perform conversion to float unix format
    expiry_time = float(form_data.get('expirationTime'))/1000

    # Make sure author isn't None:
    if not author: author = 'Anonymous'

    # Hash the password if its provided
    if password:
        hashed_password = make_password(password)
    else:
        hashed_password = None

    if not (text_input and timestamp and user_agent and expiry_time):
        LOGGER.info(ERROR_MISSING_DATA)
        return JsonResponse({'error': ERROR_MISSING_DATA}, status=400)
    


    # Get hash for url from the hash-server
    try:
        new_hash = get_hash_from_server()
    except requests.RequestException as e:
        LOGGER.error(f'{ERROR_HASH_SERVER},{e}')
        return JsonResponse({'error': ERROR_HASH_SERVER}, status=400)

    # Write down to database
    new_entry = Metadata.objects.create(
        timestamp=timestamp,
        user_agent=user_agent,
        url=new_hash,
        expiry_time=expiry_time,
        # Optional:
        author=author,
        # Use the encrypted password
        password=hashed_password
    )
    new_entry.save()

    # Create url for new paste
    curr_url = f'/block/{new_entry.url}/'

    # Create s3_key do to convention:
    s3_key = new_entry.compose_key()

    # Upload data to s3 blobstore
    try:
        upload_to_s3(s3_key, text_input)

        # Add the paste to expiry registry
        newExpiryController.add_event(expiry_time=expiry_time, id=new_entry.id)
        LOGGER.info('Entry added to expiry controller...')

        return JsonResponse({'message': 'Text saved successfully', 'url': curr_url})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)