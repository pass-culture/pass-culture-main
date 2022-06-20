from typing import Tuple

from pcapi.core.bookings import repository as bookings_repository
from pcapi.core.offers import repository as offers_repository


def get_venue_stats(venue_id: int) -> Tuple[int, int, int, int]:
    active_bookings_quantity = bookings_repository.get_active_bookings_quantity_for_venue(venue_id)
    validated_bookings_count = bookings_repository.get_validated_bookings_quantity_for_venue(venue_id)
    active_offers_count = offers_repository.get_active_offers_count_for_venue(venue_id)
    sold_out_offers_count = offers_repository.get_sold_out_offers_count_for_venue(venue_id)

    return (active_bookings_quantity, validated_bookings_count, active_offers_count, sold_out_offers_count)
