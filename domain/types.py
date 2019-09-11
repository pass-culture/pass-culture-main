from typing import List

from models.offer_type import EventType, ThingType


def get_formatted_event_or_thing_active_types(with_activation_type=False) -> List:
    event_format_event_or_thing_active_types = [
        type_obj.as_dict() for type_obj in EventType
        if type_obj.value['isActive']
    ]
    thing_format_event_or_thing_active_types = [
        type_obj.as_dict() for type_obj in ThingType
        if type_obj.value['isActive']
    ]
    all_active_types = event_format_event_or_thing_active_types + thing_format_event_or_thing_active_types

    if not with_activation_type:
        all_active_types = filter(lambda t: 'ACTIVATION' not in t['value'], all_active_types)

    return list(all_active_types)


def get_event_or_thing_active_type_values_from_sublabels(sublabels):
    event_active_type_values = [
        str(et) for et in EventType
        if et.value['sublabel'] in sublabels and et.value['isActive']
    ]
    thing_active_type_values = [
        str(tt) for tt in ThingType
        if tt.value['sublabel'] in sublabels and tt.value['isActive']
    ]
    all_active_type_values = event_active_type_values + thing_active_type_values

    return list(all_active_type_values)
