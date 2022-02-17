from unittest.mock import ANY
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
import requests_mock

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.categories import subcategories
from pcapi.core.offerers.factories import APIProviderFactory
from pcapi.core.offerers.factories import AllocineProviderFactory
from pcapi.core.offerers.factories import AllocineVenueProviderFactory
from pcapi.core.offerers.factories import VenueProviderFactory
import pcapi.core.offers.factories as offers_factories
from pcapi.core.offers.models import Offer
from pcapi.local_providers.provider_manager import do_update
from pcapi.local_providers.provider_manager import synchronize_data_for_provider
from pcapi.local_providers.provider_manager import synchronize_venue_provider
from pcapi.local_providers.provider_manager import synchronize_venue_providers_for_provider
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.generic_creators import create_venue_provider
from pcapi.repository import repository

from tests.local_providers.provider_test_utils import TestLocalProvider
from tests.test_utils import fake


def mock_update_objects():
    raise Exception


def mock_init_provider(*arg):
    raise Exception


class DoUpdateTest:
    def test_should_call_provider_objects_synchronization_function(self, app):
        # Given
        provider_mock = MagicMock()
        provider_mock.updateObjects = MagicMock()

        # When
        do_update(provider_mock, 10)

        # Then
        provider_mock.updateObjects.assert_called_once_with(10)

    @patch("pcapi.local_providers.provider_manager.build_cron_log_message")
    def test_should_call_remove_worker_id_when_exception_is_raised(self, mock_build_cron_log_message, app):
        # Given
        provider_mock = MagicMock()
        provider_mock.updateObjects = mock_update_objects

        # When
        do_update(provider_mock, 10)

        # Then
        mock_build_cron_log_message.assert_called_once_with(name="MagicMock", status=ANY)


class SynchronizeVenueProviderTest:
    @pytest.mark.usefixtures("db_session")
    def test_synchronize_venue_provider(self, app):
        api_url = "https://example.com/provider/api"
        old_provider = APIProviderFactory(id=1)
        provider = APIProviderFactory(id=2, apiUrl=api_url)
        venue_provider = VenueProviderFactory(provider=provider)
        venue = venue_provider.venue

        existing_product = offers_factories.ProductFactory(
            idAtProviders="4321",
            extraData={"prix_livre": 10},
            subcategoryId=subcategories.LIVRE_PAPIER.id,
        )
        stock_id_at_providers = f"{existing_product.idAtProviders}@{venue.siret}"
        existing_stock = offers_factories.StockFactory(
            quantity=10,
            offer__venue=venue,
            offer__product=existing_product,
            lastProviderId=old_provider.id,
            offer__idAtProvider=existing_product.idAtProviders,
            idAtProviders=stock_id_at_providers,
        )
        bookings_factories.UsedBookingFactory(stock=existing_stock)

        product_to_synchronized = offers_factories.ProductFactory(
            idAtProviders="1234",
            extraData={"prix_livre": 10},
            subcategoryId=subcategories.LIVRE_PAPIER.id,
        )

        with requests_mock.Mocker() as mock:
            response = {
                "total": 1,
                "stocks": [
                    {"ref": "1234", "available": 5},
                    {"ref": "4321", "available": 12},
                ],
            }
            mock.get(
                f"{api_url}/{venue_provider.venueIdAtOfferProvider}", [{"json": response}, {"json": {"stocks": []}}]
            )
            synchronize_venue_provider(venue_provider)

        # Check that previously synchronized stock have been updated.
        assert existing_stock.offer.lastProviderId == provider.id
        assert existing_stock.quantity == 12 + 1

        # Check that offers and stocks have been created.
        created_offer = Offer.query.filter_by(product=product_to_synchronized).one()
        assert created_offer.stocks[0].quantity == 5

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.local_providers.provider_manager.get_local_provider_class_by_name")
    @patch("pcapi.local_providers.provider_manager.do_update")
    def test_should_start_synchronization_with_linked_provider(self, mock_do_update, mock_get_provider_class, app):
        # Given
        limit = 10
        offerer = create_offerer()
        venue = create_venue(offerer)
        provider = AllocineProviderFactory()
        venue_provider = create_venue_provider(venue, provider)
        repository.save(venue_provider)
        mock_get_provider_class.return_value = TestLocalProvider

        # When
        synchronize_venue_provider(venue_provider, limit)

        # Then
        mock_do_update.assert_called_once_with(fake(TestLocalProvider), limit)

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.local_providers.provider_manager.get_local_provider_class_by_name")
    @patch("pcapi.local_providers.provider_manager.do_update")
    def test_should_init_provider_with_expected_venue_provider(self, mock_do_update, mock_get_provider_class, app):
        # Given
        limit = 10
        offerer = create_offerer()
        venue = create_venue(offerer)
        provider = AllocineProviderFactory()
        venue_provider = create_venue_provider(venue, provider)
        repository.save(venue_provider)
        mock_provider_class = MagicMock()
        mock_get_provider_class.return_value = mock_provider_class

        # When
        synchronize_venue_provider(venue_provider, limit)

        # Then
        mock_provider_class.assert_called_once_with(venue_provider)

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.local_providers.provider_manager.get_local_provider_class_by_name")
    @patch("pcapi.local_providers.provider_manager.do_update")
    def test_should_init_allocine_stocks_provider_with_expected_allocine_venue_provider(
        self, mock_do_update, mock_get_provider_class, app
    ):
        # Given
        allocine_venue_provider = AllocineVenueProviderFactory()

        mock_provider_class = MagicMock()
        mock_get_provider_class.return_value = mock_provider_class

        # When
        synchronize_venue_provider(allocine_venue_provider, None)

        # Then
        mock_provider_class.assert_called_once()
        venue_provider_mock_arg = mock_provider_class.call_args[0][0]
        assert venue_provider_mock_arg == allocine_venue_provider
        assert venue_provider_mock_arg.isDuo

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.local_providers.provider_manager.build_cron_log_message")
    def test_should_log_exception_when_one_is_raised_during_provider_initialization(
        self, mock_build_cron_log_message, app
    ):
        # Given
        provider_test = AllocineProviderFactory()
        offerer = create_offerer()
        venue = create_venue(offerer)
        venue_provider = create_venue_provider(venue, provider_test)
        repository.save(venue_provider)

        # When
        synchronize_venue_provider(venue_provider, 10)

        # Then
        mock_build_cron_log_message.assert_called_once_with(name=provider_test.localClass, status=ANY)


class SynchronizeVenueProvidersForProviderTest:
    @patch("pcapi.local_providers.provider_manager.do_update")
    @patch("pcapi.local_providers.provider_manager.get_local_provider_class_by_name")
    @pytest.mark.usefixtures("db_session")
    def test_should_entirely_synchronize_venue_provider(self, mock_get_provider_class, mock_do_update, app):
        # Given
        provider_test = AllocineProviderFactory()
        offerer = create_offerer()
        venue = create_venue(offerer)
        venue_provider = create_venue_provider(venue, provider_test)
        repository.save(venue_provider)
        mock_get_provider_class.return_value = TestLocalProvider

        # When
        synchronize_venue_providers_for_provider(provider_test.id, None)

        # Then
        mock_get_provider_class.assert_called_once()
        mock_do_update.assert_called_once_with(fake(TestLocalProvider), None)

    @patch("pcapi.local_providers.provider_manager.do_update")
    @patch("pcapi.local_providers.provider_manager.get_local_provider_class_by_name")
    @pytest.mark.usefixtures("db_session")
    def test_should_synchronize_venue_provider_with_defined_limit(self, mock_get_provider_class, mock_do_update, app):
        # Given
        provider_test = AllocineProviderFactory()
        offerer = create_offerer()
        venue = create_venue(offerer)
        venue_provider = create_venue_provider(venue, provider_test)
        repository.save(venue_provider)
        mock_get_provider_class.return_value = TestLocalProvider

        # When
        synchronize_venue_providers_for_provider(provider_test.id, 10)

        # Then
        mock_get_provider_class.assert_called_once()
        mock_do_update.assert_called_once_with(fake(TestLocalProvider), 10)

    @patch("pcapi.local_providers.provider_manager.synchronize_venue_provider")
    @pytest.mark.usefixtures("db_session")
    def test_should_call_synchronize_venue_provider(self, mock_synchronize_venue_provider, app):
        # Given
        provider_test = APIProviderFactory()
        offerer = create_offerer()
        venue = create_venue(offerer)
        venue_provider = create_venue_provider(venue, provider_test)
        repository.save(venue_provider)

        # When
        synchronize_venue_providers_for_provider(provider_test.id, 10)

        # Then
        mock_synchronize_venue_provider.assert_called_once()


class SynchronizeDataForProviderTest:
    @patch("pcapi.local_providers.provider_manager.do_update")
    @patch("pcapi.local_providers.provider_manager.get_local_provider_class_by_name")
    @pytest.mark.usefixtures("db_session")
    def test_should_call_do_update_for_specified_provider(self, mock_get_provider_class, mock_do_update, app):
        # Given
        provider_test = APIProviderFactory()
        repository.save(provider_test)
        mock_get_provider_class.return_value = TestLocalProvider

        # When
        synchronize_data_for_provider(provider_test.__class__.__name__, None)

        # Then
        mock_get_provider_class.assert_called_once()
        mock_do_update.assert_called_once_with(fake(TestLocalProvider), None)
