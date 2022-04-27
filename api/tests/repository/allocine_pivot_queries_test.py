import pytest

import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.providers.factories import AllocinePivotFactory
from pcapi.core.providers.repository import has_allocine_pivot_for_venue
from pcapi.repository.allocine_pivot_queries import get_allocine_pivot_for_venue


class HasAllocinePivotForVenueTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_return_false_when_venue_has_no_siret(self, app):
        # Given
        venue = offerers_factories.VenueFactory(siret=None, comment="En attente de siret")
        AllocinePivotFactory(siret="12345678912345")

        # When
        has_allocine_pivot = has_allocine_pivot_for_venue(venue)

        # Then
        assert not has_allocine_pivot


class GetAllocinePivotForVenueTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_not_return_value_when_venue_siret_is_none(self, app):
        # Given
        venue = offerers_factories.VenueFactory(siret=None, comment="En attente de siret")
        AllocinePivotFactory(siret="12345678912345")

        # When
        allocine_pivot = get_allocine_pivot_for_venue(venue)

        # Then
        assert not allocine_pivot

    @pytest.mark.usefixtures("db_session")
    def test_should_not_return_value_when_not_matching_in_allocine_pivot(self, app):
        # Given
        venue = offerers_factories.VenueFactory(siret="12345678912346")
        AllocinePivotFactory(siret="12345678912345")

        # When
        allocine_pivot = get_allocine_pivot_for_venue(venue)

        # Then
        assert not allocine_pivot

    @pytest.mark.usefixtures("db_session")
    def test_should_return_allocine_pivot_when_siret_is_present_in_allocine_pivot(self, app):
        # Given
        venue = offerers_factories.VenueFactory(siret="12345678912345")
        allocine_pivot = AllocinePivotFactory(siret="12345678912345")

        # When
        allocine_pivot_from_venue = get_allocine_pivot_for_venue(venue)

        # Then
        assert allocine_pivot_from_venue.id == allocine_pivot.id
