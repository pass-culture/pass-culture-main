import pytest

import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.providers.factories import AllocineTheaterFactory
from pcapi.core.providers.repository import get_allocine_theater
from pcapi.core.providers.repository import is_venue_known_by_allocine


class IsVenueKnownByAllocineTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_return_false(self, app):
        # Given
        venue = offerers_factories.VenueFactory(id=1234)
        AllocineTheaterFactory()

        # When
        has_allocine_theater = is_venue_known_by_allocine(venue)

        # Then
        assert not has_allocine_theater

    @pytest.mark.usefixtures("db_session")
    def test_should_return_true(self, app):
        # Given
        venue_id = 1234
        venue = offerers_factories.VenueFactory(id=venue_id)
        AllocineTheaterFactory(siret=venue.siret)

        # When
        has_allocine_theater = is_venue_known_by_allocine(venue)

        # Then
        assert has_allocine_theater


class GetAllocineTheaterTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_not_return_value_when_not_matching_in_allocine_theater(self, app):
        # Given
        venue = offerers_factories.VenueFactory()
        AllocineTheaterFactory()

        # When
        allocine_theater = get_allocine_theater(venue)

        # Then
        assert not allocine_theater

    @pytest.mark.usefixtures("db_session")
    def test_should_return_allocine_theater_when_venue_is_present_in_allocine_theater(self, app):
        # Given
        venue = offerers_factories.VenueFactory()
        allocine_theater = AllocineTheaterFactory(siret=venue.siret)

        # When
        allocine_theater_from_db = get_allocine_theater(venue)

        # Then
        assert allocine_theater.id == allocine_theater_from_db.id
