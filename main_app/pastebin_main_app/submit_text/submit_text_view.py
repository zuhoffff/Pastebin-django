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
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class SubmitTextView(CreateView):
    template_name = 'submit_text.html'
    model = Metadata

    form_class = PasteSubmissionForm
    submit_text_service = submitTextService
    s3_service = myS3Service
    expiry_controller = myExpController
    
    def form_valid(self, form) -> HttpResponse:
        form_data = form.cleaned_data
        text = form_data.get('text')
        password = form_data.get('password')
        expiry_time = form_data.get('expiry_time')

        timestamp = datetime.now(timezone.utc)
        
        logger.info(f"Original expiry_time: {expiry_time} (type: {type(expiry_time)})")

        # Convert the expiry_time and add to expiry registry
        epoch_expiry_time = self.submit_text_service.convert_datetime_to_utc_timestamp(expiry_time)
        self.expiry_controller.add_event(epoch_expiry_time, self.__class__.model.id)        

        logger.info(f"Converted epoch_expiry_time: {epoch_expiry_time} (type: {type(epoch_expiry_time)})")
        logger.info(f"Expiry_time after conversion method (should be unchanged): {expiry_time} (type: {type(expiry_time)})")
        
        # Get timestamp and user agent from the request metadata
        # TODO: move all possible logic to submit_text_servise for encapsulation
        user_agent = self.request.META.get('HTTP_USER_AGENT', '')
        
        logger.info(f"expiry_time: {expiry_time} (type: {type(expiry_time)})")
        logger.info(f"epoch_expiry_time: {epoch_expiry_time} (type: {type(epoch_expiry_time)})")

        # Make request to hash-server
        slug = self.submit_text_service.get_hash_from_server()

        # Process the validated form data but don't save to the database yet
        new_entry = form.save(commit=False) 
        if password: new_entry.password = make_password(password)
        new_entry.user_agent = user_agent
        new_entry.timestamp = timestamp
        new_entry.slug = slug

        logger.info(f"New entry before save: {new_entry}")
        logger.info(f"expiry_time: {new_entry.expiry_time} (type: {type(new_entry.expiry_time)})")
        logger.info(f"timestamp: {new_entry.timestamp} (type: {type(new_entry.timestamp)})")
        logger.info(f"user_agent: {new_entry.user_agent} (type: {type(new_entry.user_agent)})")
        logger.info(f"slug: {new_entry.slug} (type: {type(new_entry.slug)})")
        logger.info(f"password: {new_entry.password} (type: {type(new_entry.password)})")

        new_entry.save()

        logger.info(f"New entry saved: {new_entry}")
        
        # Save text-paste to blob store:
        self.s3_service.upload_to_s3(s3_key=slug, text_input=text)

        # Add paste to expiry registry:
        full_url = f'/paste/{new_entry.slug}/'
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