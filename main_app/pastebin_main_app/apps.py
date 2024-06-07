from django.apps import AppConfig
from threading import Thread
from main_app.pastebin_main_app.utils.myUtilFunctions import delete_expired_entry_by_id
from .utils.expiry_controller import ExpiryController 

newExpiryController = ExpiryController(delete_expired_entry_by_id)

class PastebinMainAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pastebin_main_app'

    def ready(self):        
        # TODO: make sure this is valid approach (the only solution I came up with so far)
        expiry_controller_thread = Thread(target=newExpiryController.run_expiry_controller, args=())
        expiry_controller_thread.start()
