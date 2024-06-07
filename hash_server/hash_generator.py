from hashDbWizard import HashDbWizard
import time
from logger import logger

class HashGenerator:

    # Inject class that handles database interaction logic 
    def __init__(self, db_wizard: HashDbWizard, number_of_spare_hashes=100, spare_hash_check_period=5):
        self.spare_hashes_plank = number_of_spare_hashes
        self.spare_hash_check_period = spare_hash_check_period
        self.hash_db_wizard = db_wizard
        logger.info('hash generator instance crated')

    # Ensure a certain number of spare hashes
    def ensure_spare_hashes(self):
        logger.info(f'Ensuring at least {self.spare_hashes_plank} spare hashes.')
        current_unused = self.hash_db_wizard.count_unused_hashes()
        needed_amount=(self.spare_hashes_plank-current_unused)
        logger.info(needed_amount)
        self.hash_db_wizard.insert_new_hashes(amount=needed_amount)
        logger.info(f'Ensured')
        # time.sleep(self.spare_hash_check_period)

    # Get the next unused hash
    def get_next_unused_hash(self):
        if not self.hash_db_wizard.count_unused_hashes():
            self.hash_db_wizard.insert_new_hashes(1)
        return self.hash_db_wizard.get_next_unused_hash()