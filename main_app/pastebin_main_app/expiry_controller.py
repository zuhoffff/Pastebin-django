import time
from threading import Thread, Event
import logging
from .models import Metadata
from main_app.pastebin_main_app.s3_handler import delete_from_s3

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
LOGGER = logging.getLogger(__name__)

expiry_registry = []
expiry_event = Event()

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

    while left < right:
        mid = (left + right) // 2    
        if value > lst[mid]:
            left = mid + 1
        else:
            right = mid
    
    lst.insert(left, value)
    return left

def add_event(expiry_time, id):
    global expiry_registry, expiry_event
    new_event = (expiry_time, id)
    insertion_point = insert_sorted_tuple_list(expiry_registry, new_event)

    if insertion_point == 0:
        expiry_event.set()

def run_expiry_controller():
    while True:
        if not expiry_registry:
            expiry_event.wait()
            expiry_event.clear()
            continue

        current_time = time.time()
        soonest_expiry_in = expiry_registry[0][0] - current_time

        if soonest_expiry_in <= 0:
            t = Thread(target=delete_expired_entry, args=(expiry_registry[0][1],))
            t.start()
            expiry_registry.pop(0)
        else:
            expiry_event.wait(timeout=soonest_expiry_in)
            expiry_event.clear()

def delete_expired_entry(id):
    LOGGER.info(f'Deleting expired entry with id: {id}')
    expired_entry = Metadata.objects.get(id=id)
    delete_from_s3(expired_entry.s3_key)
    expired_entry.delete()
    LOGGER.info('Expired entry deleted.')

def start_expiry_controller():
    expiry_controller_thread = Thread(target=run_expiry_controller)
    expiry_controller_thread.start()
    LOGGER.info('start_expiry_controller started')
    # return expiry_controller_thread