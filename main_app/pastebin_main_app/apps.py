from django.apps import AppConfig
from threading import Thread
from pastebin_main_app.myUtilFunctions import delete_expired_entry
from .expiry_controller import ExpiryController 
# import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
LOGGER = logging.getLogger(__name__)

newExpiryController = ExpiryController(delete_expired_entry)

class PastebinMainAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pastebin_main_app'

    def ready(self):        
        # TODO: make sure this is valid approach (the only solution I came up with so far)
        expiry_controller_thread = Thread(target=newExpiryController.run_expiry_controller, args=())
        LOGGER.info('Created thread {}'.format(expiry_controller_thread))
        expiry_controller_thread.start()
        LOGGER.info('Started thread..once?')

         # Make the instance accessible globally
        # sys.modules['pastebin_main_app.newExpiryController'] = newExpiryController
