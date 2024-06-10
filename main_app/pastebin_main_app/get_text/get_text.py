from django.http.response import HttpResponse as HttpResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.hashers import check_password
from ..models import Metadata
from django.http import HttpRequest, JsonResponse
import time
from django.core.cache import cache
import logging
from pastebin_main_app.utils.s3_handler import myS3Service
from django.views.generic.detail import DetailView

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_text(request, url):
    # Check if object on the cache
    current_data = cache.get(url)

    if current_data:
        logger.info('hit cache')
    else:
        metadata = get_object_or_404(Metadata, url=url)
        time_til_expiry = metadata.expiry_time - metadata.timestamp
        current_data = {
        'block_id': metadata.id,
        'expiry': time_til_expiry,
        'password': metadata.password,
        'author': metadata.author,
        'key': metadata.compose_key(),
        }
        cache.set(url, current_data, timeout=300)
        metadata.key_usages+=1
        metadata.save()
        logger.info('hit db')

    # Adjust the json to send it to the page
    current_data['text'] = myS3Service.retrieve_from_s3(current_data['key'])

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
