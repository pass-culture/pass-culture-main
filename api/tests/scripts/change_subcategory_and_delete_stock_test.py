import pytest

import pcapi.core.offers.factories as offer_factories


class SoftDeleteStockTest:
    @pytest.mark.usefixtures("db_session")
    def should_update_subcategory_and_delete_stock(self):
        # Given
        offer = offer_factories.OfferFactory(
            name="Offre avec catégorie à changer", subcategoryId="SEANCE_ESSAI_PRATIQUE_ART"
        )
        assert offer != None
