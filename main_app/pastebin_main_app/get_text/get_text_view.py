from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.hashers import check_password
from ..models import Metadata
from django.core.cache import cache
import logging
from pastebin_main_app.utils.s3_handler import myS3Service
from django.views import View
from django.contrib.auth.hashers import check_password
import logging
from django.forms.models import model_to_dict

logger = logging.getLogger(__name__)

class CheckProtection(View):
    model = Metadata

    def get(self, request, slug):
        try:
            self.obj=self.model.objects.get(slug=slug)
        except self.model.DoesNotExist:
            logger.info('Object does not exist. ')
        if self.obj.is_protected():
            logger.info('Text paste is protected: redirecting')
            return redirect('paste_password_prompt', slug=slug)
        else:
            logger.info('Text paste is public: redirecting to content')
            return redirect('paste_detail_view', slug=slug)

class PasswordPromptView(View):
    model = Metadata

    def get(self, request, slug):
        return render(request, 'password_prompt.html', {'slug': slug})
    
    def post(self, request, slug):
        self.obj = get_object_or_404(self.model, slug=slug)
        password = request.POST.get('password')
        if check_password(password, self.obj.password):
            logger.info('Password correct')
            # Set a session flag
            request.session[f'passed_protection_{slug}'] = True
            return redirect('paste_detail_view', slug=slug)
        else:
            logger.info('Bad password')
            return JsonResponse({'prompt_again': True})

class PasteDetailView(View):
    model = Metadata
    cache_timeout = 300
    payload = {}

    def get(self, request, slug) -> HttpResponse:
        # Verify session flag for protected content
        obj = get_object_or_404(self.model, slug=slug)
        if obj.is_protected() and not request.session.get(f'passed_protection_{slug}'):
            logger.info('Access denied: Password protection not passed')
            return redirect('paste_password_prompt', slug=slug)
        
        # Check if cached
        self.payload = cache.get(slug)
        if not self.payload:
            logger.info('Hit DB')
            self.obj = obj
            self.payload = model_to_dict(self.obj)
            self.payload['text'] = myS3Service.retrieve_from_s3(self.obj.slug)
            # Convert expiry time to convenient format
            cache.set(slug, self.payload, timeout=self.cache_timeout)
        else:
            logger.info('Hit cache')
        return render(request, 'view_paste.html', self.payload)
