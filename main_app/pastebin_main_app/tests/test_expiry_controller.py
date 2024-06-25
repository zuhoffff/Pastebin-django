from pastebin_main_app.submit_text.submit_text_service import submitTextService
from pastebin_main_app.utils.expiry_controller import ExpiryController
from django.test import TestCase
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from threading import Thread, enumerate, main_thread

class TestExpiryController(TestCase):
    def setUp(self):
        # Mock the delete function
        self.mock_delete_function = MagicMock()
        self.controller = ExpiryController(delete_expired_entry=self.mock_delete_function, run_continuously=True)

    def test_add_event(self):
        # Mock the datetime to control the current time
        with patch('pastebin_main_app.utils.expiry_controller.datetime') as mock_datetime:
            now = datetime.now()
            mock_datetime.now.return_value = now

            expiry_time = int((now + timedelta(seconds=5)).timestamp())
            self.controller.add_event(expiry_time, 'test_id')

            # Verify the event was added to the registry
            self.assertEqual(len(self.controller.expiry_registry), 1)
            self.assertEqual(self.controller.expiry_registry[0], (expiry_time, 'test_id'))

    def test_run_expiry_controller(self):
        with patch('pastebin_main_app.utils.expiry_controller.datetime') as mock_datetime:
            now = datetime.now()
            mock_datetime.now.return_value = now
            mock_datetime.side_effect = lambda: now

            expiry_time = int((now - timedelta(seconds=1)).timestamp())
            self.controller.add_event(expiry_time, 'test_id')

            controller_thread = Thread(target=self.controller.run_expiry_controller)
            controller_thread.start()

            import time
            time.sleep(1)

            self.controller.stop()
            controller_thread.join()

            self.mock_delete_function.assert_called_once_with('test_id')

    def test_expiry_event_trigger(self):
        with patch('pastebin_main_app.utils.expiry_controller.datetime') as mock_datetime:
            now = datetime.now()
            mock_datetime.now.return_value = now
            mock_datetime.side_effect = lambda: now

            future_time = int((now + timedelta(seconds=10)).timestamp())
            self.controller.add_event(future_time, 'test_future_id')
            immediate_expiry_time = int((now - timedelta(seconds=1)).timestamp())
            self.controller.add_event(immediate_expiry_time, 'test_immediate_id')

            controller_thread = Thread(target=self.controller.run_expiry_controller)
            controller_thread.start()

            import time
            time.sleep(1)

            self.controller.stop()
            controller_thread.join()

            self.mock_delete_function.assert_called_once_with('test_immediate_id')