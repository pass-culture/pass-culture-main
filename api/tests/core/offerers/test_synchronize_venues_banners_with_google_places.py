import pytest
import time_machine

from pcapi.core.offerers.factories import VenueFactory
from pcapi.core.offerers.synchronize_venues_banners_with_google_places import get_venues_without_photo


pytestmark = pytest.mark.usefixtures("db_session")


@pytest.mark.parametrize("frequency", [1, 2, 4])
def test_all_venue_banners_with_google_places_are_fetched(frequency):
    venues = VenueFactory.create_batch(
        50, isPermanent=True, _bannerUrl=None, venueTypeCode="OTHER", managingOfferer__isActive=True
    )
    venues_to_synchronize = []
    for day in range(28):
        current_day = f"2024-12-{day + 1:02d} 23:00:00"
        with time_machine.travel(current_day):
            venues_to_synchronize += get_venues_without_photo(frequency)

    assert (venues * frequency).sort(key=lambda venue: venue.id) == venues_to_synchronize.sort(
        key=lambda venue: venue.id
    )
