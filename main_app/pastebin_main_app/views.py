import dateutil.parser as dp
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
class SubmitTextView(CreateView):
    model = Metadata
    template_name='home.html'
    form_class = PasteSubmissionForm
    success_url = ...

    def __init__(self, submit_text_service_object, s3_service, **kwargs: logging.Any) -> None:
        super().__init__(**kwargs)
        self.submit_text_service=submit_text_service_object
        self.s3_service = s3_service

    def form_valid(self, form) -> HttpResponse:
        text = form.cleaned_data.get('text')

        nonform_data = self.request.POST
        timestamp = nonform_data.get('timestamp') # Needs to be converted to UNIX from iso
        time_til_expiry = nonform_data.get('expirationTime') # Needs to be converted to Unix and added to timestamp
        user_agent = nonform_data.get('userAgent')

        # Make request to hash-server
        url = self.submit_text_service.get_hash_from_server()

        # Make necessary convertations:
        timestamp = self.submit_text_service.convert_iso_to_unix(timestamp)
        expiry_time = self.submit_text_service.convert_string_to_unix_time(time_til_expiry) + timestamp 

        # Process the validated form data but don't save to the database yet
        new_entry = form.save(commit=False)
        new_entry.timestamp = timestamp
        new_entry.expiry_time = expiry_time
        new_entry.password = make_password(form.password)
        new_entry.user_agent = user_agent
        new_entry.url = url

        new_entry.save()

        # Save text-paste to blob store:
        self.s3_service.uload_to_s3(s3_key=form.compose_key(), text_input=text)

        full_url = f'/paste/{new_entry.url}/'
        return JsonResponse({'message': 'Text saved successfully', 'url': full_url})
         
class SubmitTextService():
        # Constants for error messages
    ERROR_HASH_SERVER = 'Hash-server error'
    ERROR_CREDENTIALS = 'Credentials error'
    ERROR_CLIENT = 'Client error'
    ERROR_GENERIC = 'An error occurred'
    ERROR_MISSING_DATA = 'Missing frontend data'
    ERROR_INVALID_METHOD = 'Invalid request method'

    def __init__(self, hash_server_uri) -> None:
        self.hash_server_uri = hash_server_uri

    def get_hash_from_server(self):
        try:
            response = requests.get(self.hash_server_uri)
            response.raise_for_status()
            return response.json().get('hash')
        except Exception:
            raise Exception(self.ERROR_HASH_SERVER)
    
    @staticmethod
    def convert_string_to_unix_time(time_str) -> float:
        ''' Converts {days}.{hours}.{minutes} to unix time'''
        # Parse the expiry string
        days, hours, minutes = map(int, time_str.split('.'))
        time_til_expiry = datetime.timedelta(days=days, hours=hours, minutes=minutes)
        return float(time_til_expiry.timestamp())
    
    @staticmethod
    def convert_iso_to_unix(time_iso8601):
        parsed_t = dp.parse(time_iso8601)
        t_in_seconds = parsed_t.timestamp()
        return float(t_in_seconds)