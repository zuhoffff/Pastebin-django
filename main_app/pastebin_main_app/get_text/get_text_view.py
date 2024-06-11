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
from django.views.generic import TemplateView

class PasswordPromptView(View):
    def get(self, request, slug):
        return render(request, 'password_prompt.html', {'slug': slug})


class PasteDetailView(DetailView): # or View
    model = Metadata
    cache_timeout = 300
    # context_object_name='obj'

    def dispatch(self, request: HttpRequest, *args: time.Any, **kwargs: time.Any) -> HttpResponse:
        # Check if cached:
        slug=kwargs.get('slug')
        self.obj = cache.get(slug)
        if not self.obj:
            self.obj = get_object_or_404(self.model, slug)
            self.obj.key_usages+=1
            cache.set(slug, self.obj, timeout=self.cache_timeout)

        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, slug):
        if self.obj.is_protected():
            return redirect('paste_password_prompt', slug=slug)
        else:
            return self.show_content(request=request)

    def post(self, request, slug):
        password = request.POST.get('password')
        if not check_password(password, self.obj.password):
            return redirect('paste_password_prompt', slug=slug)
        else:
            return self.show_content(request=request)

    # TODO: use detail view
    def show_content(self, request):
        return render(request, 'block.html', context=self.obj)




    
# class PasteDetailView(DetailView):
    #1. check if data expired
    #2. check if data cached
    #3. check if data protected - yes? verify, not? fall through