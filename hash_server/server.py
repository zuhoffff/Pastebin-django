import logging
import time
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from os import environ
import threading
from hash_generator import HashGenerator
from hashDbWizard import HashDbWizard
from setup_db import Hashes
from setup_db import MySession
import threading

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CustomThreadingMixIn(ThreadingMixIn):
    active_threads_count = 0

    def process_request_thread(self, request, client_address):
        thread = threading.current_thread()
        logger.info(f"Starting thread: {thread.name} for request from {client_address}")
        
        self.active_threads_count+=1
        logger.info(f'Current thread{threading.current_thread()}')
        try:
            super().process_request_thread(request, client_address)
        except Exception:
            logger.exception('Could not process request')
        finally:
            self.active_threads_count-=1
            logger.info(f"Ending thread: {thread.name}")
            logger.info(threading.enumerate())

class CustomThreadingHTTPServer(CustomThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

class Handler(BaseHTTPRequestHandler):
    def __init__(self, localHashGenerator: HashGenerator, *args, **kwargs):
        self.localHashGenerator = localHashGenerator
        super().__init__(*args, **kwargs)

    def do_GET(self):
        self.send_response(200)
        self.send_header('content-type', 'application/json')
        self.end_headers()
        try:
            hash_key = self.localHashGenerator.get_next_unused_hash()
            logger.info(f'Returned hash: {hash_key}')
            response = json.dumps({'hash': hash_key}).encode()
        except Exception:
            logger.error(f'Could not fetch hash from hash generator')
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

    def _add_spare_hashes_when_idle(self):
        if self.server.active_threads_count == 0:
            logger.info(f'active threads count {self.server.active_threads_count}')
            self.hash_generator.ensure_spare_hashes()
            time.sleep(self.time_to_check)

    def _create_spare_hashes_provider_thread(self):
        provider_thread = threading.Thread(target=self._add_spare_hashes_when_idle, args=(), daemon=True)
        logger.info(f'Created thread for server activity monitoring: {provider_thread}')
        return provider_thread

    def start_hash_server(self):
        monitoring_thread = self._create_spare_hashes_provider_thread()
        monitoring_thread.start()
        self.server.serve_forever()
        logger.info('Started hash-server')

def main():
    # Initialize the hash generator
    newDbWizard = HashDbWizard(Session = MySession, db_model=Hashes)
    newHashGenerator = HashGenerator(newDbWizard)
    newHashGenerator.ensure_spare_hashes()

    HOST = environ.get('HOST', default='0.0.0.0')
    PORT = int(environ.get('PORT', default=8000))
    server_address = (HOST, PORT)
    logger.info(f'Hash server address: {server_address}')

    handlerClass = HandlerFactory().create_handler(newHashGenerator)

    myHashServer = HashServer(server_address=server_address,
                              hash_generator=newHashGenerator,
                              time_to_check=3)
    
    myServer = CustomThreadingHTTPServer(server_address, handlerClass)
    myHashServer.initialize_hash_server(myServer)
    myHashServer.start_hash_server()

if __name__ == '__main__':
    main()