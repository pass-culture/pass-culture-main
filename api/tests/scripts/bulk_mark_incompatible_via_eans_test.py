from unittest.mock import patch

import pytest

from pcapi.core.offers.factories import OfferFactory
from pcapi.core.offers.factories import ProductFactory
from pcapi.core.testing import assert_no_duplicated_queries
from pcapi.core.testing import assert_num_queries
from pcapi.scripts.bulk_mark_incompatible_via_eans import bulk_update_is_gcu_compatible_via_eans


class BulkUpdateIsGcuCompatibleViaEansTest:
    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.scripts.bulk_mark_incompatible_via_eans.search.unindex_offer_ids")
    def test_should_mark_offers_and_products_as_incompatible_via_ean(self, mocked_unindex_offer_ids):
        # Given
        product = ProductFactory(id=1, extraData={"ean": "ABCDEFG"})
        product_1 = ProductFactory(id=2, extraData={"ean": "HIJKLMN"})
        product_2 = ProductFactory(id=3, extraData={"ean": "VWXYZ"})
        product_3 = ProductFactory(id=4, extraData={"ean": "HFGDS"})
        offer = OfferFactory(id=1, product=product)
        offer_1 = OfferFactory(id=2, product=product_1)
        offer_2 = OfferFactory(id=3, product=product_2)
        offer_3 = OfferFactory(id=4, product=product_3)

        eans_list = ["ABCDEFG", "HIJKLMN", "OPQRSTU", "HFGDS"]

        queries = 1  # update product
        queries += 1  # select offer
        queries += 2  # update offer; commit
        queries *= 2  # two batches

        # When
        with assert_num_queries(queries):
            bulk_update_is_gcu_compatible_via_eans(eans_list, 2, is_compatible=False)

        # Then
        assert not product.isGcuCompatible
        assert not product_1.isGcuCompatible
        assert product_2.isGcuCompatible
        assert not product_3.isGcuCompatible
        assert not offer.isActive
        assert not offer_1.isActive
        assert offer_2.isActive
        assert not offer_3.isActive
        assert mocked_unindex_offer_ids.call_count == 2
        first_call_args = mocked_unindex_offer_ids.mock_calls[0].args
        second_call_args = mocked_unindex_offer_ids.mock_calls[1].args
        assert set(first_call_args[0]) == {1, 2}
        assert second_call_args[0] == [4]

    @pytest.mark.usefixtures("db_session")
    def test_should_mark_products_as_compatible_via_ean(self):
        product = ProductFactory(id=1, extraData={"ean": "ABCDEFG"}, isGcuCompatible=False)
        product_1 = ProductFactory(id=2, extraData={"ean": "HIJKLMN"}, isGcuCompatible=False)
        product_2 = ProductFactory(id=3, extraData={"ean": "VWXYZ"}, isGcuCompatible=False)
        product_3 = ProductFactory(id=4, extraData={"ean": "HFGDS"}, isGcuCompatible=False)

        eans_list = ["ABCDEFG", "HIJKLMN", "OPQRSTU", "HFGDS"]

        with assert_no_duplicated_queries():
            bulk_update_is_gcu_compatible_via_eans(eans_list, 4, is_compatible=True)

        assert product.isGcuCompatible
        assert product_1.isGcuCompatible
        assert not product_2.isGcuCompatible
        assert product_3.isGcuCompatible
