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
from pcapi.utils import date as date_utils
from pcapi.utils import db as db_utils


pytestmark = pytest.mark.usefixtures("db_session")


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

        past = date_utils.get_naive_utc_now() - timedelta(days=2)
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
        futur = date_utils.get_naive_utc_now() + timedelta(days=2)
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

        previous_year = date_utils.get_naive_utc_now() - timedelta(days=365)
        two_years_ago = date_utils.get_naive_utc_now() - timedelta(days=365 * 2)

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
        provider = providers_factories.ProviderFactory()
        published_offer = educational_factories.PublishedCollectiveOfferFactory(provider=provider)
        educational_factories.UnderReviewCollectiveOfferFactory(provider=provider)

        offers = educational_repository.list_public_collective_offers(
            required_id=provider.id, displayedStatus=models.CollectiveOfferDisplayedStatus.PUBLISHED
        )

        assert len(offers) == 1
        assert offers[0].id == published_offer.id

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
        start_date = date_utils.get_naive_utc_now() - timedelta(days=2)
        end_date = date_utils.get_naive_utc_now() + timedelta(days=2)

        stock_in_range = educational_factories.CollectiveStockFactory(
            startDatetime=date_utils.get_naive_utc_now(), collectiveOffer__provider=provider
        )

        educational_factories.CollectiveStockFactory(
            startDatetime=date_utils.get_naive_utc_now() + timedelta(days=3), collectiveOffer__provider=provider
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


@pytest.fixture(name="pro_user", scope="function")
def pro_user_fixture():
    user = users_factories.ProFactory()
    offerers_factories.UserOffererFactory(user=user)
    return user


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
            filters=schemas.CollectiveOffersFilter(user_id=user_offerer.userId)
        )
        with assert_num_queries(1):
            assert offers.one() == collective_offer_draft

        offers = educational_repository.get_collective_offers_by_filters(
            filters=schemas.CollectiveOffersFilter(
                user_id=user_offerer.userId,
                statuses=[models.CollectiveOfferDisplayedStatus.DRAFT],
            )
        )
        with assert_num_queries(1):
            assert offers.one() == collective_offer_draft

    def test_get_collective_offers_expired(self):
        user_offerer = offerers_factories.UserOffererFactory()
        now = date_utils.get_naive_utc_now()
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
    def test_filter_each_status(self, pro_user, offer_status):
        offer = educational_factories.create_collective_offer_by_status(
            offer_status, venue__managingOfferer=pro_user.UserOfferers[0].offerer
        )

        result = educational_repository.get_collective_offers_by_filters(
            filters=schemas.CollectiveOffersFilter(
                user_id=pro_user.id,
                statuses=[offer_status],
            )
        )
        assert result.one() == offer

        statuses_no_result = set(models.CollectiveOfferDisplayedStatus) - {offer_status}
        result = educational_repository.get_collective_offers_by_filters(
            filters=schemas.CollectiveOffersFilter(
                user_id=pro_user.id,
                statuses=statuses_no_result,
            )
        )
        assert result.count() == 0

    def test_filter_hidden(self, pro_user):
        for status in models.CollectiveOfferDisplayedStatus:
            educational_factories.create_collective_offer_by_status(status)

        # The HIDDEN filter does not correspond to any collective offer (only templates)
        result = educational_repository.get_collective_offers_by_filters(
            filters=schemas.CollectiveOffersFilter(
                user_id=pro_user.id,
                statuses=[models.CollectiveOfferDisplayedStatus.HIDDEN],
            )
        )
        assert result.count() == 0

    def test_filter_location_type(self, pro_user):
        offer_school = educational_factories.CollectiveOfferOnSchoolLocationFactory(
            venue__managingOfferer=pro_user.UserOfferers[0].offerer
        )
        offer_address = educational_factories.CollectiveOfferOnOtherAddressLocationFactory(
            venue__managingOfferer=pro_user.UserOfferers[0].offerer
        )
        offer_to_be_defined = educational_factories.CollectiveOfferOnToBeDefinedLocationFactory(
            venue__managingOfferer=pro_user.UserOfferers[0].offerer
        )

        result = educational_repository.get_collective_offers_by_filters(
            filters=schemas.CollectiveOffersFilter(
                user_id=pro_user.id,
                location_type=models.CollectiveLocationType.SCHOOL,
            )
        )
        assert result.one() == offer_school

        result = educational_repository.get_collective_offers_by_filters(
            filters=schemas.CollectiveOffersFilter(
                user_id=pro_user.id,
                location_type=models.CollectiveLocationType.ADDRESS,
            )
        )
        assert result.one() == offer_address

        result = educational_repository.get_collective_offers_by_filters(
            filters=schemas.CollectiveOffersFilter(
                user_id=pro_user.id,
                location_type=models.CollectiveLocationType.TO_BE_DEFINED,
            )
        )
        assert result.one() == offer_to_be_defined

    def test_filter_offerer_address(self, pro_user):
        oa = offerers_factories.OffererAddressFactory()
        offer = educational_factories.CollectiveOfferOnOtherAddressLocationFactory(
            offererAddress=oa, venue__managingOfferer=pro_user.UserOfferers[0].offerer
        )
        educational_factories.CollectiveOfferOnOtherAddressLocationFactory(
            venue__managingOfferer=pro_user.UserOfferers[0].offerer
        )
        educational_factories.CollectiveOfferOnSchoolLocationFactory(
            venue__managingOfferer=pro_user.UserOfferers[0].offerer
        )
        educational_factories.CollectiveOfferOnToBeDefinedLocationFactory(
            venue__managingOfferer=pro_user.UserOfferers[0].offerer
        )

        result = educational_repository.get_collective_offers_by_filters(
            filters=schemas.CollectiveOffersFilter(
                user_id=pro_user.id,
                offerer_address_id=oa.id,
            )
        )
        assert result.one() == offer


class GetCollectiveOffersTemplateByFiltersTest:
    @pytest.mark.parametrize("offer_status", models.COLLECTIVE_OFFER_TEMPLATE_STATUSES)
    def test_filter_each_status(self, pro_user, offer_status):
        template = educational_factories.create_collective_offer_template_by_status(
            offer_status, venue__managingOfferer=pro_user.UserOfferers[0].offerer
        )

        result = educational_repository.get_collective_offers_template_by_filters(
            filters=schemas.CollectiveOffersFilter(
                user_id=pro_user.id,
                statuses=[offer_status],
            )
        )
        assert result.one() == template

        statuses_no_result = set(models.CollectiveOfferDisplayedStatus) - {offer_status}
        result = educational_repository.get_collective_offers_template_by_filters(
            filters=schemas.CollectiveOffersFilter(
                user_id=pro_user.id,
                statuses=statuses_no_result,
            )
        )
        assert result.count() == 0

    def test_formats_filter(self, pro_user):
        template = educational_factories.CollectiveOfferTemplateFactory(
            formats=[EacFormat.CONCERT, EacFormat.CONFERENCE_RENCONTRE],
            venue__managingOfferer=pro_user.UserOfferers[0].offerer,
        )
        educational_factories.CollectiveOfferTemplateFactory(
            formats=[EacFormat.CONFERENCE_RENCONTRE], venue__managingOfferer=pro_user.UserOfferers[0].offerer
        )

        result = educational_repository.get_collective_offers_template_by_filters(
            filters=schemas.CollectiveOffersFilter(
                user_id=pro_user.id,
                formats=[EacFormat.CONCERT],
            )
        ).one()
        assert result.id == template.id
