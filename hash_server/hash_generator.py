from hashDbWizard import HashDbWizard
import time

class HashGenerator:

    # Inject class that handles database interaction logic 
    def __init__(self, db_wizard: HashDbWizard, number_of_spare_hashes=100, spare_hash_check_period=5):
        self.spare_hashes_plank = number_of_spare_hashes
        self.spare_hash_check_period = spare_hash_check_period
        self.hash_db_wizard = db_wizard

    # Ensure a certain number of spare hashes
    def ensure_spare_hashes(self):
        # logger.info(f'Ensuring at least {n} spare hashes.')
        while True:
            current_unused = self.hash_db_wizard.count_unused_hashes()
            self.hash_db_wizard.insert_new_hash(amount = (self.spare_hashes_plank-current_unused))
            time.sleep(self.spare_hash_check_period)

    # Get the next unused hash
    def get_next_unused_hash(self):
        if not self.hash_db_wizard.count_unused_hashes():
            self.hash_db_wizard.insert_new_hashes(1)
        return self.hash_db_wizard.get_next_unused_hash()