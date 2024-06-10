import time
from threading import Thread, Event
from pastebin_main_app.utils.myUtilFunctions import insert_to_sorted_list_returning_position
from typing import Callable
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
LOGGER = logging.getLogger(__name__)

class ExpiryController:
    # I was in two minds whether to us DI or pass the function and desided to stick with the second option
    def __init__ (self, delete_expired_entry: Callable):
        """
        Class that performs expiry monitoring based on unix float time and object id,
        
        Args:
            delete_expired_entry (Callable): function that will perform the deletion logic for expired object, based on an id

        Dependencies:
            insert_to_sorted_list_returning_position()
            threading.Thread, threading.Event
            time
        """
        self.expiry_registry = []
        self.expiry_event = Event()
        # argument-passed outer function!
        self.delete_expired_entry = delete_expired_entry

    # takes expiry time in unix format along with id
    def add_event(self, expiry_time, id):
        """
        This function Adds a tracked event to expiry registry and sets expity event,
          so the main method performs expiry check for it;

        Args:
            expiry_time (float): float unix format expiry time of some event (database or blobstorage entry for instance);
            id (Any): some identifier (id) so expiry registry can refer to it;
        Returns:
            None
        """
        new_event = (expiry_time, id)
        insertion_point = insert_to_sorted_list_returning_position(self.expiry_registry, new_event)
        LOGGER.info(f'Entry added {expiry_time} -- {id}')

        if insertion_point == 0:
            self.expiry_event.set()

    def run_expiry_controller(self):
        LOGGER.info('The expiry controller started')
        LOGGER.info(len(self.expiry_registry))
        while True:
            if not self.expiry_registry:
                self.expiry_event.wait()
                self.expiry_event.clear()
                continue

            current_time = time.time()

            # Make sure both are float:
            time_til_next_expiry = self.expiry_registry[0][0] - current_time
            
            # LOGGER.info('Performing a check: ')
            if time_til_next_expiry <= 0:
                deletionThread = Thread(target=self.delete_expired_entry, args=(self.expiry_registry[0][1],))
                deletionThread.start()
                self.expiry_registry.pop(0)
            else:
                self.expiry_event.wait(timeout=time_til_next_expiry)
                self.expiry_event.clear()       

from .myUtilFunctions import delete_expired_entry_by_id
myExpController = ExpiryController(delete_expired_entry_by_id)