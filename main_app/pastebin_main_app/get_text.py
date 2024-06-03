from django.shortcuts import render, get_object_or_404
from django.contrib.auth.hashers import check_password
from .models import Metadata
from django.http import JsonResponse
import time
from pastebin_main_app.s3_handler import retrieve_from_s3

def get_text(request, block_id):
    metadata = get_object_or_404(Metadata, pk=block_id)
    curr_key = metadata.s3_key
    curr_expiry = metadata.expiry_time
    curr_pswd = metadata.password

    # Check if the paste has expired
    if curr_expiry < time.time():
        return render(request, 'expired.html')

    # If the text is not protected, return it immediately
    if not curr_pswd:
        try:
            text = retrieve_from_s3(curr_key)
            return render(request, 'block.html', {'block_id': block_id, 'text': text, 'author': metadata.author, 'expiry': curr_expiry})
        except Exception as e:
            return render(request, 'expired.html')

    # If the text is protected, handle authentication
    if request.method == 'POST':
        pswrd_for_check = request.POST.get('password', '')
        if check_password(pswrd_for_check, curr_pswd):
            # Password is correct, set session flag
            request.session['authenticated'] = True
            try:
                text = retrieve_from_s3(curr_key)
                return render(request, 'block.html', {'block_id': block_id, 'text': text, 'author': metadata.author, 'expiry': curr_expiry})
            except Exception as e:
                return render(request, 'expired.html')
        else:
            # Incorrect password, prompt again
            return JsonResponse({'prompt_again': True})
    else:
        # If not a POST request, prompt for password
        return JsonResponse({'prompt_again': True})
