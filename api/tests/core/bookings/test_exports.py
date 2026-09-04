import csv
from datetime import date
from datetime import timedelta
from io import StringIO

import pytest
from dateutil import tz

import pcapi.core.bookings.exports as booking_exports
import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.core.bookings.exports import get_booking_token
from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingExportType
from pcapi.core.bookings.utils import convert_booking_dates_utc_to_venue_timezone
from pcapi.core.offerers.models import Venue
from pcapi.core.offers.models import Offer
from pcapi.core.testing import assert_num_queries
from pcapi.core.users.models import User
from pcapi.utils import date as date_utils


pytestmark = pytest.mark.usefixtures("db_session")


NOW = date_utils.get_naive_utc_now()
YESTERDAY = NOW - timedelta(days=1)
TWO_DAYS_AGO = NOW - timedelta(days=2)
THREE_DAYS_AGO = NOW - timedelta(days=3)
FOUR_DAYS_AGO = NOW - timedelta(days=4)
FIVE_DAYS_AGO = NOW - timedelta(days=5)
ONE_WEEK_FROM_NOW = NOW + timedelta(weeks=1)


class GetOfferBookingsByStatusCSVTest:
    def _validate_csv_row(
        self, data_dict: dict, beneficiary: User, offer: Offer, venue: Venue, booking: Booking, status: str, duo: str
    ):
        assert data_dict["Structure"] == venue.name
        assert data_dict["Nom de l’offre"] == offer.name
        offerer_address = booking.stock.offer.offererAddress
        location = f"{offerer_address.label or venue.publicName} - {offerer_address.address.street} {offerer_address.address.postalCode} {offerer_address.address.city}"
        assert data_dict["Localisation"] == location
        booking.venueDepartmentCode = booking.venue.offererAddress.address.departmentCode
        booking.offerDepartmentCode = booking.stock.offer.offererAddress.address.departmentCode
        assert data_dict["Date de l'évènement"] == str(
            convert_booking_dates_utc_to_venue_timezone(booking.stock.beginningDatetime, booking)
        )
        assert data_dict["EAN"] == (offer.ean if offer.ean else "")
        assert data_dict["Prénom du bénéficiaire"] == beneficiary.firstName
        assert data_dict["Nom du bénéficiaire"] == beneficiary.lastName
        assert data_dict["Email du bénéficiaire"] == beneficiary.email
        assert data_dict["Téléphone du bénéficiaire"] == (beneficiary.phoneNumber or "")
        assert data_dict["Date et heure de réservation"] == str(
            booking.dateCreated.astimezone(tz.gettz("Europe/Paris"))
        )
        if booking.dateUsed:
            assert data_dict["Date et heure de validation"] == str(
                booking.dateUsed.astimezone(tz.gettz("Europe/Paris"))
            )
        else:
            assert data_dict["Date et heure de validation"] == ""
        token = get_booking_token(
            booking.token,
            booking.status,
            booking.isExternal,
            booking.stock.beginningDatetime,
        )
        if token:
            assert data_dict["Contremarque"] == token
        else:
            assert data_dict["Contremarque"] == ""
        assert data_dict["Intitulé du tarif"] == booking.stock.priceCategory.label
        assert data_dict["Prix de la réservation"] == f"{booking.amount:.2f}"
        assert data_dict["Statut de la contremarque"] == status
        if booking.reimbursementDate:
            assert data_dict["Date et heure de remboursement"] == str(
                booking.reimbursementDate.astimezone(tz.gettz("Europe/Paris"))
            )
        else:
            assert data_dict["Date et heure de remboursement"] == ""
        assert data_dict["Type d'offre"] == "offre grand public"
        assert data_dict["Code postal du bénéficiaire"] == beneficiary.postalCode
        assert data_dict["Duo"] == duo

    def should_return_validated_bookings_for_offer(self):
        beneficiary = users_factories.BeneficiaryGrant18Factory(
            email="beneficiary@example.com", firstName="Ron", lastName="Weasley", postalCode="97300"
        )
        beneficiary_2 = users_factories.BeneficiaryGrant18Factory(
            email="beneficiary2@example.com", firstName="Harry", lastName="Potter", postalCode="97300"
        )
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue = offerers_factories.VenueFactory(managingOfferer=offerer)

        offer = offers_factories.OfferFactory(venue=venue)
        stock = offers_factories.EventStockFactory(
            offer=offer, beginningDatetime=date_utils.get_naive_utc_now() + timedelta(days=10)
        )

        validated_booking = bookings_factories.UsedBookingFactory(stock=stock, user=beneficiary)
        validated_booking_2 = bookings_factories.BookingFactory(
            stock=stock, cancellation_limit_date=date_utils.get_naive_utc_now() - timedelta(days=1), user=beneficiary_2
        )
        bookings_factories.BookingFactory(stock=stock)

        stock_2 = offers_factories.EventStockFactory(
            offer=offer, beginningDatetime=date_utils.get_naive_utc_now() + timedelta(days=40)
        )
        bookings_factories.UsedBookingFactory(stock=stock_2, user=beneficiary_2)
        bookings_factories.BookingFactory(stock=stock_2)

        queries = 0
        # queries += 1  # feature flags are already cached by BeneficiaryGrant18Factory.beneficiaryImports
        queries += 1  # Get bookings

        offer_id = offer.id
        with assert_num_queries(queries):
            bookings_csv = booking_exports.export_validated_bookings_by_offer_id(
                offer_id=offer_id,
                event_beginning_date=date.today() + timedelta(days=10),
                export_type=BookingExportType.CSV,
            )

        headers, *data = csv.reader(StringIO(bookings_csv), delimiter=";")
        assert headers == booking_exports.BOOKING_EXPORT_HEADER
        assert len(data) == 2
        self._validate_csv_row(
            dict(zip(headers, data[0])), beneficiary, offer, venue, validated_booking, "validé", "Non"
        )
        self._validate_csv_row(
            dict(zip(headers, data[1])), beneficiary_2, offer, venue, validated_booking_2, "confirmé", "Non"
        )

    def should_return_validated_bookings_for_offer_with_old_cancelled_booking(self):
        beneficiary = users_factories.BeneficiaryGrant18Factory(
            email="beneficiary@example.com", firstName="Ron", lastName="Weasley", postalCode="97300"
        )
        beneficiary_2 = users_factories.BeneficiaryGrant18Factory(
            email="beneficiary2@example.com", firstName="Harry", lastName="Potter", postalCode="97300"
        )
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue = offerers_factories.VenueFactory(managingOfferer=offerer)

        offer = offers_factories.OfferFactory(venue=venue)
        stock = offers_factories.EventStockFactory(
            offer=offer, beginningDatetime=date_utils.get_naive_utc_now() + timedelta(days=10)
        )

        validated_booking = bookings_factories.UsedBookingFactory(stock=stock, user=beneficiary)
        validated_booking_2 = bookings_factories.BookingFactory(
            stock=stock, cancellation_limit_date=date_utils.get_naive_utc_now() - timedelta(days=1), user=beneficiary_2
        )
        bookings_factories.BookingFactory(stock=stock)
        bookings_factories.CancelledBookingFactory(
            stock=stock, user=beneficiary_2, cancellation_limit_date=date_utils.get_naive_utc_now() - timedelta(days=2)
        )

        stock_2 = offers_factories.EventStockFactory(
            offer=offer, beginningDatetime=date_utils.get_naive_utc_now() + timedelta(days=40)
        )
        bookings_factories.UsedBookingFactory(stock=stock_2, user=beneficiary_2)
        bookings_factories.BookingFactory(stock=stock_2)

        queries = 0
        # queries += 1  # feature flags are already cached by BeneficiaryGrant18Factory.beneficiaryImports
        queries += 1  # Get bookings

        offer_id = offer.id
        with assert_num_queries(queries):
            bookings_csv = booking_exports.export_validated_bookings_by_offer_id(
                offer_id=offer_id,
                event_beginning_date=date.today() + timedelta(days=10),
                export_type=BookingExportType.CSV,
            )

        headers, *data = csv.reader(StringIO(bookings_csv), delimiter=";")
        assert headers == booking_exports.BOOKING_EXPORT_HEADER
        assert len(data) == 2
        self._validate_csv_row(
            dict(zip(headers, data[0])), beneficiary, offer, venue, validated_booking, "validé", "Non"
        )
        self._validate_csv_row(
            dict(zip(headers, data[1])), beneficiary_2, offer, venue, validated_booking_2, "confirmé", "Non"
        )

    def should_return_validated_bookings_for_offer_with_duo(self):
        beneficiary = users_factories.BeneficiaryGrant18Factory(
            email="beneficiary@example.com", firstName="Ron", lastName="Weasley", postalCode="97300"
        )
        beneficiary_2 = users_factories.BeneficiaryGrant18Factory(
            email="beneficiary2@example.com", firstName="Harry", lastName="Potter", postalCode="97300"
        )
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue = offerers_factories.VenueFactory(managingOfferer=offerer)

        offer = offers_factories.OfferFactory(venue=venue)
        stock = offers_factories.EventStockFactory(
            offer=offer, beginningDatetime=date_utils.get_naive_utc_now() + timedelta(days=5)
        )
        validated_booking = bookings_factories.UsedBookingFactory(stock=stock, user=beneficiary, quantity=2)
        validated_booking_2 = bookings_factories.BookingFactory(
            stock=stock, cancellation_limit_date=date_utils.get_naive_utc_now() - timedelta(days=1), user=beneficiary_2
        )
        bookings_factories.BookingFactory(stock=stock)

        stock_2 = offers_factories.EventStockFactory(
            offer=offer, beginningDatetime=date_utils.get_naive_utc_now() + timedelta(days=40)
        )
        bookings_factories.UsedBookingFactory(stock=stock_2, user=beneficiary_2)
        bookings_factories.BookingFactory(stock=stock_2)

        bookings_csv = booking_exports.export_validated_bookings_by_offer_id(
            offer_id=offer.id,
            event_beginning_date=date.today() + timedelta(days=5),
            export_type=BookingExportType.CSV,
        )

        headers, *data = csv.reader(StringIO(bookings_csv), delimiter=";")
        assert headers == booking_exports.BOOKING_EXPORT_HEADER
        assert len(data) == 3
        self._validate_csv_row(
            dict(zip(headers, data[0])), beneficiary, offer, venue, validated_booking, "validé", "DUO 1"
        )
        self._validate_csv_row(
            dict(zip(headers, data[1])), beneficiary, offer, venue, validated_booking, "validé", "DUO 2"
        )
        self._validate_csv_row(
            dict(zip(headers, data[2])), beneficiary_2, offer, venue, validated_booking_2, "confirmé", "Non"
        )

    def should_return_all_bookings_for_offer(self):
        beneficiary = users_factories.BeneficiaryGrant18Factory(
            email="beneficiary@example.com", firstName="Ron", lastName="Weasley", postalCode="97300"
        )
        beneficiary_2 = users_factories.BeneficiaryGrant18Factory(
            email="beneficiary2@example.com", firstName="Harry", lastName="Potter", postalCode="97300"
        )
        beneficiary_3 = users_factories.BeneficiaryGrant18Factory(
            email="beneficiary3@example.com", firstName="Hermione", lastName="Granger", postalCode="97300"
        )
        beneficiary_4 = users_factories.BeneficiaryGrant18Factory(
            email="beneficiary4@example.com", firstName="severus", lastName="Snape", postalCode="93000"
        )
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue = offerers_factories.VenueFactory(managingOfferer=offerer)

        offer = offers_factories.OfferFactory(venue=venue)
        stock = offers_factories.EventStockFactory(
            offer=offer, beginningDatetime=date_utils.get_naive_utc_now() + timedelta(days=10)
        )
        validated_booking = bookings_factories.UsedBookingFactory(stock=stock, user=beneficiary)
        validated_booking_2 = bookings_factories.BookingFactory(
            stock=stock, cancellation_limit_date=date_utils.get_naive_utc_now() - timedelta(days=1), user=beneficiary_2
        )
        reimbursed_booking = bookings_factories.ReimbursedBookingFactory(user=beneficiary_3, stock=stock)
        new_booking = bookings_factories.BookingFactory(user=beneficiary_4, stock=stock)

        bookings_csv = booking_exports.export_bookings_by_offer_id(
            offer_id=offer.id,
            event_beginning_date=date.today() + timedelta(days=10),
            export_type=BookingExportType.CSV,
        )

        headers, *data = csv.reader(StringIO(bookings_csv), delimiter=";")
        assert headers == booking_exports.BOOKING_EXPORT_HEADER
        assert len(data) == 4
        self._validate_csv_row(
            dict(zip(headers, data[0])), beneficiary, offer, venue, validated_booking, "validé", "Non"
        )
        self._validate_csv_row(
            dict(zip(headers, data[1])), beneficiary_2, offer, venue, validated_booking_2, "confirmé", "Non"
        )
        self._validate_csv_row(
            dict(zip(headers, data[2])), beneficiary_3, offer, venue, reimbursed_booking, "remboursé", "Non"
        )
        self._validate_csv_row(dict(zip(headers, data[3])), beneficiary_4, offer, venue, new_booking, "réservé", "Non")

    def should_return_all_bookings_for_offer_with_duo(self):
        beneficiary = users_factories.BeneficiaryGrant18Factory(
            email="beneficiary@example.com", firstName="Ron", lastName="Weasley", postalCode="97300"
        )
        beneficiary_2 = users_factories.BeneficiaryGrant18Factory(
            email="beneficiary2@example.com", firstName="Harry", lastName="Potter", postalCode="97300"
        )
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue = offerers_factories.VenueFactory(managingOfferer=offerer)

        offer = offers_factories.OfferFactory(venue=venue)
        stock = offers_factories.EventStockFactory(
            offer=offer, beginningDatetime=date_utils.get_naive_utc_now() + timedelta(days=5)
        )
        validated_booking = bookings_factories.UsedBookingFactory(stock=stock, user=beneficiary, quantity=2)
        validated_booking_2 = bookings_factories.BookingFactory(
            stock=stock, cancellation_limit_date=date_utils.get_naive_utc_now() - timedelta(days=1), user=beneficiary_2
        )
        reimbursed_booking = bookings_factories.ReimbursedBookingFactory(user=beneficiary, stock=stock)
        new_booking = bookings_factories.BookingFactory(user=beneficiary_2, stock=stock, quantity=2)

        bookings_csv = booking_exports.export_bookings_by_offer_id(
            offer_id=offer.id,
            event_beginning_date=date.today() + timedelta(days=5),
            export_type=BookingExportType.CSV,
        )

        headers, *data = csv.reader(StringIO(bookings_csv), delimiter=";")
        assert headers == booking_exports.BOOKING_EXPORT_HEADER
        assert len(data) == 6
        self._validate_csv_row(
            dict(zip(headers, data[0])), beneficiary, offer, venue, validated_booking, "validé", "DUO 1"
        )
        self._validate_csv_row(
            dict(zip(headers, data[1])), beneficiary, offer, venue, validated_booking, "validé", "DUO 2"
        )
        self._validate_csv_row(
            dict(zip(headers, data[2])), beneficiary_2, offer, venue, validated_booking_2, "confirmé", "Non"
        )
        self._validate_csv_row(
            dict(zip(headers, data[3])), beneficiary, offer, venue, reimbursed_booking, "remboursé", "Non"
        )
        self._validate_csv_row(
            dict(zip(headers, data[4])), beneficiary_2, offer, venue, new_booking, "réservé", "DUO 1"
        )
        self._validate_csv_row(
            dict(zip(headers, data[5])), beneficiary_2, offer, venue, new_booking, "réservé", "DUO 2"
        )
