import pytest

from pcapi.core.offers.factories import OfferFactory
from pcapi.models import offer_type
from pcapi.scripts.bulk_update_old_offers_with_new_subcategories import bulk_update_old_offers_with_new_subcategories


class UpdateOffersSubcatTest:
    @pytest.mark.usefixtures("db_session")
    def test_update_offers_subcategory(self):
        # Given
        created_offers = OfferFactory.create_batch(
            size=3, subcategoryId=None, type=str(offer_type.ThingType.LIVRE_EDITION)
        )
        # When

        bulk_update_old_offers_with_new_subcategories()

        # Then
        assert created_offers[0].subcategoryId == "LIVRE_PAPIER"
        assert created_offers[1].subcategoryId == "LIVRE_PAPIER"
        assert created_offers[2].subcategoryId == "LIVRE_PAPIER"
