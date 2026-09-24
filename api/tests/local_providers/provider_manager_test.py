from unittest.mock import patch

import pytest

import pcapi.core.providers.factories as providers_factories
from pcapi.local_providers.provider_manager import synchronize_venue_provider
from pcapi.local_providers.provider_manager import synchronize_venue_providers

from tests.connectors.cgr import soap_definitions
from tests.local_providers.provider_test_utils import TestLocalProvider


def mock_update_objects():
    raise ValueError


def mock_init_provider(*arg):
    raise ValueError


@pytest.mark.usefixtures("db_session")
class SynchronizeVenueProviderTest:
    @pytest.mark.parametrize(
        "cinema_details_factory",
        [
            providers_factories.CGRCinemaDetailsFactory,
            providers_factories.CDSCinemaDetailsFactory,
            providers_factories.BoostCinemaDetailsFactory,
            providers_factories.EMSCinemaDetailsFactory,
        ],
    )
    @patch("pcapi.core.providers.etls.cinema_etl_template.CinemaETLProcessTemplate.execute")
    @patch("pcapi.local_providers.local_provider.LocalProvider.updateObjects")
    def test_should_start_etl_process(self, mock_updateObjects, mock_execute, cinema_details_factory, requests_mock):
        cinema_details = cinema_details_factory()
        pivot = cinema_details.cinemaProviderPivot
        venue_provider = providers_factories.VenueProviderFactory(
            provider=pivot.provider,
            venueIdAtOfferProvider=pivot.idAtProvider,
        )

        # for CGR
        requests_mock.get("http://example.com/web_service?wsdl", text=soap_definitions.WEB_SERVICE_DEFINITION)
        cinema_details.cinemaUrl = "http://example.com/web_service"

        synchronize_venue_provider(venue_provider)

        mock_execute.assert_called_with()
        mock_updateObjects.assert_not_called()


class SynchronizeVenueProvidersTest:
    @patch("pcapi.local_providers.local_provider.LocalProvider.updateObjects")
    @patch(
        "pcapi.local_providers.provider_manager._NAME_TO_LOCAL_PROVIDER_CLASS", {"AllocineStocks": TestLocalProvider}
    )
    @pytest.mark.usefixtures("db_session")
    def test_should_call_update_objects(self, mock_updateObjects):
        allocine = providers_factories.AllocineProviderFactory()
        venue_provider = providers_factories.VenueProviderFactory(provider=allocine)

        synchronize_venue_providers([venue_provider], limit=None)

        mock_updateObjects.assert_called_once_with(None)

    @patch("pcapi.local_providers.local_provider.LocalProvider.updateObjects")
    @patch(
        "pcapi.local_providers.provider_manager._NAME_TO_LOCAL_PROVIDER_CLASS", {"AllocineStocks": TestLocalProvider}
    )
    @pytest.mark.usefixtures("db_session")
    def test_should_synchronize_venue_provider_with_defined_limit(self, mock_updateObjects):
        allocine = providers_factories.AllocineProviderFactory()
        venue_provider = providers_factories.VenueProviderFactory(provider=allocine)

        synchronize_venue_providers([venue_provider], limit=10)

        mock_updateObjects.assert_called_once_with(10)

    @patch("pcapi.local_providers.provider_manager.synchronize_venue_provider")
    @pytest.mark.usefixtures("db_session")
    def test_should_call_synchronize_venue_provider(self, mock_synchronize_venue_provider):
        providers_factories.ProviderFactory()
        venue_provider = providers_factories.VenueProviderFactory()

        synchronize_venue_providers([venue_provider], limit=10)
        mock_synchronize_venue_provider.assert_called_once()

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.local_providers.provider_manager.synchronize_venue_provider")
    def test_catch_exception_and_continue(self, mock_synchronize_venue_provider):
        venue_provider_1 = providers_factories.VenueProviderFactory()
        venue_provider_2 = providers_factories.VenueProviderFactory()

        mock_synchronize_venue_provider.side_effect = ValueError()

        synchronize_venue_providers([venue_provider_1, venue_provider_2], 10)
        assert mock_synchronize_venue_provider.call_count == 2
