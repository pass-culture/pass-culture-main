""" types """
from models.offer_type import EventType, ThingType


def _format_type(t, model_name):
    result = t.value
    result['value'] = str(t)
    result['type'] = model_name
    return result


def get_formatted_types():
    event_format_types = [_format_type(et, 'Event') for et in EventType]
    thing_format_types = [_format_type(tt, 'Thing') for tt in ThingType]

    return event_format_types + thing_format_types


def get_type_values_from_sublabels(sublabels):
    event_type_values = [str(et) for et in EventType if et.value['sublabel'] in sublabels]
    thing_type_values = [str(tt) for tt in ThingType if tt.value['sublabel'] in sublabels]

    return event_type_values + thing_type_values
