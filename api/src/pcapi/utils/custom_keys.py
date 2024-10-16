from typing import Any


def compute_venue_reference(idAtProvider: str, venueId: int) -> str:
    return f"{idAtProvider}@{venueId}"


def get_field(  # pylint: disable=too-many-positional-arguments
    obj: Any,
    updates: dict,
    field: str,
    col: Any = None,
    aliases: set | None = None,
    nullable: bool = True,
) -> Any:
    # Sanity check to prevent wrongly named field, as field is litteral
    # and hence not directly linked to its corresponding schema:
    if aliases is not None and field not in aliases:
        raise ValueError(f"Unknown schema field: {field}")

    name = field if col is None else col
    current_value = getattr(obj, name)
    new_value = updates.get(field, current_value)

    if new_value is None and not nullable:
        return current_value
    return new_value
