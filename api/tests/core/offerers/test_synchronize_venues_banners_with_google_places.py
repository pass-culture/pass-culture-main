import pytest
import time_machine

from pcapi.core.offerers.factories import VenueFactory
from pcapi.core.offerers.synchronize_venues_banners_with_google_places import PlacePhoto
from pcapi.core.offerers.synchronize_venues_banners_with_google_places import get_crop_params
from pcapi.core.offerers.synchronize_venues_banners_with_google_places import get_venues_without_photo
from pcapi.utils.image_conversion import ImageRatio


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


def test_get_crop_params():
    photo = PlacePhoto(height=200, width=400, photo_reference="photo_reference", html_attributions=[])
    crop_params = get_crop_params(photo, ImageRatio.LANDSCAPE)
    assert crop_params.y_crop_percent == 0
    assert crop_params.x_crop_percent == 0.125
    assert crop_params.height_crop_percent == 1
    assert crop_params.width_crop_percent == 0.75

    photo = PlacePhoto(height=1000, width=300, photo_reference="photo_reference", html_attributions=[])
    crop_params = get_crop_params(photo, ImageRatio.LANDSCAPE)
    assert crop_params.y_crop_percent == 0.4
    assert crop_params.x_crop_percent == 0
    assert crop_params.height_crop_percent == 0.2
    assert crop_params.width_crop_percent == 1

    photo = PlacePhoto(height=400, width=200, photo_reference="photo_reference", html_attributions=[])
    crop_params = get_crop_params(photo, ImageRatio.PORTRAIT)
    assert crop_params.y_crop_percent == 0.125
    assert crop_params.x_crop_percent == 0
    assert crop_params.height_crop_percent == 0.75
    assert crop_params.width_crop_percent == 1

    photo = PlacePhoto(height=300, width=1000, photo_reference="photo_reference", html_attributions=[])
    crop_params = get_crop_params(photo, ImageRatio.PORTRAIT)
    assert crop_params.y_crop_percent == 0
    assert crop_params.x_crop_percent == 0.4
    assert crop_params.height_crop_percent == 1
    assert crop_params.width_crop_percent == 0.2
