from unittest.mock import call
from unittest.mock import patch

import pytest

from pcapi.core.offers.factories import OfferFactory
from pcapi.core.offers.factories import StockFactory
from pcapi.core.offers.factories import VenueFactory
from pcapi.repository import repository
from pcapi.scripts.stock.update_offer_and_stock_id_at_providers import _correct_id_at_providers
from pcapi.scripts.stock.update_offer_and_stock_id_at_providers import _get_titelive_offers_with_old_id_at_providers
from pcapi.scripts.stock.update_offer_and_stock_id_at_providers import update_offer_and_stock_id_at_providers


class UpdateOfferAndStockIdAtProvidersTest:
    @patch("pcapi.scripts.stock.update_offer_and_stock_id_at_providers.repository")
    @pytest.mark.usefixtures("db_session")
    def should_update_id_at_providers_for_offers_and_stocks_with_current_siret(self, mock_repository, app):
        # Given
        current_siret = "32363560700019"
        venue = VenueFactory(siret=current_siret, id=12)
        offer = OfferFactory(venue=venue, idAtProviders="9782742785988@85234081900014")
        stock = StockFactory(offer=offer, idAtProviders="9782742785988@85234081900014")

        # When
        update_offer_and_stock_id_at_providers(venue_id=12)

        # Then
        assert offer.idAtProviders == "9782742785988@32363560700019"
        assert stock.idAtProviders == "9782742785988@32363560700019"
        assert mock_repository.save.call_count == 2
        assert mock_repository.save.call_args_list == [call(offer), call(stock)]

    class GetTiteliveOffersWithOldIdAtProvidersTest:
        @pytest.mark.usefixtures("db_session")
        def should_return_offers_with_id_at_providers_including_different_siret(self, app):
            # Given
            current_siret = "32363560700019"
            expected_venue = VenueFactory(siret=current_siret)
            other_venue = VenueFactory(siret="7863560700657")
            offer1 = OfferFactory(venue=expected_venue, idAtProviders="9782742785988@85234081900014")
            offer2 = OfferFactory(venue=expected_venue, idAtProviders="9782742785988@32363560700019")
            other_offer = OfferFactory(venue=other_venue, idAtProviders="9782742785988@7863560700657")

            repository.save(offer1, offer2, other_offer)

            # When
            offers_result = _get_titelive_offers_with_old_id_at_providers(expected_venue, current_siret)

            # Then
            assert offers_result == [offer1]

    class CorrectIdAtProvidersTest:
        def should_replace_siret_in_id_at_providers_with_given_value(self):
            # Given
            current_id_at_providers = "9782742785988@85234081900014"
            current_siret = "32363560700019"

            # When
            result = _correct_id_at_providers(current_id_at_providers, current_siret)

            # Then
            assert result == "9782742785988@32363560700019"
