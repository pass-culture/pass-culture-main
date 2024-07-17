from typing import Any


def compute_venue_reference(idAtProvider: str, venueId: int) -> str:
    return f"{idAtProvider}@{venueId}"


def get_field(obj: Any, updates: dict, field: str, col: Any = None, aliases: set | None = None) -> Any:
    # Sanity check to prevent wrongly named field, as field is litteral
    # and hence not directly linked to its corresponding schema:
    if aliases is not None and field not in aliases:
        raise ValueError(f"Unknown schema field: {field}")
    name = field if col is None else col
    return updates.get(field, getattr(obj, name))
