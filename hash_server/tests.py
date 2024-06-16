import requests
import time

def make_singe_request():
    try:
        response = requests.get('http://localhost:8000')
        if response.status_code == 200:
            print(response.json())
        else:
            print(f"Failed to get a valid response. Status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {e}")

def test_hash_gen():
    from hash_generator import HashGenerator
    from hashDbWizard import HashDbWizard
    from setup_db import Hashes
    from setup_db import MySession
    
    newDbWizard = HashDbWizard(Session = MySession, db_model=Hashes)
    newHashGenerator = HashGenerator(newDbWizard)
    newHashGenerator.ensure_spare_hashes()

    print(newHashGenerator.get_next_unused_hash())

if __name__ == '__main__':
    for i in range(1000):
        make_singe_request()
        time.sleep(0.5)
