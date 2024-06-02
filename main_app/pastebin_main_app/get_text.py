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

        # Try to get the by url tail (id) 
        try:
            metadata = Metadata.objects.get(pk=block_id) # pk - primary key (id)
            curr_author = metadata.author
            curr_key = metadata.s3_key
            curr_expiry=metadata.expiry_time
            curr_pswd=metadata.password
        except metadata.DoesNotExist as e:
            return JsonResponse({f'error': 'database error  {e}'}, status=500)

        # Check if paste has password set
        if curr_pswd:
            pass

        # Try to get the text from s3
        try:
            text=retrieve_from_s3(curr_key)

            return render(request, 'block.html', {'block_id': block_id, 'text': text, 'author': curr_author, 'expiry': curr_expiry})
                
        except Exception as e:
            # if it isn't there, it's probably expired
            return render(request, 'expired.html')
            
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)