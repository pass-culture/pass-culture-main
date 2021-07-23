from datetime import datetime
from datetime import timedelta

from freezegun import freeze_time
import pytest

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.bookings.factories import BookingFactory
import pcapi.core.offers.factories as offers_factories
from pcapi.core.offers.factories import ActivationCodeFactory
from pcapi.core.offers.factories import EventStockFactory
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import OfferStatus
from pcapi.core.offers.models import OfferValidationStatus
from pcapi.core.offers.repository import check_stock_consistency
from pcapi.core.offers.repository import delete_past_draft_offers
from pcapi.core.offers.repository import find_tomorrow_event_stock_ids
from pcapi.core.offers.repository import get_active_offers_count_for_venue
from pcapi.core.offers.repository import get_available_activation_code
from pcapi.core.offers.repository import get_capped_offers_for_filters
from pcapi.core.offers.repository import get_expired_offers
from pcapi.core.offers.repository import get_offers_by_ids
from pcapi.core.offers.repository import get_sold_out_offers_count_for_venue
from pcapi.core.users import factories as users_factories
from pcapi.domain.pro_offers.offers_recap import OffersRecap
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_provider
from pcapi.model_creators.generic_creators import create_user_offerer
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.models import ThingType
from pcapi.repository import repository
from pcapi.utils.date import utc_datetime_to_department_timezone


class GetCappedOffersForFiltersTest:
    @pytest.mark.usefixtures("db_session")
    def should_return_offers_capped_to_max_offers_count(self):
        # Given
        user_offerer = offers_factories.UserOffererFactory()
        older_offer = offers_factories.OfferFactory(venue__managingOfferer=user_offerer.offerer)
        expected_offer = offers_factories.OfferFactory(
            venue=older_offer.venue, venue__managingOfferer=user_offerer.offerer
        )

        requested_max_offers_count = 1

        # When
        offers = get_capped_offers_for_filters(
            user_id=user_offerer.user.id,
            user_is_admin=user_offerer.user.isAdmin,
            offers_limit=requested_max_offers_count,
        )

        # Then
        assert isinstance(offers, OffersRecap)
        assert len(offers.offers) == 1
        assert offers.offers[0].id == expected_offer.id

    @pytest.mark.usefixtures("db_session")
    def should_return_offers_sorted_by_id_desc(self):
        # Given
        user = users_factories.UserFactory()
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)
        venue = create_venue(offerer)
        offer1 = create_offer_with_thing_product(venue)
        offer2 = create_offer_with_thing_product(venue)
        repository.save(user_offerer, offer1, offer2)

        # When
        offers = get_capped_offers_for_filters(user_id=user.id, user_is_admin=user.isAdmin, offers_limit=10)

        # Then
        assert offers.offers[0].id > offers.offers[1].id

    @pytest.mark.usefixtures("db_session")
    def should_exclude_draft_offers_when_requesting_all_offers(self, app):
        # given
        user_offerer = offers_factories.UserOffererFactory()
        non_draft_offer = offers_factories.OfferFactory(venue__managingOfferer=user_offerer.offerer)
        offers_factories.OfferFactory(
            venue__managingOfferer=user_offerer.offerer,
            validation=OfferValidationStatus.DRAFT,
        )

        # when
        offers = get_capped_offers_for_filters(
            user_id=user_offerer.user.id, user_is_admin=user_offerer.user.isAdmin, offers_limit=10
        )

        # then
        offers_id = [offer.id for offer in offers.offers]
        assert offers_id == [non_draft_offer.id]

    @pytest.mark.usefixtures("db_session")
    def should_return_offers_of_given_type(self):
        user_offerer = offers_factories.UserOffererFactory()
        requested_offer = offers_factories.OfferFactory(
            type=str(ThingType.AUDIOVISUEL), venue__managingOfferer=user_offerer.offerer
        )
        other_offer = offers_factories.OfferFactory(
            type=str(ThingType.JEUX), venue__managingOfferer=user_offerer.offerer
        )

        offers = get_capped_offers_for_filters(
            user_id=user_offerer.user.id,
            user_is_admin=user_offerer.user.isAdmin,
            offers_limit=10,
            type_id=str(ThingType.AUDIOVISUEL),
        )

        # then
        offers_id = [offer.id for offer in offers.offers]
        assert requested_offer.id in offers_id
        assert other_offer.id not in offers_id
        assert len(offers.offers) == 1

    @pytest.mark.usefixtures("db_session")
    def test_returns_offers_filtered_by_manual_creation_mode_when_provided(self):
        # given
        pro_user = users_factories.UserFactory()
        offerer = create_offerer()
        create_user_offerer(pro_user, offerer)
        venue = create_venue(offerer)
        provider = create_provider()
        manually_created_offer = create_offer_with_thing_product(venue=venue, last_provider=None, last_provider_id=None)
        imported_offer = create_offer_with_thing_product(
            venue=venue, last_provider=provider, last_provider_id=provider.id
        )

        repository.save(manually_created_offer, imported_offer, pro_user)

        # When
        offers = get_capped_offers_for_filters(
            user_id=pro_user.id, user_is_admin=pro_user.isAdmin, offers_limit=10, creation_mode="manual"
        )

        # then
        assert offers.offers[0].id == manually_created_offer.id
        assert len(offers.offers) == 1

    @pytest.mark.usefixtures("db_session")
    def test_returns_offers_filtered_by_imported_creation_mode_when_provided(self):
        # given
        pro_user = users_factories.UserFactory()
        offerer = create_offerer()
        create_user_offerer(pro_user, offerer)
        venue = create_venue(offerer)
        provider = create_provider()
        manually_created_offer = create_offer_with_thing_product(venue=venue, last_provider=None, last_provider_id=None)
        imported_offer = create_offer_with_thing_product(
            venue=venue, last_provider=provider, last_provider_id=provider.id
        )

        repository.save(manually_created_offer, imported_offer, pro_user)

        # When
        offers = get_capped_offers_for_filters(
            user_id=pro_user.id, user_is_admin=pro_user.isAdmin, offers_limit=10, creation_mode="imported"
        )

        # then
        assert offers.offers[0].id == imported_offer.id
        assert len(offers.offers) == 1

    @pytest.mark.usefixtures("db_session")
    def should_not_return_event_offers_with_only_deleted_stock_if_filtering_by_time_period(self):
        # given
        pro = users_factories.UserFactory(isAdmin=True)
        offer_in_requested_time_period = offers_factories.OfferFactory()
        offers_factories.EventStockFactory(
            offer=offer_in_requested_time_period, beginningDatetime=datetime(2020, 1, 2), isSoftDeleted=True
        )

        # When
        offers = get_capped_offers_for_filters(
            user_id=pro.id, user_is_admin=pro.isAdmin, offers_limit=10, period_beginning_date="2020-01-01T00:00:00"
        )

        # then
        offers_id = [offer.id for offer in offers.offers]
        assert offer_in_requested_time_period.id not in offers_id
        assert len(offers.offers) == 0

    @pytest.mark.usefixtures("db_session")
    def should_consider_venue_locale_datetime_when_filtering_by_date(self):
        # given
        admin = users_factories.UserFactory(isAdmin=True)
        period_beginning_date = "2020-04-21T00:00:00"
        period_ending_date = "2020-04-21T23:59:59"

        offer_in_cayenne = offers_factories.OfferFactory(venue__postalCode="97300")
        cayenne_event_datetime = datetime(2020, 4, 22, 2, 0)
        offers_factories.EventStockFactory(offer=offer_in_cayenne, beginningDatetime=cayenne_event_datetime)

        offer_in_mayotte = offers_factories.OfferFactory(venue__postalCode="97600")
        mayotte_event_datetime = datetime(2020, 4, 20, 22, 0)
        offers_factories.EventStockFactory(offer=offer_in_mayotte, beginningDatetime=mayotte_event_datetime)

        # When
        offers = get_capped_offers_for_filters(
            user_id=admin.id,
            user_is_admin=admin.isAdmin,
            offers_limit=10,
            period_beginning_date=period_beginning_date,
            period_ending_date=period_ending_date,
        )

        # then
        offers_id = [offer.id for offer in offers.offers]
        assert offer_in_cayenne.id in offers_id
        assert offer_in_mayotte.id in offers_id
        assert len(offers.offers) == 2

    class WhenUserIsAdminTest:
        @pytest.mark.usefixtures("db_session")
        def should_return_offers_of_given_venue_when_user_is_not_attached_to_its_offerer(self, app):
            # given
            admin = users_factories.UserFactory(isAdmin=True)
            offer_for_requested_venue = offers_factories.OfferFactory()
            offer_for_other_venue = offers_factories.OfferFactory()

            # when
            offers = get_capped_offers_for_filters(
                user_id=admin.id,
                user_is_admin=admin.isAdmin,
                offers_limit=10,
                venue_id=offer_for_requested_venue.venue.id,
            )

            # then
            offers_id = [offer.id for offer in offers.offers]
            assert offer_for_requested_venue.id in offers_id
            assert offer_for_other_venue.id not in offers_id
            assert len(offers.offers) == 1

        @pytest.mark.usefixtures("db_session")
        def should_return_offers_of_given_venue_when_user_is_attached_to_its_offerer(self, app):
            # given
            admin = users_factories.UserFactory(isAdmin=True)
            admin_attachment_to_offerer = offers_factories.UserOffererFactory(user=admin)
            offer_for_requested_venue = offers_factories.OfferFactory(
                venue__managingOfferer=admin_attachment_to_offerer.offerer
            )
            offer_for_other_venue = offers_factories.OfferFactory(
                venue__managingOfferer=admin_attachment_to_offerer.offerer
            )

            # when
            offers = get_capped_offers_for_filters(
                user_id=admin.id,
                user_is_admin=admin.isAdmin,
                offers_limit=10,
                venue_id=offer_for_requested_venue.venue.id,
            )

            # then
            offers_id = [offer.id for offer in offers.offers]
            assert offer_for_requested_venue.id in offers_id
            assert offer_for_other_venue.id not in offers_id
            assert len(offers.offers) == 1

        @pytest.mark.usefixtures("db_session")
        def should_return_offers_of_given_offerer_when_user_is_not_attached_to_it(self):
            # given
            admin = users_factories.UserFactory(isAdmin=True)
            offer_for_requested_offerer = offers_factories.OfferFactory()
            offer_for_other_offerer = offers_factories.OfferFactory()

            # When
            offers = get_capped_offers_for_filters(
                user_id=admin.id,
                user_is_admin=admin.isAdmin,
                offers_limit=10,
                offerer_id=offer_for_requested_offerer.venue.managingOffererId,
            )

            # then
            offers_id = [offer.id for offer in offers.offers]
            assert offer_for_requested_offerer.id in offers_id
            assert offer_for_other_offerer.id not in offers_id
            assert len(offers.offers) == 1

        @pytest.mark.usefixtures("db_session")
        def should_return_offers_of_given_offerer_when_user_is_attached_to_it(self):
            # given
            admin = users_factories.UserFactory(isAdmin=True)
            admin_attachment_to_requested_offerer = offers_factories.UserOffererFactory(user=admin)
            admin_attachment_to_other_offerer = offers_factories.UserOffererFactory(user=admin)
            offer_for_requested_offerer = offers_factories.OfferFactory(
                venue__managingOfferer=admin_attachment_to_requested_offerer.offerer
            )
            offer_for_other_offerer = offers_factories.OfferFactory(
                venue__managingOfferer=admin_attachment_to_other_offerer.offerer
            )

            # When
            offers = get_capped_offers_for_filters(
                user_id=admin.id,
                user_is_admin=admin.isAdmin,
                offers_limit=10,
                offerer_id=offer_for_requested_offerer.venue.managingOffererId,
            )

            # then
            offers_id = [offer.id for offer in offers.offers]
            assert offer_for_requested_offerer.id in offers_id
            assert offer_for_other_offerer.id not in offers_id
            assert len(offers.offers) == 1

    class WhenUserIsProTest:
        @pytest.mark.usefixtures("db_session")
        def should_not_return_offers_of_given_venue_when_user_is_not_attached_to_its_offerer(self, app):
            # given
            pro = users_factories.UserFactory(isBeneficiary=False, isAdmin=False)
            offer_for_requested_venue = offers_factories.OfferFactory()
            offer_for_other_venue = offers_factories.OfferFactory()

            # when
            offers = get_capped_offers_for_filters(
                user_id=pro.id,
                user_is_admin=pro.isAdmin,
                offers_limit=10,
                venue_id=offer_for_requested_venue.venue.id,
            )

            # then
            offers_id = [offer.id for offer in offers.offers]
            assert offer_for_requested_venue.id not in offers_id
            assert offer_for_other_venue.id not in offers_id
            assert len(offers.offers) == 0

        @pytest.mark.usefixtures("db_session")
        def should_return_offers_of_given_venue_when_user_is_attached_to_its_offerer(self, app):
            # given
            pro = users_factories.UserFactory(isBeneficiary=False, isAdmin=False)
            pro_attachment_to_offerer = offers_factories.UserOffererFactory(user=pro)
            offer_for_requested_venue = offers_factories.OfferFactory(
                venue__managingOfferer=pro_attachment_to_offerer.offerer
            )
            offer_for_other_venue = offers_factories.OfferFactory(
                venue__managingOfferer=pro_attachment_to_offerer.offerer
            )

            # when
            offers = get_capped_offers_for_filters(
                user_id=pro.id,
                user_is_admin=pro.isAdmin,
                offers_limit=10,
                venue_id=offer_for_requested_venue.venue.id,
            )

            # then
            offers_id = [offer.id for offer in offers.offers]
            assert offer_for_requested_venue.id in offers_id
            assert offer_for_other_venue.id not in offers_id
            assert len(offers.offers) == 1

        @pytest.mark.usefixtures("db_session")
        def should_not_return_offers_of_given_offerer_when_user_is_not_attached_to_it(self):
            # given
            pro = users_factories.UserFactory(isBeneficiary=False, isAdmin=False)
            offer_for_requested_offerer = offers_factories.OfferFactory()
            offer_for_other_offerer = offers_factories.OfferFactory()

            # When
            offers = get_capped_offers_for_filters(
                user_id=pro.id,
                user_is_admin=pro.isAdmin,
                offers_limit=10,
                offerer_id=offer_for_requested_offerer.venue.managingOffererId,
            )

            # then
            offers_id = [offer.id for offer in offers.offers]
            assert offer_for_requested_offerer.id not in offers_id
            assert offer_for_other_offerer.id not in offers_id
            assert len(offers.offers) == 0

        @pytest.mark.usefixtures("db_session")
        def should_return_offers_of_given_offerer_when_user_is_attached_to_it(self):
            # given
            pro = users_factories.UserFactory(isBeneficiary=False, isAdmin=False)
            pro_attachment_to_requested_offerer = offers_factories.UserOffererFactory(user=pro)
            pro_attachment_to_other_offerer = offers_factories.UserOffererFactory(user=pro)
            offer_for_requested_offerer = offers_factories.OfferFactory(
                venue__managingOfferer=pro_attachment_to_requested_offerer.offerer
            )
            offer_for_other_offerer = offers_factories.OfferFactory(
                venue__managingOfferer=pro_attachment_to_other_offerer.offerer
            )

            # When
            offers = get_capped_offers_for_filters(
                user_id=pro.id,
                user_is_admin=pro.isAdmin,
                offers_limit=10,
                offerer_id=offer_for_requested_offerer.venue.managingOffererId,
            )

            # then
            offers_id = [offer.id for offer in offers.offers]
            assert offer_for_requested_offerer.id in offers_id
            assert offer_for_other_offerer.id not in offers_id
            assert len(offers.offers) == 1

    class NameFilterTest:
        @pytest.mark.usefixtures("db_session")
        def should_return_offer_which_name_equal_keyword_when_keyword_is_less_or_equal_than_3_letters(self, app):
            # given
            user_offerer = offers_factories.UserOffererFactory()
            expected_offer = offers_factories.OfferFactory(name="ocs", venue__managingOfferer=user_offerer.offerer)
            other_offer = offers_factories.OfferFactory(name="ocsir", venue__managingOfferer=user_offerer.offerer)

            # when
            offers = get_capped_offers_for_filters(
                user_id=user_offerer.user.id,
                user_is_admin=user_offerer.user.isAdmin,
                offers_limit=10,
                name_keywords="ocs",
            )

            # then
            offers_id = [offer.id for offer in offers.offers]
            assert expected_offer.id in offers_id
            assert other_offer.id not in offers_id
            assert len(offers.offers) == 1

        @pytest.mark.usefixtures("db_session")
        def should_return_offer_which_name_contains_keyword_when_keyword_is_more_than_3_letters(self, app):
            # given
            user_offerer = offers_factories.UserOffererFactory()
            expected_offer = offers_factories.OfferFactory(
                name="seras-tu là", venue__managingOfferer=user_offerer.offerer
            )
            another_expected_offer = offers_factories.OfferFactory(
                name="François, seras-tu là ?", venue__managingOfferer=user_offerer.offerer
            )
            other_offer = offers_factories.OfferFactory(name="étais-tu là", venue__managingOfferer=user_offerer.offerer)

            # when
            offers = get_capped_offers_for_filters(
                user_id=user_offerer.user.id,
                user_is_admin=user_offerer.user.isAdmin,
                offers_limit=10,
                name_keywords="seras-tu",
            )

            # then
            offers_id = [offer.id for offer in offers.offers]
            assert expected_offer.id in offers_id
            assert another_expected_offer.id in offers_id
            assert other_offer.id not in offers_id
            assert len(offers.offers) == 2

        @pytest.mark.usefixtures("db_session")
        def should_be_case_insensitive(self, app):
            # given
            user_offerer = offers_factories.UserOffererFactory()
            expected_offer = offers_factories.OfferFactory(
                name="Mon océan", venue__managingOfferer=user_offerer.offerer
            )
            another_expected_offer = offers_factories.OfferFactory(
                name="MON océan", venue__managingOfferer=user_offerer.offerer
            )

            # when
            offers = get_capped_offers_for_filters(
                user_id=user_offerer.user.id,
                user_is_admin=user_offerer.user.isAdmin,
                offers_limit=10,
                name_keywords="mon océan",
            )

            # then
            offers_id = [offer.id for offer in offers.offers]
            assert expected_offer.id in offers_id
            assert another_expected_offer.id in offers_id
            assert len(offers.offers) == 2

        @pytest.mark.usefixtures("db_session")
        def should_be_accent_sensitive(self, app):
            # given
            user_offerer = offers_factories.UserOffererFactory()
            expected_offer = offers_factories.OfferFactory(name="ocean", venue__managingOfferer=user_offerer.offerer)
            other_offer = offers_factories.OfferFactory(name="océan", venue__managingOfferer=user_offerer.offerer)

            # when
            offers = get_capped_offers_for_filters(
                user_id=user_offerer.user.id,
                user_is_admin=user_offerer.user.isAdmin,
                offers_limit=10,
                name_keywords="ocean",
            )

            # then
            offers_id = [offer.id for offer in offers.offers]
            assert expected_offer.id in offers_id
            assert other_offer.id not in offers_id
            assert len(offers.offers) == 1

    class StatusFiltersTest:
        def init_test_data(self):
            self.venue = offers_factories.VenueFactory()
            self.offerer = self.venue.managingOfferer
            self.other_venue = offers_factories.VenueFactory(managingOfferer=self.offerer)
            self.pro = users_factories.UserFactory(isBeneficiary=False)
            self.user_offerer = offers_factories.UserOffererFactory(user=self.pro, offerer=self.offerer)

            self.sold_out_offer_on_other_venue = offers_factories.ThingOfferFactory(
                venue=self.other_venue, description="sold_out_offer_on_other_venue"
            )
            self.inactive_thing_offer_with_stock_with_remaining_quantity = offers_factories.ThingOfferFactory(
                venue=self.venue, isActive=False, description="inactive_thing_offer_with_stock_with_remaining_quantity"
            )
            self.inactive_thing_offer_without_remaining_quantity = offers_factories.ThingOfferFactory(
                venue=self.venue, isActive=False, description="inactive_thing_offer_without_remaining_quantity"
            )
            self.inactive_thing_offer_without_stock = offers_factories.ThingOfferFactory(
                venue=self.venue, isActive=False, description="inactive_thing_offer_without_stock"
            )
            self.inactive_expired_event_offer = offers_factories.EventOfferFactory(
                venue=self.venue, isActive=False, description="inactive_expired_event_offer"
            )
            self.active_thing_offer_with_one_stock_with_remaining_quantity = offers_factories.ThingOfferFactory(
                venue=self.venue, isActive=True, description="active_thing_offer_with_one_stock_with_remaining_quantity"
            )
            self.active_thing_offer_with_all_stocks_without_quantity = offers_factories.ThingOfferFactory(
                venue=self.venue, isActive=True, description="active_thing_offer_with_all_stocks_without_quantity"
            )
            self.active_event_offer_with_stock_in_the_future_without_quantity = offers_factories.EventOfferFactory(
                venue=self.venue, description="active_event_offer_with_stock_in_the_future_without_quantity"
            )
            self.active_event_offer_with_one_stock_in_the_future_with_remaining_quantity = (
                offers_factories.EventOfferFactory(
                    venue=self.venue,
                    description="active_event_offer_with_one_stock_in_the_future_with_remaining_quantity",
                )
            )
            self.sold_old_thing_offer_with_all_stocks_empty = offers_factories.ThingOfferFactory(
                venue=self.venue, description="sold_old_thing_offer_with_all_stocks_empty"
            )
            self.sold_out_event_offer_with_all_stocks_in_the_future_with_zero_remaining_quantity = (
                offers_factories.EventOfferFactory(
                    venue=self.venue,
                    description="sold_out_event_offer_with_all_stocks_in_the_future_with_zero_remaining_quantity",
                )
            )
            self.sold_out_thing_offer_without_stock = offers_factories.ThingOfferFactory(
                venue=self.venue, description="sold_out_thing_offer_without_stock"
            )
            self.sold_out_event_offer_without_stock = offers_factories.EventOfferFactory(
                venue=self.venue, description="sold_out_event_offer_without_stock"
            )
            self.sold_out_event_offer_with_only_one_stock_soft_deleted = offers_factories.EventOfferFactory(
                venue=self.venue, description="sold_out_event_offer_with_only_one_stock_soft_deleted"
            )
            self.expired_event_offer_with_stock_in_the_past_without_quantity = offers_factories.EventOfferFactory(
                venue=self.venue, description="expired_event_offer_with_stock_in_the_past_without_quantity"
            )
            self.expired_event_offer_with_all_stocks_in_the_past_with_remaining_quantity = (
                offers_factories.EventOfferFactory(
                    venue=self.venue,
                    description="expired_event_offer_with_all_stocks_in_the_past_with_remaining_quantity",
                )
            )
            self.expired_event_offer_with_all_stocks_in_the_past_with_zero_remaining_quantity = (
                offers_factories.EventOfferFactory(
                    venue=self.venue,
                    description="expired_event_offer_with_all_stocks_in_the_past_with_zero_remaining_quantity",
                )
            )
            self.expired_thing_offer_with_a_stock_expired_with_remaining_quantity = offers_factories.EventOfferFactory(
                venue=self.venue,
                description="expired_thing_offer_with_a_stock_expired_with_remaining_quantity",
            )
            self.expired_thing_offer_with_a_stock_expired_with_zero_remaining_quantity = (
                offers_factories.EventOfferFactory(
                    venue=self.venue,
                    description="expired_thing_offer_with_a_stock_expired_with_zero_remaining_quantity",
                )
            )

            five_days_ago = datetime.now() - timedelta(days=5)
            in_five_days = datetime.now() + timedelta(days=5)
            beneficiary = users_factories.UserFactory(email="jane.doe@example.com")
            offers_factories.ThingStockFactory(offer=self.sold_old_thing_offer_with_all_stocks_empty, quantity=0)
            offers_factories.ThingStockFactory(
                offer=self.active_thing_offer_with_one_stock_with_remaining_quantity, quantity=5
            )
            offers_factories.ThingStockFactory(
                offer=self.active_thing_offer_with_one_stock_with_remaining_quantity, quantity=0
            )
            offers_factories.ThingStockFactory(
                offer=self.active_thing_offer_with_all_stocks_without_quantity, quantity=None
            )
            offers_factories.EventStockFactory(
                offer=self.expired_event_offer_with_stock_in_the_past_without_quantity,
                beginningDatetime=five_days_ago,
                bookingLimitDatetime=five_days_ago,
                quantity=None,
            )
            offers_factories.EventStockFactory(
                offer=self.expired_event_offer_with_stock_in_the_past_without_quantity,
                beginningDatetime=in_five_days,
                bookingLimitDatetime=in_five_days,
                quantity=None,
                isSoftDeleted=True,
            )
            offers_factories.EventStockFactory(
                offer=self.active_event_offer_with_stock_in_the_future_without_quantity,
                beginningDatetime=in_five_days,
                bookingLimitDatetime=in_five_days,
                quantity=None,
            )
            offers_factories.EventStockFactory(
                offer=self.expired_event_offer_with_all_stocks_in_the_past_with_remaining_quantity,
                beginningDatetime=five_days_ago,
                bookingLimitDatetime=five_days_ago,
                quantity=5,
            )
            offers_factories.EventStockFactory(
                offer=self.expired_event_offer_with_all_stocks_in_the_past_with_remaining_quantity,
                beginningDatetime=five_days_ago,
                bookingLimitDatetime=five_days_ago,
                quantity=4,
            )
            stock_with_some_bookings = offers_factories.EventStockFactory(
                offer=self.active_event_offer_with_one_stock_in_the_future_with_remaining_quantity,
                beginningDatetime=in_five_days,
                bookingLimitDatetime=in_five_days,
                quantity=1,
            )
            bookings_factories.BookingFactory(user=beneficiary, stock=stock_with_some_bookings, isCancelled=True)
            offers_factories.EventStockFactory(
                offer=self.active_event_offer_with_one_stock_in_the_future_with_remaining_quantity,
                beginningDatetime=in_five_days,
                bookingLimitDatetime=in_five_days,
                quantity=0,
            )
            offers_factories.EventStockFactory(
                offer=self.expired_event_offer_with_all_stocks_in_the_past_with_zero_remaining_quantity,
                beginningDatetime=five_days_ago,
                bookingLimitDatetime=five_days_ago,
                quantity=0,
            )
            offers_factories.EventStockFactory(
                offer=self.expired_event_offer_with_all_stocks_in_the_past_with_zero_remaining_quantity,
                beginningDatetime=five_days_ago,
                bookingLimitDatetime=five_days_ago,
                quantity=0,
            )
            offers_factories.EventStockFactory(
                offer=self.sold_out_event_offer_with_all_stocks_in_the_future_with_zero_remaining_quantity,
                beginningDatetime=five_days_ago,
                bookingLimitDatetime=five_days_ago,
                quantity=5,
            )
            stock_all_booked = offers_factories.EventStockFactory(
                offer=self.sold_out_event_offer_with_all_stocks_in_the_future_with_zero_remaining_quantity,
                beginningDatetime=in_five_days,
                bookingLimitDatetime=in_five_days,
                quantity=1,
                price=0,
            )
            bookings_factories.BookingFactory(user=beneficiary, stock=stock_all_booked)
            offers_factories.ThingStockFactory(
                offer=self.inactive_thing_offer_with_stock_with_remaining_quantity, quantity=4
            )
            offers_factories.EventStockFactory(
                offer=self.active_event_offer_with_stock_in_the_future_without_quantity,
                beginningDatetime=five_days_ago,
                bookingLimitDatetime=five_days_ago,
                quantity=None,
            )
            offers_factories.EventStockFactory(
                offer=self.inactive_expired_event_offer,
                beginningDatetime=five_days_ago,
                bookingLimitDatetime=five_days_ago,
                quantity=None,
            )
            offers_factories.ThingStockFactory(offer=self.inactive_thing_offer_without_remaining_quantity, quantity=0)
            offers_factories.EventStockFactory(
                offer=self.sold_out_event_offer_with_only_one_stock_soft_deleted, quantity=10, isSoftDeleted=True
            )
            offers_factories.ThingStockFactory(
                offer=self.expired_thing_offer_with_a_stock_expired_with_remaining_quantity,
                bookingLimitDatetime=five_days_ago,
                quantity=4,
            )
            offers_factories.ThingStockFactory(
                offer=self.expired_thing_offer_with_a_stock_expired_with_zero_remaining_quantity,
                bookingLimitDatetime=five_days_ago,
                quantity=0,
            )
            in_six_days = datetime.now() + timedelta(days=6)
            self.active_event_in_six_days_offer = offers_factories.EventOfferFactory(venue=self.venue)
            offers_factories.EventStockFactory(
                offer=self.active_event_in_six_days_offer,
                beginningDatetime=in_six_days,
                bookingLimitDatetime=in_six_days,
                quantity=10,
            )
            self.draft_offer = offers_factories.EventOfferFactory(
                venue=self.venue, validation=OfferValidationStatus.DRAFT, description="draft event offer"
            )

        @pytest.mark.usefixtures("db_session")
        def should_return_only_active_offers_when_requesting_active_status(self):
            # given
            self.init_test_data()

            # when
            offers = get_capped_offers_for_filters(
                user_id=self.pro.id, user_is_admin=self.pro.isAdmin, offers_limit=5, status="ACTIVE"
            )

            # then
            offer_ids = [offer.id for offer in offers.offers]
            assert self.active_thing_offer_with_one_stock_with_remaining_quantity.id in offer_ids
            assert self.active_event_in_six_days_offer.id in offer_ids
            assert self.active_thing_offer_with_all_stocks_without_quantity.id in offer_ids
            assert self.active_event_offer_with_stock_in_the_future_without_quantity.id in offer_ids
            assert self.active_event_offer_with_one_stock_in_the_future_with_remaining_quantity.id in offer_ids
            assert self.inactive_thing_offer_without_stock.id not in offer_ids
            assert self.inactive_thing_offer_with_stock_with_remaining_quantity.id not in offer_ids
            assert self.inactive_expired_event_offer.id not in offer_ids
            assert self.inactive_thing_offer_without_remaining_quantity.id not in offer_ids
            assert self.sold_out_thing_offer_without_stock.id not in offer_ids
            assert self.sold_old_thing_offer_with_all_stocks_empty.id not in offer_ids
            assert (
                self.sold_out_event_offer_with_all_stocks_in_the_future_with_zero_remaining_quantity.id not in offer_ids
            )
            assert self.sold_out_event_offer_with_only_one_stock_soft_deleted.id not in offer_ids
            assert self.sold_out_event_offer_without_stock.id not in offer_ids
            assert self.expired_event_offer_with_stock_in_the_past_without_quantity.id not in offer_ids
            assert self.expired_thing_offer_with_a_stock_expired_with_remaining_quantity.id not in offer_ids
            assert self.expired_event_offer_with_all_stocks_in_the_past_with_remaining_quantity.id not in offer_ids
            assert self.expired_event_offer_with_all_stocks_in_the_past_with_zero_remaining_quantity.id not in offer_ids
            assert len(offers.offers) == 5

        @pytest.mark.usefixtures("db_session")
        def should_return_only_inactive_offers_when_requesting_inactive_status(self):
            # given
            self.init_test_data()

            # when
            offers = get_capped_offers_for_filters(
                user_id=self.pro.id, user_is_admin=self.pro.isAdmin, offers_limit=5, status="INACTIVE"
            )

            # then
            offer_ids = [offer.id for offer in offers.offers]
            assert self.active_thing_offer_with_one_stock_with_remaining_quantity.id not in offer_ids
            assert self.active_thing_offer_with_all_stocks_without_quantity.id not in offer_ids
            assert self.active_event_offer_with_stock_in_the_future_without_quantity.id not in offer_ids
            assert self.active_event_offer_with_one_stock_in_the_future_with_remaining_quantity.id not in offer_ids
            assert self.inactive_thing_offer_without_stock.id in offer_ids
            assert self.inactive_thing_offer_with_stock_with_remaining_quantity.id in offer_ids
            assert self.inactive_expired_event_offer.id in offer_ids
            assert self.inactive_thing_offer_without_remaining_quantity.id in offer_ids
            assert self.sold_out_thing_offer_without_stock.id not in offer_ids
            assert self.sold_old_thing_offer_with_all_stocks_empty.id not in offer_ids
            assert (
                self.sold_out_event_offer_with_all_stocks_in_the_future_with_zero_remaining_quantity.id not in offer_ids
            )
            assert self.sold_out_event_offer_with_only_one_stock_soft_deleted.id not in offer_ids
            assert self.sold_out_event_offer_without_stock.id not in offer_ids
            assert self.expired_event_offer_with_stock_in_the_past_without_quantity.id not in offer_ids
            assert self.expired_thing_offer_with_a_stock_expired_with_remaining_quantity.id not in offer_ids
            assert self.expired_thing_offer_with_a_stock_expired_with_zero_remaining_quantity.id not in offer_ids
            assert self.expired_event_offer_with_all_stocks_in_the_past_with_remaining_quantity.id not in offer_ids
            assert self.expired_event_offer_with_all_stocks_in_the_past_with_zero_remaining_quantity.id not in offer_ids
            assert len(offers.offers) == 4

        @pytest.mark.usefixtures("db_session")
        def should_return_only_sold_out_offers_when_requesting_sold_out_status(self):
            # given
            self.init_test_data()

            # when
            offers = get_capped_offers_for_filters(
                user_id=self.pro.id, user_is_admin=self.pro.isAdmin, offers_limit=10, status="SOLD_OUT"
            )

            # then
            offer_ids = [offer.id for offer in offers.offers]
            assert self.active_thing_offer_with_one_stock_with_remaining_quantity.id not in offer_ids
            assert self.active_thing_offer_with_all_stocks_without_quantity.id not in offer_ids
            assert self.active_event_offer_with_stock_in_the_future_without_quantity.id not in offer_ids
            assert self.active_event_offer_with_one_stock_in_the_future_with_remaining_quantity.id not in offer_ids
            assert self.inactive_thing_offer_without_stock.id not in offer_ids
            assert self.inactive_thing_offer_with_stock_with_remaining_quantity.id not in offer_ids
            assert self.inactive_expired_event_offer.id not in offer_ids
            assert self.inactive_thing_offer_without_remaining_quantity.id not in offer_ids
            assert self.sold_out_thing_offer_without_stock.id in offer_ids
            assert self.sold_old_thing_offer_with_all_stocks_empty.id in offer_ids
            assert self.sold_out_event_offer_with_all_stocks_in_the_future_with_zero_remaining_quantity.id in offer_ids
            assert self.sold_out_event_offer_with_only_one_stock_soft_deleted.id in offer_ids
            assert self.sold_out_event_offer_without_stock.id in offer_ids
            assert self.sold_out_offer_on_other_venue.id in offer_ids
            assert self.expired_event_offer_with_stock_in_the_past_without_quantity.id not in offer_ids
            assert self.expired_thing_offer_with_a_stock_expired_with_remaining_quantity.id not in offer_ids
            assert self.expired_thing_offer_with_a_stock_expired_with_zero_remaining_quantity.id not in offer_ids
            assert self.expired_event_offer_with_all_stocks_in_the_past_with_remaining_quantity.id not in offer_ids
            assert self.expired_event_offer_with_all_stocks_in_the_past_with_zero_remaining_quantity.id not in offer_ids
            assert len(offers.offers) == 6

        @pytest.mark.usefixtures("db_session")
        def should_return_offers_with_no_stocks_when_requesting_sold_out_status(self):
            # given
            self.init_test_data()

            # when
            offers = get_capped_offers_for_filters(
                user_id=self.pro.id, user_is_admin=self.pro.isAdmin, offers_limit=5, status="SOLD_OUT"
            )

            # then
            offer_ids = [offer.id for offer in offers.offers]
            assert self.sold_out_thing_offer_without_stock.id in offer_ids
            assert self.sold_out_event_offer_with_only_one_stock_soft_deleted.id in offer_ids

        @pytest.mark.usefixtures("db_session")
        def should_return_offers_with_no_remaining_quantity_and_no_bookings_when_requesting_sold_out_status(self):
            # given
            self.init_test_data()

            # when
            offers = get_capped_offers_for_filters(
                user_id=self.pro.id, user_is_admin=self.pro.isAdmin, offers_limit=5, status="SOLD_OUT"
            )

            # then
            offer_ids = [offer.id for offer in offers.offers]
            assert self.sold_old_thing_offer_with_all_stocks_empty.id in offer_ids

        @pytest.mark.usefixtures("db_session")
        def should_return_offers_with_no_remaining_quantity_in_the_future_when_requesting_sold_out_status(self):
            # given
            self.init_test_data()

            # when
            offers = get_capped_offers_for_filters(
                user_id=self.pro.id, user_is_admin=self.pro.isAdmin, offers_limit=5, status="SOLD_OUT"
            )

            # then
            offer_ids = [offer.id for offer in offers.offers]
            assert self.sold_out_event_offer_with_all_stocks_in_the_future_with_zero_remaining_quantity.id in offer_ids

        @pytest.mark.usefixtures("db_session")
        def should_exclude_offers_with_cancelled_bookings_when_requesting_sold_out_status(self):
            # given
            self.init_test_data()

            # when
            offers = get_capped_offers_for_filters(
                user_id=self.pro.id, user_is_admin=self.pro.isAdmin, offers_limit=5, status="SOLD_OUT"
            )

            # then
            offer_ids = [offer.id for offer in offers.offers]
            assert self.active_event_offer_with_one_stock_in_the_future_with_remaining_quantity.id not in offer_ids

        @pytest.mark.usefixtures("db_session")
        def should_return_only_expired_offers_when_requesting_expired_status(self):
            # given
            self.init_test_data()

            # when
            offers = get_capped_offers_for_filters(
                user_id=self.pro.id, user_is_admin=self.pro.isAdmin, offers_limit=5, status="EXPIRED"
            )

            # then
            offer_ids = [offer.id for offer in offers.offers]
            assert self.active_thing_offer_with_one_stock_with_remaining_quantity.id not in offer_ids
            assert self.active_thing_offer_with_all_stocks_without_quantity.id not in offer_ids
            assert self.active_event_offer_with_stock_in_the_future_without_quantity.id not in offer_ids
            assert self.active_event_offer_with_one_stock_in_the_future_with_remaining_quantity.id not in offer_ids
            assert self.inactive_thing_offer_without_stock.id not in offer_ids
            assert self.inactive_thing_offer_with_stock_with_remaining_quantity.id not in offer_ids
            assert self.inactive_expired_event_offer.id not in offer_ids
            assert self.inactive_thing_offer_without_remaining_quantity.id not in offer_ids
            assert self.sold_out_thing_offer_without_stock.id not in offer_ids
            assert self.sold_old_thing_offer_with_all_stocks_empty.id not in offer_ids
            assert (
                self.sold_out_event_offer_with_all_stocks_in_the_future_with_zero_remaining_quantity.id not in offer_ids
            )
            assert self.sold_out_event_offer_with_only_one_stock_soft_deleted.id not in offer_ids
            assert self.sold_out_event_offer_without_stock.id not in offer_ids
            assert self.expired_event_offer_with_stock_in_the_past_without_quantity.id in offer_ids
            assert self.expired_thing_offer_with_a_stock_expired_with_remaining_quantity.id in offer_ids
            assert self.expired_thing_offer_with_a_stock_expired_with_zero_remaining_quantity.id in offer_ids
            assert self.expired_event_offer_with_all_stocks_in_the_past_with_remaining_quantity.id in offer_ids
            assert self.expired_event_offer_with_all_stocks_in_the_past_with_zero_remaining_quantity.id in offer_ids
            assert len(offers.offers) == 5

        @pytest.mark.usefixtures("db_session")
        def should_return_only_pending_offers_when_requesting_pending_status(self):
            # given
            unexpired_booking_limit_date = datetime.utcnow() + timedelta(days=3)

            pending_offer = offers_factories.ThingOfferFactory(
                validation=OfferStatus.PENDING.name, name="Offre en attente"
            )
            offers_factories.StockFactory(bookingLimitDatetime=unexpired_booking_limit_date, offer=pending_offer)

            offer = offers_factories.OfferFactory(product__type=str(ThingType.INSTRUMENT))
            offers_factories.StockFactory(bookingLimitDatetime=unexpired_booking_limit_date, offer=offer)

            user = pending_offer.venue.managingOfferer

            # when
            offers = get_capped_offers_for_filters(
                user_id=user.id, user_is_admin=True, offers_limit=5, status="PENDING"
            )

            # then
            assert len(offers.offers) == 1
            assert offers.offers[0].name == "Offre en attente"
            assert offers.offers[0].status == OfferStatus.PENDING.name

        @pytest.mark.usefixtures("db_session")
        def should_return_only_rejected_offers_when_requesting_rejected_status(self):
            # given
            unexpired_booking_limit_date = datetime.utcnow() + timedelta(days=3)

            rejected_offer = offers_factories.ThingOfferFactory(
                validation=OfferValidationStatus.REJECTED, name="Offre rejetée", isActive=False
            )
            offers_factories.StockFactory(bookingLimitDatetime=unexpired_booking_limit_date, offer=rejected_offer)

            offer = offers_factories.OfferFactory(product__type=str(ThingType.INSTRUMENT))
            offers_factories.StockFactory(bookingLimitDatetime=unexpired_booking_limit_date, offer=offer)

            user = rejected_offer.venue.managingOfferer

            # when
            offers = get_capped_offers_for_filters(
                user_id=user.id, user_is_admin=True, offers_limit=5, status="REJECTED"
            )

            # then
            assert len(offers.offers) == 1
            assert offers.offers[0].name == "Offre rejetée"
            assert offers.offers[0].status == OfferStatus.REJECTED.name

        @pytest.mark.usefixtures("db_session")
        def should_return_only_sold_out_offers_and_requested_venue_when_requesting_sold_out_status_and_specific_venue(
            self,
        ):
            # given
            self.init_test_data()

            # when
            offers = get_capped_offers_for_filters(
                user_id=self.pro.id,
                user_is_admin=self.pro.isAdmin,
                offers_limit=5,
                status="SOLD_OUT",
                venue_id=self.other_venue.id,
            )

            # then
            offer_ids = [offer.id for offer in offers.offers]
            assert self.sold_out_thing_offer_without_stock.id not in offer_ids
            assert self.sold_old_thing_offer_with_all_stocks_empty.id not in offer_ids
            assert (
                self.sold_out_event_offer_with_all_stocks_in_the_future_with_zero_remaining_quantity.id not in offer_ids
            )
            assert self.sold_out_event_offer_with_only_one_stock_soft_deleted.id not in offer_ids
            assert self.sold_out_event_offer_without_stock.id not in offer_ids
            assert self.sold_out_offer_on_other_venue.id in offer_ids
            assert len(offers.offers) == 1

        @pytest.mark.usefixtures("db_session")
        def should_return_only_active_offer_on_specific_period_when_requesting_active_status_and_time_period(self):
            # given
            self.init_test_data()

            in_six_days = datetime.now() + timedelta(days=6)
            in_six_days_beginning = in_six_days.replace(hour=0, minute=0, second=0)
            in_six_days_ending = in_six_days.replace(hour=23, minute=59, second=59)

            # when
            offers = get_capped_offers_for_filters(
                user_id=self.pro.id,
                user_is_admin=self.pro.isAdmin,
                offers_limit=5,
                status="ACTIVE",
                period_beginning_date=utc_datetime_to_department_timezone(in_six_days_beginning, "75").isoformat(),
                period_ending_date=utc_datetime_to_department_timezone(in_six_days_ending, "75").isoformat(),
            )

            # then
            offer_ids = [offer.id for offer in offers.offers]
            assert self.active_event_in_six_days_offer.id in offer_ids
            assert self.active_event_offer_with_one_stock_in_the_future_with_remaining_quantity.id not in offer_ids
            assert self.active_event_offer_with_stock_in_the_future_without_quantity.id not in offer_ids
            assert self.active_thing_offer_with_all_stocks_without_quantity.id not in offer_ids
            assert self.active_thing_offer_with_one_stock_with_remaining_quantity.id not in offer_ids
            assert len(offers.offers) == 1


@pytest.mark.usefixtures("db_session")
class GetOffersByIdsTest:
    def test_filter_on_user_offerer(self):
        offer1 = offers_factories.OfferFactory()
        offerer = offer1.venue.managingOfferer
        user_offerer = offers_factories.UserOffererFactory(offerer=offerer)
        user = user_offerer.user
        offer2 = offers_factories.OfferFactory()

        query = get_offers_by_ids(user, [offer1.id, offer2.id])

        assert query.count() == 1
        assert query.one() == offer1

    def test_return_all_for_admins(self):
        offer1 = offers_factories.OfferFactory()
        offer2 = offers_factories.OfferFactory()
        user = users_factories.UserFactory(isAdmin=True)

        query = get_offers_by_ids(user, [offer1.id, offer2.id])

        assert query.count() == 2


@pytest.mark.usefixtures("db_session")
class GetActiveOffersCountForVenueTest:
    def test_counts_active_offers_for_venue(self):
        # Given
        venue = offers_factories.VenueFactory()

        active_offer = offers_factories.ThingOfferFactory(venue=venue)
        offers_factories.StockFactory(offer=active_offer)
        other_active_offer = offers_factories.EventOfferFactory(venue=venue)
        offers_factories.EventStockFactory(offer=other_active_offer)
        offers_factories.EventStockFactory(offer=other_active_offer)

        sold_out_offer = offers_factories.ThingOfferFactory(venue=venue)
        sold_out_stock = offers_factories.StockFactory(quantity=1, offer=sold_out_offer)
        bookings_factories.BookingFactory(stock=sold_out_stock)

        expired_offer = offers_factories.EventOfferFactory(venue=venue)
        yesterday = datetime.utcnow() - timedelta(days=1)
        offers_factories.EventStockFactory(offer=expired_offer, bookingLimitDatetime=yesterday)

        inactive_offer = offers_factories.ThingOfferFactory(venue=venue, isActive=False)
        offers_factories.StockFactory(offer=inactive_offer)

        active_offer_on_another_venue = offers_factories.ThingOfferFactory()
        offers_factories.StockFactory(offer=active_offer_on_another_venue)

        # When
        active_offers_count = get_active_offers_count_for_venue(venue.id)

        # Then
        assert active_offers_count == 2


@pytest.mark.usefixtures("db_session")
class GetSoldOutOffersCountForVenueTest:
    def test_counts_sold_out_offers_for_venue(self):
        # Given
        venue = offers_factories.VenueFactory()

        active_offer = offers_factories.ThingOfferFactory(venue=venue)
        offers_factories.StockFactory(offer=active_offer)

        sold_out_offer = offers_factories.ThingOfferFactory(venue=venue)
        sold_out_stock = offers_factories.StockFactory(quantity=1, offer=sold_out_offer)
        bookings_factories.BookingFactory(stock=sold_out_stock)
        other_sold_out_offer = offers_factories.EventOfferFactory(venue=venue)
        other_sold_out_stock = offers_factories.EventStockFactory(quantity=1, offer=other_sold_out_offer)
        bookings_factories.BookingFactory(stock=other_sold_out_stock)
        offers_factories.EventStockFactory(quantity=0, offer=other_sold_out_offer)

        expired_offer = offers_factories.EventOfferFactory(venue=venue)
        yesterday = datetime.utcnow() - timedelta(days=1)
        offers_factories.EventStockFactory(offer=expired_offer, bookingLimitDatetime=yesterday)

        inactive_offer = offers_factories.ThingOfferFactory(venue=venue, isActive=False)
        offers_factories.StockFactory(offer=inactive_offer)

        active_offer_on_another_venue = offers_factories.ThingOfferFactory()
        offers_factories.StockFactory(offer=active_offer_on_another_venue)

        # When
        sold_out_offers_count = get_sold_out_offers_count_for_venue(venue.id)

        # Then
        assert sold_out_offers_count == 2


@pytest.mark.usefixtures("db_session")
class CheckStockConsistenceTest:
    def test_with_inconsistencies(self):
        # consistent stock without booking
        offers_factories.StockFactory(dnBookedQuantity=0)
        # inconsistent stock without booking
        stock2 = offers_factories.StockFactory(dnBookedQuantity=5)

        # consistent stock with booking
        stock3_bookings = bookings_factories.BookingFactory(quantity=2, stock__dnBookedQuantity=3)
        stock3 = stock3_bookings.stock
        stock3.dnBookedQuantity = 2
        # inconsistent stock with booking
        stock4_bookings = bookings_factories.BookingFactory(quantity=2)
        stock4 = stock4_bookings.stock
        stock4.dnBookedQuantity = 5

        # consistent stock with cancelled booking
        stock5_bookings = bookings_factories.BookingFactory(quantity=2, isCancelled=True)
        stock5 = stock5_bookings.stock
        stock5.dnBookedQuantity = 0
        # inconsistent stock with cancelled booking
        stock6_bookings = bookings_factories.BookingFactory(quantity=2, isCancelled=True)
        stock6 = stock6_bookings.stock
        stock6.dnBookedQuantity = 2

        repository.save(stock3, stock4, stock5, stock6)

        stock_ids = set(check_stock_consistency())
        assert stock_ids == {stock2.id, stock4.id, stock6.id}


@pytest.mark.usefixtures("db_session")
class TomorrowStockTest:
    def test_find_tomorrow_event_stock_ids(self):
        tomorrow = datetime.now() + timedelta(days=1)
        stocks_tomorrow = EventStockFactory.create_batch(2, beginningDatetime=tomorrow)
        stocks_tomorrow_cancelled = EventStockFactory.create_batch(3, beginningDatetime=tomorrow)

        next_week = datetime.now() + timedelta(days=7)
        stocks_next_week = EventStockFactory.create_batch(3, beginningDatetime=next_week)

        for stock in stocks_tomorrow:
            BookingFactory.create_batch(2, stock=stock, isCancelled=False)

        for stock in stocks_tomorrow_cancelled:
            BookingFactory.create_batch(2, stock=stock, isCancelled=True)

        for stock in stocks_next_week:
            BookingFactory.create_batch(2, stock=stock, isCancelled=False)

        stock_ids = find_tomorrow_event_stock_ids()
        assert set(stock_ids) == set(stock.id for stock in stocks_tomorrow)


@pytest.mark.usefixtures("db_session")
class GetExpiredOffersTest:
    interval = [datetime(2021, 1, 1, 0, 0), datetime(2021, 1, 2, 0, 0)]
    dt_before = datetime(2020, 12, 31)
    dt_within = datetime(2021, 1, 1)
    dt_after = datetime(2021, 1, 3)

    def test_basics(self):
        offer1 = offers_factories.OfferFactory()
        offers_factories.StockFactory(offer=offer1, bookingLimitDatetime=self.dt_within)
        offer2 = offers_factories.OfferFactory()
        offers_factories.StockFactory(offer=offer2, bookingLimitDatetime=self.dt_within)
        offers_factories.StockFactory(offer=offer2, bookingLimitDatetime=self.dt_within)
        offer3 = offers_factories.OfferFactory()
        offers_factories.StockFactory(offer=offer3, bookingLimitDatetime=self.dt_before)
        offers_factories.StockFactory(offer=offer3, bookingLimitDatetime=self.dt_within)
        offers_factories.StockFactory(bookingLimitDatetime=None)
        offers_factories.StockFactory(bookingLimitDatetime=self.dt_before)
        offers_factories.StockFactory(bookingLimitDatetime=self.dt_after)

        offers = get_expired_offers(self.interval)

        assert offers.all() == [offer1, offer2, offer3]

    def test_exclude_if_latest_stock_outside_interval(self):
        offer1 = offers_factories.OfferFactory()
        offers_factories.StockFactory(offer=offer1, bookingLimitDatetime=self.dt_within)
        offer2 = offers_factories.OfferFactory()
        offers_factories.StockFactory(offer=offer2, bookingLimitDatetime=self.dt_within)
        offers_factories.StockFactory(offer=offer2, bookingLimitDatetime=self.dt_after)

        offers = get_expired_offers(self.interval)

        assert offers.all() == [offer1]


@pytest.mark.usefixtures("db_session")
class DeletePastDraftOfferTest:
    @freeze_time("2020-10-15 09:00:00")
    def test_delete_past_draft_offers(self):
        two_days_ago = datetime.utcnow() - timedelta(days=2)
        offer = offers_factories.OfferFactory(dateCreated=two_days_ago, validation=OfferValidationStatus.DRAFT)
        offers_factories.MediationFactory(offer=offer)
        offers_factories.OfferCriterionFactory(offer=offer)
        past_offer = offers_factories.OfferFactory(dateCreated=two_days_ago, validation=OfferValidationStatus.PENDING)
        today_offer = offers_factories.OfferFactory(
            dateCreated=datetime.utcnow(), validation=OfferValidationStatus.DRAFT
        )

        delete_past_draft_offers()

        offers = Offer.query.all()
        assert set(offers) == {today_offer, past_offer}


@pytest.mark.usefixtures("db_session")
class AvailableActivationCodeTest:
    def test_activation_code_is_available_for_a_stock(self):
        # GIVEN
        booking = BookingFactory()
        stock = booking.stock
        ActivationCodeFactory(booking=booking, stock=stock)  # booked_code
        not_booked_code = ActivationCodeFactory(stock=stock)

        # WHEN
        found_code = get_available_activation_code(stock)

        # THEN
        assert found_code.id == not_booked_code.id

    def test_expired_activation_code_is_not_available_for_a_stock(self):
        # GIVEN
        booking = BookingFactory()
        stock = booking.stock
        ActivationCodeFactory(booking=booking, stock=stock)  # booked_code
        ActivationCodeFactory(stock=stock, expirationDate=datetime.now() - timedelta(days=1))  # expired code

        # WHEN THEN
        assert not get_available_activation_code(stock)

    def test_activation_code_of_a_stock_is_not_available_for_another_stock(self):
        booking = BookingFactory()
        booking2 = BookingFactory()
        stock = booking.stock
        stock2 = booking2.stock
        ActivationCodeFactory(stock=stock2)

        assert not get_available_activation_code(stock)
