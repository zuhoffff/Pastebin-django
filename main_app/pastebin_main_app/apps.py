from django.apps import AppConfig
from .expiry_controller import start_expiry_controller

class PastebinMainAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pastebin_main_app'

    def ready(self):
        start_expiry_controller()
