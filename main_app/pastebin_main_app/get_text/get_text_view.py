from django.views.generic.detail import DetailView
from django.http.response import HttpResponse as HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.hashers import check_password
from ..models import Metadata
from django.http import HttpRequest, JsonResponse
import time
from django.core.cache import cache
import logging
from pastebin_main_app.utils.s3_handler import myS3Service
from django.views import View
from django.contrib.auth.hashers import check_password
from time import time
from pastebin_main_app.utils.s3_handler import myS3Service
import logging
from pastebin_main_app.utils.s3_handler import myS3Service
from django.views.generic.detail import DetailView
from django.forms.models import model_to_dict
from django.urls import reverse
# TODO: figure out design problem: use 3 views or use flag : CHECKED


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# TODO: implement session and authorisation

class CheckProtection(View):
    model = Metadata
    
    def get(self, request, slug):
        self.obj = get_object_or_404(self.model, slug=slug)
        if not self.obj.is_protected():
            return redirect('paste_detail_view',slug=slug)
            # return self.show_content(request=request)
        else:
            return redirect('paste_password_prompt', slug=slug)
        
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


class PasteDetailView(DetailView): # or View
    model = Metadata
    cache_timeout = 300
    payload = {}

    def get(self, request, slug) -> HttpResponse:
        # Check if cached:
        self.payload = cache.get(slug)
        if not self.payload:
            self.obj=get_object_or_404(self.model, slug=slug)
            self.payload=model_to_dict(self.obj)
            self.payload['text']=myS3Service.retrieve_from_s3(self.obj.slug)
            cache.set(slug, self.payload, timeout=self.cache_timeout)
        # return render(request, 'block.html', self.payload)
        return JsonResponse(self.payload)

    # TODO: double-check expiry time format!
    # def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
    #     # Check if cached:
    #     slug=kwargs.get('slug')
    #     logger.info(slug)
    #     logger.info(self.model)
    #     self.payload = cache.get(slug)
    #     if not self.payload:
    #         self.obj = get_object_or_404(self.model, slug=slug)

    #         # Refresh statistics
    #         self.obj.key_usages+=1
    #         self.obj.save()

    #         # Modify the payload
    #         self.payload = (model_to_dict(self.obj))
    #         self.payload['text'] = myS3Service.retrieve_from_s3(self.obj.slug)

    #         cache.set(slug, self.payload, timeout=self.cache_timeout)

    #         logger.info(self.payload)
    #         logger.info(self.obj)

    #     return super().dispatch(request, *args, **kwargs)
    
    

    # def post(self, request, slug):
    #     password = request.POST.get('password', '')
    #     if not check_password(password, self.obj.password):
    #         return redirect('paste_password_prompt', slug=slug)
    #     else:
    #         return self.show_content(request=request)

    # def show_content(self, request):
    #     # TODO: specify which object field to show on the page.
    #     return JsonResponse(model_to_dict(self.obj))