from unittest.mock import call
from unittest.mock import patch

import pytest

from pcapi.core.offers.factories import OfferFactory
from pcapi.core.offers.factories import ProductFactory
from pcapi.core.testing import assert_num_queries
from pcapi.scripts.bulk_mark_incompatible_via_isbns import bulk_update_is_gcu_compatible_via_isbns


class BulkUpdateIsGcuCompatibleViaIsbnsTest:
    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.scripts.bulk_mark_incompatible_via_isbns.search.unindex_offer_ids")
    def test_should_mark_offers_and_products_as_incompatible_via_isbn(self, mocked_unindex_offer_ids):
        # Given
        product = ProductFactory(id=1, extraData={"isbn": "ABCDEFG"})
        product_1 = ProductFactory(id=2, extraData={"isbn": "HIJKLMN"})
        product_2 = ProductFactory(id=3, extraData={"isbn": "VWXYZ"})
        product_3 = ProductFactory(id=4, extraData={"isbn": "HFGDS"})
        offer = OfferFactory(id=1, product=product)
        offer_1 = OfferFactory(id=2, product=product_1)
        offer_2 = OfferFactory(id=3, product=product_2)
        offer_3 = OfferFactory(id=4, product=product_3)

        isbns_list = ["ABCDEFG", "HIJKLMN", "OPQRSTU", "HFGDS"]

        queries = 1  # update product
        queries += 1  # select offer
        queries += 2  # update offer; commit
        queries *= 2  # two batches

        # When
        with assert_num_queries(queries):
            bulk_update_is_gcu_compatible_via_isbns(isbns_list, 2, is_compatible=False)

        # Then
        assert not product.isGcuCompatible
        assert not product_1.isGcuCompatible
        assert product_2.isGcuCompatible
        assert not product_3.isGcuCompatible
        assert not offer.isActive
        assert not offer_1.isActive
        assert offer_2.isActive
        assert not offer_3.isActive
        mocked_unindex_offer_ids.assert_has_calls([call([1, 2]), call([4])])

    @pytest.mark.usefixtures("db_session")
    def test_should_mark_products_as_compatible_via_isbn(self):
        product = ProductFactory(id=1, extraData={"isbn": "ABCDEFG"}, isGcuCompatible=False)
        product_1 = ProductFactory(id=2, extraData={"isbn": "HIJKLMN"}, isGcuCompatible=False)
        product_2 = ProductFactory(id=3, extraData={"isbn": "VWXYZ"}, isGcuCompatible=False)
        product_3 = ProductFactory(id=4, extraData={"isbn": "HFGDS"}, isGcuCompatible=False)

        isbns_list = ["ABCDEFG", "HIJKLMN", "OPQRSTU", "HFGDS"]

        queries = 2  # update; commit

        with assert_num_queries(queries):
            bulk_update_is_gcu_compatible_via_isbns(isbns_list, 4, is_compatible=True)

        assert product.isGcuCompatible
        assert product_1.isGcuCompatible
        assert not product_2.isGcuCompatible
        assert product_3.isGcuCompatible
