import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.providers.factories as providers_factories
from pcapi.core.providers.repository import get_allocine_theater


class GetAllocineTheaterTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_return_none_when_not_matching_in_allocine_theater(self, app):
        # Given
        venue = offerers_factories.VenueFactory()
        providers_factories.AllocineTheaterFactory()

        # When
        actual = get_allocine_theater(venue)

        # Then
        assert actual is None

    @pytest.mark.usefixtures("db_session")
    def test_should_return_allocine_theater_when_venue_is_present_in_allocine_theater(self, app):
        # Given
        venue = offerers_factories.VenueFactory()
        allocine_theater = providers_factories.AllocineTheaterFactory(siret=venue.siret)

        # When
        allocine_theater_from_db = get_allocine_theater(venue)

        # Then
        assert allocine_theater.id == allocine_theater_from_db.id
