from django.http.response import HttpResponse as HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.hashers import check_password
from ..models import Metadata
from django.core.cache import cache
import logging
from pastebin_main_app.utils.s3_handler import myS3Service
from django.views import View
from django.contrib.auth.hashers import check_password
from pastebin_main_app.utils.s3_handler import myS3Service
import logging
from pastebin_main_app.utils.s3_handler import myS3Service
from django.views.generic.detail import DetailView
from django.forms.models import model_to_dict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# TODO: implement session and authorisation

class CheckProtection(View):
    model = Metadata

    def get(self, request, slug):
        self.obj = get_object_or_404(self.model, slug=slug)
        if self.obj.is_protected():
            return redirect('paste_password_prompt', slug=slug)
        else:
            return redirect('paste_detail_view',slug=slug)
        
class PasswordPromptView(View):
    model = Metadata

    def get(self, request, slug):
        return render(request, 'password_prompt.html', {'slug': slug})
    
    def post(self, request, slug):
        self.obj = get_object_or_404(self.model, slug=slug)
        password = request.POST.get('password')
        if check_password(password, self.obj.password):
            logger.info('Password correct')
            return redirect('paste_detail_view', slug=slug)
        else:
            logger.info('bad password')
            return render(request, 'password_prompt.html', {'slug': slug})


class PasteDetailView(View):
    model = Metadata
    cache_timeout = 300
    payload = {}

    def get(self, request, slug) -> HttpResponse:
        # Check if cached:
        self.payload = cache.get(slug)
        if not self.payload:
            logger.info('hit db')
            self.obj=get_object_or_404(self.model, slug=slug)
            self.payload=model_to_dict(self.obj)
            self.payload['text']=myS3Service.retrieve_from_s3(self.obj.slug)
            # Convert expiry time to convinient format
            cache.set(slug, self.payload, timeout=self.cache_timeout)
        else:
            logger.info('hit cache')
        return render(request, 'view_paste.html', self.payload)