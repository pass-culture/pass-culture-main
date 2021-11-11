from typing import Optional


def compute_venue_reference(idAtProvider: Optional[str], venueId: int) -> Optional[str]:
    return f"{idAtProvider}@{venueId}" if idAtProvider else None
