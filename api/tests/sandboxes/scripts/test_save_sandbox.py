from datetime import datetime
from datetime import timedelta
from unittest.mock import patch

import pytest

import pcapi.core.offers.factories as offers_factories
from pcapi.sandboxes.scripts.save_sandbox import _index_all_offers


@pytest.mark.usefixtures("db_session")
class IndexAllOffersTest:
    def test_index_all_offers(self):
        publication_date = datetime.utcnow() - timedelta(days=3)
        booking_allowed_date = datetime.utcnow() + timedelta(days=14)

        # active, published, booking date in the future and active -> should be indexed
        offer_1 = offers_factories.StockFactory(
            offer__isActive=True,
            offer__publicationDatetime=publication_date,
            offer__bookingAllowedDatetime=booking_allowed_date,
        ).offer

        # active with bookable stock -> should be indexed
        offer_2 = offers_factories.StockFactory().offer

        # published with a booking date in the future, but inactive
        # -> should not be indexed
        offers_factories.StockFactory(
            offer__publicationDatetime=None,
            offer__bookingAllowedDatetime=booking_allowed_date,
        ).offer

        # inactive or without any bookable stock -> should not indexed
        offers_factories.StockFactory(offer__publicationDatetime=None).offer
        offers_factories.OfferFactory(isActive=False)
        offers_factories.OfferFactory(isActive=True)

        with patch("pcapi.core.search.reindex_offer_ids") as mock_reindex_offer_ids:
            _index_all_offers()
            mock_reindex_offer_ids.assert_called_once()
            assert set(mock_reindex_offer_ids.call_args[0][0]) == {offer_1.id, offer_2.id}
