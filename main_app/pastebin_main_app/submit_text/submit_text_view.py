from pastebin_main_app.submit_text.submission_form import PasteSubmissionForm
from django.contrib.auth.hashers import make_password
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.views.generic.edit import CreateView
from django.db.models.base import Model as Model
from pastebin_main_app.models import Metadata
from django.shortcuts import HttpResponse
from datetime import datetime, timezone
from pastebin_main_app.submit_text.submit_text_service import submitTextService
from pastebin_main_app.utils.expiry_controller import myExpController
from pastebin_main_app.utils.s3_handler import myS3Service
import logging
import pytz
from django.utils.timezone import make_aware, make_naive

# from pyinstrument import Profiler
# profiler = Profiler()
# logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# TODO: expiry time bugs sometimes (maybe problem related to UTC and timezones)
# in submission form expiry_time "local" time is saved as "utc" time, and get written to db like that: this causes time bug

# TODO: fix When user craetes a lot of pastes something goes wrong with password check (probably problem is related to check_protection view)
# TODO: fix: sometimes unprotected pastes can not be accessed (require session flag)
# TODO: fix logger

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
        user_timezone = self.request.POST.get('timezone', 'UTC')

        user_tz = pytz.timezone(user_timezone)
        naive_expiry_time = make_naive(expiry_time, pytz.UTC)
        # Localize to user's timezone
        localized_expiry_time = user_tz.localize(naive_expiry_time)
        utc_expiry_time = localized_expiry_time.astimezone(pytz.UTC)

        logger.info(f"tz: {user_tz} timezone: {user_timezone} utc: {utc_expiry_time}")

        timestamp = datetime.now(timezone.utc)

        # Calculate the int utc epoch expiry time to add to expiry registry
        epoch_expiry_time = int(utc_expiry_time.timestamp())
        self.expiry_controller.add_event(epoch_expiry_time, self.__class__.model.id)        
        
        # Get timestamp and user agent from the request metadata
        user_agent = self.request.META.get('HTTP_USER_AGENT', '')

        # Make request to hash-server
        slug = self.submit_text_service.get_hash_from_server()

        # Process the validated form data but don't save to the database yet
        new_entry = form.save(commit=False) 
        new_entry.expiry_time = utc_expiry_time
        if password: new_entry.password = make_password(password)
        new_entry.user_agent = user_agent
        new_entry.timestamp = timestamp
        new_entry.slug = slug

        logger.debug(f"expiry_time: {new_entry.expiry_time} (type: {type(new_entry.expiry_time)})")
        logger.debug(f"timestamp: {new_entry.timestamp} (type: {type(new_entry.timestamp)})")
        logger.debug(f"user_agent: {new_entry.user_agent} (type: {type(new_entry.user_agent)})")
        logger.debug(f"slug: {new_entry.slug} (type: {type(new_entry.slug)})")
        logger.debug(f"password: {new_entry.password} (type: {type(new_entry.password)})")
        logger.debug(f"author: {new_entry.author} (type: {type(new_entry.author)})")
        logger.debug(f"name: {new_entry.name} (type: {type(new_entry.name)})")

        new_entry.save()

        logger.info("New metadata entry saved")
        
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
    
    def form_invalid(self, form):
        logger.error('the form is invalid')
        response_data = {
            'success': False,
            'error': 'Invalid form data',
        }
        return JsonResponse(response_data)