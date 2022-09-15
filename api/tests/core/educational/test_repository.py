from datetime import datetime
from datetime import timedelta

from dateutil import tz
from freezegun import freeze_time
import pytest

from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import repository as educational_repository
from pcapi.core.educational.models import CollectiveBookingStatus
from pcapi.core.educational.models import CollectiveBookingStatusFilter
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.users import factories as users_factories
from pcapi.utils.date import utc_datetime_to_department_timezone


pytestmark = pytest.mark.usefixtures("db_session")


@freeze_time("2022-03-20")
class FindByProUserTest:
    def test_should_return_only_expected_collective_booking_attributes(self, app):
        # Given
        booking_date = datetime(2022, 3, 15, 10, 15, 0)
        redactor = educational_factories.EducationalRedactorFactory(
            email="reda.ktheur@example.com", firstName="Reda", lastName="Khteur", civility="M."
        )
        institution = educational_factories.EducationalInstitutionFactory()
        user_offerer = offerers_factories.UserOffererFactory()
        collective_stock = educational_factories.CollectiveStockFactory(
            collectiveOffer__name="Le chant des cigales",
            collectiveOffer__venue__managingOfferer=user_offerer.offerer,
        )
        collective_booking = educational_factories.UsedCollectiveBookingFactory(
            educationalRedactor=redactor,
            dateUsed=booking_date + timedelta(days=10),
            collectiveStock=collective_stock,
            dateCreated=booking_date,
            educationalInstitution=institution,
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
        assert expected_booking_recap.institutionName == institution.name
        assert expected_booking_recap.institutionType == institution.institutionType
        assert expected_booking_recap.institutionCity == institution.city
        assert expected_booking_recap.institutionPhoneNumber == institution.phoneNumber
        assert expected_booking_recap.institutionPostalCode == institution.postalCode
        assert expected_booking_recap.institutionId == institution.id
        assert expected_booking_recap.bookedAt == booking_date.astimezone(tz.gettz("Europe/Paris"))
        assert expected_booking_recap.status is CollectiveBookingStatus.USED
        assert expected_booking_recap.isConfirmed is True
        assert expected_booking_recap.bookingAmount == collective_stock.price
        assert expected_booking_recap.bookedAt == booking_date.astimezone(tz.gettz("Europe/Paris"))
        assert expected_booking_recap.usedAt == (booking_date + timedelta(days=10)).astimezone(tz.gettz("Europe/Paris"))
        assert expected_booking_recap.cancellationLimitDate == collective_booking.cancellationLimitDate.astimezone(
            tz.gettz("Europe/Paris")
        )

    def test_should_return_only_validated_collective_bookings_for_requested_period(self, app):
        # Given
        booking_date = datetime(2022, 3, 15, 10, 15, 0)
        user_offerer = offerers_factories.UserOffererFactory()
        educational_factories.UsedCollectiveBookingFactory(
            dateUsed=booking_date + timedelta(days=10),
            collectiveStock__collectiveOffer__venue__managingOfferer=user_offerer.offerer,
            dateCreated=booking_date,
        )

        used_collective_booking_1 = educational_factories.UsedCollectiveBookingFactory(
            dateUsed=booking_date + timedelta(days=3),
            collectiveStock__collectiveOffer__venue__managingOfferer=user_offerer.offerer,
            dateCreated=booking_date,
        )

        used_collective_booking_2 = educational_factories.UsedCollectiveBookingFactory(
            dateUsed=booking_date + timedelta(days=4),
            collectiveStock__collectiveOffer__venue__managingOfferer=user_offerer.offerer,
            dateCreated=booking_date,
        )

        educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__venue__managingOfferer=user_offerer.offerer,
            dateCreated=booking_date,
        )

        # When
        total_bookings, collective_bookings = educational_repository.find_collective_bookings_by_pro_user(
            user=user_offerer.user,
            booking_period=(booking_date - timedelta(days=5), booking_date + timedelta(days=5)),
            status_filter=CollectiveBookingStatusFilter.VALIDATED,
        )

        # Then
        assert total_bookings == 2
        assert {collective_bookings[0].offerId, collective_bookings[1].offerId} == {
            used_collective_booking_1.collectiveStock.collectiveOfferId,
            used_collective_booking_2.collectiveStock.collectiveOfferId,
        }

    def test_should_return_only_reimbursed_collective_bookings_for_requested_period(self, app):
        # Given
        booking_date = datetime(2022, 3, 15, 10, 15, 0)
        user_offerer = offerers_factories.UserOffererFactory()
        educational_factories.ReimbursedCollectiveBookingFactory(
            reimbursementDate=booking_date + timedelta(days=1),
            collectiveStock__collectiveOffer__venue__managingOfferer=user_offerer.offerer,
            dateCreated=booking_date,
        )

        reimbursed_collective_booking_1 = educational_factories.ReimbursedCollectiveBookingFactory(
            reimbursementDate=booking_date + timedelta(days=2),
            collectiveStock__collectiveOffer__venue__managingOfferer=user_offerer.offerer,
            dateCreated=booking_date,
        )

        reimbursed_collective_booking_2 = educational_factories.ReimbursedCollectiveBookingFactory(
            reimbursementDate=booking_date + timedelta(days=4),
            collectiveStock__collectiveOffer__venue__managingOfferer=user_offerer.offerer,
            dateCreated=booking_date,
        )

        educational_factories.ReimbursedCollectiveBookingFactory(
            reimbursementDate=booking_date + timedelta(days=8),
            collectiveStock__collectiveOffer__venue__managingOfferer=user_offerer.offerer,
            dateCreated=booking_date,
        )

        educational_factories.UsedCollectiveBookingFactory(
            collectiveStock__collectiveOffer__venue__managingOfferer=user_offerer.offerer,
            dateCreated=booking_date,
        )

        # When
        total_bookings, collective_bookings = educational_repository.find_collective_bookings_by_pro_user(
            user=user_offerer.user,
            booking_period=(booking_date + timedelta(days=1), booking_date + timedelta(days=5)),
            status_filter=CollectiveBookingStatusFilter.REIMBURSED,
        )

        # Then
        assert total_bookings == 2
        assert {collective_bookings[0].offerId, collective_bookings[1].offerId} == {
            reimbursed_collective_booking_1.collectiveStock.collectiveOfferId,
            reimbursed_collective_booking_2.collectiveStock.collectiveOfferId,
        }

    def test_should_return_confirmed_collective_bookings_when_booking_is_in_confirmation_period(self, app):
        # Given
        booking_date = datetime.utcnow() - timedelta(days=5)
        user_offerer = offerers_factories.UserOffererFactory()
        educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__venue__managingOfferer=user_offerer.offerer,
            dateCreated=booking_date,
            cancellationLimitDate=datetime.utcnow() - timedelta(days=1),
        )

        # When
        _, collective_bookings = educational_repository.find_collective_bookings_by_pro_user(
            user=user_offerer.user,
            booking_period=(booking_date - timedelta(days=365), booking_date + timedelta(days=365)),
        )

        # Then
        collective_booking = collective_bookings[0]
        assert collective_booking.isConfirmed is True

    def test_should_return_cancellation_date_when_booking_has_been_cancelled(self, app):
        # Given
        booking_date = datetime.utcnow() - timedelta(days=5)
        user_offerer = offerers_factories.UserOffererFactory()
        booking = educational_factories.CancelledCollectiveBookingFactory(
            collectiveStock__collectiveOffer__venue__managingOfferer=user_offerer.offerer,
            dateCreated=booking_date,
            cancellationDate=booking_date + timedelta(days=2),
        )

        # When
        _, collective_bookings = educational_repository.find_collective_bookings_by_pro_user(
            user=user_offerer.user,
            booking_period=(booking_date - timedelta(days=10), booking_date + timedelta(days=10)),
        )

        # Then
        collective_booking = collective_bookings[0]
        assert collective_booking.cancelledAt == booking.cancellationDate.astimezone(tz.gettz("Europe/Paris"))

    def test_should_return_correct_number_of_matching_offerers_bookings_linked_to_user(self, app):
        # Given
        booking_date = datetime.utcnow() - timedelta(days=5)
        pro = users_factories.ProFactory()

        user_offerer_1 = offerers_factories.UserOffererFactory(user=pro)
        educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__venue__managingOfferer=user_offerer_1.offerer,
            dateCreated=booking_date,
        )

        user_offerer_2 = offerers_factories.UserOffererFactory(user=pro)
        educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__venue__managingOfferer=user_offerer_2.offerer,
            dateCreated=booking_date - timedelta(days=2),
        )

        # When
        total_collective_bookings, collective_bookings = educational_repository.find_collective_bookings_by_pro_user(
            user=pro,
            booking_period=(booking_date - timedelta(days=5), booking_date + timedelta(days=5)),
        )

        # Then
        assert total_collective_bookings == 2
        assert len(collective_bookings) == 2

    def test_should_return_bookings_from_first_page(self, app):
        # Given
        user_offerer = offerers_factories.UserOffererFactory()
        educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__venue__managingOfferer=user_offerer.offerer,
            dateCreated=datetime.utcnow() - timedelta(days=1),
        )
        collective_booking = educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__venue__managingOfferer=user_offerer.offerer,
            dateCreated=datetime.utcnow() - timedelta(hours=1),
        )

        # When
        total_bookings, collective_bookings = educational_repository.find_collective_bookings_by_pro_user(
            user=user_offerer.user,
            booking_period=(datetime.utcnow() - timedelta(days=10), datetime.utcnow() + timedelta(days=10)),
            page=1,
            per_page_limit=1,
        )

        # Then
        assert total_bookings == 2
        assert len(collective_bookings) == 1
        assert collective_bookings[0].offerId == collective_booking.collectiveStock.collectiveOfferId

    def test_should_not_return_bookings_when_offerer_link_is_not_validated(self, app):
        # Given
        booking_date = datetime.utcnow() - timedelta(days=5)
        user_offerer = offerers_factories.UserOffererFactory(validationToken="token")
        educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__venue__managingOfferer=user_offerer.offerer,
            dateCreated=booking_date,
        )

        # When
        _, collective_bookings = educational_repository.find_collective_bookings_by_pro_user(
            user=user_offerer.user,
            booking_period=(booking_date - timedelta(days=10), booking_date + timedelta(days=10)),
        )

        # Then
        assert len(collective_bookings) == 0

    def test_should_return_only_booking_for_requested_venue(self, app):
        # Given
        booking_date = datetime.utcnow() - timedelta(days=5)
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__venue__managingOfferer=user_offerer.offerer,
            dateCreated=booking_date,
        )
        booking_to_be_found = educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__venue=venue,
            collectiveStock__price=5000,
            dateCreated=booking_date,
        )

        # When
        total_bookings, collective_bookings = educational_repository.find_collective_bookings_by_pro_user(
            user=user_offerer.user,
            booking_period=(booking_date - timedelta(days=10), booking_date + timedelta(days=10)),
            venue_id=venue.id,
        )

        # Then
        assert total_bookings == 1
        assert len(collective_bookings) == 1
        collective_booking = collective_bookings[0]
        assert collective_booking.offerId == booking_to_be_found.collectiveStock.collectiveOfferId
        assert collective_booking.bookingAmount == booking_to_be_found.collectiveStock.price

    def test_should_return_only_booking_for_requested_event_date(self, app):
        # Given
        booking_date = datetime.utcnow() - timedelta(days=5)
        user_offerer = offerers_factories.UserOffererFactory()
        event_date = datetime.utcnow() + timedelta(days=30, hours=20)
        educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__venue__managingOfferer=user_offerer.offerer,
            dateCreated=booking_date,
        )
        booking_to_be_found = educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__venue__managingOfferer=user_offerer.offerer,
            collectiveStock__price=5000,
            collectiveStock__beginningDatetime=event_date,
            dateCreated=booking_date,
        )

        # When
        total_bookings, collective_bookings = educational_repository.find_collective_bookings_by_pro_user(
            user=user_offerer.user,
            booking_period=(booking_date - timedelta(days=10), booking_date + timedelta(days=10)),
            event_date=event_date.date(),
        )

        # Then
        assert total_bookings == 1
        assert len(collective_bookings) == 1
        collective_booking = collective_bookings[0]
        assert collective_booking.offerId == booking_to_be_found.collectiveStock.collectiveOfferId
        assert collective_booking.bookingAmount == booking_to_be_found.collectiveStock.price

    def should_consider_venue_locale_datetime_when_filtering_by_event_date(self, app):
        # Given
        booking_date = datetime.utcnow() - timedelta(days=5)
        user_offerer = offerers_factories.UserOffererFactory()
        event_datetime = datetime(2022, 4, 21, 20, 00)
        collective_offer_in_cayenne = educational_factories.CollectiveOfferFactory(
            venue__postalCode="97300", venue__managingOfferer=user_offerer.offerer
        )
        cayenne_event_datetime = datetime(2022, 4, 22, 2, 0)
        stock_in_cayenne = educational_factories.CollectiveStockFactory(
            collectiveOffer=collective_offer_in_cayenne, beginningDatetime=cayenne_event_datetime
        )
        cayenne_collective_booking = educational_factories.CollectiveBookingFactory(collectiveStock=stock_in_cayenne)

        offer_in_mayotte = educational_factories.CollectiveOfferFactory(
            venue__postalCode="97600", venue__managingOfferer=user_offerer.offerer
        )
        mayotte_event_datetime = datetime(2022, 4, 20, 22, 0)
        stock_in_mayotte = educational_factories.CollectiveStockFactory(
            collectiveOffer=offer_in_mayotte, beginningDatetime=mayotte_event_datetime
        )
        mayotte_collective_booking = educational_factories.CollectiveBookingFactory(collectiveStock=stock_in_mayotte)

        # When
        total_bookings, collective_bookings = educational_repository.find_collective_bookings_by_pro_user(
            user=user_offerer.user,
            booking_period=(booking_date - timedelta(days=10), booking_date + timedelta(days=10)),
            event_date=event_datetime.date(),
        )

        # Then
        assert total_bookings == 2
        assert len(collective_bookings) == 2
        collective_bookings_ids = {booking.collectiveBookingId for booking in collective_bookings}
        assert {cayenne_collective_booking.id, mayotte_collective_booking.id} == collective_bookings_ids

    def test_should_return_only_bookings_for_requested_booking_period(self, app):
        # Given
        user_offerer = offerers_factories.UserOffererFactory()
        booking_beginning_period = datetime(2020, 12, 24, 10, 30).date()
        booking_ending_period = datetime(2020, 12, 26, 15, 00).date()
        booking_status_filter = CollectiveBookingStatusFilter.BOOKED
        expected_booking = educational_factories.CollectiveBookingFactory(
            dateCreated=datetime(2020, 12, 26, 15, 30),
            collectiveStock__collectiveOffer__venue__managingOfferer=user_offerer.offerer,
        )
        educational_factories.CollectiveBookingFactory(
            dateCreated=datetime(2020, 12, 29, 15, 30),
            collectiveStock__collectiveOffer__venue__managingOfferer=user_offerer.offerer,
        )
        educational_factories.CollectiveBookingFactory(
            dateCreated=datetime(2020, 12, 22, 15, 30),
            collectiveStock__collectiveOffer__venue__managingOfferer=user_offerer.offerer,
        )

        # When
        _, collective_bookings = educational_repository.find_collective_bookings_by_pro_user(
            user=user_offerer.user,
            booking_period=(booking_beginning_period, booking_ending_period),
            status_filter=booking_status_filter,
        )

        # Then
        assert len(collective_bookings) == 1
        collective_booking = collective_bookings[0]
        assert collective_booking.bookedAt == utc_datetime_to_department_timezone(
            expected_booking.dateCreated, expected_booking.venue.departementCode
        )

    def should_consider_venue_locale_datetime_when_filtering_by_booking_period(self, app):
        # Given
        user_offerer = offerers_factories.UserOffererFactory()
        requested_booking_period_beginning = datetime(2020, 4, 21, 20, 00).date()
        requested_booking_period_ending = datetime(2020, 4, 22, 20, 00).date()

        offer_in_cayenne = educational_factories.CollectiveOfferFactory(
            venue__postalCode="97300", venue__managingOfferer=user_offerer.offerer
        )
        cayenne_booking_datetime = datetime(2020, 4, 22, 2, 0)
        cayenne_booking = educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer=offer_in_cayenne, dateCreated=cayenne_booking_datetime
        )

        offer_in_mayotte = educational_factories.CollectiveOfferFactory(
            venue__postalCode="97600", venue__managingOfferer=user_offerer.offerer
        )
        mayotte_booking_datetime = datetime(2020, 4, 20, 23, 0)
        mayotte_booking = educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer=offer_in_mayotte, dateCreated=mayotte_booking_datetime
        )

        # When
        total_bookings, collective_bookings = educational_repository.find_collective_bookings_by_pro_user(
            user=user_offerer.user,
            booking_period=(requested_booking_period_beginning, requested_booking_period_ending),
        )

        # Then
        assert total_bookings == 2
        assert len(collective_bookings) == 2
        collective_bookings_ids = {booking.collectiveBookingId for booking in collective_bookings}
        assert {cayenne_booking.id, mayotte_booking.id} == collective_bookings_ids
