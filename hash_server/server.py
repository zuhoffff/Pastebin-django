import logging
import time
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from os import environ
import threading
from hash_generator import HashGenerator
from hashDbWizard import HashDbWizard
from setup_db import Hashes, session_factory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CustomThreadingMixIn(ThreadingMixIn):
    """Mix-in class to handle each request in a new thread."""
    
    def process_request(self, request, client_address):
        logger.info(f"Active threads before processing: {threading.active_count()}")
        super().process_request(request, client_address)

class CustomThreadingHTTPServer(CustomThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

class Handler(BaseHTTPRequestHandler):
    def __init__(self, localHashGenerator, *args, **kwargs):
        self.localHashGenerator = localHashGenerator
        super().__init__(*args, **kwargs)

    def do_GET(self):
        self.send_response(200)
        self.send_header('content-type', 'application/json')
        self.end_headers()
        try:
            hash_key = self.localHashGenerator.get_next_unused_hash()
            response = json.dumps({'hash': hash_key}).encode()
        except Exception as e:
            logger.error(f'Could not fetch hash from hash generator: {e}')
            response = json.dumps({'error': 'Hash generation failed'}).encode()

        self.wfile.write(response)

class HandlerFactory:
    @staticmethod
    def create_handler(InjectedClass):
        class CustomHandler(Handler):
            def __init__(self, *args, **kwargs):
                super().__init__(InjectedClass, *args, **kwargs)
        return CustomHandler

class HashServer:
    def __init__(self, server_address, hash_generator, time_to_check):
        self.address = server_address
        self.hash_generator = hash_generator
        self.time_to_check = time_to_check
        self.server = None

    def initialize_hash_server(self, custom_server):
        self.server = custom_server

    def _add_spare_hashes_when_idle(self):
        while True:
            active_threads = threading.active_count() - 2
            if active_threads <= 1:
                logger.info(f'Active threads count: {active_threads}')
                self.hash_generator.ensure_spare_hashes()
            time.sleep(self.time_to_check)

    def _create_spare_hashes_provider_thread(self):
        provider_thread = threading.Thread(target=self._add_spare_hashes_when_idle, daemon=True)
        logger.info(f'Created thread for server activity monitoring: {provider_thread}')
        return provider_thread

    def start_hash_server(self):
        monitoring_thread = self._create_spare_hashes_provider_thread()
        monitoring_thread.start()
        self.server.serve_forever()
        logger.info('Started hash-server')

def main():
    newDbWizard = HashDbWizard(session_factory=session_factory, db_model=Hashes)
    newHashGenerator = HashGenerator(newDbWizard)
    newHashGenerator.ensure_spare_hashes()

    HOST = environ.get('HOST', default='0.0.0.0')
    PORT = int(environ.get('PORT', default=8000))
    server_address = (HOST, PORT)
    logger.info(f'Hash server address: {server_address}')

    handlerClass = HandlerFactory.create_handler(newHashGenerator)

    myHashServer = HashServer(server_address=server_address, hash_generator=newHashGenerator, time_to_check=3)
    myHTTPServer = CustomThreadingHTTPServer(server_address, handlerClass)
    myHashServer.initialize_hash_server(myHTTPServer)
    myHashServer.start_hash_server()

if __name__ == '__main__':
    main()