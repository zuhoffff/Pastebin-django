from django.http import JsonResponse
from .models import Metadata
from django.views.decorators.csrf import csrf_exempt
import logging
from pastebin_main_app.s3_handler import upload_to_s3
import requests
from os import environ
from pastebin_main_app.expiry_controller import add_event


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
    text_input = request.POST.get('text')
    timestamp = request.POST.get('timestamp')
    user_agent = request.POST.get('userAgent')
    author = request.POST.get('author')
    password = request.POST.get('password')
    # Perform conversion to float unix format
    expiry_time = float(request.POST.get('expirationTime'))/1000

    # Make sure author isn't None:
    if not author: author = 'Anonymous' 

    if not (text_input and timestamp and user_agent and expiry_time):
        LOGGER.info(ERROR_MISSING_DATA)
        return JsonResponse({'error': ERROR_MISSING_DATA}, status=400)

    # Get hash from the hash-server
    try:
        s3_key = get_hash_from_server()
    except requests.RequestException as e:
        LOGGER.error(f'{ERROR_HASH_SERVER},{e}')
        return JsonResponse({'error': ERROR_HASH_SERVER}, status=400)

    # Write down to database
    new_entry = Metadata.objects.create(
        timestamp=timestamp,
        user_agent=user_agent,
        s3_key=s3_key,
        expiry_time=expiry_time,
        # Optional:
        author=author,
        password=password
    )
    new_entry.save()

    # Create url for new paste
    curr_url = f'/block/{new_entry.id}/'

    # Upload data to s3 blobstore
    try:
        upload_to_s3(s3_key, text_input)

        # Add the pasete to expiry registry
        add_event(expiry_time=expiry_time, id=new_entry.id)

        return JsonResponse({'message': 'Text saved successfully', 'url': curr_url})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)