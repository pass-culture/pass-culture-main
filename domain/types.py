from typing import List

from models.offer_type import EventType, ThingType


def get_formatted_event_or_thing_types(with_activation_type=False) -> List:
    event_format_event_or_thing_types = [type_obj.as_dict() for type_obj in EventType]
    thing_format_event_or_thing_types = [type_obj.as_dict() for type_obj in ThingType]
    all_types = event_format_event_or_thing_types + thing_format_event_or_thing_types
    all_types = filter(lambda t: t['value'] != str(ThingType.JEUX), all_types)

    if not with_activation_type:
        all_types = filter(lambda t: 'ACTIVATION' not in t['value'], all_types)

    return list(all_types)


def get_event_or_thing_type_values_from_sublabels(sublabels):
    event_type_values = [str(et) for et in EventType if et.value['sublabel'] in sublabels]
    thing_type_values = [str(tt) for tt in ThingType if tt.value['sublabel'] in sublabels]
    all_type_values = event_type_values + thing_type_values
    all_type_values = filter(lambda t: t != 'ThingType.JEUX', all_type_values)

    return list(all_type_values)
