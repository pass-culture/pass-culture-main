import pytest

from pcapi.core.offers.factories import OfferFactory
from pcapi.core.offers.models import Offer
from pcapi.models import db
from pcapi.scripts.bulk_update_old_offers_with_new_subcategories import bulk_update_old_offers_with_new_subcategories


class UpdateOffersSubcatTest:
    @pytest.mark.usefixtures("db_session")
    def test_update_offers_subcategory(self):
        # Given
        book_offers = OfferFactory.create_batch(size=3)
        for offer in book_offers:
            offer.subcategoryId = None
            offer.type = "ThingType.LIVRE_EDITION"
            db.session.add(offer)
        concert_offers = OfferFactory.create_batch(size=2)
        for offer in concert_offers:
            offer.subcategoryId = None
            offer.type = "EventType.MUSIQUE"
            db.session.add(offer)
        db.session.commit()

        # When
        bulk_update_old_offers_with_new_subcategories()

        # Then
        assert Offer.query.filter(Offer.subcategoryId == "LIVRE_PAPIER").count() == 3
        assert Offer.query.filter(Offer.subcategoryId == "CONCERT").count() == 2
