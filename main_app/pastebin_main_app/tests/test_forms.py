from pastebin_main_app.submit_text.submit_text_service import submitTextService
from pastebin_main_app.utils.expiry_controller import ExpiryController
from django.test import TestCase
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from threading import Thread, enumerate, main_thread

from pastebin_main_app.homepage.slug_form import SlugForm

# Mock the db model:
class TestSlugForm(TestCase):
    @patch('pastebin_main_app.models.Metadata')
    def test_slug_exists(self,MockMetadata):
        mock_instance = MockMetadata.return_value
        mock_instance.slug = '==AA'
        form = SlugForm(data={'slug':'==AA'})
        if form.is_valid():
            self.assertEqual(form.check_if_exists(), True)

    @patch('pastebin_main_app.models.Metadata')
    def test_slug_not_exist(self,MockMetadata):
        mock_instance = MockMetadata.return_value
        mock_instance.slug = 'nnnn'
        form = SlugForm(data={'slug':'==AA'})
        if form.is_valid():
            self.assertEqual(form.check_if_exists(), False)


# class TestSubmissionForm(TestCase):
    
