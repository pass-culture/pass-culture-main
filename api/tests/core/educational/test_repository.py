from datetime import datetime
from datetime import timedelta

import pytest

from pcapi.core.categories.models import EacFormat
from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import models
from pcapi.core.educational import repository as educational_repository
from pcapi.core.educational import schemas
from pcapi.core.educational.factories import create_collective_offer_by_status
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.providers import factories as providers_factories
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import factories as users_factories
from pcapi.models import db
from pcapi.models import offer_mixin
from pcapi.utils import db as db_utils


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
        assert expected_booking_recap.status is models.CollectiveBookingStatus.USED
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
            status_filter=models.CollectiveBookingStatusFilter.VALIDATED,
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
            status_filter=models.CollectiveBookingStatusFilter.REIMBURSED,
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
        user_offerer = offerers_factories.NewUserOffererFactory()
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
            collectiveStock__startDatetime=event_date,
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
            collectiveOffer=collective_offer_in_cayenne, startDatetime=cayenne_event_datetime
        )
        cayenne_collective_booking = educational_factories.CollectiveBookingFactory(collectiveStock=stock_in_cayenne)

        offer_in_mayotte = educational_factories.CollectiveOfferFactory(
            venue__postalCode="97600", venue__managingOfferer=user_offerer.offerer
        )
        mayotte_event_datetime = datetime(2022, 4, 20, 22, 0)
        stock_in_mayotte = educational_factories.CollectiveStockFactory(
            collectiveOffer=offer_in_mayotte, startDatetime=mayotte_event_datetime
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
        booking_status_filter = models.CollectiveBookingStatusFilter.BOOKED
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
    ALL_STATUS = set(models.CollectiveOfferDisplayedStatus)

    ALL_STATUS_WITHOUT_NEW = ALL_STATUS - {
        models.CollectiveOfferDisplayedStatus.CANCELLED,
        models.CollectiveOfferDisplayedStatus.REIMBURSED,
    }

    # The HIDDEN filter is not relevant for a models.CollectiveOffer
    ALL_STATUS_WITHOUT_INACTIVE = ALL_STATUS - {models.CollectiveOfferDisplayedStatus.HIDDEN}

    def test_filter_by_booked_status(self):
        booked_offer = create_collective_offer_by_status(models.CollectiveOfferDisplayedStatus.BOOKED)
        pending_offer = create_collective_offer_by_status(models.CollectiveOfferDisplayedStatus.UNDER_REVIEW)

        base_query = db.session.query(models.CollectiveOffer)
        filtered_booked_query = educational_repository.filter_collective_offers_by_statuses(
            base_query, [models.CollectiveOfferDisplayedStatus.BOOKED]
        )

        assert filtered_booked_query.one() == booked_offer

        filtered_pending_query = educational_repository.filter_collective_offers_by_statuses(
            base_query, [models.CollectiveOfferDisplayedStatus.UNDER_REVIEW]
        )

        assert filtered_pending_query.count() == 1
        assert filtered_pending_query.first() == pending_offer

    @pytest.mark.parametrize("status", ALL_STATUS - set([models.CollectiveOfferDisplayedStatus.UNDER_REVIEW]))
    def test_filter_by_multiple_status(self, status):
        booked_offer = create_collective_offer_by_status(models.CollectiveOfferDisplayedStatus.BOOKED)
        _pending_offer = create_collective_offer_by_status(models.CollectiveOfferDisplayedStatus.UNDER_REVIEW)

        filtered_booked_query = educational_repository.filter_collective_offers_by_statuses(
            db.session.query(models.CollectiveOffer), [models.CollectiveOfferDisplayedStatus.BOOKED, status]
        )

        assert filtered_booked_query.one() == booked_offer

    @pytest.mark.parametrize(
        "status", ALL_STATUS_WITHOUT_INACTIVE - set([models.CollectiveOfferDisplayedStatus.UNDER_REVIEW])
    )
    def test_filter_by_status(self, status):
        offer = create_collective_offer_by_status(status)
        _pending_offer = create_collective_offer_by_status(models.CollectiveOfferDisplayedStatus.UNDER_REVIEW)

        filtered_booked_query = educational_repository.filter_collective_offers_by_statuses(
            db.session.query(models.CollectiveOffer), [status]
        )

        assert filtered_booked_query.one() == offer

    @pytest.mark.parametrize(
        "status", ALL_STATUS_WITHOUT_INACTIVE - set([models.CollectiveOfferDisplayedStatus.UNDER_REVIEW])
    )
    def test_filter_pending(self, status):
        _other_offer = create_collective_offer_by_status(status)
        pending_offer = create_collective_offer_by_status(models.CollectiveOfferDisplayedStatus.UNDER_REVIEW)

        filtered_booked_query = educational_repository.filter_collective_offers_by_statuses(
            db.session.query(models.CollectiveOffer), [models.CollectiveOfferDisplayedStatus.UNDER_REVIEW]
        )

        assert filtered_booked_query.one() == pending_offer

    @pytest.mark.parametrize(
        "status", ALL_STATUS_WITHOUT_INACTIVE - set([models.CollectiveOfferDisplayedStatus.PUBLISHED])
    )
    def test_filter_active(self, status):
        other_offer = create_collective_offer_by_status(status)
        published_offer = create_collective_offer_by_status(models.CollectiveOfferDisplayedStatus.PUBLISHED)

        base_query = db.session.query(models.CollectiveOffer)
        filtered_query = educational_repository.filter_collective_offers_by_statuses(
            base_query, [models.CollectiveOfferDisplayedStatus.PUBLISHED]
        )
        assert filtered_query.one() == published_offer

        filtered_out_query = educational_repository.filter_collective_offers_by_statuses(base_query, [status])
        assert filtered_out_query.one() == other_offer

    def test_all_filters(self):
        all_offers = [create_collective_offer_by_status(s) for s in self.ALL_STATUS_WITHOUT_INACTIVE]

        filtered_query = educational_repository.filter_collective_offers_by_statuses(
            db.session.query(models.CollectiveOffer), list(self.ALL_STATUS_WITHOUT_INACTIVE)
        )
        filtered_query_ids = {offer.id for offer in filtered_query}

        assert filtered_query_ids == {offer.id for offer in all_offers}
        assert filtered_query.count() == len(self.ALL_STATUS_WITHOUT_INACTIVE)

    def test_filter_expired_do_not_retrieve_ended(self):
        _ended_offer = create_collective_offer_by_status(models.CollectiveOfferDisplayedStatus.ENDED)
        expired_offer = create_collective_offer_by_status(models.CollectiveOfferDisplayedStatus.EXPIRED)

        base_query = db.session.query(models.CollectiveOffer)
        filtered_query = educational_repository.filter_collective_offers_by_statuses(
            base_query, [models.CollectiveOfferDisplayedStatus.EXPIRED]
        )

        assert base_query.count() == 2
        assert filtered_query.one() == expired_offer

    @pytest.mark.parametrize("status", ALL_STATUS_WITHOUT_INACTIVE)
    def test_filter_statuses_but_one(self, status):
        all_offers_status_by_id = {create_collective_offer_by_status(s).id: s for s in self.ALL_STATUS_WITHOUT_INACTIVE}

        filtered_status = [status_enum for status_enum in self.ALL_STATUS_WITHOUT_INACTIVE if status_enum != status]

        base_query = db.session.query(models.CollectiveOffer)

        filtered_query = educational_repository.filter_collective_offers_by_statuses(base_query, filtered_status)

        assert base_query.count() == len(self.ALL_STATUS_WITHOUT_INACTIVE)

        filtered_query_status = {all_offers_status_by_id[offer.id] for offer in filtered_query}

        assert filtered_query_status == {
            offer_status for offer_status in all_offers_status_by_id.values() if status != offer_status
        }
        assert filtered_query.count() == len(self.ALL_STATUS_WITHOUT_INACTIVE) - 1

    def test_filter_with_no_statuses(self):
        booked_offer = educational_factories.CollectiveOfferFactory(
            validation=offer_mixin.OfferValidationStatus.APPROVED
        )
        stock = educational_factories.CollectiveStockFactory(collectiveOffer=booked_offer)
        _booking = educational_factories.CollectiveBookingFactory(
            collectiveStock=stock, status=models.CollectiveBookingStatus.CONFIRMED
        )

        pending_offer = educational_factories.CollectiveOfferFactory(
            validation=offer_mixin.OfferValidationStatus.PENDING
        )

        filtered_nostatus_query = educational_repository.filter_collective_offers_by_statuses(
            db.session.query(models.CollectiveOffer), []
        )

        assert filtered_nostatus_query.count() == 2
        assert set(filtered_nostatus_query.all()) == {pending_offer, booked_offer}

    def test_filter_with_statuses_none(self):
        booked_offer = educational_factories.CollectiveOfferFactory(
            validation=offer_mixin.OfferValidationStatus.APPROVED
        )
        stock = educational_factories.CollectiveStockFactory(collectiveOffer=booked_offer)
        _booking = educational_factories.CollectiveBookingFactory(
            collectiveStock=stock, status=models.CollectiveBookingStatus.CONFIRMED
        )

        pending_offer = educational_factories.CollectiveOfferFactory(
            validation=offer_mixin.OfferValidationStatus.PENDING
        )

        filtered_nostatus_query = educational_repository.filter_collective_offers_by_statuses(
            db.session.query(models.CollectiveOffer), None
        )

        assert filtered_nostatus_query.count() == 2
        assert set(filtered_nostatus_query.all()) == {pending_offer, booked_offer}

    def test_filter_inactive_offer_due_to_booking_date_passed(self):
        offer = educational_factories.CollectiveOfferFactory()

        past = datetime.utcnow() - timedelta(days=2)
        _stock = educational_factories.CollectiveStockFactory(bookingLimitDatetime=past, collectiveOffer=offer)

        base_query = db.session.query(models.CollectiveOffer)
        filtered_inactive_query = educational_repository.filter_collective_offers_by_statuses(
            base_query, [models.CollectiveOfferDisplayedStatus.EXPIRED]
        )

        filtered_active_query = educational_repository.filter_collective_offers_by_statuses(
            base_query, [models.CollectiveOfferDisplayedStatus.PUBLISHED]
        )

        assert filtered_inactive_query.one() == offer
        assert filtered_active_query.count() == 0

    def test_filter_out_active_offer_due_to_booking_date_passed(self):
        offer = educational_factories.CollectiveOfferFactory()
        futur = datetime.utcnow() + timedelta(days=2)
        _stock = educational_factories.CollectiveStockFactory(bookingLimitDatetime=futur, collectiveOffer=offer)

        base_query = db.session.query(models.CollectiveOffer)
        filtered_inactive_query = educational_repository.filter_collective_offers_by_statuses(
            base_query, [models.CollectiveOfferDisplayedStatus.EXPIRED]
        )

        filtered_active_query = educational_repository.filter_collective_offers_by_statuses(
            base_query, [models.CollectiveOfferDisplayedStatus.PUBLISHED]
        )

        assert filtered_inactive_query.count() == 0
        assert filtered_active_query.one() == offer

    def test_reimbursed_status(self):
        create_collective_offer_by_status(models.CollectiveOfferDisplayedStatus.REIMBURSED)

        filtered_query = educational_repository.filter_collective_offers_by_statuses(
            db.session.query(models.CollectiveOffer), [models.CollectiveOfferDisplayedStatus.ENDED]
        )

        assert filtered_query.count() == 0

    def test_hidden_status(self):
        create_collective_offer_by_status(models.CollectiveOfferDisplayedStatus.HIDDEN)
        create_collective_offer_by_status(models.CollectiveOfferDisplayedStatus.UNDER_REVIEW)

        filtered_query = educational_repository.filter_collective_offers_by_statuses(
            db.session.query(models.CollectiveOffer), [models.CollectiveOfferDisplayedStatus.HIDDEN]
        )

        # The HIDDEN filter is not relevant for a models.CollectiveOffer, it is only used for CollectiveOfferTemplate
        assert filtered_query.count() == 0

    @pytest.mark.parametrize("status", ALL_STATUS_WITHOUT_INACTIVE)
    def test_filter_each_statuses(self, status):
        offer = educational_factories.create_collective_offer_by_status(status)

        base_query = db.session.query(models.CollectiveOffer)
        filtered_query = educational_repository.filter_collective_offers_by_statuses(base_query, statuses=[status])
        assert filtered_query.one() == offer

        statuses_no_result = set(models.CollectiveOfferDisplayedStatus) - {status}
        filtered_query = educational_repository.filter_collective_offers_by_statuses(
            base_query, statuses=statuses_no_result
        )
        assert filtered_query.count() == 0


class HasCollectiveOffersForProgramAndVenueIdsTest:
    def test_has_collective_offers_for_program_and_venueids_test(self, app):
        program = educational_factories.EducationalInstitutionProgramFactory(name="program")
        other_program = educational_factories.EducationalInstitutionProgramFactory(name="other_program")

        venue = offerers_factories.VenueFactory()
        other_venue = offerers_factories.VenueFactory()

        venue_not_in_program_anymore = offerers_factories.VenueFactory()

        institution = educational_factories.EducationalInstitutionFactory(
            programAssociations=[
                educational_factories.EducationalInstitutionProgramAssociationFactory(
                    program=program,
                )
            ]
        )
        other_institution = educational_factories.EducationalInstitutionFactory(
            programAssociations=[
                educational_factories.EducationalInstitutionProgramAssociationFactory(
                    program=other_program,
                )
            ]
        )

        institution_not_in_program_anymore = educational_factories.EducationalInstitutionFactory(
            programAssociations=[
                educational_factories.EducationalInstitutionProgramAssociationFactory(
                    program=program,
                    timespan=db_utils.make_timerange(start=datetime(2022, 1, 1), end=datetime(2022, 1, 31)),
                )
            ]
        )

        educational_factories.CollectiveOfferFactory(venue=venue, institution=institution)
        educational_factories.CollectiveOfferFactory(
            venue=venue_not_in_program_anymore, institution=institution_not_in_program_anymore
        )
        educational_factories.CollectiveOfferFactory(venue=venue)
        educational_factories.CollectiveOfferFactory(venue=other_venue, institution=other_institution)

        venue_id = venue.id

        with assert_num_queries(1):
            assert educational_repository.has_collective_offers_for_program_and_venue_ids("program", [venue_id]) == True

        assert (
            educational_repository.has_collective_offers_for_program_and_venue_ids("other_program", [venue.id]) == False
        )

        assert (
            educational_repository.has_collective_offers_for_program_and_venue_ids("program", [other_venue.id]) == False
        )

        assert (
            educational_repository.has_collective_offers_for_program_and_venue_ids(
                "program", [venue_not_in_program_anymore.id]
            )
            == False
        )

    def test_has_collective_offers_for_program_after_leaving_program(self, app):
        program = educational_factories.EducationalInstitutionProgramFactory(name="program")

        venue = offerers_factories.VenueFactory()
        venue_used_by_leaving_institution = offerers_factories.VenueFactory()

        leaving_institution = educational_factories.EducationalInstitutionFactory()
        institution = educational_factories.EducationalInstitutionFactory()

        previous_year = datetime.utcnow() - timedelta(days=365)
        two_years_ago = datetime.utcnow() - timedelta(days=365 * 2)

        educational_factories.EducationalInstitutionProgramAssociationFactory(
            institution=leaving_institution,
            program=program,
            timespan=db_utils.make_timerange(two_years_ago, previous_year),
        )

        educational_factories.EducationalInstitutionProgramAssociationFactory(
            institution=institution, program=program, timespan=db_utils.make_timerange(previous_year, None)
        )

        educational_factories.CollectiveOfferFactory(venue=venue, institution=institution)

        educational_factories.CollectiveOfferFactory(
            venue=venue_used_by_leaving_institution, institution=leaving_institution
        )

        assert educational_repository.has_collective_offers_for_program_and_venue_ids("program", [venue.id]) == True
        assert (
            educational_repository.has_collective_offers_for_program_and_venue_ids(
                "program", [venue_used_by_leaving_institution.id]
            )
            == False
        )


class OffererHasOngoingCollectiveBookingsTest:
    @pytest.mark.parametrize(
        "factory",
        [
            educational_factories.ConfirmedCollectiveBookingFactory,
            educational_factories.PendingCollectiveBookingFactory,
        ],
    )
    def test_has_bookings(self, app, factory):
        offerer = offerers_factories.OffererFactory()
        factory(offerer=offerer)
        educational_factories.ReimbursedCollectiveBookingFactory(offerer=offerer)

        offerer_id = offerer.id
        with assert_num_queries(1):
            assert educational_repository.offerer_has_ongoing_collective_bookings(offerer_id=offerer_id) is True

    @pytest.mark.parametrize(
        "factory",
        [
            educational_factories.ConfirmedCollectiveBookingFactory,
            educational_factories.PendingCollectiveBookingFactory,
            educational_factories.UsedCollectiveBookingFactory,
        ],
    )
    def test_has_bookings_include_used(self, app, factory):
        offerer = offerers_factories.OffererFactory()
        factory(offerer=offerer)
        educational_factories.ReimbursedCollectiveBookingFactory(offerer=offerer)

        offerer_id = offerer.id
        with assert_num_queries(1):
            assert (
                educational_repository.offerer_has_ongoing_collective_bookings(offerer_id=offerer_id, include_used=True)
                is True
            )

    def test_has_no_booking(self, app):
        offerer = offerers_factories.OffererFactory()
        educational_factories.ReimbursedCollectiveBookingFactory(offerer=offerer)
        educational_factories.CancelledCollectiveBookingFactory(offerer=offerer)
        educational_factories.UsedCollectiveBookingFactory(offerer=offerer)

        offerer_id = offerer.id
        with assert_num_queries(1):
            assert educational_repository.offerer_has_ongoing_collective_bookings(offerer_id=offerer_id) is False


class ListPublicCollectiveOffersTest:
    def test_should_return_offers_for_provider(self, app):
        provider = providers_factories.ProviderFactory()
        offer = educational_factories.create_collective_offer_by_status(
            models.CollectiveOfferDisplayedStatus.PUBLISHED, provider=provider
        )

        other_provider = providers_factories.ProviderFactory()
        educational_factories.create_collective_offer_by_status(
            models.CollectiveOfferDisplayedStatus.PUBLISHED, provider=other_provider
        )  # another offer from different provider

        offers = educational_repository.list_public_collective_offers(required_id=provider.id)

        assert len(offers) == 1
        assert offers[0].id == offer.id

    def test_should_filter_by_status(self, app):
        # TODO: (rprasquier) adapt this test to use the new status on the public API
        provider = providers_factories.ProviderFactory()
        approved_offer = educational_factories.create_collective_offer_by_status(
            models.CollectiveOfferDisplayedStatus.PUBLISHED, provider=provider
        )

        educational_factories.create_collective_offer_by_status(
            models.CollectiveOfferDisplayedStatus.UNDER_REVIEW, provider=provider
        )

        offers = educational_repository.list_public_collective_offers(
            required_id=provider.id, status=offer_mixin.CollectiveOfferStatus.ACTIVE
        )

        assert len(offers) == 1
        assert offers[0].id == approved_offer.id

    def test_should_filter_by_venue(self, app):
        provider = providers_factories.ProviderFactory()
        venue = offerers_factories.VenueFactory()
        offer = educational_factories.create_collective_offer_by_status(
            models.CollectiveOfferDisplayedStatus.PUBLISHED, provider=provider, venue=venue
        )

        other_venue = offerers_factories.VenueFactory()
        educational_factories.create_collective_offer_by_status(
            models.CollectiveOfferDisplayedStatus.PUBLISHED, provider=provider, venue=other_venue
        )  # another offer from same provider

        offers = educational_repository.list_public_collective_offers(required_id=provider.id, venue_id=venue.id)

        assert len(offers) == 1
        assert offers[0].id == offer.id

    def test_should_filter_by_date_range(self, app):
        provider = providers_factories.ProviderFactory()
        start_date = datetime.utcnow() - timedelta(days=2)
        end_date = datetime.utcnow() + timedelta(days=2)

        stock_in_range = educational_factories.CollectiveStockFactory(
            startDatetime=datetime.utcnow(), collectiveOffer__provider=provider
        )

        educational_factories.CollectiveStockFactory(
            startDatetime=datetime.utcnow() + timedelta(days=3), collectiveOffer__provider=provider
        )

        offers = educational_repository.list_public_collective_offers(
            required_id=provider.id,
            period_beginning_date=start_date.isoformat(),
            period_ending_date=end_date.isoformat(),
        )

        assert len(offers) == 1
        assert offers[0].id == stock_in_range.collectiveOffer.id

    def test_should_filter_by_ids(self, app):
        provider = providers_factories.ProviderFactory()
        offer1 = educational_factories.create_collective_offer_by_status(
            models.CollectiveOfferDisplayedStatus.PUBLISHED, provider=provider
        )
        offer2 = educational_factories.create_collective_offer_by_status(
            models.CollectiveOfferDisplayedStatus.PUBLISHED, provider=provider
        )
        educational_factories.create_collective_offer_by_status(
            models.CollectiveOfferDisplayedStatus.PUBLISHED, provider=provider
        )  # another offer

        offers = educational_repository.list_public_collective_offers(
            required_id=provider.id, ids=[offer1.id, offer2.id]
        )

        assert len(offers) == 2
        assert {offer.id for offer in offers} == {offer1.id, offer2.id}

    def test_should_respect_limit(self, app):
        provider = providers_factories.ProviderFactory()
        for _ in range(3):
            educational_factories.create_collective_offer_by_status(
                models.CollectiveOfferDisplayedStatus.PUBLISHED, provider=provider
            )

        offers = educational_repository.list_public_collective_offers(required_id=provider.id, limit=2)

        assert len(offers) == 2


@pytest.fixture(name="admin_user", scope="function")
def admin_user_fixture():
    return users_factories.AdminFactory()


class GetFilteredCollectiveOffersTest:
    def test_get_prebooked_collective_offers(self):
        user_offerer = offerers_factories.UserOffererFactory()
        collective_offer_prebooked = educational_factories.CollectiveOfferFactory(
            venue__managingOfferer=user_offerer.offerer
        )
        collective_stock_prebooked = educational_factories.CollectiveStockFactory(
            collectiveOffer=collective_offer_prebooked
        )
        educational_factories.CollectiveBookingFactory(
            collectiveStock=collective_stock_prebooked,
            status=models.CollectiveBookingStatus.CANCELLED.value,
        )
        educational_factories.CollectiveBookingFactory(
            collectiveStock=collective_stock_prebooked,
            status=models.CollectiveBookingStatus.PENDING.value,
        )

        collective_offer_cancelled = educational_factories.CollectiveOfferFactory(
            venue__managingOfferer=user_offerer.offerer
        )
        collective_stock_cancelled = educational_factories.CollectiveStockFactory(
            collectiveOffer=collective_offer_cancelled
        )
        educational_factories.CollectiveBookingFactory(
            collectiveStock=collective_stock_cancelled,
            status=models.CollectiveBookingStatus.PENDING.value,
        )
        educational_factories.CollectiveBookingFactory(
            collectiveStock=collective_stock_cancelled,
            status=models.CollectiveBookingStatus.CANCELLED.value,
        )

        offers = educational_repository.get_collective_offers_by_filters(
            filters=schemas.CollectiveOffersFilter(
                user_id=user_offerer.userId,
                user_is_admin=False,
                statuses=[models.CollectiveOfferDisplayedStatus.PREBOOKED],
            )
        )
        assert offers.all() == [collective_offer_prebooked]

    def test_get_ended_collective_offers(self):
        user_offerer = offerers_factories.UserOffererFactory()
        collective_offer_ended = educational_factories.CollectiveOfferFactory(
            venue__managingOfferer=user_offerer.offerer
        )
        collective_stock_ended = educational_factories.CollectiveStockFactory(
            collectiveOffer=collective_offer_ended,
            startDatetime=datetime(year=2000, month=1, day=1),
        )
        educational_factories.CollectiveBookingFactory(
            collectiveStock=collective_stock_ended,
            status=models.CollectiveBookingStatus.USED.value,
        )

        offers = educational_repository.get_collective_offers_by_filters(
            filters=schemas.CollectiveOffersFilter(
                user_id=user_offerer.userId,
                user_is_admin=False,
                statuses=[models.CollectiveOfferDisplayedStatus.ENDED],
            )
        )
        assert offers.all() == [collective_offer_ended]

    def test_get_collective_offers_with_formats(self):
        user_offerer = offerers_factories.UserOffererFactory()
        collective_offer = educational_factories.CollectiveOfferFactory(
            venue__managingOfferer=user_offerer.offerer, formats=[EacFormat.CONCERT]
        )
        educational_factories.CollectiveOfferFactory(
            venue__managingOfferer=user_offerer.offerer,
            formats=[EacFormat.CONFERENCE_RENCONTRE],
        )

        offers = educational_repository.get_collective_offers_by_filters(
            filters=schemas.CollectiveOffersFilter(
                user_id=user_offerer.userId,
                user_is_admin=False,
                formats=[EacFormat.CONCERT],
            )
        )
        assert offers.one() == collective_offer

    def test_get_collective_offers_archived(self):
        user_offerer = offerers_factories.UserOffererFactory()

        _collective_offer_unarchived = educational_factories.CollectiveOfferFactory(
            venue__managingOfferer=user_offerer.offerer
        )
        collective_offer_archived = educational_factories.CollectiveOfferFactory(
            venue__managingOfferer=user_offerer.offerer,
            isActive=False,
            dateArchived=datetime(year=2000, month=1, day=1),
        )

        offers = educational_repository.get_collective_offers_by_filters(
            filters=schemas.CollectiveOffersFilter(
                user_id=user_offerer.userId,
                user_is_admin=False,
                statuses=[models.CollectiveOfferDisplayedStatus.ARCHIVED],
            )
        )
        assert offers.one() == collective_offer_archived

    def test_get_collective_offers_draft(self):
        user_offerer = offerers_factories.UserOffererFactory()

        collective_offer_draft = educational_factories.CollectiveOfferFactory(
            validation=offer_mixin.OfferValidationStatus.DRAFT.value,
            venue__managingOfferer=user_offerer.offerer,
        )

        offers = educational_repository.get_collective_offers_by_filters(
            filters=schemas.CollectiveOffersFilter(user_id=user_offerer.userId, user_is_admin=False)
        )
        with assert_num_queries(1):
            assert offers.one() == collective_offer_draft

        offers = educational_repository.get_collective_offers_by_filters(
            filters=schemas.CollectiveOffersFilter(
                user_id=user_offerer.userId,
                user_is_admin=False,
                statuses=[models.CollectiveOfferDisplayedStatus.DRAFT],
            )
        )
        with assert_num_queries(1):
            assert offers.one() == collective_offer_draft

    def test_get_collective_offers_expired(self):
        user_offerer = offerers_factories.UserOffererFactory()
        now = datetime.utcnow()
        future = now + timedelta(days=5)
        past = now - timedelta(days=2)

        # expired offer without booking
        collective_offer_expired = educational_factories.CollectiveOfferFactory(
            validation=offer_mixin.OfferValidationStatus.APPROVED.value,
            venue__managingOfferer=user_offerer.offerer,
        )

        educational_factories.CollectiveStockFactory(
            collectiveOffer=collective_offer_expired,
            startDatetime=future,
            bookingLimitDatetime=past,
        )

        # expired offer with pending booking
        collective_offer_prebooked_expired = educational_factories.CollectiveOfferFactory(
            validation=offer_mixin.OfferValidationStatus.APPROVED.value,
            venue__managingOfferer=user_offerer.offerer,
        )

        collective_stock_prebooked_expired = educational_factories.CollectiveStockFactory(
            collectiveOffer=collective_offer_prebooked_expired,
            startDatetime=future,
            bookingLimitDatetime=past,
        )

        educational_factories.CollectiveBookingFactory(
            collectiveStock=collective_stock_prebooked_expired,
            confirmationLimitDate=past,
            status=models.CollectiveBookingStatus.CANCELLED.value,
            cancellationReason=models.CollectiveBookingCancellationReasons.EXPIRED.value,
        )

        offers = educational_repository.get_collective_offers_by_filters(
            filters=schemas.CollectiveOffersFilter(
                user_id=user_offerer.userId,
                user_is_admin=False,
                statuses=[models.CollectiveOfferDisplayedStatus.EXPIRED],
            )
        )
        offers_list = offers.all()
        assert len(offers_list) == 2
        assert set(offers_list) == {
            collective_offer_expired,
            collective_offer_prebooked_expired,
        }

    @pytest.mark.parametrize(
        "offer_status",
        set(models.CollectiveOfferDisplayedStatus) - {models.CollectiveOfferDisplayedStatus.HIDDEN},
    )
    def test_filter_each_status(self, admin_user, offer_status):
        offer = educational_factories.create_collective_offer_by_status(offer_status)

        result = educational_repository.get_collective_offers_by_filters(
            filters=schemas.CollectiveOffersFilter(
                user_id=admin_user.id,
                user_is_admin=True,
                statuses=[offer_status],
            )
        )
        assert result.one() == offer

        statuses_no_result = set(models.CollectiveOfferDisplayedStatus) - {offer_status}
        result = educational_repository.get_collective_offers_by_filters(
            filters=schemas.CollectiveOffersFilter(
                user_id=admin_user.id, user_is_admin=True, statuses=statuses_no_result
            )
        )
        assert result.count() == 0

    def test_filter_hidden(self, admin_user):
        for status in models.CollectiveOfferDisplayedStatus:
            educational_factories.create_collective_offer_by_status(status)

        # The HIDDEN filter does not correspond to any collective offer (only templates)
        result = educational_repository.get_collective_offers_by_filters(
            filters=schemas.CollectiveOffersFilter(
                user_id=admin_user.id,
                user_is_admin=True,
                statuses=[models.CollectiveOfferDisplayedStatus.HIDDEN],
            )
        )
        assert result.count() == 0

    def test_filter_location_type(self, admin_user):
        offer_school = educational_factories.CollectiveOfferOnSchoolLocationFactory()
        offer_address = educational_factories.CollectiveOfferOnOtherAddressLocationFactory()
        offer_to_be_defined = educational_factories.CollectiveOfferOnToBeDefinedLocationFactory()

        result = educational_repository.get_collective_offers_by_filters(
            filters=schemas.CollectiveOffersFilter(
                user_id=admin_user.id, user_is_admin=True, location_type=models.CollectiveLocationType.SCHOOL
            )
        )
        assert result.one() == offer_school

        result = educational_repository.get_collective_offers_by_filters(
            filters=schemas.CollectiveOffersFilter(
                user_id=admin_user.id, user_is_admin=True, location_type=models.CollectiveLocationType.ADDRESS
            )
        )
        assert result.one() == offer_address

        result = educational_repository.get_collective_offers_by_filters(
            filters=schemas.CollectiveOffersFilter(
                user_id=admin_user.id, user_is_admin=True, location_type=models.CollectiveLocationType.TO_BE_DEFINED
            )
        )
        assert result.one() == offer_to_be_defined

    def test_filter_offerer_address(self, admin_user):
        oa = offerers_factories.OffererAddressFactory()
        offer = educational_factories.CollectiveOfferOnOtherAddressLocationFactory(offererAddress=oa)
        educational_factories.CollectiveOfferOnOtherAddressLocationFactory()
        educational_factories.CollectiveOfferOnSchoolLocationFactory()
        educational_factories.CollectiveOfferOnToBeDefinedLocationFactory()

        result = educational_repository.get_collective_offers_by_filters(
            filters=schemas.CollectiveOffersFilter(user_id=admin_user.id, user_is_admin=True, offerer_address_id=oa.id)
        )
        assert result.one() == offer


class GetCollectiveOffersTemplateByFiltersTest:
    @pytest.mark.parametrize("offer_status", models.COLLECTIVE_OFFER_TEMPLATE_STATUSES)
    def test_filter_each_status(self, admin_user, offer_status):
        template = educational_factories.create_collective_offer_template_by_status(offer_status)

        result = educational_repository.get_collective_offers_template_by_filters(
            filters=schemas.CollectiveOffersFilter(user_id=admin_user.id, user_is_admin=True, statuses=[offer_status])
        )
        assert result.one() == template

        statuses_no_result = set(models.CollectiveOfferDisplayedStatus) - {offer_status}
        result = educational_repository.get_collective_offers_template_by_filters(
            filters=schemas.CollectiveOffersFilter(
                user_id=admin_user.id, user_is_admin=True, statuses=statuses_no_result
            )
        )
        assert result.count() == 0

    def test_formats_filter(self, admin_user):
        template = educational_factories.CollectiveOfferTemplateFactory(
            formats=[EacFormat.CONCERT, EacFormat.CONFERENCE_RENCONTRE]
        )
        educational_factories.CollectiveOfferTemplateFactory(formats=[EacFormat.CONFERENCE_RENCONTRE])

        result = educational_repository.get_collective_offers_template_by_filters(
            filters=schemas.CollectiveOffersFilter(
                user_id=admin_user.id, user_is_admin=True, formats=[EacFormat.CONCERT]
            )
        ).one()
        assert result.id == template.id
