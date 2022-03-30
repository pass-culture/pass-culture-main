from datetime import datetime
from datetime import timedelta
from decimal import Decimal

from dateutil import tz
import pytest

from pcapi.core.bookings.factories import EducationalBookingFactory
from pcapi.core.bookings.factories import RefusedEducationalBookingFactory
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import repository as educational_repository
from pcapi.core.educational.models import CollectiveBookingStatus
from pcapi.core.educational.repository import get_confirmed_educational_bookings_amount
from pcapi.core.offers import factories as offers_factories


pytestmark = pytest.mark.usefixtures("db_session")


class EducationalRepositoryTest:
    def test_get_not_cancelled_educational_bookings_amount(self, db_session):
        educational_institution = educational_factories.EducationalInstitutionFactory()
        another_educational_institution = educational_factories.EducationalInstitutionFactory()
        educational_year = educational_factories.EducationalYearFactory(adageId="1")
        another_educational_year = educational_factories.EducationalYearFactory(adageId="2")
        EducationalBookingFactory(
            amount=Decimal(20.00),
            quantity=20,
            educationalBooking__educationalInstitution=educational_institution,
            educationalBooking__educationalYear=educational_year,
        )
        EducationalBookingFactory(
            amount=Decimal(400.00),
            quantity=1,
            educationalBooking__educationalInstitution=educational_institution,
            educationalBooking__educationalYear=educational_year,
            status=BookingStatus.CONFIRMED,
        )
        EducationalBookingFactory(
            amount=Decimal(400.00),
            quantity=1,
            educationalBooking__educationalInstitution=educational_institution,
            educationalBooking__educationalYear=educational_year,
            status=BookingStatus.USED,
        )
        EducationalBookingFactory(
            amount=Decimal(20.00),
            quantity=20,
            educationalBooking__educationalInstitution=educational_institution,
            educationalBooking__educationalYear=educational_year,
            status=BookingStatus.PENDING,
        )
        RefusedEducationalBookingFactory(
            amount=Decimal(10.00),
            quantity=20,
            educationalBooking__educationalInstitution=educational_institution,
            educationalBooking__educationalYear=educational_year,
        )
        EducationalBookingFactory(
            amount=Decimal(10.00),
            quantity=20,
            educationalBooking__educationalInstitution=another_educational_institution,
            educationalBooking__educationalYear=educational_year,
            status=BookingStatus.CONFIRMED,
        )
        EducationalBookingFactory(
            amount=Decimal(10.00),
            quantity=20,
            educationalBooking__educationalInstitution=educational_institution,
            educationalBooking__educationalYear=another_educational_year,
            status=BookingStatus.CONFIRMED,
        )

        total_amount = get_confirmed_educational_bookings_amount(educational_institution.id, educational_year.adageId)
        assert total_amount == Decimal(1200.00)


class FindByProUserTest:
    def test_should_return_only_expected_collective_booking_attributes(self, app):
        # Given
        booking_date = datetime(2022, 3, 15, 10, 15, 0)
        redactor = educational_factories.EducationalRedactorFactory(
            email="reda.ktheur@example.com", firstName="Reda", lastName="Khteur", civility="M."
        )
        user_offerer = offers_factories.UserOffererFactory()
        collective_stock = educational_factories.CollectiveStockFactory(
            collectiveOffer__name="Le chant des cigales", collectiveOffer__venue__managingOfferer=user_offerer.offerer
        )
        educational_factories.CollectiveBookingFactory(
            educationalRedactor=redactor,
            status=CollectiveBookingStatus.USED,
            dateUsed=booking_date + timedelta(days=10),
            collectiveStock=collective_stock,
            dateCreated=booking_date,
            offerer=user_offerer.offerer,
        )

        # When
        total_bookings, collective_bookings = educational_repository.find_collective_bookings_by_pro_user(
            user=user_offerer.user,
            booking_period=(booking_date - timedelta(days=365), booking_date + timedelta(days=365)),
        )

        # Then
        assert total_bookings == 1
        assert len(collective_bookings) == 1
        expected_booking_recap = collective_bookings[0]
        assert expected_booking_recap.offerId == collective_stock.collectiveOffer.id
        assert expected_booking_recap.offerName == "Le chant des cigales"
        assert expected_booking_recap.redactorFirstname == "Reda"
        assert expected_booking_recap.redactorLastname == "Khteur"
        assert expected_booking_recap.redactorEmail == "reda.ktheur@example.com"
        assert expected_booking_recap.bookedAt == booking_date.astimezone(tz.gettz("Europe/Paris"))
        assert expected_booking_recap.status is CollectiveBookingStatus.USED
        assert expected_booking_recap.isConfirmed is False
        assert expected_booking_recap.bookingAmount == collective_stock.price
        assert expected_booking_recap.bookedAt == booking_date.astimezone(tz.gettz("Europe/Paris"))
        assert expected_booking_recap.usedAt == (booking_date + timedelta(days=10)).astimezone(tz.gettz("Europe/Paris"))
        assert expected_booking_recap.cancellationLimitDate is None

    # def test_should_return_only_validated_bookings_for_requested_period(self, app):
    #     pro = users_factories.ProFactory()
    #     offerer = offers_factories.OffererFactory()
    #     offers_factories.UserOffererFactory(user=pro, offerer=offerer)
    #     venue = offers_factories.VenueFactory(managingOfferer=offerer)
    #     offer = offers_factories.ThingOfferFactory(venue=venue)
    #     stock = offers_factories.ThingStockFactory(offer=offer, price=0)
    #
    #     booking_date = datetime(2020, 1, 1, 10, 0, 0)
    #
    #     bookings_factories.UsedIndividualBookingFactory(
    #         stock=stock, quantity=1, dateCreated=booking_date, dateUsed=(booking_date + timedelta(days=1))
    #     )
    #     used_booking_1 = bookings_factories.EducationalBookingFactory(
    #         stock=stock, dateCreated=booking_date, dateUsed=(booking_date + timedelta(days=3))
    #     )
    #     used_booking_2 = bookings_factories.UsedIndividualBookingFactory(
    #         stock=stock, quantity=1, dateCreated=booking_date, dateUsed=(booking_date + timedelta(days=4))
    #     )
    #     bookings_factories.UsedIndividualBookingFactory(
    #         stock=stock, quantity=1, dateCreated=booking_date, dateUsed=(booking_date + timedelta(days=8))
    #     )
    #
    #     bookings_recap_paginated = booking_repository.find_collective_bookings_by_pro_user(
    #         user=pro,
    #         booking_period=((booking_date + timedelta(2)), (booking_date + timedelta(5))),
    #         status_filter=BookingStatusFilter.VALIDATED,
    #     )
    #
    #     assert len(bookings_recap_paginated.bookings_recap) == 2
    #     assert bookings_recap_paginated.bookings_recap[0]._booking_token in [used_booking_1.token, used_booking_2.token]
    #     assert bookings_recap_paginated.bookings_recap[1]._booking_token in [used_booking_1.token, used_booking_2.token]
    #
    # def test_should_return_only_reimbursed_bookings_for_requested_period(self, app):
    #     pro = users_factories.ProFactory()
    #     offerer = offers_factories.OffererFactory()
    #     offers_factories.UserOffererFactory(user=pro, offerer=offerer)
    #     venue = offers_factories.VenueFactory(managingOfferer=offerer)
    #     stock = offers_factories.ThingStockFactory(offer__venue=venue, price=10)
    #
    #     booking_date = datetime(2020, 1, 1, 10, 0, 0)
    #
    #     bookings_factories.UsedIndividualBookingFactory(
    #         stock=stock, quantity=1, dateCreated=booking_date, reimbursementDate=(booking_date + timedelta(days=1))
    #     )
    #     reimbursed_booking_1 = bookings_factories.UsedIndividualBookingFactory(
    #         stock=stock, quantity=1, dateCreated=booking_date, reimbursementDate=(booking_date + timedelta(days=2))
    #     )
    #     reimbursed_booking_2 = bookings_factories.EducationalBookingFactory(
    #         stock=stock, quantity=1, dateCreated=booking_date, reimbursementDate=(booking_date + timedelta(days=3))
    #     )
    #     bookings_factories.UsedIndividualBookingFactory(
    #         stock=stock, quantity=1, dateCreated=booking_date, reimbursementDate=(booking_date + timedelta(days=4))
    #     )
    #
    #     bookings_recap_paginated = booking_repository.find_collective_bookings_by_pro_user(
    #         user=pro,
    #         booking_period=((booking_date + timedelta(1)), (booking_date + timedelta(3))),
    #         status_filter=BookingStatusFilter.REIMBURSED,
    #     )
    #
    #     assert len(bookings_recap_paginated.bookings_recap) == 2
    #     assert bookings_recap_paginated.bookings_recap[0]._booking_token in [
    #         reimbursed_booking_1.token,
    #         reimbursed_booking_2.token,
    #     ]
    #     assert bookings_recap_paginated.bookings_recap[1]._booking_token in [
    #         reimbursed_booking_1.token,
    #         reimbursed_booking_2.token,
    #     ]
    #
    # def test_should_return_booking_as_duo_when_quantity_is_two(self, app):
    #     # Given
    #     beneficiary = users_factories.BeneficiaryGrant18Factory(
    #         email="beneficiary@example.com", firstName="Ron", lastName="Weasley"
    #     )
    #     pro = users_factories.ProFactory()
    #     offerer = offers_factories.OffererFactory()
    #     offers_factories.UserOffererFactory(user=pro, offerer=offerer)
    #
    #     venue = offers_factories.VenueFactory(managingOfferer=offerer)
    #     product = offers_factories.ThingProductFactory(name="Harry Potter")
    #     offer = offers_factories.ThingOfferFactory(venue=venue, product=product)
    #     stock = offers_factories.ThingStockFactory(offer=offer, price=0)
    #     bookings_factories.IndividualBookingFactory(user=beneficiary, stock=stock, quantity=2)
    #
    #     # When
    #     bookings_recap_paginated = booking_repository.find_collective_bookings_by_pro_user(
    #         user=pro, booking_period=(one_year_before_booking, one_year_after_booking)
    #     )
    #
    #     # Then
    #     assert len(bookings_recap_paginated.bookings_recap) == 2
    #     expected_booking_recap = bookings_recap_paginated.bookings_recap[0]
    #     assert expected_booking_recap.booking_is_duo is True
    #
    # def test_should_not_duplicate_bookings_when_user_is_admin_and_bookings_offerer_has_multiple_user(self, app):
    #     # Given
    #     admin = users_factories.AdminFactory()
    #     offerer = offers_factories.OffererFactory()
    #     offers_factories.UserOffererFactory(offerer=offerer)
    #     offers_factories.UserOffererFactory(offerer=offerer)
    #     offers_factories.UserOffererFactory(offerer=offerer)
    #
    #     bookings_factories.IndividualBookingFactory(stock__offer__venue__managingOfferer=offerer, quantity=2)
    #
    #     # When
    #     bookings_recap_paginated = booking_repository.find_collective_bookings_by_pro_user(
    #         user=admin, booking_period=(one_year_before_booking, one_year_after_booking)
    #     )
    #
    #     # Then
    #     assert len(bookings_recap_paginated.bookings_recap) == 2
    #     expected_booking_recap = bookings_recap_paginated.bookings_recap[0]
    #     assert expected_booking_recap.booking_is_duo is True
    #
    # def test_should_return_event_booking_when_booking_is_on_an_event(self, app):
    #     # Given
    #     beneficiary = users_factories.BeneficiaryGrant18Factory(
    #         email="beneficiary@example.com", firstName="Ron", lastName="Weasley"
    #     )
    #     pro = users_factories.ProFactory()
    #     offerer = offers_factories.OffererFactory()
    #     offers_factories.UserOffererFactory(user=pro, offerer=offerer)
    #
    #     venue = offers_factories.VenueFactory(managingOfferer=offerer)
    #     product = offers_factories.ThingProductFactory(name="Harry Potter")
    #     offer = offers_factories.ThingOfferFactory(venue=venue, product=product)
    #     stock = offers_factories.ThingStockFactory(
    #         offer=offer, price=0, beginningDatetime=datetime.utcnow() + timedelta(hours=98)
    #     )
    #     yesterday = datetime.utcnow() - timedelta(days=1)
    #     bookings_factories.IndividualBookingFactory(
    #         individualBooking__user=beneficiary,
    #         stock=stock,
    #         dateCreated=yesterday,
    #         token="ABCDEF",
    #         status=BookingStatus.PENDING,
    #     )
    #
    #     # When
    #     bookings_recap_paginated = booking_repository.find_collective_bookings_by_pro_user(
    #         user=pro, booking_period=(one_year_before_booking, one_year_after_booking)
    #     )
    #
    #     # Then
    #     assert len(bookings_recap_paginated.bookings_recap) == 1
    #     expected_booking_recap = bookings_recap_paginated.bookings_recap[0]
    #     assert expected_booking_recap.offer_identifier == stock.offer.id
    #     assert expected_booking_recap.offer_name == stock.offer.name
    #     assert expected_booking_recap.beneficiary_firstname == "Ron"
    #     assert expected_booking_recap.beneficiary_lastname == "Weasley"
    #     assert expected_booking_recap.beneficiary_email == "beneficiary@example.com"
    #     assert expected_booking_recap.booking_date == yesterday.astimezone(tz.gettz("Europe/Paris"))
    #     assert expected_booking_recap.booking_token == "ABCDEF"
    #     assert expected_booking_recap.booking_is_used is False
    #     assert expected_booking_recap.booking_is_cancelled is False
    #     assert expected_booking_recap.booking_is_reimbursed is False
    #     assert expected_booking_recap.booking_is_confirmed is False
    #     assert expected_booking_recap.event_beginning_datetime == stock.beginningDatetime.astimezone(
    #         tz.gettz("Europe/Paris")
    #     )
    #     assert isinstance(expected_booking_recap.booking_status_history, booking_recap_history.BookingRecapHistory)
    #
    # def test_should_return_event_confirmed_booking_when_booking_is_on_an_event_in_confirmation_period(self, app):
    #     # Given
    #     beneficiary = users_factories.BeneficiaryGrant18Factory(
    #         email="beneficiary@example.com", firstName="Ron", lastName="Weasley"
    #     )
    #     pro = users_factories.ProFactory()
    #     offerer = offers_factories.OffererFactory()
    #     offers_factories.UserOffererFactory(user=pro, offerer=offerer)
    #
    #     venue = offers_factories.VenueFactory(managingOfferer=offerer)
    #     product = offers_factories.ThingProductFactory(name="Harry Potter")
    #     offer = offers_factories.ThingOfferFactory(venue=venue, product=product)
    #     stock = offers_factories.ThingStockFactory(
    #         offer=offer, price=0, beginningDatetime=datetime.utcnow() + timedelta(hours=98)
    #     )
    #     more_than_two_days_ago = datetime.utcnow() - timedelta(days=3)
    #     bookings_factories.IndividualBookingFactory(
    #         user=beneficiary, stock=stock, dateCreated=more_than_two_days_ago, token="ABCDEF"
    #     )
    #
    #     # When
    #     bookings_recap_paginated = booking_repository.find_collective_bookings_by_pro_user(
    #         user=pro, booking_period=(one_year_before_booking, one_year_after_booking)
    #     )
    #
    #     # Then
    #     expected_booking_recap = bookings_recap_paginated.bookings_recap[0]
    #     assert expected_booking_recap.booking_is_confirmed is True
    #     assert isinstance(expected_booking_recap.booking_status_history, booking_recap_history.BookingRecapHistory)
    #
    # def test_should_return_cancellation_date_when_booking_has_been_cancelled(self, app):
    #     # Given
    #     beneficiary = users_factories.BeneficiaryGrant18Factory(
    #         email="beneficiary@example.com", firstName="Ron", lastName="Weasley"
    #     )
    #     pro = users_factories.ProFactory()
    #     offerer = offers_factories.OffererFactory()
    #     offers_factories.UserOffererFactory(user=pro, offerer=offerer)
    #
    #     venue = offers_factories.VenueFactory(managingOfferer=offerer)
    #     product = offers_factories.ThingProductFactory(name="Harry Potter")
    #     offer = offers_factories.ThingOfferFactory(venue=venue, product=product)
    #     stock = offers_factories.ThingStockFactory(offer=offer, price=5)
    #     yesterday = datetime.utcnow() - timedelta(days=1)
    #     bookings_factories.CancelledIndividualBookingFactory(
    #         user=beneficiary,
    #         stock=stock,
    #         dateCreated=yesterday,
    #         token="ABCDEF",
    #         amount=5,
    #     )
    #
    #     # When
    #     bookings_recap_paginated = booking_repository.find_collective_bookings_by_pro_user(
    #         user=pro, booking_period=(one_year_before_booking, one_year_after_booking)
    #     )
    #
    #     # Then
    #     assert len(bookings_recap_paginated.bookings_recap) == 1
    #     expected_booking_recap = bookings_recap_paginated.bookings_recap[0]
    #     assert expected_booking_recap.booking_is_cancelled is True
    #     assert expected_booking_recap.booking_status_history.cancellation_date is not None
    #
    # def test_should_return_validation_date_when_booking_has_been_used_and_not_cancelled_not_reimbursed(self, app):
    #     # Given
    #     beneficiary = users_factories.BeneficiaryGrant18Factory()
    #     pro = users_factories.ProFactory()
    #     offerer = offers_factories.OffererFactory()
    #     offers_factories.UserOffererFactory(user=pro, offerer=offerer)
    #
    #     venue = offers_factories.VenueFactory(managingOfferer=offerer)
    #     product = offers_factories.EventProductFactory()
    #     offer = offers_factories.EventOfferFactory(venue=venue, product=product)
    #     stock = offers_factories.EventStockFactory(offer=offer, price=5)
    #     yesterday = datetime.utcnow() - timedelta(days=1)
    #     bookings_factories.UsedIndividualBookingFactory(
    #         user=beneficiary,
    #         stock=stock,
    #         dateCreated=yesterday,
    #         token="ABCDEF",
    #         amount=5,
    #     )
    #
    #     # When
    #     bookings_recap_paginated = booking_repository.find_collective_bookings_by_pro_user(
    #         user=pro, booking_period=(one_year_before_booking, one_year_after_booking)
    #     )
    #
    #     # Then
    #     assert len(bookings_recap_paginated.bookings_recap) == 1
    #     expected_booking_recap = bookings_recap_paginated.bookings_recap[0]
    #     assert expected_booking_recap.booking_is_used is True
    #     assert expected_booking_recap.booking_is_cancelled is False
    #     assert expected_booking_recap.booking_is_reimbursed is False
    #     assert expected_booking_recap.booking_status_history.date_confirmed is not None
    #     assert expected_booking_recap.booking_status_history.date_used is not None
    #
    # def test_should_return_correct_number_of_matching_offerers_bookings_linked_to_user(self, app):
    #     # Given
    #     beneficiary = users_factories.BeneficiaryGrant18Factory(
    #         email="beneficiary@example.com", firstName="Ron", lastName="Weasley"
    #     )
    #     pro = users_factories.ProFactory()
    #     offerer = offers_factories.OffererFactory()
    #     offers_factories.UserOffererFactory(user=pro, offerer=offerer)
    #
    #     venue = offers_factories.VenueFactory(managingOfferer=offerer)
    #     product = offers_factories.ThingProductFactory(name="Harry Potter")
    #     offer = offers_factories.ThingOfferFactory(venue=venue, product=product)
    #     stock = offers_factories.ThingStockFactory(offer=offer, price=0)
    #     today = datetime.utcnow()
    #     bookings_factories.IndividualBookingFactory(user=beneficiary, stock=stock, dateCreated=today, token="ABCD")
    #
    #     offerer2 = offers_factories.OffererFactory(siren="8765432")
    #     offers_factories.UserOffererFactory(user=pro, offerer=offerer2)
    #
    #     venue2 = offers_factories.VenueFactory(managingOfferer=offerer, siret="8765432098765")
    #     offer2 = offers_factories.ThingOfferFactory(venue=venue2)
    #     stock2 = offers_factories.ThingStockFactory(offer=offer2, price=0)
    #     bookings_factories.IndividualBookingFactory(user=beneficiary, stock=stock2, dateCreated=today, token="FGHI")
    #
    #     # When
    #     bookings_recap_paginated = booking_repository.find_collective_bookings_by_pro_user(
    #         user=pro, booking_period=(one_year_before_booking, one_year_after_booking)
    #     )
    #
    #     # Then
    #     assert len(bookings_recap_paginated.bookings_recap) == 2
    #
    # def test_should_return_bookings_from_first_page(self, app):
    #     # Given
    #     beneficiary = users_factories.BeneficiaryGrant18Factory(email="beneficiary@example.com")
    #     pro = users_factories.ProFactory()
    #     offerer = offers_factories.OffererFactory()
    #     offers_factories.UserOffererFactory(user=pro, offerer=offerer)
    #
    #     venue = offers_factories.VenueFactory(managingOfferer=offerer)
    #     offer = offers_factories.EventOfferFactory(venue=venue)
    #     stock = offers_factories.EventStockFactory(offer=offer, price=0)
    #     today = datetime.utcnow()
    #     yesterday = datetime.utcnow() - timedelta(days=1)
    #     bookings_factories.IndividualBookingFactory(user=beneficiary, stock=stock, dateCreated=yesterday, token="ABCD")
    #     booking2 = bookings_factories.IndividualBookingFactory(
    #         user=beneficiary, stock=stock, dateCreated=today, token="FGHI"
    #     )
    #
    #     # When
    #     bookings_recap_paginated = booking_repository.find_collective_bookings_by_pro_user(
    #         user=pro, booking_period=(one_year_before_booking, one_year_after_booking), page=1, per_page_limit=1
    #     )
    #
    #     # Then
    #     assert len(bookings_recap_paginated.bookings_recap) == 1
    #     assert bookings_recap_paginated.bookings_recap[0].booking_token == booking2.token
    #     assert bookings_recap_paginated.page == 1
    #     assert bookings_recap_paginated.pages == 2
    #     assert bookings_recap_paginated.total == 2
    #
    # def test_should_not_return_bookings_when_offerer_link_is_not_validated(self, app):
    #     # Given
    #     beneficiary = users_factories.BeneficiaryGrant18Factory()
    #     pro = users_factories.ProFactory()
    #     offerer = offers_factories.OffererFactory(postalCode="97300")
    #     offers_factories.UserOffererFactory(user=pro, offerer=offerer, validationToken="token")
    #
    #     venue = offers_factories.VenueFactory(managingOfferer=offerer, isVirtual=True, siret=None)
    #     product = offers_factories.ThingProductFactory(name="Harry Potter")
    #     offer = offers_factories.ThingOfferFactory(venue=venue, product=product, extraData=dict({"isbn": "9876543234"}))
    #     stock = offers_factories.ThingStockFactory(offer=offer, price=0)
    #     bookings_factories.IndividualBookingFactory(user=beneficiary, stock=stock)
    #
    #     # When
    #     bookings_recap_paginated = booking_repository.find_collective_bookings_by_pro_user(
    #         user=pro, booking_period=(one_year_before_booking, one_year_after_booking)
    #     )
    #
    #     # Then
    #     assert bookings_recap_paginated.bookings_recap == []
    #
    # def test_should_return_one_booking_recap_item_when_quantity_booked_is_one(self, app):
    #     # Given
    #     beneficiary = users_factories.BeneficiaryGrant18Factory()
    #     pro = users_factories.ProFactory()
    #     offerer = offers_factories.OffererFactory(postalCode="97300")
    #     offers_factories.UserOffererFactory(user=pro, offerer=offerer)
    #
    #     venue = offers_factories.VenueFactory(managingOfferer=offerer)
    #     offer = offers_factories.EventOfferFactory(venue=venue, isDuo=True)
    #     stock = offers_factories.EventStockFactory(offer=offer, price=0, beginningDatetime=datetime.utcnow())
    #     today = datetime.utcnow()
    #     booking = bookings_factories.IndividualBookingFactory(
    #         user=beneficiary, stock=stock, dateCreated=today, token="FGHI"
    #     )
    #
    #     # When
    #     bookings_recap_paginated = booking_repository.find_collective_bookings_by_pro_user(
    #         user=pro, booking_period=(one_year_before_booking, one_year_after_booking), page=1, per_page_limit=4
    #     )
    #
    #     # Then
    #     assert len(bookings_recap_paginated.bookings_recap) == 1
    #     assert bookings_recap_paginated.bookings_recap[0].booking_token == booking.token
    #     assert bookings_recap_paginated.page == 1
    #     assert bookings_recap_paginated.pages == 1
    #     assert bookings_recap_paginated.total == 1
    #
    # def test_should_return_two_booking_recap_items_when_quantity_booked_is_two(self, app):
    #     # Given
    #     beneficiary = users_factories.BeneficiaryGrant18Factory()
    #     pro = users_factories.ProFactory()
    #     offerer = offers_factories.OffererFactory(postalCode="97300")
    #     offers_factories.UserOffererFactory(user=pro, offerer=offerer)
    #
    #     venue = offers_factories.VenueFactory(managingOfferer=offerer)
    #     offer = offers_factories.EventOfferFactory(venue=venue, isDuo=True)
    #     stock = offers_factories.EventStockFactory(offer=offer, price=0, beginningDatetime=datetime.utcnow())
    #     today = datetime.utcnow()
    #     booking = bookings_factories.IndividualBookingFactory(
    #         user=beneficiary, stock=stock, dateCreated=today, token="FGHI", quantity=2
    #     )
    #
    #     # When
    #     bookings_recap_paginated = booking_repository.find_collective_bookings_by_pro_user(
    #         user=pro, booking_period=(one_year_before_booking, one_year_after_booking), page=1, per_page_limit=4
    #     )
    #
    #     # Then
    #     assert len(bookings_recap_paginated.bookings_recap) == 2
    #     assert bookings_recap_paginated.bookings_recap[0].booking_token == booking.token
    #     assert bookings_recap_paginated.bookings_recap[1].booking_token == booking.token
    #     assert bookings_recap_paginated.page == 1
    #     assert bookings_recap_paginated.pages == 1
    #     assert bookings_recap_paginated.total == 2
    #
    # def test_should_return_booking_date_with_offerer_timezone_when_venue_is_digital(self, app):
    #     # Given
    #     beneficiary = users_factories.BeneficiaryGrant18Factory()
    #     pro = users_factories.ProFactory()
    #     offerer = offers_factories.OffererFactory(postalCode="97300")
    #     offers_factories.UserOffererFactory(user=pro, offerer=offerer)
    #
    #     venue = offers_factories.VenueFactory(managingOfferer=offerer, isVirtual=True, siret=None)
    #     product = offers_factories.ThingProductFactory(name="Harry Potter")
    #     offer = offers_factories.ThingOfferFactory(venue=venue, product=product)
    #     stock = offers_factories.ThingStockFactory(offer=offer, price=0)
    #     booking_date = datetime(2020, 1, 1, 10, 0, 0) - timedelta(days=1)
    #     bookings_factories.UsedIndividualBookingFactory(
    #         user=beneficiary,
    #         stock=stock,
    #         dateCreated=booking_date,
    #         token="ABCDEF",
    #     )
    #
    #     # When
    #     bookings_recap_paginated = booking_repository.find_collective_bookings_by_pro_user(
    #         user=pro, booking_period=(booking_date - timedelta(days=365), booking_date + timedelta(days=365))
    #     )
    #
    #     # Then
    #     assert len(bookings_recap_paginated.bookings_recap) == 1
    #     expected_booking_recap = bookings_recap_paginated.bookings_recap[0]
    #     assert expected_booking_recap.booking_date == booking_date.astimezone(tz.gettz("America/Cayenne"))
    #
    # def test_should_return_booking_isbn_when_information_is_available(self, app):
    #     # Given
    #     beneficiary = users_factories.BeneficiaryGrant18Factory()
    #     pro = users_factories.ProFactory()
    #     offerer = offers_factories.OffererFactory(postalCode="97300")
    #     offers_factories.UserOffererFactory(user=pro, offerer=offerer)
    #
    #     venue = offers_factories.VenueFactory(managingOfferer=offerer, isVirtual=True, siret=None)
    #     product = offers_factories.ThingProductFactory(name="Harry Potter")
    #     offer = offers_factories.ThingOfferFactory(venue=venue, product=product, extraData=dict({"isbn": "9876543234"}))
    #     stock = offers_factories.ThingStockFactory(offer=offer, price=0)
    #     booking_date = datetime(2020, 1, 1, 10, 0, 0) - timedelta(days=1)
    #     bookings_factories.UsedIndividualBookingFactory(
    #         user=beneficiary,
    #         stock=stock,
    #         dateCreated=booking_date,
    #         token="ABCDEF",
    #     )
    #
    #     # When
    #     bookings_recap_paginated = booking_repository.find_collective_bookings_by_pro_user(
    #         user=pro, booking_period=(booking_date - timedelta(days=365), booking_date + timedelta(days=365))
    #     )
    #
    #     # Then
    #     expected_booking_recap = bookings_recap_paginated.bookings_recap[0]
    #     assert expected_booking_recap.offer_isbn == "9876543234"
    #
    # def test_should_return_only_booking_for_requested_venue(self, app):
    #     # Given
    #     pro_user = users_factories.ProFactory()
    #     user_offerer = offers_factories.UserOffererFactory(user=pro_user)
    #
    #     bookings_factories.IndividualBookingFactory(stock__offer__venue__managingOfferer=user_offerer.offerer)
    #     booking_two = bookings_factories.IndividualBookingFactory(
    #         stock__offer__venue__managingOfferer=user_offerer.offerer
    #     )
    #
    #     # When
    #     bookings_recap_paginated = booking_repository.find_collective_bookings_by_pro_user(
    #         user=pro_user,
    #         booking_period=(one_year_before_booking, one_year_after_booking),
    #         venue_id=booking_two.venue.id,
    #     )
    #
    #     # Then
    #     assert len(bookings_recap_paginated.bookings_recap) == 1
    #     expected_booking_recap = bookings_recap_paginated.bookings_recap[0]
    #     assert expected_booking_recap.offer_identifier == booking_two.stock.offer.id
    #     assert expected_booking_recap.offer_name == booking_two.stock.offer.name
    #     assert expected_booking_recap.booking_amount == booking_two.amount
    #
    # def test_should_return_only_booking_for_requested_event_date(self, app):
    #     # Given
    #     user_offerer = offers_factories.UserOffererFactory()
    #     event_date = datetime(2020, 12, 24, 10, 30)
    #     expected_booking = bookings_factories.IndividualBookingFactory(
    #         stock=offers_factories.EventStockFactory(
    #             beginningDatetime=event_date, offer__venue__managingOfferer=user_offerer.offerer
    #         )
    #     )
    #     bookings_factories.IndividualBookingFactory(
    #         stock=offers_factories.EventStockFactory(offer__venue__managingOfferer=user_offerer.offerer)
    #     )
    #     bookings_factories.IndividualBookingFactory(
    #         stock=offers_factories.ThingStockFactory(offer__venue__managingOfferer=user_offerer.offerer)
    #     )
    #
    #     # When
    #     bookings_recap_paginated = booking_repository.find_collective_bookings_by_pro_user(
    #         user=user_offerer.user,
    #         booking_period=(one_year_before_booking, one_year_after_booking),
    #         event_date=event_date.date(),
    #     )
    #
    #     # Then
    #     assert len(bookings_recap_paginated.bookings_recap) == 1
    #     resulting_booking_recap = bookings_recap_paginated.bookings_recap[0]
    #     assert resulting_booking_recap.booking_token == expected_booking.token
    #
    # def should_consider_venue_locale_datetime_when_filtering_by_event_date(self, app):
    #     # Given
    #     user_offerer = offers_factories.UserOffererFactory()
    #     event_datetime = datetime(2020, 4, 21, 20, 00)
    #
    #     offer_in_cayenne = offers_factories.OfferFactory(
    #         venue__postalCode="97300", venue__managingOfferer=user_offerer.offerer
    #     )
    #     cayenne_event_datetime = datetime(2020, 4, 22, 2, 0)
    #     stock_in_cayenne = offers_factories.EventStockFactory(
    #         offer=offer_in_cayenne, beginningDatetime=cayenne_event_datetime
    #     )
    #     cayenne_booking = bookings_factories.IndividualBookingFactory(stock=stock_in_cayenne)
    #
    #     offer_in_mayotte = offers_factories.OfferFactory(
    #         venue__postalCode="97600", venue__managingOfferer=user_offerer.offerer
    #     )
    #     mayotte_event_datetime = datetime(2020, 4, 20, 22, 0)
    #     stock_in_mayotte = offers_factories.EventStockFactory(
    #         offer=offer_in_mayotte, beginningDatetime=mayotte_event_datetime
    #     )
    #     mayotte_booking = bookings_factories.IndividualBookingFactory(stock=stock_in_mayotte)
    #
    #     # When
    #     bookings_recap_paginated = booking_repository.find_collective_bookings_by_pro_user(
    #         user=user_offerer.user,
    #         booking_period=(one_year_before_booking, one_year_after_booking),
    #         event_date=event_datetime.date(),
    #     )
    #
    #     # Then
    #     assert len(bookings_recap_paginated.bookings_recap) == 2
    #     bookings_tokens = [booking_recap.booking_token for booking_recap in bookings_recap_paginated.bookings_recap]
    #     assert cayenne_booking.token in bookings_tokens
    #     assert mayotte_booking.token in bookings_tokens
    #
    # def test_should_return_only_bookings_for_requested_booking_period(self, app):
    #     # Given
    #     user_offerer = offers_factories.UserOffererFactory()
    #     booking_beginning_period = datetime(2020, 12, 24, 10, 30).date()
    #     booking_ending_period = datetime(2020, 12, 26, 15, 00).date()
    #     booking_status_filter = BookingStatusFilter.BOOKED
    #     expected_booking = bookings_factories.IndividualBookingFactory(
    #         dateCreated=datetime(2020, 12, 26, 15, 30),
    #         stock=offers_factories.ThingStockFactory(offer__venue__managingOfferer=user_offerer.offerer),
    #     )
    #     bookings_factories.IndividualBookingFactory(
    #         dateCreated=datetime(2020, 12, 29, 15, 30),
    #         stock=offers_factories.ThingStockFactory(offer__venue__managingOfferer=user_offerer.offerer),
    #     )
    #     bookings_factories.IndividualBookingFactory(
    #         dateCreated=datetime(2020, 12, 22, 15, 30),
    #         stock=offers_factories.ThingStockFactory(offer__venue__managingOfferer=user_offerer.offerer),
    #     )
    #
    #     # When
    #     bookings_recap_paginated = booking_repository.find_collective_bookings_by_pro_user(
    #         user=user_offerer.user,
    #         booking_period=(booking_beginning_period, booking_ending_period),
    #         status_filter=booking_status_filter,
    #     )
    #
    #     # Then
    #     assert len(bookings_recap_paginated.bookings_recap) == 1
    #     resulting_booking_recap = bookings_recap_paginated.bookings_recap[0]
    #     assert resulting_booking_recap.booking_date == utc_datetime_to_department_timezone(
    #         expected_booking.dateCreated, expected_booking.venue.departementCode
    #     )
    #
    # def should_consider_venue_locale_datetime_when_filtering_by_booking_period(self, app):
    #     # Given
    #     user_offerer = offers_factories.UserOffererFactory()
    #     requested_booking_period_beginning = datetime(2020, 4, 21, 20, 00).date()
    #     requested_booking_period_ending = datetime(2020, 4, 22, 20, 00).date()
    #
    #     offer_in_cayenne = offers_factories.OfferFactory(
    #         venue__postalCode="97300", venue__managingOfferer=user_offerer.offerer
    #     )
    #     cayenne_booking_datetime = datetime(2020, 4, 22, 2, 0)
    #     stock_in_cayenne = offers_factories.EventStockFactory(
    #         offer=offer_in_cayenne,
    #     )
    #     cayenne_booking = bookings_factories.IndividualBookingFactory(
    #         stock=stock_in_cayenne, dateCreated=cayenne_booking_datetime
    #     )
    #
    #     offer_in_mayotte = offers_factories.OfferFactory(
    #         venue__postalCode="97600", venue__managingOfferer=user_offerer.offerer
    #     )
    #     mayotte_booking_datetime = datetime(2020, 4, 20, 23, 0)
    #     stock_in_mayotte = offers_factories.EventStockFactory(
    #         offer=offer_in_mayotte,
    #     )
    #     mayotte_booking = bookings_factories.IndividualBookingFactory(
    #         stock=stock_in_mayotte, dateCreated=mayotte_booking_datetime
    #     )
    #
    #     # When
    #     bookings_recap_paginated = booking_repository.find_collective_bookings_by_pro_user(
    #         user=user_offerer.user,
    #         booking_period=(requested_booking_period_beginning, requested_booking_period_ending),
    #     )
    #
    #     # Then
    #     assert len(bookings_recap_paginated.bookings_recap) == 2
    #     bookings_tokens = [booking_recap.booking_token for booking_recap in bookings_recap_paginated.bookings_recap]
    #     assert cayenne_booking.token in bookings_tokens
    #     assert mayotte_booking.token in bookings_tokens
    #
    # def test_should_set_educational_booking_confirmation_date_in_history(self, app) -> None:
    #     # Given
    #     pro = users_factories.ProFactory()
    #     offerer = offers_factories.OffererFactory()
    #     offers_factories.UserOffererFactory(user=pro, offerer=offerer)
    #
    #     venue = offers_factories.VenueFactory(managingOfferer=offerer)
    #     offer = offers_factories.ThingOfferFactory(venue=venue)
    #     stock = offers_factories.ThingStockFactory(
    #         offer=offer, price=0, beginningDatetime=datetime.utcnow() + timedelta(hours=98)
    #     )
    #     yesterday = datetime.utcnow() - timedelta(days=1)
    #     bookings_factories.EducationalBookingFactory(
    #         educationalBooking__confirmationDate=datetime(2022, 1, 1),
    #         stock=stock,
    #         dateCreated=yesterday,
    #     )
    #
    #     # When
    #     bookings_recap_paginated = booking_repository.find_collective_bookings_by_pro_user(
    #         user=pro, booking_period=(one_year_before_booking, one_year_after_booking)
    #     )
    #
    #     # Then
    #     assert len(bookings_recap_paginated.bookings_recap) == 1
    #     expected_booking_recap = bookings_recap_paginated.bookings_recap[0]
    #     assert isinstance(expected_booking_recap.booking_status_history, booking_recap_history.BookingRecapHistory)
    #     assert expected_booking_recap.booking_status_history.confirmation_date == datetime(2022, 1, 1)
    #
    # def test_should_set_booking_recap_pending_in_history(self, app) -> None:
    #     # Given
    #     pro = users_factories.ProFactory()
    #     offerer = offers_factories.OffererFactory()
    #     offers_factories.UserOffererFactory(user=pro, offerer=offerer)
    #
    #     venue = offers_factories.VenueFactory(managingOfferer=offerer)
    #     offer = offers_factories.ThingOfferFactory(venue=venue)
    #     stock = offers_factories.ThingStockFactory(
    #         offer=offer, price=0, beginningDatetime=datetime.utcnow() + timedelta(hours=98)
    #     )
    #     yesterday = datetime.utcnow() - timedelta(days=1)
    #     bookings_factories.EducationalBookingFactory(
    #         status=BookingStatus.PENDING,
    #         stock=stock,
    #         dateCreated=yesterday,
    #     )
    #
    #     # When
    #     bookings_recap_paginated = booking_repository.find_collective_bookings_by_pro_user(
    #         user=pro, booking_period=(one_year_before_booking, one_year_after_booking)
    #     )
    #
    #     # Then
    #     assert len(bookings_recap_paginated.bookings_recap) == 1
    #     expected_booking_recap = bookings_recap_paginated.bookings_recap[0]
    #     assert isinstance(
    #         expected_booking_recap.booking_status_history,
    #         booking_recap_history.BookingRecapPendingHistory,
    #     )
    #     assert expected_booking_recap.booking_status_history.booking_date == yesterday.astimezone(
    #         tz.gettz("Europe/Paris")
    #     )
    #
    # def test_should_return_token_as_none_when_educational_booking(self, app):
    #     # Given
    #     pro = users_factories.ProFactory()
    #     offerer = offers_factories.OffererFactory()
    #     offers_factories.UserOffererFactory(user=pro, offerer=offerer)
    #     venue = offers_factories.VenueFactory(managingOfferer=offerer)
    #
    #     bookings_factories.EducationalBookingFactory(
    #         stock__offer__venue=venue,
    #     )
    #
    #     # When
    #     beginning_period = datetime.fromisoformat("2021-10-15")
    #     ending_period = datetime.fromisoformat("2032-02-15")
    #     bookings_recap_paginated = booking_repository.find_collective_bookings_by_pro_user(
    #         user=pro, booking_period=(beginning_period, ending_period)
    #     )
    #
    #     # Then
    #     assert len(bookings_recap_paginated.bookings_recap) == 1
    #     expected_booking_recap = bookings_recap_paginated.bookings_recap[0]
    #     assert expected_booking_recap.booking_token == None
    #
    # def test_should_return_only_bookings_for_requested_offer_type(self, app):
    #     # Given
    #     user_offerer = offers_factories.UserOffererFactory()
    #     bookings_factories.IndividualBookingFactory(
    #         dateCreated=default_booking_date,
    #         stock__offer__venue__managingOfferer=user_offerer.offerer,
    #     )
    #     bookings_factories.EducationalBookingFactory(
    #         stock__offer__venue__managingOfferer=user_offerer.offerer,
    #     )
    #
    #     # When
    #     individual_bookings_recap_paginated = booking_repository.find_collective_bookings_by_pro_user(
    #         user=user_offerer.user,
    #         booking_period=(one_year_before_booking, one_year_after_booking),
    #         offer_type=OfferType.INDIVIDUAL_OR_DUO,
    #     )
    #     educational_bookings_recap_paginated = booking_repository.find_collective_bookings_by_pro_user(
    #         user=user_offerer.user,
    #         booking_period=(one_year_before_booking, one_year_after_booking),
    #         offer_type=OfferType.EDUCATIONAL,
    #     )
    #     all_bookings_recap_paginated = booking_repository.find_collective_bookings_by_pro_user(
    #         user=user_offerer.user,
    #         booking_period=(one_year_before_booking, one_year_after_booking),
    #     )
    #
    #     # Then
    #     assert len(individual_bookings_recap_paginated.bookings_recap) == 1
    #     individual_resulting_booking_recap = individual_bookings_recap_paginated.bookings_recap[0]
    #     assert individual_resulting_booking_recap.booking_is_educational == False
    #     assert len(educational_bookings_recap_paginated.bookings_recap) == 1
    #     educational_resulting_booking_recap = educational_bookings_recap_paginated.bookings_recap[0]
    #     assert educational_resulting_booking_recap.booking_is_educational == True
    #     assert len(all_bookings_recap_paginated.bookings_recap) == 2
