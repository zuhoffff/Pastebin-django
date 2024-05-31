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


@csrf_exempt
def submit_text(request):
    if request.method == 'POST':
        text_input = request.POST.get('text')
        timestamp = request.POST.get('timestamp')
        user_agent = request.POST.get('userAgent')

        if text_input and timestamp and user_agent:
            LOGGER.info('Data receiced!')
            
            # Make request to hash-server
            try:
                resp = requests.get(environ.get('HASH_SERVER_URI'))
                resp.raise_for_status()
                curr_key=resp.json().get('hash')
                LOGGER.info(f'Obtained hash: ***')
                
            except Exception as e:
                LOGGER.info(f'Could not get hash from the hash-server {e}')
                return JsonResponse({'error': 'Hash-server error:'}, status=500)

            # Save the metadata to your database
            new_entry = Metadata.objects.create(
                timestamp=timestamp,
                user_agent=user_agent,
                s3_key=curr_key 
            )
            new_entry.save()

            LOGGER.info('db entry added')

            # Save the text into s3 blobstore:
            try:
                s3.put_object(Bucket=BUCKET_NAME, Key=str(curr_key), Body=str(text_input)) # key must be string
                LOGGER.info('Object uploaded, trying to send link')

                curr_url=f'/block/{new_entry.id}/'
                return JsonResponse({'message': 'Text saved successfully', 'url': curr_url})
            
            except (NoCredentialsError, PartialCredentialsError) as e:
                LOGGER.info({'error': 'Credentials error'})
                return JsonResponse({'error': 'Credentials error'}, status=500)
            
            except ClientError as e:
                LOGGER.info({'error': 'Client error'})
                return JsonResponse({'error': 'Client error'}, status=500)
            
            except Exception as e:
                LOGGER.info({'error': 'An error occurred'})
                return JsonResponse({'error': 'An error occurred'}, status=500)
        
        else:
            return JsonResponse({'error': 'Missing data'}, status=400)
        
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    
import base64