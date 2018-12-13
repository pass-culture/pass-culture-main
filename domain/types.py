""" types """
from models.offer_type import EventType, ThingType

def get_formatted_event_or_thing_types(with_activation_type=False) -> dict:
    event_format_event_or_thing_types = [type_obj.as_dict() for type_obj in EventType]
    thing_format_event_or_thing_types = [type_obj.as_dict() for type_obj in ThingType]
    all_types = event_format_event_or_thing_types + thing_format_event_or_thing_types

    if not with_activation_type:
        all_types = [t for t in all_types if 'ACTIVATION' not in t['value']]

    return all_types

def get_event_or_thing_type_values_from_sublabels(sublabels):
    event_type_values = [str(et) for et in EventType if et.value['sublabel'] in sublabels]
    thing_type_values = [str(tt) for tt in ThingType if tt.value['sublabel'] in sublabels]

    return event_type_values + thing_type_values
