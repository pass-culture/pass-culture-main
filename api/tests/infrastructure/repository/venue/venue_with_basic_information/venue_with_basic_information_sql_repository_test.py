import pytest

import pcapi.core.offerers.factories as offerers_factories
from pcapi.domain.venue.venue_with_basic_information.venue_with_basic_information import VenueWithBasicInformation
from pcapi.infrastructure.repository.venue.venue_with_basic_information.venue_with_basic_information_sql_repository import (
    VenueWithBasicInformationSQLRepository,
)


pytestmark = pytest.mark.usefixtures("db_session")


class VenueWithBasicInformationSQLRepositoryTest:
    def setup_method(self):
        self.venue_sql_repository = VenueWithBasicInformationSQLRepository()

    def test_returns_a_venue_when_venue_with_siret_is_found(self):
        venue = offerers_factories.VenueFactory()

        found_venue = self.venue_sql_repository.find_by_siret(venue.siret)

        assert isinstance(found_venue, VenueWithBasicInformation)
        assert found_venue.siret == venue.siret
        assert found_venue.identifier == venue.id

    def test_returns_a_venue_when_venue_with_name_is_found(self):
        name = "Shared venue name"
        venue1 = offerers_factories.VenueFactory(name=name, siret=None, comment="no siret")
        offerers_factories.VenueFactory(name=name, siret=None, comment="no siret")

        found_venues = self.venue_sql_repository.find_by_name(
            name,
            venue1.managingOffererId,
        )

        assert len(found_venues) == 1
        found_venue = found_venues[0]
        assert isinstance(found_venue, VenueWithBasicInformation)
        assert found_venue.name == name
        assert found_venue.identifier == venue1.id
        assert found_venue.siret is None
