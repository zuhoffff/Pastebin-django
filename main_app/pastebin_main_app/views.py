from django.forms import BaseModelForm
from django.shortcuts import render, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import CreateView
from submit_text.submition_form import PasteSubmissionForm
from django.contrib.auth.hashers import make_password
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import logging
from main_app.pastebin_main_app.utils.s3_handler import upload_to_s3
import requests
from os import environ
from pastebin_main_app.apps import newExpiryController
import datetime
from models import Metadata
from .. import SubmitTextService_MixinStatic

@csrf_exempt
class SubmitTextView(CreateView, SubmitTextService_MixinStatic):
    model = Metadata
    template_name='home.html'
    form_class = PasteSubmissionForm
    success_url = ...

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        nonform_data = self.request.POST
        nonform_data.get('text')
        nonform_data.get('timestamp') # Needs to be converted to UNIX from iso
        nonform_data.get('expirationTime') # Needs to be converted to Unix and added to timestamp

        # Make request to hash-server by calling static method:
        SubmitTextService_MixinStatic.get_hash_from_server()


        return super().form_valid(form)

    # def post(self, request: HttpRequest, *args: str, **kwargs: logging.Any) -> HttpResponse:
    #     return super().post(request, *args, **kwargs)
         
class SubmitTextService_MixinStatic():
        # Constants for error messages
    ERROR_HASH_SERVER = 'Hash-server error'
    ERROR_CREDENTIALS = 'Credentials error'
    ERROR_CLIENT = 'Client error'
    ERROR_GENERIC = 'An error occurred'
    ERROR_MISSING_DATA = 'Missing frontend data'
    ERROR_INVALID_METHOD = 'Invalid request method'

    @staticmethod
    def get_hash_from_server(HASH_SERVER_URI):
        response = requests.get(HASH_SERVER_URI)
        # response.raise_for_status()
        return response.json().get('hash')
    
    @staticmethod
    def convert_string_to_unix_time(expiry_str) -> float:
        ''' Converts {days}.{hours}.{minutes} to unix time'''
        # Parse the expiry string
        days, hours, minutes = map(int, expiry_str.split('.'))
        time_til_expiry = datetime.timedelta(days=days, hours=hours, minutes=minutes)
        return float(time_til_expiry.timestamp())