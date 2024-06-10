# from django.views.generic.detail import DetailView
# from django.http.response import HttpResponse as HttpResponse
# from django.shortcuts import render, get_object_or_404
# from django.contrib.auth.hashers import check_password
# from ..models import Metadata
# from django.http import HttpRequest, JsonResponse
# import time
# from django.core.cache import cache
# import logging
# from pastebin_main_app.utils.s3_handler import myS3Service
# from django.views.generic.detail import DetailView

# class CheckPasswordView(View):
    

# class GetTextView(DetailView):
#     model=Metadata
#     template_name = 'block.html'
#     context_object_name = 'metadata'

    

#     def get_object(self, queryset=None):
#         return get_object_or_404(Metadata, slug=self.kwargs['url']) # url is a slug

#     def render_to_response(self, context, **response_kwargs: logging.Any):
#         if self.get_object.password:
#             return HttpResponse

#         return super().render_to_response(context, **response_kwargs)
#     #1. check if data expired
#     #2. check if data cached
#     #3. check if data protected - yes? verify, not? fall through