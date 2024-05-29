from django.http import JsonResponse
from .models import Metadata
from django.views.decorators.csrf import csrf_exempt
import logging
from pastebin_main_app.setup_s3 import s3, BUCKET_NAME
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
LOGGER = logging.getLogger(__name__)


@csrf_exempt
def submit_text(request):
    if request.method == 'POST':
        text_input = request.POST.get('text')
        timestamp = request.POST.get('timestamp')
        user_agent = request.POST.get('userAgent')

        if text_input and timestamp and user_agent:
            
            # Save the metadata to your database
            new_entry = Metadata.objects.create(
                timestamp=timestamp,
                user_agent=user_agent
            )   
            
            # TODO: Get the key from hash-server and save it to db
            # temporary I'll use id as s3_key
            s3_key = new_entry.id

            # Save the text into s3 blobstore:
            try:
                s3.put_object(text_input, s3_key)

                curr_url=f'/block/{new_entry.id}/'

                return JsonResponse({'message': 'Text saved successfully', 'url': curr_url})
            except (NoCredentialsError, PartialCredentialsError) as e:
                return JsonResponse({'error': 'Credentials error'}, status=500)
            
            except ClientError as e:
                return JsonResponse({'error': 'Client error'}, status=500)
            
            except Exception as e:
                return JsonResponse({'error': 'An error occurred'}, status=500)
        
        else:
            return JsonResponse({'error': 'Missing data'}, status=400)
        
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)