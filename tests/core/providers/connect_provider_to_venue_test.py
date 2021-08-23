from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offers.factories import VenueFactory
from pcapi.core.providers.api import connect_venue_to_provider
from pcapi.core.providers.exceptions import NoSiretSpecified
from pcapi.core.providers.exceptions import ProviderWithoutApiImplementation
from pcapi.core.providers.exceptions import VenueSiretNotRegistered
from pcapi.core.providers.models import VenueProvider
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_provider
from pcapi.model_creators.generic_creators import create_venue
from pcapi.repository import repository


@pytest.mark.usefixtures("db_session")
@patch(
    "pcapi.infrastructure.repository.stock_provider.provider_api.ProviderAPI.is_siret_registered",
    return_value=True,
)
def test_when_venue_id_at_offer_provider_is_given(can_be_synchronized, app):
    # Given
    venue_id_at_offer_provider = "id_for_remote_system"
    venue = VenueFactory(siret="12345678912345")
    provider = offerers_factories.APIProviderFactory()

    # When
    connect_venue_to_provider(venue, provider, venue_id_at_offer_provider)

    # Then
    venue_provider = VenueProvider.query.one()
    assert venue_provider.venueIdAtOfferProvider == venue_id_at_offer_provider
    can_be_synchronized.assert_called_once_with("id_for_remote_system")


@pytest.mark.usefixtures("db_session")
@patch(
    "pcapi.infrastructure.repository.stock_provider.provider_api.ProviderAPI.is_siret_registered",
    return_value=True,
)
def test_use_siret_as_default(can_be_synchronized, app):
    # Given
    venue = VenueFactory(siret="12345678912345")
    provider = offerers_factories.APIProviderFactory()

    # When
    connect_venue_to_provider(venue, provider, None)

    # Then
    venue_provider = VenueProvider.query.one()
    assert venue_provider.venueIdAtOfferProvider == "12345678912345"
    can_be_synchronized.assert_called_once_with("12345678912345")


class WhenProviderImplementsProviderAPITest:
    def setup_class(self):
        self.find_by_id = MagicMock()

    @pytest.mark.usefixtures("db_session")
    @patch(
        "pcapi.core.providers.api._siret_can_be_synchronized",
        return_value=True,
    )
    def should_connect_venue_when_synchronization_is_allowed(self, app):
        # Given
        offerer = create_offerer()

        venue = create_venue(offerer)
        provider = offerers_factories.APIProviderFactory()

        repository.save(venue)

        self.find_by_id.return_value = venue
        stock_repository = MagicMock()
        stock_repository.can_be_synchronized.return_value = True

        # When
        connect_venue_to_provider(venue, provider)

        # Then
        fnac_venue_provider = VenueProvider.query.one()
        assert fnac_venue_provider.venue == venue

    @pytest.mark.usefixtures("db_session")
    @patch(
        "pcapi.core.providers.api._siret_can_be_synchronized",
        return_value=False,
    )
    def should_not_connect_venue_when_synchronization_is_not_allowed(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer, siret="12345678912345")
        provider = offerers_factories.APIProviderFactory(name="FNAC")

        repository.save(venue)

        self.find_by_id.return_value = venue
        stock_repository = MagicMock()
        stock_repository.can_be_synchronized.return_value = False

        # when
        with pytest.raises(VenueSiretNotRegistered):
            connect_venue_to_provider(venue, provider)

        # then
        assert not VenueProvider.query.first()

    @pytest.mark.usefixtures("db_session")
    def should_not_connect_venue_when_venue_has_no_siret(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer, siret=None, is_virtual=True)
        provider = offerers_factories.APIProviderFactory(name="FNAC")

        repository.save(venue)

        self.find_by_id.return_value = venue

        # when
        with pytest.raises(NoSiretSpecified):
            connect_venue_to_provider(venue, provider)

        # then
        assert not VenueProvider.query.first()


class WhenProviderIsSomethingElseTest:
    def setup_class(self):
        self.find_by_id = MagicMock()

    @pytest.mark.usefixtures("db_session")
    def should_raise_an_error(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        provider = create_provider(local_class="TestLocalProvider")
        repository.save(venue, provider)

        self.find_by_id.return_value = venue

        # When
        with pytest.raises(ProviderWithoutApiImplementation):
            connect_venue_to_provider(venue, provider)

        # Then
        assert not VenueProvider.query.first()
