import pytest

from pcapi.core.offerers.models import Venue
from pcapi.core.offers import factories


@pytest.mark.usefixtures("db_session")
class VenueTimezonePropertyTest:
    def test_europe_paris_is_default_timezone(self):
        venue = factories.VenueFactory(postalCode="75000")

        assert venue.timezone == "Europe/Paris"

    def test_return_timezone_given_venue_departement_code(self):
        venue = factories.VenueFactory(postalCode="97300")

        assert venue.timezone == "America/Cayenne"


@pytest.mark.usefixtures("db_session")
class VenueTimezoneSqlQueryTest:
    def test_europe_paris_is_default_timezone(self):
        factories.VenueFactory(postalCode="75000")

        query_result = Venue.query.filter(Venue.timezone == "Europe/Paris").all()

        assert len(query_result) == 1

    def test_return_timezone_given_venue_departement_code(self):
        factories.VenueFactory(postalCode="97300")

        query_result = Venue.query.filter(Venue.timezone == "America/Cayenne").all()

        assert len(query_result) == 1
