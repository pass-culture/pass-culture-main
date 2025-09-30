import pytest

import pcapi.core.artist.factories as artists_factories
import pcapi.core.offers.factories as offers_factories


pytestmark = pytest.mark.usefixtures("db_session")


class IsEligibleForSearchTest:
    def test_artist_without_searchable_offers_is_not_eligible_for_search(self):
        artist = artists_factories.ArtistFactory()

        assert artist.is_eligible_for_search is False

    def test_artist_with_searchable_offers_is_eligible_for_search(self):
        artist = artists_factories.ArtistFactory()
        product = offers_factories.ProductFactory()
        artists_factories.ArtistProductLinkFactory(artist_id=artist.id, product_id=product.id)
        offer = offers_factories.StockFactory(offer__product=product).offer

        assert offer.is_eligible_for_search is True
        assert artist.is_eligible_for_search is True

    def test_blacklisted_artist_with_searchable_offers_is_not_eligible_for_search(self):
        artist = artists_factories.ArtistFactory()
        product = offers_factories.ProductFactory()
        artists_factories.ArtistProductLinkFactory(artist_id=artist.id, product_id=product.id)
        offer = offers_factories.StockFactory(offer__product=product).offer

        assert offer.is_eligible_for_search is True
        assert artist.is_eligible_for_search is True

        artist.is_blacklisted = True

        assert artist.is_eligible_for_search is False
