import pytest

import pcapi.core.bookings.factories as booking_factories
from pcapi.core.categories.subcategories import ALL_SUBCATEGORIES_DICT
import pcapi.core.offers.factories as offer_factories
from pcapi.scripts.update_event_offer_to_non_event import update_event_offer_to_non_event


class SoftDeleteStockTest:
    @pytest.mark.usefixtures("db_session")
    def should_update_subcategory_and_delete_stock(self):

        # Given
        offer = offer_factories.OfferFactory(
            name="Offre avec catégorie à changer", subcategoryId=ALL_SUBCATEGORIES_DICT["SEANCE_ESSAI_PRATIQUE_ART"].id
        )
        stock1 = offer_factories.StockFactory(
            offer=offer,
            beginningDatetime="2022-02-22 14:45:00",
            bookingLimitDatetime="2022-02-22 00:00:00",
            price=300,
            quantity=20,
        )
        booking_factories.IndividualBookingFactory(stock=stock1)

        stock2 = offer_factories.StockFactory(
            offer=offer,
            beginningDatetime="2022-03-15 12:45:00",
            bookingLimitDatetime="2022-03-15 00:00:00",
            price=250,
            quantity=50,
        )
        booking_factories.IndividualBookingFactory(stock=stock2)
        booking_factories.IndividualBookingFactory(stock=stock2)

        currentStock = offer_factories.StockFactory(
            offer=offer,
            beginningDatetime="2022-03-15 14:45:00",
            bookingLimitDatetime="2022-03-15 00:00:00",
            price=290,
            quantity=10,
        )

        # When
        update_event_offer_to_non_event(offer.id, ALL_SUBCATEGORIES_DICT["ABO_PRATIQUE_ART"].id)

        # Then
        assert stock1.isSoftDeleted
        assert stock2.isSoftDeleted
        assert currentStock.beginningDatetime is None
        assert currentStock.bookingLimitDatetime is None
