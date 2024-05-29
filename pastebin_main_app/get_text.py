from django.http import JsonResponse
from .models import Metadata
from django.views.decorators.csrf import csrf_exempt
import logging
from pastebin_main_app.setup_s3 import s3, BUCKET_NAME
from django.shortcuts import render, get_object_or_404
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError


@csrf_exempt
def get_text(request, block_id):

    metadata = get_object_or_404(Metadata, id=block_id)

    curr_key = metadata.s3_key

    try:
        s3_object = s3.get_object(Bucket=BUCKET_NAME, Key=curr_key)
        text = s3_object['Body'].read().decode('utf-8')
        return render(request, 'block.html', {block_id: block_id, text: text})
    
    except (NoCredentialsError, PartialCredentialsError) as e:
        return JsonResponse({'error': 'Credentials error'}, status=500)
    
    except ClientError as e:
        return JsonResponse({'error': 'Client error'}, status=500)
    
    except Exception as e:
        return JsonResponse({'error': 'An error occurred'}, status=500)
