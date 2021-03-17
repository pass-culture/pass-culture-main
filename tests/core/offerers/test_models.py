import pytest

from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.models import Venue
from pcapi.core.offers import factories
import pcapi.core.offers.factories as offers_factories


@pytest.mark.usefixtures("db_session")
class VenueTimezonePropertyTest:
    def test_europe_paris_is_default_timezone(self):
        venue = factories.VenueFactory(postalCode="75000")

        assert venue.timezone == "Europe/Paris"

    def test_return_timezone_given_venue_departement_code(self):
        venue = factories.VenueFactory(postalCode="97300")

        assert venue.timezone == "America/Cayenne"

    def test_return_managing_offerer_timezone_when_venue_is_virtual(self):
        venue = factories.VirtualVenueFactory(managingOfferer__postalCode="97300")

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

    def test_return_managing_offerer_timezone_when_venue_is_virtual(self):
        factories.VirtualVenueFactory(managingOfferer__postalCode="97300")

        query_result = Venue.query.filter(Venue.timezone == "America/Cayenne").all()

        assert len(query_result) == 1


@pytest.mark.usefixtures("db_session")
class OffererDepartementCodePropertyTest:
    def test_metropole_postal_code(self):
        offerer = offers_factories.OffererFactory(postalCode="75000")

        assert offerer.departementCode == "75"

    def test_drom_postal_code(self):
        offerer = offers_factories.OffererFactory(postalCode="97300")

        assert offerer.departementCode == "973"


@pytest.mark.usefixtures("db_session")
class OffererDepartementCodeSQLExpressionTest:
    def test_metropole_postal_code(self):
        offers_factories.OffererFactory(postalCode="75000")

        query_result = Offerer.query.filter(Offerer.departementCode == "75").all()

        assert len(query_result) == 1

    def test_drom_postal_code(self):
        offers_factories.OffererFactory(postalCode="97300")

        query_result = Offerer.query.filter(Offerer.departementCode == "973").all()

        assert len(query_result) == 1
