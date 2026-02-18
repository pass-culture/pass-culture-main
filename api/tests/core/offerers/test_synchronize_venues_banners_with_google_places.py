import logging
from unittest.mock import patch

import googlemaps
import pytest
import time_machine

from pcapi.core.offerers import synchronize_venues_banners_with_google_places
from pcapi.core.offerers.factories import GooglePlacesInfoFactory
from pcapi.core.offerers.factories import VenueFactory


pytestmark = pytest.mark.usefixtures("db_session")


@pytest.mark.parametrize("frequency", [1, 2, 4])
def test_all_venue_banners_with_google_places_are_fetched(frequency):
    venues = VenueFactory.create_batch(
        5, isPermanent=True, _bannerUrl=None, venueTypeCode="OTHER", managingOfferer__isActive=True
    )
    venues_to_synchronize = []
    for day in range(28):
        current_day = f"2024-12-{day + 1:02d} 23:00:00"
        with time_machine.travel(current_day):
            venues_to_synchronize += synchronize_venues_banners_with_google_places.get_venues_without_photo(frequency)

    assert (venues * frequency).sort(key=lambda venue: venue.id) == venues_to_synchronize.sort(
        key=lambda venue: venue.id
    )


class SynchronizeVenuesBannersWithGooglePlacesTest:
    @patch(
        "pcapi.core.offerers.synchronize_venues_banners_with_google_places.get_place_id", return_value="new_place_id"
    )
    @patch(
        "pcapi.core.offerers.synchronize_venues_banners_with_google_places.get_place_photos_and_owner",
        side_effect=[
            googlemaps.exceptions.ApiError(status="NOT_FOUND"),
            synchronize_venues_banners_with_google_places.PlaceDetails(name="Nom du lieu", photos=[]),
        ],
    )
    def test_update_place_id_on_not_found(self, _mock_get_place_photos_and_owner, _mock_get_place_id):
        venue = VenueFactory()
        venue.googlePlacesInfo = GooglePlacesInfoFactory()
        synchronize_venues_banners_with_google_places.synchronize_venues_banners_with_google_places([venue])

        assert venue.googlePlacesInfo.placeId == "new_place_id"

    @patch(
        "pcapi.core.offerers.synchronize_venues_banners_with_google_places.get_place_photos_and_owner",
        side_effect=googlemaps.exceptions.ApiError(status="INVALID_REQUEST"),
    )
    def test_raise_on_error(self, _mock_get_place_photos_and_owner, caplog):
        venue = VenueFactory()
        venue.googlePlacesInfo = GooglePlacesInfoFactory()
        with caplog.at_level(logging.ERROR):
            synchronize_venues_banners_with_google_places.synchronize_venues_banners_with_google_places([venue])

        assert caplog.records[0].message == f"[gmaps_banner_synchro]venue id: {venue.id} error: INVALID_REQUEST"
