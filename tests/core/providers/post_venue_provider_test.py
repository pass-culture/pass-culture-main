import pytest

from pcapi.core.providers import api
from pcapi.models import ApiErrors
from pcapi.routes.serialization.venue_provider_serialize import PostVenueProviderBody


class CreateVenueProviderTest:
    @pytest.mark.usefixtures("db_session")
    def test_prevent_creation_for_non_existing_provider(self):
        # Given
        providerId = "AE"
        venueId = "AE"
        venue_provider = PostVenueProviderBody(providerId=providerId, venueId=venueId)

        # When
        with pytest.raises(ApiErrors) as error:
            api.create_venue_provider(venue_provider)

        # Then
        assert error.value.errors["provider"] == ["Cette source n'est pas disponible"]
