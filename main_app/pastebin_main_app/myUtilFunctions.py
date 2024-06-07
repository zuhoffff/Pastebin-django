def insert_to_sorted_list_returning_position(lst, value):
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

def delete_expired_entry_by_id(id):
    from .models import Metadata
    from pastebin_main_app.s3_handler import delete_from_s3
    expired_entry = Metadata.objects.get(id=id)
    delete_from_s3(expired_entry.url)