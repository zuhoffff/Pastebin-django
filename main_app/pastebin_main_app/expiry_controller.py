import time
from threading import Thread, Event
from .models import Metadata
from main_app.pastebin_main_app.s3_handler import delete_from_s3
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
LOGGER = logging.getLogger(__name__)

expiry_registry = []
expiry_event=Event()

def insert_sorted_tuple_list(lst, value):
    """
    Inserts a value into a sorted list (even of tuples), keeping the order (ascending).
    
    Parameters:
    lst (list of tuples): The sorted list to insert into.
    value (tuple): The value to insert.
    
    Returns:
    int: The insertion point.
    """

    left, right = 0, len(lst)

    while left<right:
        mid=(left+right)//2    
        if value > lst[mid]:
            left=mid + 1
        else:
            right=mid
    
    lst.insert(left, value)
    return left

def add_event(expiry_time, id):
    new_event=(expiry_time, id)
    # Keep the registry sorted
    insertion_point = insert_sorted_tuple_list(expiry_registry, new_event)

    if insertion_point == 0:
    # Send signal or smth to terminate the sleep
        expiry_event.set()

def run_expiry_controller(check_period = 60):
    while True:
        current_time=time.time()
        soonest_expiry_in=expiry_registry[0][0] - current_time
            # If paste exipres in less then or minute, create thread to delete it
        if soonest_expiry_in <= 0:
            t = Thread(delete_expired_entry(),args=(expiry_registry[0][1]))
            t.start()            
            expiry_registry.pop(0)
        else:
            # Wait for the soonest expiry
            time.sleep(soonest_expiry_in/1000) # Convert to seconds

def delete_expired_entry(id):
    print('Debug deletion {}))'.format(id))
    # expired_entry = Metadata.objects.get(id)
    # delete_from_s3(expired_entry.s3_key)
    # expired_entry.delete()
    # LOGGER.info('Expited entry deleted.')