from datetime import datetime
from datetime import timedelta

import pytest

from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import repository as educational_repository
from pcapi.core.educational.factories import create_collective_offer_by_status
from pcapi.core.educational.models import CollectiveBookingStatus
from pcapi.core.educational.models import CollectiveBookingStatusFilter
from pcapi.core.educational.models import CollectiveOffer
from pcapi.core.educational.models import CollectiveOfferDisplayedStatus
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers.repository import _filter_collective_offers_by_statuses
from pcapi.core.users import factories as users_factories
from pcapi.models import offer_mixin


pytestmark = pytest.mark.usefixtures("db_session")


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
        assert expected_booking_recap.collectiveStock.collectiveOfferId == collective_stock.collectiveOffer.id
        assert expected_booking_recap.collectiveStock.collectiveOffer.name == "Le chant des cigales"
        assert expected_booking_recap.educationalInstitution.name == institution.name
        assert expected_booking_recap.educationalInstitution.institutionType == institution.institutionType
        assert expected_booking_recap.educationalInstitution.city == institution.city
        assert expected_booking_recap.educationalInstitution.phoneNumber == institution.phoneNumber
        assert expected_booking_recap.educationalInstitution.postalCode == institution.postalCode
        assert expected_booking_recap.educationalInstitutionId == institution.id
        assert expected_booking_recap.status is CollectiveBookingStatus.USED
        assert expected_booking_recap.isConfirmed is True
        assert expected_booking_recap.collectiveStock.price == collective_stock.price
        assert expected_booking_recap.dateCreated == booking_date
        assert expected_booking_recap.dateUsed == (booking_date + timedelta(days=10))
        assert expected_booking_recap.cancellationLimitDate == collective_booking.cancellationLimitDate

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
        assert {
            collective_bookings[0].collectiveStock.collectiveOfferId,
            collective_bookings[1].collectiveStock.collectiveOfferId,
        } == {
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
        assert {
            collective_bookings[0].collectiveStock.collectiveOfferId,
            collective_bookings[1].collectiveStock.collectiveOfferId,
        } == {
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
        assert collective_booking.cancellationDate == booking.cancellationDate

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
        assert (
            collective_bookings[0].collectiveStock.collectiveOfferId
            == collective_booking.collectiveStock.collectiveOfferId
        )

    def test_should_not_return_bookings_when_offerer_link_is_not_validated(self, app):
        # Given
        booking_date = datetime.utcnow() - timedelta(days=5)
        user_offerer = offerers_factories.NotValidatedUserOffererFactory()
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
        assert (
            collective_booking.collectiveStock.collectiveOfferId
            == booking_to_be_found.collectiveStock.collectiveOfferId
        )
        assert collective_booking.collectiveStock.price == booking_to_be_found.collectiveStock.price

    def test_should_return_only_booking_for_requested_event_date(self, app):
        # Given
        booking_date = datetime.utcnow() - timedelta(days=5)
        user_offerer = offerers_factories.UserOffererFactory()
        event_date = datetime.utcnow() + timedelta(days=30)
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
        assert (
            collective_booking.collectiveStock.collectiveOfferId
            == booking_to_be_found.collectiveStock.collectiveOfferId
        )
        assert collective_booking.collectiveStock.price == booking_to_be_found.collectiveStock.price

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
        collective_bookings_ids = {booking.id for booking in collective_bookings}
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
        assert collective_booking.dateCreated == expected_booking.dateCreated

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
        collective_bookings_ids = {booking.id for booking in collective_bookings}
        assert {cayenne_booking.id, mayotte_booking.id} == collective_bookings_ids


class FilterCollectiveOfferByStatusesTest:
    def test_filter_by_booked_status(self, app):
        # Given
        booked_offer = create_collective_offer_by_status(CollectiveOfferDisplayedStatus.BOOKED)

        pending_offer = create_collective_offer_by_status(CollectiveOfferDisplayedStatus.PENDING)

        base_query = CollectiveOffer.query

        # When
        filtered_booked_query = _filter_collective_offers_by_statuses(
            base_query, [CollectiveOfferDisplayedStatus.BOOKED.value]
        )

        # Then
        assert filtered_booked_query.count() == 1
        assert filtered_booked_query.first() == booked_offer

        # When
        filtered_pending_query = _filter_collective_offers_by_statuses(
            base_query, [CollectiveOfferDisplayedStatus.PENDING.value]
        )

        # Then
        assert filtered_pending_query.count() == 1
        assert filtered_pending_query.first() == pending_offer

    @pytest.mark.parametrize(
        "status",
        [
            # All but PENDING
            CollectiveOfferDisplayedStatus.ACTIVE,
            CollectiveOfferDisplayedStatus.REJECTED,
            CollectiveOfferDisplayedStatus.PREBOOKED,
            CollectiveOfferDisplayedStatus.BOOKED,
            CollectiveOfferDisplayedStatus.INACTIVE,
            CollectiveOfferDisplayedStatus.EXPIRED,
            CollectiveOfferDisplayedStatus.ENDED,
            CollectiveOfferDisplayedStatus.CANCELLED,
            CollectiveOfferDisplayedStatus.ARCHIVED,
        ],
    )
    def test_filter_by_multiple_status(self, app, status):
        # Given
        booked_offer = create_collective_offer_by_status(CollectiveOfferDisplayedStatus.BOOKED)
        _pending_offer = create_collective_offer_by_status(CollectiveOfferDisplayedStatus.PENDING)

        base_query = CollectiveOffer.query

        # When
        filtered_booked_query = _filter_collective_offers_by_statuses(
            base_query, [CollectiveOfferDisplayedStatus.BOOKED.value, status.value]
        )

        # Then
        assert filtered_booked_query.count() == 1
        assert filtered_booked_query.first() == booked_offer

    @pytest.mark.parametrize(
        "status",
        [
            # CollectiveOfferDisplayedStatus.PENDING,
            CollectiveOfferDisplayedStatus.REJECTED,
            CollectiveOfferDisplayedStatus.PREBOOKED,
            CollectiveOfferDisplayedStatus.BOOKED,
            CollectiveOfferDisplayedStatus.EXPIRED,
            CollectiveOfferDisplayedStatus.ENDED,
            CollectiveOfferDisplayedStatus.ARCHIVED,
            CollectiveOfferDisplayedStatus.ACTIVE,
        ],
    )
    def test_filter_by_status(self, app, status):
        # Given
        offer = create_collective_offer_by_status(status)
        _pending_offer = create_collective_offer_by_status(CollectiveOfferDisplayedStatus.PENDING)

        base_query = CollectiveOffer.query

        # When
        filtered_booked_query = _filter_collective_offers_by_statuses(base_query, [status.value])

        # Then
        assert filtered_booked_query.count() == 1
        assert filtered_booked_query.first() == offer

    @pytest.mark.parametrize(
        "status",
        [
            # CollectiveOfferDisplayedStatus.PENDING,
            CollectiveOfferDisplayedStatus.REJECTED,
            CollectiveOfferDisplayedStatus.PREBOOKED,
            CollectiveOfferDisplayedStatus.BOOKED,
            CollectiveOfferDisplayedStatus.EXPIRED,
            CollectiveOfferDisplayedStatus.ENDED,
            CollectiveOfferDisplayedStatus.ARCHIVED,
            CollectiveOfferDisplayedStatus.ACTIVE,
        ],
    )
    def test_filter_pending(self, app, status):
        _other_offer = create_collective_offer_by_status(status)
        pending_offer = create_collective_offer_by_status(CollectiveOfferDisplayedStatus.PENDING)

        base_query = CollectiveOffer.query
        filtered_booked_query = _filter_collective_offers_by_statuses(base_query, ["PENDING"])

        assert filtered_booked_query.count() == 1
        assert filtered_booked_query.first() == pending_offer

    def test_all_filters(self, app):
        all_status = [
            CollectiveOfferDisplayedStatus.PENDING,
            CollectiveOfferDisplayedStatus.REJECTED,
            CollectiveOfferDisplayedStatus.PREBOOKED,
            CollectiveOfferDisplayedStatus.BOOKED,
            CollectiveOfferDisplayedStatus.EXPIRED,
            CollectiveOfferDisplayedStatus.ENDED,
            CollectiveOfferDisplayedStatus.ARCHIVED,
            CollectiveOfferDisplayedStatus.ACTIVE,
        ]

        all_offers_by_status = {s.value: create_collective_offer_by_status(s) for s in all_status}

        base_query = CollectiveOffer.query
        all_status_values = [enum.value for enum in all_status]

        # When
        filtered_query = _filter_collective_offers_by_statuses(base_query, all_status_values)

        # Then
        filtered_query_ids = {order.id for order in filtered_query}
        assert filtered_query_ids == {order.id for order in all_offers_by_status.values()}

        assert filtered_query.count() == 8

    @pytest.mark.parametrize(
        "status",
        [
            CollectiveOfferDisplayedStatus.PENDING,
            CollectiveOfferDisplayedStatus.REJECTED,
            CollectiveOfferDisplayedStatus.PREBOOKED,
            CollectiveOfferDisplayedStatus.BOOKED,
            CollectiveOfferDisplayedStatus.EXPIRED,
            CollectiveOfferDisplayedStatus.ENDED,
            CollectiveOfferDisplayedStatus.ARCHIVED,
        ],
    )
    def test_filter_statuses_but_one(self, app, status):
        # # Given
        all_status = [
            CollectiveOfferDisplayedStatus.PENDING,
            CollectiveOfferDisplayedStatus.REJECTED,
            CollectiveOfferDisplayedStatus.PREBOOKED,
            CollectiveOfferDisplayedStatus.BOOKED,
            CollectiveOfferDisplayedStatus.EXPIRED,
            CollectiveOfferDisplayedStatus.ENDED,
            CollectiveOfferDisplayedStatus.ARCHIVED,
        ]

        all_offers_by_status = {s.value: create_collective_offer_by_status(s) for s in all_status}
        _offer_not_filtered = all_offers_by_status[status.value]

        filtered_status = [status_enum.value for status_enum in all_status if status_enum != status]

        base_query = CollectiveOffer.query

        # When
        filtered_query = _filter_collective_offers_by_statuses(base_query, filtered_status)

        # Then
        assert base_query.count() == 7

        filtered_query_ids = {order.id for order in filtered_query}

        assert filtered_query_ids == {
            order.id for order_status, order in all_offers_by_status.items() if status.value != order_status
        }
        assert filtered_query.count() == 6

    def test_filter_with_no_statuses(self, app):
        # Given
        booked_offer = educational_factories.CollectiveOfferFactory(
            validation=offer_mixin.OfferValidationStatus.APPROVED
        )
        stock = educational_factories.CollectiveStockFactory(collectiveOffer=booked_offer)
        _booking = educational_factories.CollectiveBookingFactory(
            collectiveStock=stock, status=CollectiveBookingStatus.CONFIRMED
        )

        _pending_offer = educational_factories.CollectiveOfferFactory(
            validation=offer_mixin.OfferValidationStatus.PENDING
        )

        base_query = CollectiveOffer.query
        # When
        filtered_nostatus_query = _filter_collective_offers_by_statuses(base_query, [])

        # Then
        assert filtered_nostatus_query.count() == 2

    def test_filter_with_statuses_has_none(self, app):
        # Given
        booked_offer = educational_factories.CollectiveOfferFactory(
            validation=offer_mixin.OfferValidationStatus.APPROVED
        )
        stock = educational_factories.CollectiveStockFactory(collectiveOffer=booked_offer)
        _booking = educational_factories.CollectiveBookingFactory(
            collectiveStock=stock, status=CollectiveBookingStatus.CONFIRMED
        )

        pending_offer = educational_factories.CollectiveOfferFactory(
            validation=offer_mixin.OfferValidationStatus.PENDING
        )

        base_query = CollectiveOffer.query
        # When
        filtered_nostatus_query = _filter_collective_offers_by_statuses(base_query, None)

        # Then
        assert filtered_nostatus_query.count() == 2
        assert set(filtered_nostatus_query.all()) == {pending_offer, booked_offer}
