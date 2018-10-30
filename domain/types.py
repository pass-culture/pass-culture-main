""" types """
from models.offer_type import EventType, ThingType


def get_formatted_types(as_admin=False):
    event_format_types = [_format_type(type, 'Event') for type in EventType]
    thing_format_types = [_format_type(type, 'Thing') for type in ThingType]
    all_types = event_format_types + thing_format_types

    if not as_admin:
        all_types = [t for t in all_types if 'ACTIVATION' not in t['value']]

    return all_types

def get_type_values_from_sublabels(sublabels):
    event_type_values = [str(et) for et in EventType if et.value['sublabel'] in sublabels]
    thing_type_values = [str(tt) for tt in ThingType if tt.value['sublabel'] in sublabels]

    return event_type_values + thing_type_values

def _format_type(type, model_name):
    result = type.value
    result['value'] = str(type)
    result['type'] = model_name
    return result
    
def get_types_by_value():
    all_types = get_format_types()
    types_by_value = {}
    for all_type in all_types:
        types_by_value[all_type['value']] = all_type
    return types_by_value
