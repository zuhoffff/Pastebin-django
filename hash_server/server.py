import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from os import environ
import threading
from hash_generator import HashGenerator
from hashDbWizard import HashDbWizard
from setup_db import Hashes, engine
from logger import logger
import time

# Modify threading mix to log new threads:
class CustomThreadingMixIn(ThreadingMixIn):
    active_threads = 0
    logger.info(active_threads)

    def process_request_thread(self, request, client_address):
        # Log the creation of a new thread
        thread = threading.current_thread()
        logger.info(thread)
        logger.info(f"Starting thread: {thread.name} for request from {client_address}")
        
        # Add thread to the active threads list
        self.active_threads+=1
        try:
            super().process_request_thread(request, client_address)
        finally:
            # Remove thread from the active threads list once done
            self.active_threads-=1
            logger.info(f"Ending thread: {thread.name}")

class CustomThreadingHTTPServer(CustomThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

class Handler(BaseHTTPRequestHandler):
    def __init__(self, localHashGenerator: HashGenerator, *args, **kwargs):
        self.localHashGenerator = localHashGenerator
        super().__init__(*args, **kwargs)

    def do_GET(self):
        logger.info('we are inside handler class')
        self.send_response(200)
        self.send_header('content-type', 'application/json')
        self.end_headers()
        logger.info('header is ok.')
        try:
            hash_key = self.localHashGenerator.get_next_unused_hash()
            logger.info(f'Returned hash: {hash_key}')
            response = json.dumps({'hash': hash_key}).encode()
        except Exception as e:
            logger.error(f'Something is wrong with hash-generator: {e}')
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
    def __init__(self, server_address: tuple, hash_generator, time_to_check: int, ) -> None:
        self.address = server_address
        self.hash_generator = hash_generator
        self.time_to_check = time_to_check
        self.server = None

    def initialize_hash_server(self, custom_server):
        self.server = custom_server

    def _check_for_requests(self):
        if self.server.active_threads == 0:
            self.hash_generator.ensure_spare_hashes()
            time.sleep(self.time_to_check)

    def _create_spare_hashes_provider_thread(self):
         # Create separate thread for activity monitoring:
        provider_thread = threading.Thread(target=self._check_for_requests, args=(), daemon=True)
        return provider_thread

    def _handle_background_tasks(self):
        self._create_spare_hashes_provider_thread().start()

    def start_hash_server(self):
        self._handle_background_tasks()
        self.server.serve_forever()

def main():
    # Initialize the hash generator
    newDbWizard = HashDbWizard(engine=engine, db_model=Hashes)
    newHashGenerator = HashGenerator(newDbWizard)
    # Refill db with hashes just in case
    newHashGenerator.ensure_spare_hashes()

    HOST = environ.get('HOST', default='0.0.0.0')
    PORT = int(environ.get('PORT', default=8000))
    server_address = (HOST, PORT)

    handlerClass = HandlerFactory().create_handler(newHashGenerator)

    myHashServer = HashServer(server_address=server_address,
                              hash_generator=newHashGenerator,
                              time_to_check=5)
    
    myServer = CustomThreadingHTTPServer(server_address, handlerClass)
    myHashServer.initialize_hash_server(myServer)
    myHashServer.start_hash_server()

if __name__ == '__main__':
    main()