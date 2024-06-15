from hashDbWizard import HashDbWizard
import logging

logger = logging.getLogger(__name__)

class HashGenerator:

    # Inject class that handles database interaction logic 
    def __init__(self, db_wizard: HashDbWizard, number_of_spare_hashes=100, spare_hash_check_period=5):
        self.spare_hashes_plank = number_of_spare_hashes
        self.spare_hash_check_period = spare_hash_check_period
        self.hash_db_wizard = db_wizard

    # Ensure a certain number of spare hashes
    def ensure_spare_hashes(self):
        current_unused = self.hash_db_wizard.count_unused_hashes()
        needed_amount=(self.spare_hashes_plank-current_unused)
        self.hash_db_wizard.insert_new_hashes(amount=needed_amount)
        logger.info(f'Added {needed_amount} hashes to queue')

    # Get the next unused hash
    def get_next_unused_hash(self):
        if not self.hash_db_wizard.count_unused_hashes():
            self.hash_db_wizard.insert_new_hashes(1)
        return self.hash_db_wizard.get_next_unused_hash()