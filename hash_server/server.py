import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from os import environ
from hash_generator import get_next_unused_hash, main as hash_gen_main
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
LOGGER = logging.getLogger(__name__)

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('content-type', 'application/json')
        self.end_headers()

        try:
            hash_key = get_next_unused_hash()
            LOGGER.info(f'Returned hash: {hash_key}')
        except Exception as e:
            LOGGER.info('Something is wrong with hash-generator')
            response = json.dumps({'error'}).encode()

        response = json.dumps({'hash': hash_key }).encode()

        self.wfile.write(response)


def main():
    # Initialize the hash generator which works continiously
    hash_gen_main()

    HOST = environ.get('HOST',default='0.0.0.0')
    PORT = int( environ.get('PORT',default=8000) )

    server_address = (HOST,PORT)

    server=HTTPServer(server_address, handler)
    print(f'Server is running on:{server_address}')

    server.serve_forever()

if __name__ == '__main__':
    main()