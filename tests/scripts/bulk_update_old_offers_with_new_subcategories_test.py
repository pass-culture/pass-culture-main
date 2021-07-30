import pytest

from pcapi.core.offers.factories import OfferFactory
from pcapi.models import offer_type
from pcapi.scripts.bulk_update_old_offers_with_new_subcategories import bulk_update_old_offers_with_new_subcategories


class UpdateOffersSubcatTest:
    @pytest.mark.usefixtures("db_session")
    def test_update_offers_subcategory(self):
        # Given
        # OfferFactory.create_batch(size=10, subcategoryId=None, type=offer_type.ThingType.LIVRE_EDITION.value)
        OfferFactory()
        # When

        # bulk_update_old_offers_with_new_subcategories()

        # Then
        pass
