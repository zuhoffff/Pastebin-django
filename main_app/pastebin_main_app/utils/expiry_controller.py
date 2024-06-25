from datetime import datetime
from threading import Thread, Event
from pastebin_main_app.utils.my_util_functions import insert_to_sorted_list_returning_position
from typing import Callable
import logging

logger = logging.getLogger(__name__)

class ExpiryController:
    # I was in two minds whether to us DI or pass the function and desided to stick with the second option
    def __init__ (self, delete_expired_entry: Callable, run_continuously = True):
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
        self.run_continuously = run_continuously

    # takes expiry time in unix format along with id
    def add_event(self, expiry_time: int, id: str):
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
        logger.info(f'Expiry time added {expiry_time} -- {id}')

        if insertion_point == 0:
            self.expiry_event.set()

    def run_expiry_controller(self):
        logger.info('expiry controller started')
        while self.run_continuously:
            if not self.expiry_registry:
                self.expiry_event.wait()
                self.expiry_event.clear()
                logger.info('Waiting for new events')
                continue

            current_time = int(datetime.now().timestamp())
            logger.info(f'Current time: {current_time}')

            time_til_next_expiry = self.expiry_registry[0][0] - current_time
            logger.info(f'Time until next expiry: {time_til_next_expiry}')

            if time_til_next_expiry <= 0:
                deletionThread = Thread(target=self.delete_expired_entry, args=(self.expiry_registry[0][1],))
                deletionThread.start()
                self.expiry_registry.pop(0)
                logger.info('Processing and deleting expired event')
            else:
                self.expiry_event.wait(timeout=time_til_next_expiry)
                self.expiry_event.clear()
                logger.info('Waiting for the next expiry event')
    
    # for debug purposes
    def stop(self):
        self.run_continuously = False  # Method to stop the loop
        self.expiry_event.set() 
        print('stoped')

from .my_util_functions import delete_expired_entry_by_id
myExpController = ExpiryController(delete_expired_entry_by_id)