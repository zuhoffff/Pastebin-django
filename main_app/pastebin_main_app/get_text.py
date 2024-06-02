from django.http import JsonResponse
from .models import Metadata
from django.views.decorators.csrf import csrf_exempt
import logging
from pastebin_main_app.s3_handler import retrieve_from_s3
from django.shortcuts import render
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError


@csrf_exempt
def get_text(request, block_id):
    if request.method == 'GET':    
        try:
            metadata = Metadata.objects.get(pk=block_id) # pk - primary key (id)
            curr_author = metadata.author
            curr_key = metadata.s3_key
        except metadata.DoesNotExist as e:
            return JsonResponse({f'error': 'database error  {e}'}, status=500)

        try:
            text =retrieve_from_s3(curr_key)

            return render(request, 'block.html', {'block_id': block_id, 'text': text, 'author': curr_author})
        
        except (NoCredentialsError, PartialCredentialsError) as e:
            return JsonResponse({f'error': 'Credentials error {e}'}, status=500)
        
        except ClientError as e:
            return JsonResponse({f'error': 'Client error {e}'}, status=500)
        
        except Exception as e:
            return JsonResponse({f'error': 'An error occurred {e}'}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)