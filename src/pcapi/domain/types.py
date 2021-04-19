from pcapi.models.offer_type import EventType
from pcapi.models.offer_type import ThingType


def get_formatted_active_product_types() -> list:
    active_event_format_types = [type_obj.as_dict() for type_obj in EventType if type_obj.value["isActive"]]
    active_thing_format_types = [type_obj.as_dict() for type_obj in ThingType if type_obj.value["isActive"]]
    all_active_types = active_event_format_types + active_thing_format_types

    all_active_types = filter(lambda t: "ACTIVATION" not in t["value"], all_active_types)

    return list(all_active_types)
