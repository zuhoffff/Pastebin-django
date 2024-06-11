from django.db.models.base import Model as Model
from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import CreateView
from .submition_form import PasteSubmissionForm
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ..models import Metadata
from .submit_text_service import submitTextService
from ..utils.s3_handler import myS3Service
from ..utils.expiry_controller import myExpController
from django.utils.decorators import method_decorator
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class SubmitTextView(CreateView):
    template_name = 'home.html'
    model = Metadata

    form_class = PasteSubmissionForm
    submit_text_service = submitTextService
    s3_service = myS3Service
    expiry_controller = myExpController
    
    def form_valid(self, form) -> HttpResponse:
        logger.info('we are in form valid method')
        form_data = form.cleaned_data
        text = form_data.get('text')
        expiry_time = form_data.get('expiry_time')
        password = form_data.get('password')
        
        # Convert the expiry_time
        expiry_time = self.submit_text_service.convert_datetime_to_utc_timestamp(expiry_time)

        logger.info(f'I\'ve retrieved some fields: {text}')

         # Get timestamp and user agent from the request metadata
        # TODO: replace with the frontend precise timestamp
        timestamp = self.submit_text_service.get_current_int_utc_timestamp()
        user_agent = self.request.META.get('HTTP_USER_AGENT', '')

        logger.info(f'I\'ve retrieved some metadata fields: {user_agent}')
        
        logger.info(timestamp)
        logger.info(expiry_time)

        # Make request to hash-server
        slug = self.submit_text_service.get_hash_from_server()


        # Process the validated form data but don't save to the database yet
        new_entry = form.save(commit=False)
        new_entry.timestamp = timestamp
        new_entry.expiry_time = expiry_time
        new_entry.password = make_password(password)
        new_entry.user_agent = user_agent
        new_entry.slug = slug

        logger.info(new_entry)

        new_entry.save()

        logger.info(new_entry)
        
        # Save text-paste to blob store:
        self.s3_service.upload_to_s3(s3_key=slug, text_input=text)

        # Add paste to expiry registry:
        self.expiry_controller.add_event(expiry_time, self.__class__.model.id)        

        full_url = f'/paste/{new_entry.url}/'
        response_data = {
            'success': True,
            'message': 'Form submitted successfully!',
            'url': full_url,
        }
        return JsonResponse(response_data)
        # return JsonResponse({'message': 'Text saved successfully', 'url': full_url})
    
    def form_invalid(self, form):
        logger.error('the form is invalid')
        response_data = {
            'success': False,
            'error': 'Invalid form data',
        }
        return JsonResponse(response_data)