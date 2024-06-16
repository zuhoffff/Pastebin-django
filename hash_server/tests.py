import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

def make_single_request():
    try:
        response = requests.get('http://localhost:8000')
        if response.status_code == 200:
            print(response.json())
        else:
            print(f"Failed to get a valid response. Status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    num_requests = 1000
    num_workers = 100  # Number of threads to use for making requests

    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = [executor.submit(make_single_request) for _ in range(num_requests)]

        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Request generated an exception: {e}")

if __name__ == '__main__':
    main()