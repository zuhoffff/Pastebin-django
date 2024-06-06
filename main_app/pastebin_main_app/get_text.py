from django.shortcuts import render, get_object_or_404
from django.contrib.auth.hashers import check_password
from .models import Metadata
from django.http import JsonResponse
import time
from pastebin_main_app.s3_handler import retrieve_from_s3
from django.core.cache import cache
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
LOGGER = logging.getLogger(__name__)

def get_text(request, url):
    # Check if object on the cache
    current_data = cache.get(url)

    if current_data:
        LOGGER.info('hit cache')
    else:
        metadata = get_object_or_404(Metadata, url=url)
        current_data = {
        'block_id': metadata.id,
        'expiry': metadata.expiry_time,
        'password': metadata.password,
        'author': metadata.author,
        'key': metadata.compose_key(),
        }
        cache.set(url, current_data, timeout=300)
        metadata.key_usages+=1
        metadata.save()
        LOGGER.info('hit db')

    # Check if the paste has expired
    if current_data['expiry'] < time.time():
        return render(request, 'expired.html')

    # Adjust the json to send it to the page
    current_data['text'] = retrieve_from_s3(current_data['key'])

    # If the text is not protected, return it immediately
    if not current_data['password']:
        try:
            return render(request, 'block.html', current_data)
        except Exception as e:
            return render(request, 'expired.html')
    
    # If the text is protected, handle authentication
    else:
        if not request.method == 'POST':
            # If not a POST request, prompt for password
            return render(request, 'password_prompt.html', {'submission_id': url})
        else:
            pswrd_for_check = request.POST.get('password', '')
            if check_password(pswrd_for_check, current_data['password']):
                # Password is correct, set session flag
                request.session['authenticated'] = True
                try:
                    return render(request, 'block.html', current_data)
                except Exception as e:
                    return render(request, 'expired.html')
            else:
                # Incorrect password, prompt again
                return JsonResponse({'prompt_again': True})
