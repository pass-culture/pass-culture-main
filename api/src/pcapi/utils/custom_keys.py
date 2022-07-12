def compute_venue_reference(idAtProvider: str | None, venueId: int) -> str | None:
    return f"{idAtProvider}@{venueId}" if idAtProvider else None
