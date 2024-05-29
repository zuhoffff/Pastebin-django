from django.http import JsonResponse
from .models import Metadata
from django.views.decorators.csrf import csrf_exempt
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
LOGGER = logging.getLogger(__name__)


@csrf_exempt
def submit_text(request):
    if request.method == 'POST':
        text_input = request.POST.get('text')
        timestamp = request.POST.get('timestamp')
        user_agent = request.POST.get('userAgent')

        if text_input and timestamp and user_agent:

            curr_url=f'/block/{text_model.id}/'
            response_data = {
                'message': 'Data received successfully',
                'url': f'{curr_url}'  # Replace with actual URL if needed
            }
            # Save the text input and metadata to your database
            text_model = Metadata.objects.create(
                timestamp=timestamp,
                user_agent=user_agent
            )   


            return JsonResponse(response_data)

        return JsonResponse({'error': 'Missing data'}, status=400)

    return JsonResponse({'message': 'Invalid request method'}, status=405)
