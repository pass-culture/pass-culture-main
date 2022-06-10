import pytest

import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.providers.exceptions import UnknownVenueToAlloCine
import pcapi.core.providers.factories as providers_factories
from pcapi.core.providers.repository import AllocineVenue
from pcapi.core.providers.repository import get_allocine_theater


class IsVenueKnownByAllocineTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_throw(self, app):
        # Given
        venue = offerers_factories.VenueFactory(id=1234)
        providers_factories.AllocineTheaterFactory()
        providers_factories.AllocinePivotFactory()

        # When / Then
        with pytest.raises(UnknownVenueToAlloCine):
            AllocineVenue(venue)

    @pytest.mark.usefixtures("db_session")
    def test_should_return_theater_when_allocine_theater_is_present(self, app):
        # Given
        venue_id = 1234
        venue = offerers_factories.VenueFactory(id=venue_id)
        allocine_theater = providers_factories.AllocineTheaterFactory(siret=venue.siret)

        # When
        allocine_venue = AllocineVenue(venue)

        # Then
        assert allocine_venue.get_theater() == allocine_theater

    @pytest.mark.usefixtures("db_session")
    def test_should_return_true_when_allocine_pivot_is_present(self, app):
        # Given
        venue_id = 1234
        venue = offerers_factories.VenueFactory(id=venue_id)
        allocine_pivot = providers_factories.AllocinePivotFactory(venue=venue)

        # When
        allocine_venue = AllocineVenue(venue)

        # Then
        assert allocine_venue.get_pivot() == allocine_pivot


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
