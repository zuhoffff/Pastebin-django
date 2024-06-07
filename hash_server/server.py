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

class myHandler(BaseHTTPRequestHandler):
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

# Handler Factory:
def create_handler(hash_generator):
    class CustomHandler(myHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(hash_generator, *args, **kwargs)
    return CustomHandler

def main():
        
    # Initialize the hash generator which works continuously
    newDbWizard = HashDbWizard(engine=engine, db_model=Hashes)
    newHashGenerator = HashGenerator(newDbWizard)
    newHashGenerator.ensure_spare_hashes()
    HOST = environ.get('HOST', default='0.0.0.0')
    logger.info(HOST)
    PORT = int(environ.get('PORT', default=8000))
    logger.info(PORT)

    server_address = (HOST, PORT)
    handlerClass = create_handler(newHashGenerator)
    server = CustomThreadingHTTPServer(server_address, handlerClass)
    logger.info(f'Server is running on: {server_address}')

    def check_for_requests():
        if server.active_threads == 0:
            newHashGenerator.ensure_spare_hashes()
            time.sleep(5)
    
    # Create separate thread for activity monitoring:
    monitorThread = threading.Thread(target=check_for_requests, args=())
    monitorThread.start()

    server.serve_forever()

if __name__ == '__main__':
    main()