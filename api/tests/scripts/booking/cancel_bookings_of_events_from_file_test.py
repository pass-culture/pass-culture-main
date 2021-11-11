import pytest

from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingCancellationReasons
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.offers.factories import OffererFactory
from pcapi.core.offers.factories import ThingOfferFactory
from pcapi.core.offers.factories import ThingStockFactory
from pcapi.core.offers.factories import VenueFactory
import pcapi.core.users.factories as users_factories
from pcapi.scripts.booking.cancel_bookings_of_events_from_file import _cancel_bookings_of_offers_from_rows


@pytest.mark.usefixtures("db_session")
class CancelBookingsOfEventsFromFileTest:
    def test_cancel_bookings_of_offers_from_rows(self):
        beneficiary = users_factories.BeneficiaryGrant18Factory(email="user@example.net")

        offerer_to_cancel = OffererFactory(name="Librairie les petits parapluies gris", siren="123456789")
        offerer_to_not_cancel = OffererFactory(name="L'amicale du club de combat", siren="987654321")

        venue_to_cancel = VenueFactory(managingOfferer=offerer_to_cancel, siret="12345678912345")
        venue_to_not_cancel = VenueFactory(managingOfferer=offerer_to_not_cancel, siret="54321987654321")

        offer_to_cancel = ThingOfferFactory(venue=venue_to_cancel)
        offer_to_not_cancel = ThingOfferFactory(venue=venue_to_not_cancel)

        stock_to_cancel = ThingStockFactory(offer=offer_to_cancel)
        stock_to_not_cancel = ThingStockFactory(offer=offer_to_not_cancel)

        self.booking_to_cancel = BookingFactory(user=beneficiary, stock=stock_to_cancel, isUsed=False, dateUsed=None)
        self.booking_to_not_cancel = BookingFactory(user=beneficiary, stock=stock_to_not_cancel)

        self.booking_2QLYYA_not_to_cancel = BookingFactory(user=beneficiary, stock=stock_to_cancel, token="2QLYYA")
        self.booking_BMTUME_not_to_cancel = BookingFactory(user=beneficiary, stock=stock_to_cancel, token="BMTUME")
        self.booking_LUJ9AM_not_to_cancel = BookingFactory(user=beneficiary, stock=stock_to_cancel, token="LUJ9AM")
        self.booking_DA8YLU_not_to_cancel = BookingFactory(user=beneficiary, stock=stock_to_cancel, token="DA8YLU")
        self.booking_Q46YHM_not_to_cancel = BookingFactory(user=beneficiary, stock=stock_to_cancel, token="Q46YHM")

        self.csv_rows = [
            [
                "id offre",
                "Structure",
                "Département",
                "Offre",
                "Date de l'évènement",
                "Nb Réservations",
                "A annuler ?",
                "Commentaire",
            ],
            [
                offer_to_cancel.id,
                offer_to_cancel.name,
                "75000",
                offer_to_cancel.name,
                "2020-06-19 18:00:48",
                1,
                "Oui",
                "",
            ],
            [
                offer_to_not_cancel.id,
                offerer_to_not_cancel.name,
                offer_to_not_cancel.name,
                "93000",
                "2020-06-20 18:00:12",
                1,
                "Non",
                "",
            ],
        ]

        _cancel_bookings_of_offers_from_rows(self.csv_rows, BookingCancellationReasons.OFFERER)

        # Then
        saved_booking = Booking.query.get(self.booking_to_cancel.id)
        assert saved_booking.isCancelled is True
        assert saved_booking.status is BookingStatus.CANCELLED
        assert saved_booking.cancellationReason == BookingCancellationReasons.OFFERER
        assert saved_booking.cancellationDate is not None
        assert saved_booking.isUsed is False
        assert saved_booking.status is not BookingStatus.USED
        assert saved_booking.dateUsed is None

        saved_booking = Booking.query.get(self.booking_to_not_cancel.id)
        assert saved_booking.isCancelled is False
        assert saved_booking.status is not BookingStatus.CANCELLED
        assert saved_booking.cancellationDate is None

        saved_2QLYYA_booking = Booking.query.get(self.booking_2QLYYA_not_to_cancel.id)
        assert saved_2QLYYA_booking.isCancelled is False
        assert saved_2QLYYA_booking.status is not BookingStatus.CANCELLED
        assert saved_2QLYYA_booking.cancellationDate is None

        saved_BMTUME_booking = Booking.query.get(self.booking_BMTUME_not_to_cancel.id)
        assert saved_BMTUME_booking.isCancelled is False
        assert saved_BMTUME_booking.status is not BookingStatus.CANCELLED
        assert saved_BMTUME_booking.cancellationDate is None

        saved_LUJ9AM_booking = Booking.query.get(self.booking_LUJ9AM_not_to_cancel.id)
        assert saved_LUJ9AM_booking.isCancelled is False
        assert saved_LUJ9AM_booking.status is not BookingStatus.CANCELLED
        assert saved_LUJ9AM_booking.cancellationDate is None

        saved_DA8YLU_booking = Booking.query.get(self.booking_DA8YLU_not_to_cancel.id)
        assert saved_DA8YLU_booking.isCancelled is False
        assert saved_DA8YLU_booking.status is not BookingStatus.CANCELLED
        assert saved_DA8YLU_booking.cancellationDate is None

        saved_Q46YHM_booking = Booking.query.get(self.booking_Q46YHM_not_to_cancel.id)
        assert saved_Q46YHM_booking.isCancelled is False
        assert saved_Q46YHM_booking.status is not BookingStatus.CANCELLED
        assert saved_Q46YHM_booking.cancellationDate is None
