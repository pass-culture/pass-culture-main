from datetime import datetime
from datetime import timedelta

from freezegun import freeze_time
import pytest

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.categories import categories
from pcapi.core.categories import subcategories
import pcapi.core.criteria.factories as criteria_factories
import pcapi.core.educational.factories as educational_factories
import pcapi.core.educational.models as educational_models
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offers import factories
from pcapi.core.offers import models
from pcapi.core.offers import repository
import pcapi.core.providers.factories as providers_factories
from pcapi.core.users import factories as users_factories
from pcapi.domain.pro_offers.offers_recap import OffersRecap
from pcapi.models import offer_mixin
import pcapi.repository.repository as db_repository
from pcapi.utils.date import utc_datetime_to_department_timezone


class GetCappedOffersForFiltersTest:
    @pytest.mark.usefixtures("db_session")
    def should_return_offers_capped_to_max_offers_count(self):
        # Given
        user_offerer = offerers_factories.UserOffererFactory()
        older_offer = factories.OfferFactory(venue__managingOfferer=user_offerer.offerer)
        factories.OfferFactory(venue=older_offer.venue, venue__managingOfferer=user_offerer.offerer)

        requested_max_offers_count = 1

        # When
        offers = repository.get_capped_offers_for_filters(
            user_id=user_offerer.user.id,
            user_is_admin=user_offerer.user.has_admin_role,
            offers_limit=requested_max_offers_count,
        )

        # Then
        assert isinstance(offers, OffersRecap)
        assert len(offers.offers) == 1

    @pytest.mark.usefixtures("db_session")
    def should_return_offers_sorted_by_id_desc(self):
        # Given
        user_offerer = offerers_factories.UserOffererFactory()
        user = user_offerer.user
        offerer = user_offerer.offerer
        factories.OfferFactory(venue__managingOfferer=offerer)
        factories.OfferFactory(venue__managingOfferer=offerer)

        # When
        offers = repository.get_capped_offers_for_filters(
            user_id=user.id,
            user_is_admin=user.has_admin_role,
            offers_limit=10,
        )

        # Then
        assert offers.offers[0].id > offers.offers[1].id

    @pytest.mark.usefixtures("db_session")
    def should_exclude_draft_offers_when_requesting_all_offers(self, app):
        # given
        user_offerer = offerers_factories.UserOffererFactory()
        non_draft_offer = factories.OfferFactory(venue__managingOfferer=user_offerer.offerer)
        factories.OfferFactory(
            venue__managingOfferer=user_offerer.offerer,
            validation=offer_mixin.OfferValidationStatus.DRAFT,
        )

        # when
        offers = repository.get_capped_offers_for_filters(
            user_id=user_offerer.user.id,
            user_is_admin=user_offerer.user.has_admin_role,
            offers_limit=10,
        )

        # then
        offers_id = [offer.id for offer in offers.offers]
        assert offers_id == [non_draft_offer.id]

    @pytest.mark.usefixtures("db_session")
    def should_return_offers_of_given_subcategory_id(self):
        user_offerer = offerers_factories.UserOffererFactory()
        requested_offer = factories.OfferFactory(
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id, venue__managingOfferer=user_offerer.offerer
        )
        other_offer = factories.OfferFactory(
            subcategoryId=subcategories.JEU_SUPPORT_PHYSIQUE.id, venue__managingOfferer=user_offerer.offerer
        )

        offers = repository.get_capped_offers_for_filters(
            user_id=user_offerer.user.id,
            user_is_admin=user_offerer.user.has_admin_role,
            offers_limit=10,
            category_id=categories.FILM.id,
        )

        # then
        offers_id = [offer.id for offer in offers.offers]
        assert requested_offer.id in offers_id
        assert other_offer.id not in offers_id
        assert len(offers.offers) == 1

    @pytest.mark.usefixtures("db_session")
    def test_filter_on_creation_mode(self):
        venue = offerers_factories.VenueFactory()
        manual_offer = factories.OfferFactory(venue=venue)
        provider = providers_factories.ProviderFactory()
        synced_offer = factories.OfferFactory(venue=venue, lastProvider=provider)
        pro_user = users_factories.ProFactory(offerers=[venue.managingOfferer])

        offers = repository.get_capped_offers_for_filters(
            user_id=pro_user.id,
            user_is_admin=False,
            offers_limit=10,
            creation_mode="manual",
        )
        assert len(offers.offers) == 1
        assert offers.offers[0].id == manual_offer.id

        offers = repository.get_capped_offers_for_filters(
            user_id=pro_user.id,
            user_is_admin=False,
            offers_limit=10,
            creation_mode="imported",
        )
        assert len(offers.offers) == 1
        assert offers.offers[0].id == synced_offer.id

    @pytest.mark.usefixtures("db_session")
    def should_not_return_event_offers_with_only_deleted_stock_if_filtering_by_time_period(self):
        # given
        pro = users_factories.ProFactory()
        offer_in_requested_time_period = factories.OfferFactory()
        factories.EventStockFactory(
            offer=offer_in_requested_time_period, beginningDatetime=datetime(2020, 1, 2), isSoftDeleted=True
        )

        # When
        offers = repository.get_capped_offers_for_filters(
            user_id=pro.id,
            user_is_admin=pro.has_admin_role,
            offers_limit=10,
            period_beginning_date="2020-01-01T00:00:00",
        )

        # then
        offers_id = [offer.id for offer in offers.offers]
        assert offer_in_requested_time_period.id not in offers_id
        assert len(offers.offers) == 0

    @pytest.mark.usefixtures("db_session")
    def should_consider_venue_locale_datetime_when_filtering_by_date(self):
        # given
        admin = users_factories.AdminFactory()
        period_beginning_date = "2020-04-21T00:00:00"
        period_ending_date = "2020-04-21T23:59:59"

        offer_in_cayenne = factories.OfferFactory(venue__postalCode="97300")
        cayenne_event_datetime = datetime(2020, 4, 22, 2, 0)
        factories.EventStockFactory(offer=offer_in_cayenne, beginningDatetime=cayenne_event_datetime)

        offer_in_mayotte = factories.OfferFactory(venue__postalCode="97600")
        mayotte_event_datetime = datetime(2020, 4, 20, 22, 0)
        factories.EventStockFactory(offer=offer_in_mayotte, beginningDatetime=mayotte_event_datetime)

        # When
        offers = repository.get_capped_offers_for_filters(
            user_id=admin.id,
            user_is_admin=admin.has_admin_role,
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
            admin = users_factories.AdminFactory()
            offer_for_requested_venue = factories.OfferFactory()
            offer_for_other_venue = factories.OfferFactory()

            # when
            offers = repository.get_capped_offers_for_filters(
                user_id=admin.id,
                user_is_admin=admin.has_admin_role,
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
            admin = users_factories.AdminFactory()
            admin_attachment_to_offerer = offerers_factories.UserOffererFactory(user=admin)
            offer_for_requested_venue = factories.OfferFactory(
                venue__managingOfferer=admin_attachment_to_offerer.offerer
            )
            offer_for_other_venue = factories.OfferFactory(venue__managingOfferer=admin_attachment_to_offerer.offerer)

            # when
            offers = repository.get_capped_offers_for_filters(
                user_id=admin.id,
                user_is_admin=admin.has_admin_role,
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
            admin = users_factories.AdminFactory()
            offer_for_requested_offerer = factories.OfferFactory()
            offer_for_other_offerer = factories.OfferFactory()

            # When
            offers = repository.get_capped_offers_for_filters(
                user_id=admin.id,
                user_is_admin=admin.has_admin_role,
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
            admin = users_factories.AdminFactory()
            admin_attachment_to_requested_offerer = offerers_factories.UserOffererFactory(user=admin)
            admin_attachment_to_other_offerer = offerers_factories.UserOffererFactory(user=admin)
            offer_for_requested_offerer = factories.OfferFactory(
                venue__managingOfferer=admin_attachment_to_requested_offerer.offerer
            )
            offer_for_other_offerer = factories.OfferFactory(
                venue__managingOfferer=admin_attachment_to_other_offerer.offerer
            )

            # When
            offers = repository.get_capped_offers_for_filters(
                user_id=admin.id,
                user_is_admin=admin.has_admin_role,
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
            pro = users_factories.ProFactory()
            offer_for_requested_venue = factories.OfferFactory()
            offer_for_other_venue = factories.OfferFactory()

            # when
            offers = repository.get_capped_offers_for_filters(
                user_id=pro.id,
                user_is_admin=pro.has_admin_role,
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
            pro = users_factories.ProFactory()
            pro_attachment_to_offerer = offerers_factories.UserOffererFactory(user=pro)
            offer_for_requested_venue = factories.OfferFactory(venue__managingOfferer=pro_attachment_to_offerer.offerer)
            offer_for_other_venue = factories.OfferFactory(venue__managingOfferer=pro_attachment_to_offerer.offerer)

            # when
            offers = repository.get_capped_offers_for_filters(
                user_id=pro.id,
                user_is_admin=pro.has_admin_role,
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
            pro = users_factories.ProFactory()
            offer_for_requested_offerer = factories.OfferFactory()
            offer_for_other_offerer = factories.OfferFactory()

            # When
            offers = repository.get_capped_offers_for_filters(
                user_id=pro.id,
                user_is_admin=pro.has_admin_role,
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
            pro = users_factories.ProFactory()
            pro_attachment_to_requested_offerer = offerers_factories.UserOffererFactory(user=pro)
            pro_attachment_to_other_offerer = offerers_factories.UserOffererFactory(user=pro)
            offer_for_requested_offerer = factories.OfferFactory(
                venue__managingOfferer=pro_attachment_to_requested_offerer.offerer
            )
            offer_for_other_offerer = factories.OfferFactory(
                venue__managingOfferer=pro_attachment_to_other_offerer.offerer
            )

            # When
            offers = repository.get_capped_offers_for_filters(
                user_id=pro.id,
                user_is_admin=pro.has_admin_role,
                offers_limit=10,
                offerer_id=offer_for_requested_offerer.venue.managingOffererId,
            )

            # then
            offers_id = [offer.id for offer in offers.offers]
            assert offer_for_requested_offerer.id in offers_id
            assert offer_for_other_offerer.id not in offers_id
            assert len(offers.offers) == 1

    class NameOrIsbnFilterTest:
        @pytest.mark.usefixtures("db_session")
        def should_return_offer_which_name_equal_keyword_when_keyword_is_less_or_equal_than_3_letters(self, app):
            # given
            user_offerer = offerers_factories.UserOffererFactory()
            expected_offer = factories.OfferFactory(name="ocs", venue__managingOfferer=user_offerer.offerer)
            other_offer = factories.OfferFactory(name="ocsir", venue__managingOfferer=user_offerer.offerer)

            # when
            offers = repository.get_capped_offers_for_filters(
                user_id=user_offerer.user.id,
                user_is_admin=user_offerer.user.has_admin_role,
                offers_limit=10,
                name_keywords_or_isbn="ocs",
            )

            # then
            offers_id = [offer.id for offer in offers.offers]
            assert expected_offer.id in offers_id
            assert other_offer.id not in offers_id
            assert len(offers.offers) == 1

        @pytest.mark.usefixtures("db_session")
        def should_return_offer_which_name_contains_keyword_when_keyword_is_more_than_3_letters(self, app):
            # given
            user_offerer = offerers_factories.UserOffererFactory()
            expected_offer = factories.OfferFactory(name="seras-tu là", venue__managingOfferer=user_offerer.offerer)
            another_expected_offer = factories.OfferFactory(
                name="François, seras-tu là ?", venue__managingOfferer=user_offerer.offerer
            )
            other_offer = factories.OfferFactory(name="étais-tu là", venue__managingOfferer=user_offerer.offerer)

            # when
            offers = repository.get_capped_offers_for_filters(
                user_id=user_offerer.user.id,
                user_is_admin=user_offerer.user.has_admin_role,
                offers_limit=10,
                name_keywords_or_isbn="seras-tu",
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
            user_offerer = offerers_factories.UserOffererFactory()
            expected_offer = factories.OfferFactory(name="Mon océan", venue__managingOfferer=user_offerer.offerer)
            another_expected_offer = factories.OfferFactory(
                name="MON océan", venue__managingOfferer=user_offerer.offerer
            )

            # when
            offers = repository.get_capped_offers_for_filters(
                user_id=user_offerer.user.id,
                user_is_admin=user_offerer.user.has_admin_role,
                offers_limit=10,
                name_keywords_or_isbn="mon océan",
            )

            # then
            offers_id = [offer.id for offer in offers.offers]
            assert expected_offer.id in offers_id
            assert another_expected_offer.id in offers_id
            assert len(offers.offers) == 2

        @pytest.mark.usefixtures("db_session")
        def should_be_accent_sensitive(self, app):
            # given
            user_offerer = offerers_factories.UserOffererFactory()
            expected_offer = factories.OfferFactory(name="ocean", venue__managingOfferer=user_offerer.offerer)
            other_offer = factories.OfferFactory(name="océan", venue__managingOfferer=user_offerer.offerer)

            # when
            offers = repository.get_capped_offers_for_filters(
                user_id=user_offerer.user.id,
                user_is_admin=user_offerer.user.has_admin_role,
                offers_limit=10,
                name_keywords_or_isbn="ocean",
            )

            # then
            offers_id = [offer.id for offer in offers.offers]
            assert expected_offer.id in offers_id
            assert other_offer.id not in offers_id
            assert len(offers.offers) == 1

        @pytest.mark.usefixtures("db_session")
        def should_return_offer_which_isbn_is_equally_to_name_keyword_or_isbn(self, app):
            # given
            user_offerer = offerers_factories.UserOffererFactory()
            expected_offer = factories.OfferFactory(
                name="seras-tu là", venue__managingOfferer=user_offerer.offerer, extraData={"isbn": "1234567891234"}
            )
            other_offer = factories.OfferFactory(
                name="François, seras-tu là ?",
                venue__managingOfferer=user_offerer.offerer,
                extraData={"isbn": "1234567891235"},
            )

            # when
            offers = repository.get_capped_offers_for_filters(
                user_id=user_offerer.user.id,
                user_is_admin=user_offerer.user.has_admin_role,
                offers_limit=10,
                name_keywords_or_isbn="1234567891234",
            )

            # then
            offers_id = [offer.id for offer in offers.offers]
            assert expected_offer.id in offers_id
            assert other_offer.id not in offers_id
            assert len(offers.offers) == 1

    class StatusFiltersTest:
        def init_test_data(self):
            self.venue = offerers_factories.VenueFactory()
            self.offerer = self.venue.managingOfferer
            self.other_venue = offerers_factories.VenueFactory(managingOfferer=self.offerer)
            self.pro = users_factories.ProFactory()
            self.user_offerer = offerers_factories.UserOffererFactory(user=self.pro, offerer=self.offerer)

            self.sold_out_offer_on_other_venue = factories.ThingOfferFactory(
                venue=self.other_venue, description="sold_out_offer_on_other_venue"
            )
            self.inactive_thing_offer_with_stock_with_remaining_quantity = factories.ThingOfferFactory(
                venue=self.venue, isActive=False, description="inactive_thing_offer_with_stock_with_remaining_quantity"
            )
            self.inactive_thing_offer_without_remaining_quantity = factories.ThingOfferFactory(
                venue=self.venue, isActive=False, description="inactive_thing_offer_without_remaining_quantity"
            )
            self.inactive_thing_offer_without_stock = factories.ThingOfferFactory(
                venue=self.venue, isActive=False, description="inactive_thing_offer_without_stock"
            )
            self.inactive_expired_event_offer = factories.EventOfferFactory(
                venue=self.venue, isActive=False, description="inactive_expired_event_offer"
            )
            self.active_thing_offer_with_one_stock_with_remaining_quantity = factories.ThingOfferFactory(
                venue=self.venue, isActive=True, description="active_thing_offer_with_one_stock_with_remaining_quantity"
            )
            self.active_thing_offer_with_all_stocks_without_quantity = factories.ThingOfferFactory(
                venue=self.venue, isActive=True, description="active_thing_offer_with_all_stocks_without_quantity"
            )
            self.active_event_offer_with_stock_in_the_future_without_quantity = factories.EventOfferFactory(
                venue=self.venue, description="active_event_offer_with_stock_in_the_future_without_quantity"
            )
            self.active_event_offer_with_one_stock_in_the_future_with_remaining_quantity = factories.EventOfferFactory(
                venue=self.venue,
                description="active_event_offer_with_one_stock_in_the_future_with_remaining_quantity",
            )
            self.sold_old_thing_offer_with_all_stocks_empty = factories.ThingOfferFactory(
                venue=self.venue, description="sold_old_thing_offer_with_all_stocks_empty"
            )
            self.sold_out_event_offer_with_all_stocks_in_the_future_with_zero_remaining_quantity = (
                factories.EventOfferFactory(
                    venue=self.venue,
                    description="sold_out_event_offer_with_all_stocks_in_the_future_with_zero_remaining_quantity",
                )
            )
            self.sold_out_thing_offer_without_stock = factories.ThingOfferFactory(
                venue=self.venue, description="sold_out_thing_offer_without_stock"
            )
            self.sold_out_event_offer_without_stock = factories.EventOfferFactory(
                venue=self.venue, description="sold_out_event_offer_without_stock"
            )
            self.sold_out_event_offer_with_only_one_stock_soft_deleted = factories.EventOfferFactory(
                venue=self.venue, description="sold_out_event_offer_with_only_one_stock_soft_deleted"
            )
            self.expired_event_offer_with_stock_in_the_past_without_quantity = factories.EventOfferFactory(
                venue=self.venue, description="expired_event_offer_with_stock_in_the_past_without_quantity"
            )
            self.expired_event_offer_with_all_stocks_in_the_past_with_remaining_quantity = factories.EventOfferFactory(
                venue=self.venue,
                description="expired_event_offer_with_all_stocks_in_the_past_with_remaining_quantity",
            )
            self.expired_event_offer_with_all_stocks_in_the_past_with_zero_remaining_quantity = (
                factories.EventOfferFactory(
                    venue=self.venue,
                    description="expired_event_offer_with_all_stocks_in_the_past_with_zero_remaining_quantity",
                )
            )
            self.expired_thing_offer_with_a_stock_expired_with_remaining_quantity = factories.EventOfferFactory(
                venue=self.venue,
                description="expired_thing_offer_with_a_stock_expired_with_remaining_quantity",
            )
            self.expired_thing_offer_with_a_stock_expired_with_zero_remaining_quantity = factories.EventOfferFactory(
                venue=self.venue,
                description="expired_thing_offer_with_a_stock_expired_with_zero_remaining_quantity",
            )

            five_days_ago = datetime.utcnow() - timedelta(days=5)
            in_five_days = datetime.utcnow() + timedelta(days=5)
            beneficiary = users_factories.BeneficiaryGrant18Factory(email="jane.doe@example.com")
            factories.ThingStockFactory(offer=self.sold_old_thing_offer_with_all_stocks_empty, quantity=0)
            factories.ThingStockFactory(
                offer=self.active_thing_offer_with_one_stock_with_remaining_quantity, quantity=5
            )
            factories.ThingStockFactory(
                offer=self.active_thing_offer_with_one_stock_with_remaining_quantity, quantity=0
            )
            factories.ThingStockFactory(offer=self.active_thing_offer_with_all_stocks_without_quantity, quantity=None)
            factories.EventStockFactory(
                offer=self.expired_event_offer_with_stock_in_the_past_without_quantity,
                beginningDatetime=five_days_ago,
                bookingLimitDatetime=five_days_ago,
                quantity=None,
            )
            factories.EventStockFactory(
                offer=self.expired_event_offer_with_stock_in_the_past_without_quantity,
                beginningDatetime=in_five_days,
                bookingLimitDatetime=in_five_days,
                quantity=None,
                isSoftDeleted=True,
            )
            factories.EventStockFactory(
                offer=self.active_event_offer_with_stock_in_the_future_without_quantity,
                beginningDatetime=in_five_days,
                bookingLimitDatetime=in_five_days,
                quantity=None,
            )
            factories.EventStockFactory(
                offer=self.expired_event_offer_with_all_stocks_in_the_past_with_remaining_quantity,
                beginningDatetime=five_days_ago,
                bookingLimitDatetime=five_days_ago,
                quantity=5,
            )
            factories.EventStockFactory(
                offer=self.expired_event_offer_with_all_stocks_in_the_past_with_remaining_quantity,
                beginningDatetime=five_days_ago,
                bookingLimitDatetime=five_days_ago,
                quantity=4,
            )
            stock_with_some_bookings = factories.EventStockFactory(
                offer=self.active_event_offer_with_one_stock_in_the_future_with_remaining_quantity,
                beginningDatetime=in_five_days,
                bookingLimitDatetime=in_five_days,
                quantity=1,
            )
            bookings_factories.CancelledBookingFactory(user=beneficiary, stock=stock_with_some_bookings)
            factories.EventStockFactory(
                offer=self.active_event_offer_with_one_stock_in_the_future_with_remaining_quantity,
                beginningDatetime=in_five_days,
                bookingLimitDatetime=in_five_days,
                quantity=0,
            )
            factories.EventStockFactory(
                offer=self.expired_event_offer_with_all_stocks_in_the_past_with_zero_remaining_quantity,
                beginningDatetime=five_days_ago,
                bookingLimitDatetime=five_days_ago,
                quantity=0,
            )
            factories.EventStockFactory(
                offer=self.expired_event_offer_with_all_stocks_in_the_past_with_zero_remaining_quantity,
                beginningDatetime=five_days_ago,
                bookingLimitDatetime=five_days_ago,
                quantity=0,
            )
            factories.EventStockFactory(
                offer=self.sold_out_event_offer_with_all_stocks_in_the_future_with_zero_remaining_quantity,
                beginningDatetime=five_days_ago,
                bookingLimitDatetime=five_days_ago,
                quantity=5,
            )
            stock_all_booked = factories.EventStockFactory(
                offer=self.sold_out_event_offer_with_all_stocks_in_the_future_with_zero_remaining_quantity,
                beginningDatetime=in_five_days,
                bookingLimitDatetime=in_five_days,
                quantity=1,
                price=0,
            )
            bookings_factories.BookingFactory(user=beneficiary, stock=stock_all_booked)
            factories.ThingStockFactory(offer=self.inactive_thing_offer_with_stock_with_remaining_quantity, quantity=4)
            factories.EventStockFactory(
                offer=self.active_event_offer_with_stock_in_the_future_without_quantity,
                beginningDatetime=five_days_ago,
                bookingLimitDatetime=five_days_ago,
                quantity=None,
            )
            factories.EventStockFactory(
                offer=self.inactive_expired_event_offer,
                beginningDatetime=five_days_ago,
                bookingLimitDatetime=five_days_ago,
                quantity=None,
            )
            factories.ThingStockFactory(offer=self.inactive_thing_offer_without_remaining_quantity, quantity=0)
            factories.EventStockFactory(
                offer=self.sold_out_event_offer_with_only_one_stock_soft_deleted, quantity=10, isSoftDeleted=True
            )
            factories.ThingStockFactory(
                offer=self.expired_thing_offer_with_a_stock_expired_with_remaining_quantity,
                bookingLimitDatetime=five_days_ago,
                quantity=4,
            )
            factories.ThingStockFactory(
                offer=self.expired_thing_offer_with_a_stock_expired_with_zero_remaining_quantity,
                bookingLimitDatetime=five_days_ago,
                quantity=0,
            )
            in_six_days = datetime.utcnow() + timedelta(days=6)
            self.active_event_in_six_days_offer = factories.EventOfferFactory(venue=self.venue)
            factories.EventStockFactory(
                offer=self.active_event_in_six_days_offer,
                beginningDatetime=in_six_days,
                bookingLimitDatetime=in_six_days,
                quantity=10,
            )
            self.draft_offer = factories.EventOfferFactory(
                venue=self.venue, validation=offer_mixin.OfferValidationStatus.DRAFT, description="draft event offer"
            )

        @pytest.mark.usefixtures("db_session")
        def should_return_only_active_offers_when_requesting_active_status(self):
            # given
            self.init_test_data()

            # when
            offers = repository.get_capped_offers_for_filters(
                user_id=self.pro.id, user_is_admin=self.pro.has_admin_role, offers_limit=5, status="ACTIVE"
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
            offers = repository.get_capped_offers_for_filters(
                user_id=self.pro.id, user_is_admin=self.pro.has_admin_role, offers_limit=5, status="INACTIVE"
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
            offers = repository.get_capped_offers_for_filters(
                user_id=self.pro.id, user_is_admin=self.pro.has_admin_role, offers_limit=10, status="SOLD_OUT"
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
            offers = repository.get_capped_offers_for_filters(
                user_id=self.pro.id, user_is_admin=self.pro.has_admin_role, offers_limit=10, status="SOLD_OUT"
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
            offers = repository.get_capped_offers_for_filters(
                user_id=self.pro.id, user_is_admin=self.pro.has_admin_role, offers_limit=5, status="SOLD_OUT"
            )

            # then
            offer_ids = [offer.id for offer in offers.offers]
            assert self.sold_old_thing_offer_with_all_stocks_empty.id in offer_ids

        @pytest.mark.usefixtures("db_session")
        def should_return_offers_with_no_remaining_quantity_in_the_future_when_requesting_sold_out_status(self):
            # given
            self.init_test_data()

            # when
            offers = repository.get_capped_offers_for_filters(
                user_id=self.pro.id, user_is_admin=self.pro.has_admin_role, offers_limit=5, status="SOLD_OUT"
            )

            # then
            offer_ids = [offer.id for offer in offers.offers]
            assert self.sold_out_event_offer_with_all_stocks_in_the_future_with_zero_remaining_quantity.id in offer_ids

        @pytest.mark.usefixtures("db_session")
        def should_exclude_offers_with_cancelled_bookings_when_requesting_sold_out_status(self):
            # given
            self.init_test_data()

            # when
            offers = repository.get_capped_offers_for_filters(
                user_id=self.pro.id, user_is_admin=self.pro.has_admin_role, offers_limit=5, status="SOLD_OUT"
            )

            # then
            offer_ids = [offer.id for offer in offers.offers]
            assert self.active_event_offer_with_one_stock_in_the_future_with_remaining_quantity.id not in offer_ids

        @pytest.mark.usefixtures("db_session")
        def should_return_only_expired_offers_when_requesting_expired_status(self):
            # given
            self.init_test_data()

            # when
            offers = repository.get_capped_offers_for_filters(
                user_id=self.pro.id, user_is_admin=self.pro.has_admin_role, offers_limit=5, status="EXPIRED"
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

            pending_offer = factories.ThingOfferFactory(
                validation=offer_mixin.OfferStatus.PENDING.name, name="Offre en attente"
            )
            factories.StockFactory(bookingLimitDatetime=unexpired_booking_limit_date, offer=pending_offer)

            offer = factories.OfferFactory(product__subcategoryId=subcategories.ACHAT_INSTRUMENT.id)
            factories.StockFactory(bookingLimitDatetime=unexpired_booking_limit_date, offer=offer)

            user = pending_offer.venue.managingOfferer

            # when
            offers = repository.get_capped_offers_for_filters(
                user_id=user.id, user_is_admin=True, offers_limit=5, status="PENDING"
            )

            # then
            assert len(offers.offers) == 1
            assert offers.offers[0].name == "Offre en attente"
            assert offers.offers[0].status == offer_mixin.OfferStatus.PENDING.name

        @pytest.mark.usefixtures("db_session")
        def should_return_only_rejected_offers_when_requesting_rejected_status(self):
            # given
            unexpired_booking_limit_date = datetime.utcnow() + timedelta(days=3)

            rejected_offer = factories.ThingOfferFactory(
                validation=offer_mixin.OfferValidationStatus.REJECTED, name="Offre rejetée", isActive=False
            )
            factories.StockFactory(bookingLimitDatetime=unexpired_booking_limit_date, offer=rejected_offer)

            offer = factories.OfferFactory(product__subcategoryId=subcategories.ACHAT_INSTRUMENT.id)
            factories.StockFactory(bookingLimitDatetime=unexpired_booking_limit_date, offer=offer)

            user = rejected_offer.venue.managingOfferer

            # when
            offers = repository.get_capped_offers_for_filters(
                user_id=user.id, user_is_admin=True, offers_limit=5, status="REJECTED"
            )

            # then
            assert len(offers.offers) == 1
            assert offers.offers[0].name == "Offre rejetée"
            assert offers.offers[0].status == offer_mixin.OfferStatus.REJECTED.name

        @pytest.mark.usefixtures("db_session")
        def should_return_only_sold_out_offers_and_requested_venue_when_requesting_sold_out_status_and_specific_venue(
            self,
        ):
            # given
            self.init_test_data()

            # when
            offers = repository.get_capped_offers_for_filters(
                user_id=self.pro.id,
                user_is_admin=self.pro.has_admin_role,
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

            in_six_days = datetime.utcnow() + timedelta(days=6)
            in_six_days_beginning = in_six_days.replace(hour=0, minute=0, second=0)
            in_six_days_ending = in_six_days.replace(hour=23, minute=59, second=59)

            # when
            offers = repository.get_capped_offers_for_filters(
                user_id=self.pro.id,
                user_is_admin=self.pro.has_admin_role,
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
        offer1 = factories.OfferFactory()
        offerer = offer1.venue.managingOfferer
        user_offerer = offerers_factories.UserOffererFactory(offerer=offerer)
        user = user_offerer.user
        offer2 = factories.OfferFactory()

        query = repository.get_offers_by_ids(user, [offer1.id, offer2.id])

        assert query.count() == 1
        assert query.one() == offer1

    def test_return_all_for_admins(self):
        offer1 = factories.OfferFactory()
        offer2 = factories.OfferFactory()
        user = users_factories.AdminFactory()

        query = repository.get_offers_by_ids(user, [offer1.id, offer2.id])

        assert query.count() == 2


@pytest.mark.usefixtures("db_session")
class GetActiveOffersCountForVenueTest:
    def test_counts_active_offers_for_venue(self):
        # Given
        venue = offerers_factories.VenueFactory()

        active_offer = factories.ThingOfferFactory(venue=venue)
        factories.StockFactory(offer=active_offer)
        other_active_offer = factories.EventOfferFactory(venue=venue)
        factories.EventStockFactory(offer=other_active_offer)
        factories.EventStockFactory(offer=other_active_offer)

        sold_out_offer = factories.ThingOfferFactory(venue=venue)
        sold_out_stock = factories.StockFactory(quantity=1, offer=sold_out_offer)
        bookings_factories.BookingFactory(stock=sold_out_stock)

        expired_offer = factories.EventOfferFactory(venue=venue)
        yesterday = datetime.utcnow() - timedelta(days=1)
        factories.EventStockFactory(offer=expired_offer, bookingLimitDatetime=yesterday)

        inactive_offer = factories.ThingOfferFactory(venue=venue, isActive=False)
        factories.StockFactory(offer=inactive_offer)

        active_offer_on_another_venue = factories.ThingOfferFactory()
        factories.StockFactory(offer=active_offer_on_another_venue)

        # When
        active_offers_count = repository.get_active_offers_count_for_venue(venue.id)

        # Then
        assert active_offers_count == 2


@pytest.mark.usefixtures("db_session")
class GetSoldOutOffersCountForVenueTest:
    def test_counts_sold_out_offers_for_venue(self):
        # Given
        venue = offerers_factories.VenueFactory()

        active_offer = factories.ThingOfferFactory(venue=venue)
        factories.StockFactory(offer=active_offer)

        sold_out_offer = factories.ThingOfferFactory(venue=venue)
        sold_out_stock = factories.StockFactory(quantity=1, offer=sold_out_offer)
        bookings_factories.BookingFactory(stock=sold_out_stock)
        other_sold_out_offer = factories.EventOfferFactory(venue=venue)
        other_sold_out_stock = factories.EventStockFactory(quantity=1, offer=other_sold_out_offer)
        bookings_factories.BookingFactory(stock=other_sold_out_stock)
        factories.EventStockFactory(quantity=0, offer=other_sold_out_offer)

        expired_offer = factories.EventOfferFactory(venue=venue)
        yesterday = datetime.utcnow() - timedelta(days=1)
        factories.EventStockFactory(offer=expired_offer, bookingLimitDatetime=yesterday)

        inactive_offer = factories.ThingOfferFactory(venue=venue, isActive=False)
        factories.StockFactory(offer=inactive_offer)

        active_offer_on_another_venue = factories.ThingOfferFactory()
        factories.StockFactory(offer=active_offer_on_another_venue)

        # When
        sold_out_offers_count = repository.get_sold_out_offers_count_for_venue(venue.id)

        # Then
        assert sold_out_offers_count == 2


@pytest.mark.usefixtures("db_session")
class CheckStockConsistenceTest:
    def test_with_inconsistencies(self):
        # consistent stock without booking
        factories.StockFactory(dnBookedQuantity=0)
        # inconsistent stock without booking
        stock2 = factories.StockFactory(dnBookedQuantity=5)

        # consistent stock with booking
        stock3_bookings = bookings_factories.BookingFactory(quantity=2, stock__dnBookedQuantity=3)
        stock3 = stock3_bookings.stock
        stock3.dnBookedQuantity = 2
        # inconsistent stock with booking
        stock4_bookings = bookings_factories.BookingFactory(quantity=2)
        stock4 = stock4_bookings.stock
        stock4.dnBookedQuantity = 5

        # consistent stock with cancelled booking
        stock5_bookings = bookings_factories.CancelledBookingFactory(quantity=2)
        stock5 = stock5_bookings.stock
        stock5.dnBookedQuantity = 0
        # inconsistent stock with cancelled booking
        stock6_bookings = bookings_factories.CancelledBookingFactory(quantity=2)
        stock6 = stock6_bookings.stock
        stock6.dnBookedQuantity = 2

        db_repository.save(stock3, stock4, stock5, stock6)

        stock_ids = set(repository.check_stock_consistency())
        assert stock_ids == {stock2.id, stock4.id, stock6.id}


@pytest.mark.usefixtures("db_session")
class IncomingEventStocksTest:
    def setup_stocks(self):
        today = datetime.utcnow() + timedelta(hours=1)
        tomorrow = datetime.utcnow() + timedelta(days=1)
        next_week = datetime.utcnow() + timedelta(days=7)

        self.stock_today = factories.EventStockFactory(beginningDatetime=today)
        bookings_factories.BookingFactory.create_batch(2, stock=self.stock_today)

        offer = factories.OfferFactory(venue__departementCode="97", venue__postalCode="97180")
        self.stock_today_overseas = factories.EventStockFactory(beginningDatetime=today, offer=offer)
        bookings_factories.BookingFactory(stock=self.stock_today_overseas)

        self.stock_today_cancelled = factories.EventStockFactory(beginningDatetime=today)
        bookings_factories.CancelledBookingFactory(stock=self.stock_today_cancelled)

        self.stock_tomorrow = factories.EventStockFactory(beginningDatetime=tomorrow)
        bookings_factories.BookingFactory(stock=self.stock_tomorrow)

        self.stock_tomorrow_cancelled = factories.EventStockFactory(beginningDatetime=tomorrow)
        bookings_factories.CancelledBookingFactory(stock=self.stock_tomorrow_cancelled)

        self.stock_next_week = factories.EventStockFactory(beginningDatetime=next_week)
        bookings_factories.BookingFactory(stock=self.stock_next_week)

    def test_find_tomorrow_event_stock_ids(self):
        self.setup_stocks()

        query = repository.find_event_stocks_happening_in_x_days(number_of_days=1).with_entities(models.Stock.id)
        assert {stock_id for stock_id, in query} == {self.stock_tomorrow.id}

    def test_find_event_stocks_happening_in_7_days(self):
        self.setup_stocks()

        query = repository.find_event_stocks_happening_in_x_days(number_of_days=7)
        assert {stock.id for stock in query} == {self.stock_next_week.id}

    @freeze_time("2020-10-15 15:00:00")
    def test_find_today_event_stock_ids_metropolitan_france(self):
        self.setup_stocks()

        today_min = datetime(2020, 10, 15, 12, 00)
        today_max = datetime(2020, 10, 15, 23, 00)

        stock_ids = repository.find_today_event_stock_ids_metropolitan_france(today_min, today_max)

        assert set(stock_ids) == {self.stock_today.id}

    @freeze_time("2020-10-15 15:00:00")
    def test_find_today_event_stock_ids_by_departments(self):
        self.setup_stocks()

        today_min = datetime(2020, 10, 15, 8, 00)
        today_max = datetime(2020, 10, 15, 19, 00)

        departments_prefixes = ["971"]

        stock_ids = repository.find_today_event_stock_ids_from_departments(today_min, today_max, departments_prefixes)

        assert set(stock_ids) == {self.stock_today_overseas.id}


@pytest.mark.usefixtures("db_session")
class GetExpiredOffersTest:
    interval = [datetime(2021, 1, 1, 0, 0), datetime(2021, 1, 2, 0, 0)]
    dt_before = datetime(2020, 12, 31)
    dt_within = datetime(2021, 1, 1)
    dt_after = datetime(2021, 1, 3)

    def test_basics(self):
        offer1 = factories.OfferFactory()
        factories.StockFactory(offer=offer1, bookingLimitDatetime=self.dt_within)
        offer2 = factories.OfferFactory()
        factories.StockFactory(offer=offer2, bookingLimitDatetime=self.dt_within)
        factories.StockFactory(offer=offer2, bookingLimitDatetime=self.dt_within)
        offer3 = factories.OfferFactory()
        factories.StockFactory(offer=offer3, bookingLimitDatetime=self.dt_before)
        factories.StockFactory(offer=offer3, bookingLimitDatetime=self.dt_within)
        factories.StockFactory(bookingLimitDatetime=None)
        factories.StockFactory(bookingLimitDatetime=self.dt_before)
        factories.StockFactory(bookingLimitDatetime=self.dt_after)

        offers = repository.get_expired_offers(self.interval)

        assert offers.all() == [offer1, offer2, offer3]

    def test_exclude_if_latest_stock_outside_interval(self):
        offer1 = factories.OfferFactory()
        factories.StockFactory(offer=offer1, bookingLimitDatetime=self.dt_within)
        offer2 = factories.OfferFactory()
        factories.StockFactory(offer=offer2, bookingLimitDatetime=self.dt_within)
        factories.StockFactory(offer=offer2, bookingLimitDatetime=self.dt_after)

        offers = repository.get_expired_offers(self.interval)

        assert offers.all() == [offer1]


@pytest.mark.usefixtures("db_session")
class DeletePastDraftOfferTest:
    @freeze_time("2020-10-15 09:00:00")
    def test_delete_past_draft_offers(self):
        two_days_ago = datetime.utcnow() - timedelta(days=2)
        criterion = criteria_factories.CriterionFactory()
        offer = factories.OfferFactory(
            dateCreated=two_days_ago, validation=offer_mixin.OfferValidationStatus.DRAFT, criteria=[criterion]
        )
        factories.MediationFactory(offer=offer)
        past_offer = factories.OfferFactory(
            dateCreated=two_days_ago, validation=offer_mixin.OfferValidationStatus.PENDING
        )
        today_offer = factories.OfferFactory(
            dateCreated=datetime.utcnow(), validation=offer_mixin.OfferValidationStatus.DRAFT
        )

        repository.delete_past_draft_offers()

        offers = models.Offer.query.all()
        assert set(offers) == {today_offer, past_offer}

    @freeze_time("2020-10-15 09:00:00")
    def test_delete_past_draft_collective_offers(self):
        two_days_ago = datetime.utcnow() - timedelta(days=2)
        educational_factories.CollectiveOfferFactory(
            dateCreated=two_days_ago, validation=offer_mixin.OfferValidationStatus.DRAFT
        )
        past_offer = educational_factories.CollectiveOfferFactory(
            dateCreated=two_days_ago, validation=offer_mixin.OfferValidationStatus.PENDING
        )
        today_offer = educational_factories.CollectiveOfferFactory(
            dateCreated=datetime.utcnow(), validation=offer_mixin.OfferValidationStatus.DRAFT
        )
        # past offer with collective stock but user did not finalize offer creation
        # with institution association
        educational_factories.CollectiveStockFactory(
            collectiveOffer__dateCreated=two_days_ago,
            collectiveOffer__validation=offer_mixin.OfferValidationStatus.DRAFT,
        )

        repository.delete_past_draft_collective_offers()

        collective_offers = educational_models.CollectiveOffer.query.all()
        assert set(collective_offers) == {today_offer, past_offer}


@pytest.mark.usefixtures("db_session")
class AvailableActivationCodeTest:
    def test_activation_code_is_available_for_a_stock(self):
        # GIVEN
        booking = bookings_factories.BookingFactory()
        stock = booking.stock
        factories.ActivationCodeFactory(booking=booking, stock=stock)  # booked_code
        not_booked_code = factories.ActivationCodeFactory(stock=stock)

        # WHEN
        found_code = repository.get_available_activation_code(stock)

        # THEN
        assert found_code.id == not_booked_code.id

    def test_expired_activation_code_is_not_available_for_a_stock(self):
        # GIVEN
        booking = bookings_factories.BookingFactory()
        stock = booking.stock
        factories.ActivationCodeFactory(booking=booking, stock=stock)  # booked_code
        factories.ActivationCodeFactory(
            stock=stock, expirationDate=datetime.utcnow() - timedelta(days=1)
        )  # expired code

        # WHEN THEN
        assert not repository.get_available_activation_code(stock)

    def test_activation_code_of_a_stock_is_not_available_for_another_stock(self):
        booking = bookings_factories.BookingFactory()
        booking2 = bookings_factories.BookingFactory()
        stock = booking.stock
        stock2 = booking2.stock
        factories.ActivationCodeFactory(stock=stock2)

        assert not repository.get_available_activation_code(stock)


@pytest.mark.usefixtures("db_session")
class GetCollectiveOffersTemplateByFiltersTest:
    def test_status_filter_no_crash(self):
        # given
        user = users_factories.AdminFactory()
        template = educational_factories.CollectiveOfferTemplateFactory()
        educational_factories.CollectiveOfferTemplateFactory(validation=offer_mixin.OfferValidationStatus.REJECTED)
        # when
        result = repository.get_collective_offers_template_by_filters(
            user_id=user.id,
            user_is_admin=True,
            status=offer_mixin.OfferStatus.ACTIVE.name,
        ).all()
        # then
        assert len(result) == 1
        assert result[0].id == template.id
