import pytest

from pcapi.core.offers.factories import OfferFactory
from pcapi.core.offers.models import Offer
from pcapi.models import db
from pcapi.repository import repository
from pcapi.scripts.bulk_inactivate_offers import bulk_inactivate_offers


class BulkMarkIncompatibleViaOfferIdsTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_mark_offers_and_products_as_incompatible_via_offer_ids(self):
        # Given
        offer = OfferFactory(id=1)
        offer_1 = OfferFactory(id=2)
        offer_2 = OfferFactory(id=5)
        repository.save(offer, offer_1, offer_2)

        offer_ids_list = ["1", "2", "3"]

        # When
        bulk_inactivate_offers(offer_ids_list, 2)

        # Then
        offers = db.session.query(Offer).order_by(Offer.id).all()
        assert not offers[0].isActive
        assert not offers[1].isActive
        assert offers[2].isActive
