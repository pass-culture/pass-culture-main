from datetime import datetime

import pytest

from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.models import Venue
from pcapi.core.offers.models import Offer
from pcapi.models import Product
from pcapi.repository import repository
from pcapi.scripts.bulk_update_old_offers_with_new_subcategories import bulk_update_old_offers_with_new_subcategories


class UpdateOffersSubcatTest:
    @pytest.mark.usefixtures("db_session")
    def test_update_offers_subcategory(self):
        # Given
        created_product = Product(
            type="ThingType.LIVRE_EDITION", name="product1", mediaUrls="toto", isNational=True, id=1
        )
        repository.save(created_product)
        created_offerer = Offerer(
            id=1, dateCreated=datetime(2021, 1, 1), name="offerer1", postalCode="75012", city="Paris", siren="123456789"
        )
        repository.save(created_offerer)

        created_venue = Venue(
            id=1,
            name="venue1",
            managingOffererId=1,
            isVirtual=False,
            siret="12345678932321",
            postalCode="75012",
            city="Paris",
        )
        repository.save(created_venue)

        created_offers = Offer(
            id=1,
            productId=1,
            venueId=1,
            type="ThingType.LIVRE_EDITION",
            name="offer1",
            mediaUrls="toto",
            isNational=True,
            isDuo=False,
            dateCreated=datetime(2021, 1, 1),
            isEducational=True,
        )
        repository.save(created_offers)

        # When
        bulk_update_old_offers_with_new_subcategories()

        # Then
        assert created_offers.subcategoryId == "LIVRE_PAPIER"
