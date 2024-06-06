import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from os import environ
from hash_generator import ensure_spare_hashes, get_next_unused_hash, main as hash_gen_main
import logging
import threading, time

# TODO: remake into class

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
LOGGER = logging.getLogger(__name__)

# Modify threading mix to log new threads:
class CustomThreadingMixIn(ThreadingMixIn):
    active_threads = 0

    def process_request_thread(self, request, client_address):
        # Log the creation of a new thread
        thread = threading.current_thread()
        LOGGER.info(f"Starting thread: {thread.name} for request from {client_address}")
        
        # Add thread to the active threads list
        self.active_threads+=1
        try:
            super().process_request_thread(request, client_address)
        finally:
            # Remove thread from the active threads list once done
            self.active_threads-=1
            LOGGER.info(f"Ending thread: {thread.name}")

class CustomThreadingHTTPServer(CustomThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('content-type', 'application/json')
        self.end_headers()

        try:
            hash_key = get_next_unused_hash()
            LOGGER.info(f'Returned hash: {hash_key}')
            response = json.dumps({'hash': hash_key}).encode()
        except Exception as e:
            LOGGER.error(f'Something is wrong with hash-generator: {e}')
            response = json.dumps({'error': 'Hash generation failed'}).encode()

        self.wfile.write(response)

def main():
    # Initialize the hash generator which works continuously
    hash_gen_main()

    HOST = environ.get('HOST', default='0.0.0.0')
    PORT = int(environ.get('PORT', default=8000))

    server_address = (HOST, PORT)
    server = CustomThreadingHTTPServer(server_address, handler)
    LOGGER.info(f'Server is running on: {server_address}')

    def monitor_server_activity():
        if server.active_threads == 0:
            ensure_spare_hashes()
        time.sleep(5)
    
    # Create separate thread for activity monitoring:
    monitorThread = threading.Thread(target=monitor_server_activity, args=())
    monitorThread.run()

    server.serve_forever()

if __name__ == '__main__':
    main()