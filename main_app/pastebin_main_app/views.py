from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import CreateView
from django.views.generic import TemplateView
from pastebin_main_app.submit_text.submition_form import PasteSubmissionForm
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import logging
from models import Metadata

@csrf_exempt
class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PasteSubmissionForm()
        return context

@csrf_exempt
class SubmitTextView(CreateView):
    model = Metadata
    form_class = PasteSubmissionForm

    def __init__(self, submit_text_service_object, s3_service, expiry_controller, **kwargs: logging.Any) -> None:
        super().__init__(**kwargs)
        self.submit_text_service=submit_text_service_object
        self.s3_service = s3_service
        self.expiry_controller = expiry_controller

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

        # Add paste to expiry registry:
        self.expiry_controller.add_event(expiry_time, self.__class__.model.id)        

        full_url = f'/paste/{new_entry.url}/'

        return JsonResponse({'message': 'Text saved successfully', 'url': full_url})
    def form_invalid(self):
        return JsonResponse({'error': 'Invalid form data'}, status=400)