from unittest.mock import patch

import pytest
import requests_mock

import pcapi.core.providers.factories as providers_factories
from pcapi.core.offers.models import Offer
from pcapi.core.providers.repository import get_provider_by_local_class
from pcapi.local_providers.provider_manager import synchronize_data_for_provider
from pcapi.local_providers.provider_manager import synchronize_ems_venue_provider
from pcapi.local_providers.provider_manager import synchronize_venue_provider
from pcapi.local_providers.provider_manager import synchronize_venue_providers
from pcapi.models import db
from pcapi.repository import repository

from tests.local_providers.cinema_providers.ems import fixtures as ems_fixtures
from tests.local_providers.provider_test_utils import TestLocalProvider


def mock_update_objects():
    raise ValueError


def mock_init_provider(*arg):
    raise ValueError


class SynchronizeVenueProviderTest:
    @pytest.mark.usefixtures("db_session")
    @patch(
        "pcapi.local_providers.provider_manager._NAME_TO_LOCAL_PROVIDER_CLASS", {"AllocineStocks": TestLocalProvider}
    )
    @patch("pcapi.local_providers.local_provider.LocalProvider.updateObjects")
    def test_should_start_synchronization_with_linked_provider(self, mock_updateObjects):
        # Given
        allocine = providers_factories.AllocineProviderFactory()
        venue_provider = providers_factories.VenueProviderFactory(provider=allocine)

        synchronize_venue_provider(venue_provider, limit=10)

        mock_updateObjects.assert_called_once_with(10)


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


class SynchronizeDataForProviderTest:
    @patch("pcapi.local_providers.local_provider.LocalProvider.updateObjects")
    @patch("pcapi.local_providers.provider_manager._NAME_TO_LOCAL_PROVIDER_CLASS", {"Provider": TestLocalProvider})
    @pytest.mark.usefixtures("db_session")
    def test_should_call_do_update_for_specified_provider(self, mock_updateObjects, app):
        provider_test = providers_factories.AllocineProviderFactory()
        repository.save(provider_test)

        synchronize_data_for_provider(provider_test.__class__.__name__, None)

        mock_updateObjects.assert_called_once_with(None)


class SynchronizeEMSVenueProviderTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_synchronize_ems_venue_provider(self):
        ems_provider = get_provider_by_local_class("EMSStocks")
        venue_provider = providers_factories.VenueProviderFactory(provider=ems_provider, venueIdAtOfferProvider="0063")
        pivot = providers_factories.EMSCinemaProviderPivotFactory(idAtProvider=venue_provider.venueIdAtOfferProvider)
        ems_cinema_details = providers_factories.EMSCinemaDetailsFactory(cinemaProviderPivot=pivot, lastVersion=0)
        with requests_mock.Mocker() as requests_mocker:
            requests_mocker.get("https://fake_url.com?version=0", json=ems_fixtures.DATA_VERSION_0)
            requests_mocker.get("https://example.com/FR/poster/982D31BE/600/CDFG5.jpg", content=bytes())

            synchronize_ems_venue_provider(venue_provider)

            assert ems_cinema_details.lastVersion == 86400
            assert venue_provider.lastSyncDate
            assert db.session.query(Offer).count() == 1
