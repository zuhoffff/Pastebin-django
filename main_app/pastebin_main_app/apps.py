from django.apps import AppConfig
from threading import Thread
from pastebin_main_app.myUtilFunctions import delete_expired_entry
from .expiry_controller import ExpiryController 
# import sys

newExpiryController = ExpiryController(delete_expired_entry)

class PastebinMainAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pastebin_main_app'

    def ready(self):        
        # TODO: make sure this is valid approach (the only solution I came up with so far)
        expiry_controller_thread = Thread(target=newExpiryController.run_expiry_controller, args=())
        expiry_controller_thread.run()

         # Make the instance accessible globally
        # sys.modules['pastebin_main_app.newExpiryController'] = newExpiryController
