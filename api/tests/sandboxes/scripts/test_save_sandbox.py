from datetime import datetime
from datetime import timedelta
from unittest.mock import patch

import pytest

import pcapi.core.offers.factories as offers_factories
from pcapi.sandboxes.scripts.save_sandbox import _index_all_offers


@pytest.mark.usefixtures("db_session")
class IndexAllOffersTest:
    def test_index_all_offers(self):
        offer_1 = offers_factories.OfferFactory(isActive=False)
        publication_date = datetime.utcnow() + timedelta(days=14)
        offers_factories.FutureOfferFactory(offer=offer_1, publicationDate=publication_date)
        offer_2 = offers_factories.OfferFactory(isActive=True)
        offers_factories.FutureOfferFactory(offer=offer_2, publicationDate=publication_date)
        offer_3 = offers_factories.OfferFactory()
        offers_factories.StockFactory(offer=offer_3)
        offer_4 = offers_factories.OfferFactory(isActive=False)
        offers_factories.StockFactory(offer=offer_4)

        with patch("pcapi.core.search.reindex_offer_ids") as mock_reindex_offer_ids:
            _index_all_offers()
            mock_reindex_offer_ids.assert_called_once()
            assert set(mock_reindex_offer_ids.call_args[0][0]) == set([offer_1.id, offer_2.id, offer_3.id])
