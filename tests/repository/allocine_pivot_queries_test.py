import pytest
from werkzeug.exceptions import NotFound

from pcapi.core.offers import factories as offers_factories
from pcapi.core.providers.factories import AllocinePivotFactory
from pcapi.repository.allocine_pivot_queries import get_allocine_pivot_for_venue
from pcapi.repository.allocine_pivot_queries import has_allocine_pivot_for_venue


class HasAllocinePivotForVenueTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_return_false_when_venue_has_no_siret(self, app):
        # Given
        venue = offers_factories.VenueFactory(siret=None, comment="En attente de siret")
        AllocinePivotFactory(siret="12345678912345")

        # When
        has_allocine_pivot = has_allocine_pivot_for_venue(venue)

        # Then
        assert not has_allocine_pivot


class GetAllocinePivotForVenueTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_not_return_value_when_venue_siret_is_none(self, app):
        # Given
        venue = offers_factories.VenueFactory(siret=None, comment="En attente de siret")
        AllocinePivotFactory(siret="12345678912345")

        # When
        with pytest.raises(NotFound) as exception:
            get_allocine_pivot_for_venue(venue)

        # Then
        assert str(exception.value) == "404 Not Found: No Allocine pivot was found for the venue with SIRET: None"

    @pytest.mark.usefixtures("db_session")
    def test_should_not_return_value_when_not_matching_in_allocine_pivot(self, app):
        # Given
        venue = offers_factories.VenueFactory(siret="12345678912346")
        AllocinePivotFactory(siret="12345678912345")

        # When
        with pytest.raises(NotFound) as exception:
            get_allocine_pivot_for_venue(venue)

        # Then
        assert (
            str(exception.value)
            == "404 Not Found: No Allocine pivot was found for the venue with SIRET: 12345678912346"
        )

    @pytest.mark.usefixtures("db_session")
    def test_should_return_allocine_pivot_when_siret_is_present_in_allocine_pivot(self, app):
        # Given
        venue = offers_factories.VenueFactory(siret="12345678912345")
        allocine_pivot = AllocinePivotFactory(siret="12345678912345")

        # When
        allocine_pivot_from_venue = get_allocine_pivot_for_venue(venue)

        # Then
        assert allocine_pivot_from_venue.id == allocine_pivot.id
