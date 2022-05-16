import pytest

import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.providers.factories import AllocinePivotFactory
from pcapi.core.providers.repository import get_allocine_pivot_for_venue
from pcapi.core.providers.repository import has_allocine_pivot_for_venue


class HasAllocinePivotForVenueTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_return_false(self, app):
        # Given
        venue = offerers_factories.VenueFactory(id=1234)
        another_venue = offerers_factories.VenueFactory(id=4567)
        AllocinePivotFactory(venue=another_venue)

        # When
        has_allocine_pivot = has_allocine_pivot_for_venue(venue)

        # Then
        assert not has_allocine_pivot

    @pytest.mark.usefixtures("db_session")
    def test_should_return_true(self, app):
        # Given
        venue_id = 1234
        venue = offerers_factories.VenueFactory(id=venue_id)
        AllocinePivotFactory(venue=venue)

        # When
        has_allocine_pivot = has_allocine_pivot_for_venue(venue)

        # Then
        assert has_allocine_pivot


class GetAllocinePivotForVenueTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_not_return_value_when_not_matching_in_allocine_pivot(self, app):
        # Given
        venue = offerers_factories.VenueFactory()
        another_venue = offerers_factories.VenueFactory()
        AllocinePivotFactory(venue=another_venue)

        # When
        allocine_pivot = get_allocine_pivot_for_venue(venue)

        # Then
        assert not allocine_pivot

    @pytest.mark.usefixtures("db_session")
    def test_should_return_allocine_pivot_when_venue_is_present_in_allocine_pivot(self, app):
        # Given
        venue = offerers_factories.VenueFactory()
        allocine_pivot = AllocinePivotFactory(venue=venue)

        # When
        allocine_pivot_from_venue = get_allocine_pivot_for_venue(venue)

        # Then
        assert allocine_pivot_from_venue.id == allocine_pivot.id
