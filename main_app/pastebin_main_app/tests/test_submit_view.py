from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta, timezone
from pastebin_main_app.models import Metadata

class SubmitTextViewTests(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.url = reverse('submit_text')  # Adjust to your URL name
        self.valid_form_data = {
            'text': 'Sample text',
            'password': 'password123',
            'expiry_time': (datetime.now() + timedelta(days=1)),  # Ensure a future date/time
        }

    @patch('pastebin_main_app.utils.s3_handler.myS3Service.upload_to_s3')
    @patch('pastebin_main_app.submit_text.submit_text_service.submitTextService.get_hash_from_server', return_value='mockslug')
    @patch('pastebin_main_app.utils.expiry_controller.myExpController.add_event')
    def test_form_valid_submission(self, mock_add_event, mock_get_hash, mock_upload_to_s3):
        """
        Test form submission with valid data.
        """
        response = self.client.post(self.url, data=self.valid_form_data, HTTP_USER_AGENT='test-agent')

        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        # self.assertTrue(response_data[''])
        self.assertIn('url', response_data)
        self.assertEqual(response_data['message'], 'Form submitted successfully!')

        # Check that the entry was saved in the database
        new_entry = Metadata.objects.first()
        self.assertIsNotNone(new_entry)
        self.assertEqual(new_entry.slug, 'mockslug')
        self.assertEqual(new_entry.user_agent, 'test-agent')

        # Check that external services were called correctly
        mock_get_hash.assert_called_once()
        mock_upload_to_s3.assert_called_once_with(s3_key='mockslug', text_input='Sample text')

        # Check that the expiry event was registered
        expiry_time = self.valid_form_data['expiry_time']
        epoch_expiry_time = int(datetime.fromisoformat(expiry_time).timestamp())
        mock_add_event.assert_called_once_with(epoch_expiry_time, new_entry.id)

    def test_form_invalid_submission(self):
        """
        Test form submission with invalid data.
        """
        invalid_form_data = {
            'text': '',  # Invalid because it's empty
            'password': 'password123',
            'expiry_time': (datetime.now() - timedelta(days=1)).isoformat(),  # Invalid because it's a past date/time
        }
        response = self.client.post(self.url, data=invalid_form_data, HTTP_USER_AGENT='test-agent')

        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        # self.assertFalse(response_data[''])
        self.assertEqual(response_data['error'], 'Invalid form data')

        # Ensure no new entry was created in the database
        self.assertEqual(Metadata.objects.count(), 0)

    @patch('pastebin_main_app.submit_text.submit_text_service.submitTextService.get_hash_from_server', return_value='mockslug')
    @patch('pastebin_main_app.submit_text.submit_text_service.submitTextService.convert_datetime_to_utc_timestamp')
    def test_service_interactions(self, mock_convert_timestamp, mock_get_hash):
        """
        Test that services interact as expected.
        """
        mock_convert_timestamp.return_value = int(datetime.now().timestamp()) + 86400  # Mocked timestamp for expiry

        response = self.client.post(self.url, data=self.valid_form_data, HTTP_USER_AGENT='test-agent')

        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        # self.assertTrue(response_data[''])

        # Check that services were called as expected
        mock_get_hash.assert_called_once()
        mock_convert_timestamp.assert_called_once_with(self.valid_form_data['expiry_time'])

    def tearDown(self):
        # Cleanup any created data if necessary
        Metadata.objects.all().delete()
