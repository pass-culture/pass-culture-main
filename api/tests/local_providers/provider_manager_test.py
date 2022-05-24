from decimal import Decimal
from unittest.mock import MagicMock
from unittest.mock import patch

from freezegun import freeze_time
import pytest
import requests_mock

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.categories import subcategories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.offers.models import Offer
import pcapi.core.providers.factories as providers_factories
from pcapi.local_providers.provider_manager import synchronize_data_for_provider
from pcapi.local_providers.provider_manager import synchronize_venue_provider
from pcapi.local_providers.provider_manager import synchronize_venue_providers_for_provider
from pcapi.repository import repository

from tests.local_providers.provider_test_utils import TestLocalProvider


def mock_update_objects():
    raise Exception


def mock_init_provider(*arg):
    raise Exception


class SynchronizeVenueProviderTest:
    @pytest.mark.usefixtures("db_session")
    # FIXME (jsdupuis, 2022-05-24) : freeze_time to be removed after the 1st of june
    @freeze_time("2022-06-01 09:00:00")
    def test_synchronize_venue_provider(self, app):
        api_url = "https://example.com/provider/api"
        old_provider = providers_factories.APIProviderFactory(id=1)
        provider = providers_factories.APIProviderFactory(id=2, apiUrl=api_url)
        venue_provider = providers_factories.VenueProviderFactory(provider=provider)
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
        bookings_factories.BookingFactory(stock=existing_stock)

        product_to_synchronized = offers_factories.ProductFactory(
            idAtProviders="1234",
            extraData={"prix_livre": 10},
            subcategoryId=subcategories.LIVRE_PAPIER.id,
        )
        another_product_to_synchronized = offers_factories.ProductFactory(
            idAtProviders="6789",
            extraData={"prix_livre": 7},
            subcategoryId=subcategories.LIVRE_PAPIER.id,
        )

        with requests_mock.Mocker() as mock:
            response = {
                "total": 1,
                "stocks": [
                    {"ref": "1234", "available": 5, "price": 10},
                    {"ref": "4321", "available": 12, "price": 10.30},
                    {"ref": "6789", "available": 3},
                ],
            }
            mock.get(
                f"{api_url}/{venue_provider.venueIdAtOfferProvider}", [{"json": response}, {"json": {"stocks": []}}]
            )
            synchronize_venue_provider(venue_provider)

        # Check that previously synchronized stock have been updated.
        assert existing_stock.offer.lastProviderId == provider.id
        assert existing_stock.price == Decimal("10.30")
        assert existing_stock.quantity == 12 + existing_stock.dnBookedQuantity

        # Check that offers and stocks have been created.
        created_offer = Offer.query.filter_by(product=product_to_synchronized).one()
        assert created_offer.stocks[0].quantity == 5

        # Check that offers and stocks have not been created when price is missing.
        no_offer_created = Offer.query.filter_by(product=another_product_to_synchronized).one_or_none()
        assert no_offer_created is None

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.local_providers.provider_manager.get_local_provider_class_by_name")
    @patch("pcapi.local_providers.local_provider.LocalProvider.updateObjects")
    def test_should_start_synchronization_with_linked_provider(self, mock_updateObjects, mock_get_provider_class):
        # Given
        allocine = providers_factories.AllocineProviderFactory()
        venue_provider = providers_factories.VenueProviderFactory(provider=allocine)
        mock_get_provider_class.return_value = TestLocalProvider

        # When
        synchronize_venue_provider(venue_provider, limit=10)

        # Then
        mock_updateObjects.assert_called_once_with(10)

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.local_providers.provider_manager.get_local_provider_class_by_name")
    @patch("pcapi.local_providers.local_provider.LocalProvider.updateObjects")
    def test_should_init_allocine_stocks_provider_with_expected_allocine_venue_provider(
        self, mock_updateObjects, mock_get_provider_class, app
    ):
        # Given
        allocine_venue_provider = providers_factories.AllocineVenueProviderFactory()

        mock_provider_class = MagicMock()
        mock_get_provider_class.return_value = mock_provider_class

        # When
        synchronize_venue_provider(allocine_venue_provider, None)

        # Then
        mock_provider_class.assert_called_once()
        venue_provider_mock_arg = mock_provider_class.call_args[0][0]
        assert venue_provider_mock_arg == allocine_venue_provider
        assert venue_provider_mock_arg.isDuo


class SynchronizeVenueProvidersForProviderTest:
    @patch("pcapi.local_providers.local_provider.LocalProvider.updateObjects")
    @patch("pcapi.local_providers.provider_manager.get_local_provider_class_by_name")
    @pytest.mark.usefixtures("db_session")
    def test_should_entirely_synchronize_venue_provider(self, mock_get_provider_class, mock_updateObjects):
        # Given
        allocine = providers_factories.AllocineProviderFactory()
        providers_factories.VenueProviderFactory(provider=allocine)
        mock_get_provider_class.return_value = TestLocalProvider

        # When
        synchronize_venue_providers_for_provider(allocine.id, limit=None)

        # Then
        mock_get_provider_class.assert_called_once()
        mock_updateObjects.assert_called_once_with(None)

    @patch("pcapi.local_providers.local_provider.LocalProvider.updateObjects")
    @patch("pcapi.local_providers.provider_manager.get_local_provider_class_by_name")
    @pytest.mark.usefixtures("db_session")
    def test_should_synchronize_venue_provider_with_defined_limit(self, mock_get_provider_class, mock_updateObjects):
        # Given
        allocine = providers_factories.AllocineProviderFactory()
        providers_factories.VenueProviderFactory(provider=allocine)
        mock_get_provider_class.return_value = TestLocalProvider

        # When
        synchronize_venue_providers_for_provider(allocine.id, limit=10)

        # Then
        mock_get_provider_class.assert_called_once()
        mock_updateObjects.assert_called_once_with(10)

    @patch("pcapi.local_providers.provider_manager.synchronize_venue_provider")
    @pytest.mark.usefixtures("db_session")
    def test_should_call_synchronize_venue_provider(self, mock_synchronize_venue_provider):
        provider = providers_factories.ProviderFactory()
        providers_factories.VenueProviderFactory(provider=provider)

        synchronize_venue_providers_for_provider(provider.id, limit=10)
        mock_synchronize_venue_provider.assert_called_once()

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.local_providers.provider_manager.synchronize_venue_provider")
    def test_catch_exception_and_continue(self, mock_synchronize_venue_provider):
        provider = providers_factories.ProviderFactory(localClass="Unknown")
        providers_factories.VenueProviderFactory(provider=provider)
        providers_factories.VenueProviderFactory(provider=provider)

        mock_synchronize_venue_provider.side_effect = ValueError()

        synchronize_venue_providers_for_provider(provider.id, 10)
        assert mock_synchronize_venue_provider.call_count == 2


class SynchronizeDataForProviderTest:
    @patch("pcapi.local_providers.local_provider.LocalProvider.updateObjects")
    @patch("pcapi.local_providers.provider_manager.get_local_provider_class_by_name")
    @pytest.mark.usefixtures("db_session")
    def test_should_call_do_update_for_specified_provider(self, mock_get_provider_class, mock_updateObjects, app):
        # Given
        provider_test = providers_factories.APIProviderFactory()
        repository.save(provider_test)
        mock_get_provider_class.return_value = TestLocalProvider

        # When
        synchronize_data_for_provider(provider_test.__class__.__name__, None)

        # Then
        mock_get_provider_class.assert_called_once()
        mock_updateObjects.assert_called_once_with(None)
