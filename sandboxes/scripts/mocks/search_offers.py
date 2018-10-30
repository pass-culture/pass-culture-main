""" search offers """"

from domain.types import get_format_types

def get_all_events_or_things_by_type():
    types = get_format_types()
    print(types)
