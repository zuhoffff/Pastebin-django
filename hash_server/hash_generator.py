from hashDbWizard import HashDbWizard
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HashGenerator:

    # Inject class that handles database interaction logic 
    def __init__(self, db_wizard: HashDbWizard, number_of_spare_hashes=100, spare_hash_check_period=5):
        self.hash_db_wizard = db_wizard
        self.spare_hashes_plank = number_of_spare_hashes
        self.spare_hash_check_period = spare_hash_check_period

    # Ensure a certain number of spare hashes
    def ensure_spare_hashes(self):
        current_unused = self.hash_db_wizard.count_unused_hashes()
        needed_amount=(self.spare_hashes_plank-current_unused)
        if needed_amount > 0:
            self.hash_db_wizard.insert_new_hashes(amount=needed_amount)
            logger.info(f'Added {needed_amount} hashes to db')

    # Get the next unused hash
    def get_next_unused_hash(self):
        hash = self.hash_db_wizard.get_next_unused_hash()
        logger.info(hash)
        if not hash:
            self.hash_db_wizard.insert_new_hashes(1)
            hash = self.hash_db_wizard.get_next_unused_hash()
        return hash