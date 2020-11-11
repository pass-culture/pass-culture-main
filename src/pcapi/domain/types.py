from typing import List

from pcapi.models.offer_type import EventType
from pcapi.models.offer_type import ThingType


def get_formatted_active_product_types() -> List:
    active_event_format_types = [type_obj.as_dict() for type_obj in EventType if type_obj.value["isActive"]]
    active_thing_format_types = [type_obj.as_dict() for type_obj in ThingType if type_obj.value["isActive"]]
    all_active_types = active_event_format_types + active_thing_format_types

    all_active_types = filter(lambda t: "ACTIVATION" not in t["value"], all_active_types)

    return list(all_active_types)


def get_active_product_type_values_from_sublabels(sublabels):
    active_event_type_values = [
        str(et) for et in EventType if et.value["sublabel"] in sublabels and et.value["isActive"]
    ]
    active_thing_type_values = [
        str(tt) for tt in ThingType if tt.value["sublabel"] in sublabels and tt.value["isActive"]
    ]
    all_active_type_values = active_event_type_values + active_thing_type_values

    return list(all_active_type_values)
