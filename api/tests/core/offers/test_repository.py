import datetime
import logging
from unittest.mock import patch

import pytest
import sqlalchemy as sqla
import sqlalchemy.exc as sa_exc
import sqlalchemy.orm as sa_orm
import time_machine

import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.providers.constants as providers_constants
import pcapi.core.providers.factories as providers_factories
import pcapi.repository.repository as db_repository
from pcapi.core.categories import pro_categories
from pcapi.core.categories import subcategories
from pcapi.core.geography import factories as geography_factories
from pcapi.core.offers import exceptions
from pcapi.core.offers import factories
from pcapi.core.offers import models
from pcapi.core.offers import repository
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import factories as users_factories
from pcapi.models import db
from pcapi.models import offer_mixin
from pcapi.utils.date import utc_datetime_to_department_timezone


class GetCappedOffersForFiltersTest:
    @pytest.mark.usefixtures("db_session")
    def test_perf_offers_capped_to_max_offers_count(self):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offer = factories.OfferFactory(venue=venue)
        factories.ThingStockFactory(offer=offer)
        factories.MediationFactory(offer=offer)
        provider = providers_factories.AllocineProviderFactory()
        factories.OfferFactory(venue=venue, lastProvider=provider)
        product = factories.ProductFactory()
        factories.OfferFactory(venue=venue, product=product)
        event = factories.EventOfferFactory(venue=venue)
        factories.EventStockFactory(offer=event)
        digital_event = factories.DigitalOfferFactory(venue=venue)
        factories.StockFactory(offer=digital_event)

        # 1 to get user
        # 1 to get user_offerer
        # 1 to get offers
        with assert_num_queries(3):
            offers = repository.get_capped_offers_for_filters(
                user_id=user_offerer.user.id,
                user_is_admin=user_offerer.user.has_admin_role,
                offers_limit=50,
            )

        assert len(offers) == 5

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
        assert len(offers) == 1

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
        assert offers[0].id > offers[1].id

    @pytest.mark.usefixtures("db_session")
    def should_include_draft_offers_when_requesting_all_offers(self, app):
        # given
        user_offerer = offerers_factories.UserOffererFactory()
        non_draft_offer = factories.OfferFactory(venue__managingOfferer=user_offerer.offerer)
        draft_offer = factories.OfferFactory(
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
        offers_id = {offer.id for offer in offers}
        assert offers_id == {non_draft_offer.id, draft_offer.id}

    @pytest.mark.usefixtures("db_session")
    def should_return_offers_of_given_subcategory_id(self):
        user_offerer = offerers_factories.UserOffererFactory()
        requested_offer = factories.OfferFactory(
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
            venue__managingOfferer=user_offerer.offerer,
        )
        # other offer
        factories.OfferFactory(
            subcategoryId=subcategories.JEU_SUPPORT_PHYSIQUE.id,
            venue__managingOfferer=user_offerer.offerer,
        )

        offers = repository.get_capped_offers_for_filters(
            user_id=user_offerer.user.id,
            user_is_admin=user_offerer.user.has_admin_role,
            offers_limit=10,
            category_id=pro_categories.FILM.id,
        )

        # then
        assert len(offers) == 1
        assert requested_offer.id == offers[0].id

    @pytest.mark.usefixtures("db_session")
    def test_filter_on_creation_mode(self):
        venue = offerers_factories.VenueFactory()
        manual_offer = factories.OfferFactory(venue=venue)
        provider = providers_factories.ProviderFactory()
        synced_offer = factories.OfferFactory(venue=venue, lastProvider=provider)
        pro_user = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=venue.managingOfferer)

        offers = repository.get_capped_offers_for_filters(
            user_id=pro_user.id,
            user_is_admin=False,
            offers_limit=10,
            creation_mode="manual",
        )
        assert len(offers) == 1
        assert offers[0].id == manual_offer.id

        offers = repository.get_capped_offers_for_filters(
            user_id=pro_user.id,
            user_is_admin=False,
            offers_limit=10,
            creation_mode="imported",
        )
        assert len(offers) == 1
        assert offers[0].id == synced_offer.id

    @pytest.mark.usefixtures("db_session")
    def should_not_return_event_offers_with_only_deleted_stock_if_filtering_by_time_period(
        self,
    ):
        # given
        pro = users_factories.ProFactory()
        offer_in_requested_time_period = factories.OfferFactory()
        factories.EventStockFactory(
            offer=offer_in_requested_time_period,
            beginningDatetime=datetime.datetime(2020, 1, 2),
            isSoftDeleted=True,
        )

        # When
        offers = repository.get_capped_offers_for_filters(
            user_id=pro.id,
            user_is_admin=pro.has_admin_role,
            offers_limit=10,
            period_beginning_date="2020-01-01T00:00:00",
        )

        # then
        assert len(offers) == 0

    @pytest.mark.usefixtures("db_session")
    def should_consider_venue_locale_datetime_when_filtering_by_date(self):
        # given
        admin = users_factories.AdminFactory()
        period_beginning_date = datetime.date(2020, 4, 21)
        period_ending_date = datetime.date(2020, 4, 21)

        cayenne_offerer_address = offerers_factories.OffererAddressFactory(address__timezone="America/Cayenne")
        offer_in_cayenne = factories.OfferFactory(
            venue__postalCode="97300",
            offererAddress=cayenne_offerer_address,
        )
        cayenne_event_datetime = datetime.datetime(2020, 4, 22, 2, 0)
        factories.EventStockFactory(offer=offer_in_cayenne, beginningDatetime=cayenne_event_datetime)

        mayotte_offerer_address = offerers_factories.OffererAddressFactory(address__timezone="Indian/Mayotte")
        offer_in_mayotte = factories.OfferFactory(
            venue__postalCode="97600",
            offererAddress=mayotte_offerer_address,
        )
        mayotte_event_datetime = datetime.datetime(2020, 4, 20, 22, 0)
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
        offers_id = [offer.id for offer in offers]
        assert offer_in_cayenne.id in offers_id
        assert offer_in_mayotte.id in offers_id
        assert len(offers) == 2

        # Now ensures the offers are filtered out if we begin the search the day after
        offers = repository.get_capped_offers_for_filters(
            user_id=admin.id,
            user_is_admin=admin.has_admin_role,
            offers_limit=10,
            period_beginning_date=period_beginning_date + datetime.timedelta(days=1),
        )
        assert len(offers) == 0

        # Now ensures the offers are filtered out if we end the search the day before
        offers = repository.get_capped_offers_for_filters(
            user_id=admin.id,
            user_is_admin=admin.has_admin_role,
            offers_limit=10,
            period_ending_date=period_ending_date - datetime.timedelta(days=1),
        )
        assert len(offers) == 0

    class WhenUserIsAdminTest:
        @pytest.mark.usefixtures("db_session")
        def should_return_offers_of_given_venue_when_user_is_not_attached_to_its_offerer(self, app):
            # given
            admin = users_factories.AdminFactory()
            offer_for_requested_venue = factories.OfferFactory()
            # offer for other venue
            factories.OfferFactory()

            # when
            offers = repository.get_capped_offers_for_filters(
                user_id=admin.id,
                user_is_admin=admin.has_admin_role,
                offers_limit=10,
                venue_id=offer_for_requested_venue.venue.id,
            )

            # then
            assert len(offers) == 1
            assert offer_for_requested_venue.id == offers[0].id

        @pytest.mark.usefixtures("db_session")
        def should_return_offers_of_given_venue_when_user_is_attached_to_its_offerer(self, app):
            # given
            admin = users_factories.AdminFactory()
            admin_attachment_to_offerer = offerers_factories.UserOffererFactory(user=admin)
            offer_for_requested_venue = factories.OfferFactory(
                venue__managingOfferer=admin_attachment_to_offerer.offerer
            )
            # offer for other venue
            factories.OfferFactory(venue__managingOfferer=admin_attachment_to_offerer.offerer)

            # when
            offers = repository.get_capped_offers_for_filters(
                user_id=admin.id,
                user_is_admin=admin.has_admin_role,
                offers_limit=10,
                venue_id=offer_for_requested_venue.venue.id,
            )

            # then
            assert len(offers) == 1
            assert offer_for_requested_venue.id == offers[0].id

        @pytest.mark.usefixtures("db_session")
        def should_return_offers_of_given_offerer_when_user_is_not_attached_to_it(self):
            # given
            admin = users_factories.AdminFactory()
            offer_for_requested_offerer = factories.OfferFactory()
            # offer for other offerer
            factories.OfferFactory()

            # When
            offers = repository.get_capped_offers_for_filters(
                user_id=admin.id,
                user_is_admin=admin.has_admin_role,
                offers_limit=10,
                offerer_id=offer_for_requested_offerer.venue.managingOffererId,
            )

            # then
            assert len(offers) == 1
            assert offer_for_requested_offerer.id == offers[0].id

        @pytest.mark.usefixtures("db_session")
        def should_return_offers_of_given_offerer_when_user_is_attached_to_it(self):
            # given
            admin = users_factories.AdminFactory()
            admin_attachment_to_requested_offerer = offerers_factories.UserOffererFactory(user=admin)
            admin_attachment_to_other_offerer = offerers_factories.UserOffererFactory(user=admin)
            offer_for_requested_offerer = factories.OfferFactory(
                venue__managingOfferer=admin_attachment_to_requested_offerer.offerer
            )
            # offer for other offerer
            factories.OfferFactory(venue__managingOfferer=admin_attachment_to_other_offerer.offerer)

            # When
            offers = repository.get_capped_offers_for_filters(
                user_id=admin.id,
                user_is_admin=admin.has_admin_role,
                offers_limit=10,
                offerer_id=offer_for_requested_offerer.venue.managingOffererId,
            )

            # then
            assert len(offers) == 1
            assert offer_for_requested_offerer.id == offers[0].id

    class WhenUserIsProTest:
        @pytest.mark.usefixtures("db_session")
        def should_not_return_offers_of_given_venue_when_user_is_not_attached_to_its_offerer(self, app):
            # given
            pro = users_factories.ProFactory()
            offer_for_requested_venue = factories.OfferFactory()
            # offer for other venue
            factories.OfferFactory()

            # when
            offers = repository.get_capped_offers_for_filters(
                user_id=pro.id,
                user_is_admin=pro.has_admin_role,
                offers_limit=10,
                venue_id=offer_for_requested_venue.venue.id,
            )

            # then
            assert len(offers) == 0

        @pytest.mark.usefixtures("db_session")
        def should_return_offers_of_given_venue_when_user_is_attached_to_its_offerer(self, app):
            # given
            pro = users_factories.ProFactory()
            pro_attachment_to_offerer = offerers_factories.UserOffererFactory(user=pro)
            offer_for_requested_venue = factories.OfferFactory(venue__managingOfferer=pro_attachment_to_offerer.offerer)
            # offer for other venue
            factories.OfferFactory(venue__managingOfferer=pro_attachment_to_offerer.offerer)

            # when
            offers = repository.get_capped_offers_for_filters(
                user_id=pro.id,
                user_is_admin=pro.has_admin_role,
                offers_limit=10,
                venue_id=offer_for_requested_venue.venue.id,
            )

            # then
            assert len(offers) == 1
            assert offer_for_requested_venue.id == offers[0].id

        @pytest.mark.usefixtures("db_session")
        def should_not_return_offers_of_given_offerer_when_user_is_not_attached_to_it(
            self,
        ):
            # given
            pro = users_factories.ProFactory()
            offer_for_requested_offerer = factories.OfferFactory()
            # offer for other offerer
            factories.OfferFactory()

            # When
            offers = repository.get_capped_offers_for_filters(
                user_id=pro.id,
                user_is_admin=pro.has_admin_role,
                offers_limit=10,
                offerer_id=offer_for_requested_offerer.venue.managingOffererId,
            )

            # then
            assert len(offers) == 0

        @pytest.mark.usefixtures("db_session")
        def should_return_offers_of_given_offerer_when_user_is_attached_to_it(self):
            # given
            pro = users_factories.ProFactory()
            pro_attachment_to_requested_offerer = offerers_factories.UserOffererFactory(user=pro)
            pro_attachment_to_other_offerer = offerers_factories.UserOffererFactory(user=pro)
            offer_for_requested_offerer = factories.OfferFactory(
                venue__managingOfferer=pro_attachment_to_requested_offerer.offerer
            )
            # offer for other offerer
            factories.OfferFactory(venue__managingOfferer=pro_attachment_to_other_offerer.offerer)

            # When
            offers = repository.get_capped_offers_for_filters(
                user_id=pro.id,
                user_is_admin=pro.has_admin_role,
                offers_limit=10,
                offerer_id=offer_for_requested_offerer.venue.managingOffererId,
            )

            # then
            assert len(offers) == 1
            assert offer_for_requested_offerer.id == offers[0].id

    class NameOrIsbnFilterTest:
        @pytest.mark.usefixtures("db_session")
        def should_return_offer_which_name_equal_keyword_when_keyword_is_less_or_equal_than_3_letters(
            self,
        ):
            # given
            user_offerer = offerers_factories.UserOffererFactory()
            expected_offer = factories.OfferFactory(name="ocs", venue__managingOfferer=user_offerer.offerer)
            # other offer
            factories.OfferFactory(name="ocsir", venue__managingOfferer=user_offerer.offerer)

            # when
            offers = repository.get_capped_offers_for_filters(
                user_id=user_offerer.user.id,
                user_is_admin=user_offerer.user.has_admin_role,
                offers_limit=10,
                name_keywords_or_ean="ocs",
            )

            # then
            assert len(offers) == 1
            assert expected_offer.id == offers[0].id

        @pytest.mark.usefixtures("db_session")
        def should_return_offer_which_name_contains_keyword_when_keyword_is_more_than_3_letters(self, app):
            # given
            user_offerer = offerers_factories.UserOffererFactory()
            expected_offer = factories.OfferFactory(name="seras-tu là", venue__managingOfferer=user_offerer.offerer)
            another_expected_offer = factories.OfferFactory(
                name="François, seras-tu là ?",
                venue__managingOfferer=user_offerer.offerer,
            )
            other_offer = factories.OfferFactory(name="étais-tu là", venue__managingOfferer=user_offerer.offerer)

            # when
            offers = repository.get_capped_offers_for_filters(
                user_id=user_offerer.user.id,
                user_is_admin=user_offerer.user.has_admin_role,
                offers_limit=10,
                name_keywords_or_ean="seras-tu",
            )

            # then
            assert len(offers) == 2
            offers_id = [offer.id for offer in offers]
            assert expected_offer.id in offers_id
            assert another_expected_offer.id in offers_id
            assert other_offer.id not in offers_id

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
                name_keywords_or_ean="mon océan",
            )

            # then
            assert len(offers) == 2
            offers_id = [offer.id for offer in offers]
            assert expected_offer.id in offers_id
            assert another_expected_offer.id in offers_id

        @pytest.mark.usefixtures("db_session")
        def should_be_accent_sensitive(self, app):
            # given
            user_offerer = offerers_factories.UserOffererFactory()
            expected_offer = factories.OfferFactory(name="ocean", venue__managingOfferer=user_offerer.offerer)
            # other offer
            factories.OfferFactory(name="océan", venue__managingOfferer=user_offerer.offerer)

            # when
            offers = repository.get_capped_offers_for_filters(
                user_id=user_offerer.user.id,
                user_is_admin=user_offerer.user.has_admin_role,
                offers_limit=10,
                name_keywords_or_ean="ocean",
            )

            # then
            assert len(offers) == 1
            assert expected_offer.id == offers[0].id

        @pytest.mark.usefixtures("db_session")
        def should_return_offer_which_ean_is_equal_to_name_keyword_or_ean(self):
            # given
            user_offerer = offerers_factories.UserOffererFactory()
            expected_offer = factories.OfferFactory(
                name="seras-tu là",
                venue__managingOfferer=user_offerer.offerer,
                ean="1234567891234",
            )
            # other offer
            factories.OfferFactory(
                name="François, seras-tu là ?",
                venue__managingOfferer=user_offerer.offerer,
                ean="1234567891235",
            )

            # when
            offers = repository.get_capped_offers_for_filters(
                user_id=user_offerer.user.id,
                user_is_admin=user_offerer.user.has_admin_role,
                offers_limit=10,
                name_keywords_or_ean="1234567891234",
            )

            # then
            assert len(offers) == 1
            assert expected_offer.id == offers[0].id

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
                venue=self.venue,
                isActive=False,
                description="inactive_thing_offer_with_stock_with_remaining_quantity",
            )
            self.inactive_thing_offer_without_remaining_quantity = factories.ThingOfferFactory(
                venue=self.venue,
                isActive=False,
                description="inactive_thing_offer_without_remaining_quantity",
            )
            self.inactive_thing_offer_without_stock = factories.ThingOfferFactory(
                venue=self.venue,
                isActive=False,
                description="inactive_thing_offer_without_stock",
            )
            self.inactive_expired_event_offer = factories.EventOfferFactory(
                venue=self.venue,
                isActive=False,
                description="inactive_expired_event_offer",
            )
            self.active_thing_offer_with_one_stock_with_remaining_quantity = factories.ThingOfferFactory(
                venue=self.venue,
                isActive=True,
                description="active_thing_offer_with_one_stock_with_remaining_quantity",
            )
            self.active_thing_offer_with_all_stocks_without_quantity = factories.ThingOfferFactory(
                venue=self.venue,
                isActive=True,
                description="active_thing_offer_with_all_stocks_without_quantity",
            )
            self.active_event_offer_with_stock_in_the_future_without_quantity = factories.EventOfferFactory(
                venue=self.venue,
                description="active_event_offer_with_stock_in_the_future_without_quantity",
            )
            self.active_event_offer_with_one_stock_in_the_future_with_remaining_quantity = factories.EventOfferFactory(
                venue=self.venue,
                description="active_event_offer_with_one_stock_in_the_future_with_remaining_quantity",
            )
            self.sold_old_thing_offer_with_all_stocks_empty = factories.ThingOfferFactory(
                venue=self.venue,
                description="sold_old_thing_offer_with_all_stocks_empty",
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
                venue=self.venue,
                description="sold_out_event_offer_with_only_one_stock_soft_deleted",
            )
            self.expired_event_offer_with_stock_in_the_past_without_quantity = factories.EventOfferFactory(
                venue=self.venue,
                description="expired_event_offer_with_stock_in_the_past_without_quantity",
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

            five_days_ago = datetime.datetime.utcnow() - datetime.timedelta(days=5)
            in_five_days = datetime.datetime.utcnow() + datetime.timedelta(days=5)
            beneficiary = users_factories.BeneficiaryGrant18Factory(email="jane.doe@example.com")
            factories.ThingStockFactory(offer=self.sold_old_thing_offer_with_all_stocks_empty, quantity=0)
            factories.ThingStockFactory(
                offer=self.active_thing_offer_with_one_stock_with_remaining_quantity,
                quantity=5,
            )
            factories.ThingStockFactory(
                offer=self.active_thing_offer_with_one_stock_with_remaining_quantity,
                quantity=0,
            )
            factories.ThingStockFactory(
                offer=self.active_thing_offer_with_all_stocks_without_quantity,
                quantity=None,
            )
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
            factories.ThingStockFactory(
                offer=self.inactive_thing_offer_with_stock_with_remaining_quantity,
                quantity=4,
            )
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
                offer=self.sold_out_event_offer_with_only_one_stock_soft_deleted,
                quantity=10,
                isSoftDeleted=True,
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
            in_six_days = datetime.datetime.utcnow() + datetime.timedelta(days=6)
            self.active_event_in_six_days_offer = factories.EventOfferFactory(venue=self.venue)
            factories.EventStockFactory(
                offer=self.active_event_in_six_days_offer,
                beginningDatetime=in_six_days,
                bookingLimitDatetime=in_six_days,
                quantity=10,
            )
            self.draft_offer = factories.EventOfferFactory(
                venue=self.venue,
                validation=offer_mixin.OfferValidationStatus.DRAFT,
                description="draft event offer",
            )

        @pytest.mark.usefixtures("db_session")
        def should_return_only_active_offers_when_requesting_active_status(self):
            # given
            self.init_test_data()

            # when
            offers = repository.get_capped_offers_for_filters(
                user_id=self.pro.id,
                user_is_admin=self.pro.has_admin_role,
                offers_limit=5,
                status="ACTIVE",
            )

            # then
            offer_ids = [offer.id for offer in offers]
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
            assert len(offers) == 5

        @pytest.mark.usefixtures("db_session")
        def should_return_only_inactive_offers_when_requesting_inactive_status(self):
            # given
            self.init_test_data()

            # when
            offers = repository.get_capped_offers_for_filters(
                user_id=self.pro.id,
                user_is_admin=self.pro.has_admin_role,
                offers_limit=5,
                status="INACTIVE",
            )

            # then
            offer_ids = [offer.id for offer in offers]
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
            assert len(offers) == 4

        @pytest.mark.usefixtures("db_session")
        def should_return_only_sold_out_offers_when_requesting_sold_out_status(self):
            # given
            self.init_test_data()

            # when
            offers = repository.get_capped_offers_for_filters(
                user_id=self.pro.id,
                user_is_admin=self.pro.has_admin_role,
                offers_limit=10,
                status="SOLD_OUT",
            )

            # then
            offer_ids = [offer.id for offer in offers]
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
            assert len(offers) == 6

        @pytest.mark.usefixtures("db_session")
        def should_return_offers_with_no_stocks_when_requesting_sold_out_status(self):
            # given
            self.init_test_data()

            # when
            offers = repository.get_capped_offers_for_filters(
                user_id=self.pro.id,
                user_is_admin=self.pro.has_admin_role,
                offers_limit=10,
                status="SOLD_OUT",
            )

            # then
            offer_ids = [offer.id for offer in offers]
            assert self.sold_out_thing_offer_without_stock.id in offer_ids
            assert self.sold_out_event_offer_with_only_one_stock_soft_deleted.id in offer_ids

        @pytest.mark.usefixtures("db_session")
        def should_return_offers_with_no_remaining_quantity_and_no_bookings_when_requesting_sold_out_status(
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
            )

            # then
            offer_ids = [offer.id for offer in offers]
            assert self.sold_old_thing_offer_with_all_stocks_empty.id in offer_ids

        @pytest.mark.usefixtures("db_session")
        def should_return_offers_with_no_remaining_quantity_in_the_future_when_requesting_sold_out_status(
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
            )

            # then
            offer_ids = [offer.id for offer in offers]
            assert self.sold_out_event_offer_with_all_stocks_in_the_future_with_zero_remaining_quantity.id in offer_ids

        @pytest.mark.usefixtures("db_session")
        def should_exclude_offers_with_cancelled_bookings_when_requesting_sold_out_status(
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
            )

            # then
            offer_ids = [offer.id for offer in offers]
            assert self.active_event_offer_with_one_stock_in_the_future_with_remaining_quantity.id not in offer_ids

        @pytest.mark.usefixtures("db_session")
        def should_return_only_expired_offers_when_requesting_expired_status(self):
            # given
            self.init_test_data()

            # when
            offers = repository.get_capped_offers_for_filters(
                user_id=self.pro.id,
                user_is_admin=self.pro.has_admin_role,
                offers_limit=5,
                status="EXPIRED",
            )

            # then
            offer_ids = [offer.id for offer in offers]
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
            assert len(offers) == 5

        @pytest.mark.usefixtures("db_session")
        def should_return_only_pending_offers_when_requesting_pending_status(self):
            # given
            unexpired_booking_limit_date = datetime.datetime.utcnow() + datetime.timedelta(days=3)

            pending_offer = factories.ThingOfferFactory(
                validation=offer_mixin.OfferStatus.PENDING.name, name="Offre en attente"
            )
            factories.StockFactory(bookingLimitDatetime=unexpired_booking_limit_date, offer=pending_offer)

            offer = factories.OfferFactory(subcategoryId=subcategories.ACHAT_INSTRUMENT.id)
            factories.StockFactory(bookingLimitDatetime=unexpired_booking_limit_date, offer=offer)

            user = pending_offer.venue.managingOfferer

            # when
            offers = repository.get_capped_offers_for_filters(
                user_id=user.id, user_is_admin=True, offers_limit=5, status="PENDING"
            )

            # then
            assert len(offers) == 1
            assert offers[0].name == "Offre en attente"
            assert offers[0].status == offer_mixin.OfferStatus.PENDING.name

        @pytest.mark.usefixtures("db_session")
        def should_return_only_rejected_offers_when_requesting_rejected_status(self):
            # given
            unexpired_booking_limit_date = datetime.datetime.utcnow() + datetime.timedelta(days=3)

            rejected_offer = factories.ThingOfferFactory(
                validation=offer_mixin.OfferValidationStatus.REJECTED,
                name="Offre rejetée",
                isActive=False,
            )
            factories.StockFactory(bookingLimitDatetime=unexpired_booking_limit_date, offer=rejected_offer)

            offer = factories.OfferFactory(subcategoryId=subcategories.ACHAT_INSTRUMENT.id)
            factories.StockFactory(bookingLimitDatetime=unexpired_booking_limit_date, offer=offer)

            user = rejected_offer.venue.managingOfferer

            # when
            offers = repository.get_capped_offers_for_filters(
                user_id=user.id, user_is_admin=True, offers_limit=5, status="REJECTED"
            )

            # then
            assert len(offers) == 1
            assert offers[0].name == "Offre rejetée"
            assert offers[0].status == offer_mixin.OfferStatus.REJECTED.name

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
            offer_ids = [offer.id for offer in offers]
            assert self.sold_out_thing_offer_without_stock.id not in offer_ids
            assert self.sold_old_thing_offer_with_all_stocks_empty.id not in offer_ids
            assert (
                self.sold_out_event_offer_with_all_stocks_in_the_future_with_zero_remaining_quantity.id not in offer_ids
            )
            assert self.sold_out_event_offer_with_only_one_stock_soft_deleted.id not in offer_ids
            assert self.sold_out_event_offer_without_stock.id not in offer_ids
            assert self.sold_out_offer_on_other_venue.id in offer_ids
            assert len(offers) == 1

        @pytest.mark.usefixtures("db_session")
        def should_return_only_active_offer_on_specific_period_when_requesting_active_status_and_time_period(
            self,
        ):
            # given
            self.init_test_data()

            in_six_days = datetime.datetime.utcnow() + datetime.timedelta(days=6)
            in_six_days_beginning = in_six_days.replace(hour=0, minute=0, second=0)
            in_six_days_ending = in_six_days.replace(hour=23, minute=59, second=59)

            # when
            offers = repository.get_capped_offers_for_filters(
                user_id=self.pro.id,
                user_is_admin=self.pro.has_admin_role,
                offers_limit=5,
                status="ACTIVE",
                period_beginning_date=utc_datetime_to_department_timezone(in_six_days_beginning, "75").date(),
                period_ending_date=utc_datetime_to_department_timezone(in_six_days_ending, "75").date(),
            )

            # then
            offer_ids = [offer.id for offer in offers]
            assert self.active_event_in_six_days_offer.id in offer_ids
            assert self.active_event_offer_with_one_stock_in_the_future_with_remaining_quantity.id not in offer_ids
            assert self.active_event_offer_with_stock_in_the_future_without_quantity.id not in offer_ids
            assert self.active_thing_offer_with_all_stocks_without_quantity.id not in offer_ids
            assert self.active_thing_offer_with_one_stock_with_remaining_quantity.id not in offer_ids
            assert len(offers) == 1


@pytest.mark.usefixtures("db_session")
class GetOffersByPublicationDateTest:
    def test_get_offers_by_publication_date(self):
        factories.OfferFactory()  # Offer not in the future, i.e. no publication_date

        publication_date = datetime.datetime.utcnow().replace(minute=0, second=0, microsecond=0) + datetime.timedelta(
            days=30
        )

        offer_before = factories.OfferFactory()
        publication_date_before = publication_date - datetime.timedelta(hours=1)
        factories.FutureOfferFactory(offer=offer_before, publicationDate=publication_date_before)

        offer_to_publish_1 = factories.OfferFactory()
        future_offer_to_publish_1 = factories.FutureOfferFactory(
            offer=offer_to_publish_1, publicationDate=publication_date
        )
        offer_to_publish_2 = factories.OfferFactory()
        future_offer_to_publish_2 = factories.FutureOfferFactory(
            offer=offer_to_publish_2,
            publicationDate=publication_date - datetime.timedelta(minutes=13),
        )
        # Simulates an Offer manually published then unpublished with a publicationDate within the range of 15 minutes considered, should not be returned by the function
        offer_manually_published = factories.OfferFactory()
        factories.FutureOfferFactory(
            offer=offer_manually_published,
            publicationDate=publication_date - datetime.timedelta(minutes=13),
            isSoftDeleted=True,
        )

        offer_after = factories.OfferFactory()
        publication_date_after = publication_date + datetime.timedelta(minutes=17)
        factories.FutureOfferFactory(offer=offer_after, publicationDate=publication_date_after)

        offers_query, future_offers_query = repository.get_offers_by_publication_date(publication_date=publication_date)
        assert offers_query.count() == 2
        assert offers_query.all() == [offer_to_publish_1, offer_to_publish_2]
        assert future_offers_query.count() == 2
        assert future_offers_query.all() == [
            future_offer_to_publish_1,
            future_offer_to_publish_2,
        ]


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
        today = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        tomorrow = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        next_week = datetime.datetime.utcnow() + datetime.timedelta(days=7)

        address_paris = geography_factories.AddressFactory()
        address_overseas = geography_factories.AddressFactory(postalCode="97180", departmentCode="971")

        offerer_address = offerers_factories.OffererAddressFactory(address=address_paris)
        offer = factories.OfferFactory(
            venue__departementCode="75",
            venue__postalCode="75002",
            offererAddress=offerer_address,
        )
        self.stock_today = factories.EventStockFactory(beginningDatetime=today, offer=offer)
        bookings_factories.BookingFactory.create_batch(2, stock=self.stock_today)

        overseas_offerer_address = offerers_factories.OffererAddressFactory(address=address_overseas)
        offer = factories.OfferFactory(
            venue__departementCode="97",
            venue__postalCode="97180",
            offererAddress=overseas_offerer_address,
        )
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
        assert {stock_id for (stock_id,) in query} == {self.stock_tomorrow.id}

    def test_find_event_stocks_happening_in_7_days(self):
        self.setup_stocks()

        query = repository.find_event_stocks_happening_in_x_days(number_of_days=7)
        assert {stock.id for stock in query} == {self.stock_next_week.id}

    @time_machine.travel("2024-10-15 15:00:00")
    def test_find_today_event_stock_ids_metropolitan_france(self):
        self.setup_stocks()

        today_min = datetime.datetime(2024, 10, 15, 12, 00)
        today_max = datetime.datetime(2024, 10, 15, 23, 00)

        stock_ids = repository.find_today_event_stock_ids_metropolitan_france(today_min, today_max)

        assert set(stock_ids) == {self.stock_today.id}

    @time_machine.travel("2024-10-15 15:00:00")
    def test_find_today_event_stock_ids_by_departments(self):
        self.setup_stocks()

        today_min = datetime.datetime(2024, 10, 15, 8, 00)
        today_max = datetime.datetime(2024, 10, 15, 19, 00)

        departments_prefixes = ["971"]

        stock_ids = repository.find_today_event_stock_ids_from_departments(today_min, today_max, departments_prefixes)

        assert set(stock_ids) == {self.stock_today_overseas.id}

    @time_machine.travel("2024-10-15 15:00:00")
    def test_find_today_event_stock_ids_by_departments_with_address_different_than_the_venue(
        self,
    ):
        self.setup_stocks()

        today_min = datetime.datetime(2024, 10, 15, 8, 00)
        today_max = datetime.datetime(2024, 10, 15, 19, 00)

        departments_prefixes = ["971", "75"]

        stock_ids = repository.find_today_event_stock_ids_from_departments(today_min, today_max, departments_prefixes)

        assert set(stock_ids) == {self.stock_today_overseas.id, self.stock_today.id}

    @time_machine.travel("2024-10-15 15:00:00")
    def test_find_today_event_stock_ids_by_departments_with_address_different_than_the_venue_2(
        self,
    ):
        self.setup_stocks()

        today_min = datetime.datetime(2024, 10, 15, 8, 00)
        today_max = datetime.datetime(2024, 10, 15, 19, 00)

        departments_prefixes = ["971"]

        stock_ids = repository.find_today_event_stock_ids_from_departments(today_min, today_max, departments_prefixes)

        assert set(stock_ids) == {self.stock_today_overseas.id}

    @time_machine.travel("2024-10-15 15:00:00")
    def test_find_today_event_stock_ids_by_departments_with_address_different_than_the_venue_3(
        self,
    ):
        self.setup_stocks()

        today_min = datetime.datetime(2024, 10, 15, 8, 00)
        today_max = datetime.datetime(2024, 10, 15, 19, 00)

        departments_prefixes = ["75"]

        stock_ids = repository.find_today_event_stock_ids_from_departments(today_min, today_max, departments_prefixes)

        assert set(stock_ids) == {self.stock_today.id}

    @time_machine.travel("2024-10-15 15:00:00")
    def test_find_today_digital_stock_ids_by_departments_with_address_different_than_the_venue(
        self,
    ):
        self.setup_stocks()

        # add digital offer
        today = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        offer = factories.OfferFactory(venue__departementCode="97", venue__postalCode="97180")
        digital_stock = factories.StockWithActivationCodesFactory(beginningDatetime=today, offer=offer)
        bookings_factories.BookingFactory(stock=digital_stock)

        today_min = datetime.datetime(2024, 10, 15, 8, 00)
        today_max = datetime.datetime(2024, 10, 15, 19, 00)

        departments_prefixes = ["75"]

        stock_ids = repository.find_today_event_stock_ids_from_departments(today_min, today_max, departments_prefixes)

        assert set(stock_ids) == {self.stock_today.id, digital_stock.id}


@pytest.mark.usefixtures("db_session")
class GetExpiredOffersTest:
    interval = [
        datetime.datetime(2021, 1, 1, 0, 0),
        datetime.datetime(2021, 1, 2, 0, 0),
    ]
    dt_before = datetime.datetime(2020, 12, 31)
    dt_within = datetime.datetime(2021, 1, 1)
    dt_after = datetime.datetime(2021, 1, 3)

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
            stock=stock,
            expirationDate=datetime.datetime.utcnow() - datetime.timedelta(days=1),
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


class UpdateStockQuantityToDnBookedQuantityTest:
    def test_update_stock_quantity_to_dn_booked_quantity(self, db_session):
        # given
        offer = factories.OfferFactory()
        stock = factories.StockFactory(offer=offer, quantity=10, dnBookedQuantity=5)
        stock_id = stock.id
        # simulate concurent change
        db.session.query(models.Stock).filter(models.Stock.id == stock_id).update(
            {
                models.Stock.dnBookedQuantity: 6,
            },
            synchronize_session=False,
        )
        assert stock.quantity == 10
        # when
        repository.update_stock_quantity_to_dn_booked_quantity(stock.id)
        # then
        db_session.refresh(stock)
        assert stock.quantity == 6


@pytest.mark.usefixtures("db_session")
class GetPaginatedActiveOfferIdsTest:
    def test_limit_and_page_arguments(self):
        venue = offerers_factories.VenueFactory()
        offer1 = factories.OfferFactory(venue=venue)
        offer2 = factories.OfferFactory(venue=venue)
        offer3 = factories.OfferFactory(venue=venue)

        assert repository.get_paginated_active_offer_ids(batch_size=2, page=1) == [
            offer1.id,
            offer2.id,
        ]
        assert repository.get_paginated_active_offer_ids(batch_size=2, page=2) == [offer3.id]

    def test_exclude_inactive_offers(self):
        venue = offerers_factories.VenueFactory()
        offer1 = factories.OfferFactory(venue=venue, isActive=True)
        _offer2 = factories.OfferFactory(venue=venue, isActive=False)

        assert repository.get_paginated_active_offer_ids(batch_size=2, page=1) == [offer1.id]


@pytest.mark.usefixtures("db_session")
class GetPaginatedOfferIdsByVenueIdTest:
    def test_limit_and_page_arguments(self):
        venue1 = offerers_factories.VenueFactory()
        offer1 = factories.OfferFactory(venue=venue1)
        offer2 = factories.OfferFactory(venue=venue1)
        offer3 = factories.OfferFactory(venue=venue1)
        _other_venue_offer = factories.OfferFactory()

        assert repository.get_paginated_offer_ids_by_venue_id(venue1.id, limit=2, page=0) == [offer1.id, offer2.id]
        assert repository.get_paginated_offer_ids_by_venue_id(venue1.id, limit=2, page=1) == [offer3.id]

    def test_include_inactive_offers(self):
        venue = offerers_factories.VenueFactory()
        offer1 = factories.OfferFactory(venue=venue, isActive=True)
        offer2 = factories.OfferFactory(venue=venue, isActive=False)

        assert repository.get_paginated_offer_ids_by_venue_id(venue.id, limit=2, page=0) == [offer1.id, offer2.id]


@pytest.mark.usefixtures("db_session")
class ExcludeOffersFromInactiveVenueProviderTest:
    def test_exclude_offers_from_inactive_venue_provider(self):
        stock_api_provider = providers_factories.AllocineProviderFactory(
            localClass=providers_constants.PASS_CULTURE_STOCKS_FAKE_CLASS_NAME
        )
        active_venue_provider = providers_factories.VenueProviderFactory(isActive=True)
        inactive_venue_provider = providers_factories.VenueProviderFactory(isActive=False)
        offer_from_active_venue_provider = factories.OfferFactory(
            lastProvider=active_venue_provider.provider,
            venue=active_venue_provider.venue,
        )
        offer_not_from_provider = factories.OfferFactory()
        offer_from_inactive_venue_provider = factories.OfferFactory(
            lastProvider=inactive_venue_provider.provider,
            venue=inactive_venue_provider.venue,
        )
        offer_from_deleted_venue_provider = factories.OfferFactory(
            lastProvider=inactive_venue_provider.provider,
        )
        offer_from_stock_api = factories.OfferFactory(lastProvider=stock_api_provider)

        result_query = repository.exclude_offers_from_inactive_venue_provider(db.session.query(models.Offer))
        selected_offers = result_query.all()

        assert offer_from_active_venue_provider in selected_offers
        assert offer_not_from_provider in selected_offers
        assert offer_from_stock_api in selected_offers
        assert offer_from_inactive_venue_provider not in selected_offers
        assert offer_from_deleted_venue_provider not in selected_offers


@pytest.mark.usefixtures("db_session")
class GetStocksListFiltersTest:
    def test_basic(self):
        stock = factories.EventStockFactory()

        # When
        stocks = repository.get_filtered_stocks(
            venue=stock.offer.venue,
            offer=stock.offer,
        )

        # Then
        assert stocks.count() == 1

    def test_filtered_stock_by_price_category(self):
        # Given
        stock = factories.EventStockFactory()
        factories.EventStockFactory()

        # When
        stocks = repository.get_filtered_stocks(
            venue=stock.offer.venue,
            offer=stock.offer,
            price_category_id=stock.priceCategoryId,
        )

        # Then
        assert stocks.count() == 1

    def test_filtered_stock_by_date(self):
        # Given
        beginning_datetime = datetime.datetime(2020, 10, 15, 0, 0, 0)
        offer = factories.OfferFactory()
        factories.EventStockFactory(offer=offer, beginningDatetime=beginning_datetime)
        factories.EventStockFactory(
            offer=offer,
            beginningDatetime=beginning_datetime + datetime.timedelta(days=1),
        )
        # When
        stocks = repository.get_filtered_stocks(
            venue=offer.venue,
            offer=offer,
            date=beginning_datetime.date(),
        )

        # Then
        assert stocks.count() == 1

    def test_filtered_stocks_by_hour(self):
        # Given
        beginning_datetime = datetime.datetime(2020, 10, 15, 12, 0, 0)
        same_hour_other_day = datetime.datetime(2020, 10, 16, 12, 0, 0)
        same_hour_other_minutes_other_day = datetime.datetime(2020, 10, 16, 12, 45, 0)
        same_day_other_hour = datetime.datetime(2020, 10, 15, 0, 0, 0)
        same_day_same_hour_other_minutes = datetime.datetime(2020, 10, 15, 12, 45, 0)

        venue = offerers_factories.VenueFactory(timezone="Pacific/Tahiti", departementCode="987", postalCode="98700")
        offer = factories.OfferFactory(venue=venue)
        factories.EventStockFactory(offer=offer, beginningDatetime=beginning_datetime)
        factories.EventStockFactory(offer=offer, beginningDatetime=same_hour_other_day)
        factories.EventStockFactory(offer=offer, beginningDatetime=same_hour_other_minutes_other_day)
        factories.EventStockFactory(offer=offer, beginningDatetime=same_day_other_hour)
        factories.EventStockFactory(offer=offer, beginningDatetime=same_day_same_hour_other_minutes)

        # When
        stocks = repository.get_filtered_stocks(venue=venue, offer=offer, time=beginning_datetime.time())

        # Then
        assert stocks.count() == 2

    def test_filtered_stock_by_minutes(self):
        # Given
        beginning_datetime = datetime.datetime(2020, 10, 15, 0, 0, 0)
        venue = offerers_factories.VenueFactory(
            timezone="America/Martinique", departementCode="972", postalCode="97200"
        )
        offer = factories.OfferFactory(venue=venue)
        factories.EventStockFactory(offer=offer, beginningDatetime=beginning_datetime)
        factories.EventStockFactory(
            offer=offer,
            beginningDatetime=beginning_datetime + datetime.timedelta(hours=1),
        )
        factories.EventStockFactory(
            offer=offer,
            beginningDatetime=beginning_datetime + datetime.timedelta(minutes=1),
        )

        # When
        stocks = repository.get_filtered_stocks(
            venue=venue,
            offer=offer,
            time=beginning_datetime.time(),
        )

        # Then
        assert stocks.count() == 1

    def test_filtered_stock_by_seconds(self):
        # Given
        beginning_datetime = datetime.datetime(2020, 10, 20, 1, 0, 0)
        venue = offerers_factories.VenueFactory(timezone="Indian/Reunion", departementCode="974", postalCode="97400")
        offer = factories.OfferFactory(venue=venue)
        factories.EventStockFactory(offer=offer, beginningDatetime=beginning_datetime)
        factories.EventStockFactory(
            offer=offer,
            beginningDatetime=beginning_datetime + datetime.timedelta(seconds=1),
        )
        factories.EventStockFactory(
            offer=offer,
            beginningDatetime=beginning_datetime + datetime.timedelta(seconds=60),
        )

        # When
        stocks = repository.get_filtered_stocks(
            venue=venue,
            offer=offer,
            time=beginning_datetime.time(),
        )

        # Then
        assert stocks.count() == 2

    @time_machine.travel("2020-02-20 01:00:00")
    def test_filtered_stock_by_time_find_summer_and_winter_time_when_launch_in_winter(
        self,
    ):
        # Given
        beginning_datetime_1 = datetime.datetime(2021, 3, 27, 2, 0, 0)
        beginning_datetime_2 = datetime.datetime(2021, 3, 28, 1, 0, 0)
        beginning_datetime_3 = datetime.datetime(2021, 3, 29, 1, 0, 0)

        venue = offerers_factories.VenueFactory(timezone="Europe/Paris", departementCode="78", postalCode="78220")

        offer = factories.OfferFactory(venue=venue)
        factories.EventStockFactory(offer=offer, beginningDatetime=beginning_datetime_1)
        factories.EventStockFactory(
            offer=offer,
            beginningDatetime=beginning_datetime_2,
        )
        factories.EventStockFactory(
            offer=offer,
            beginningDatetime=beginning_datetime_3,
        )

        # When
        stocks = repository.get_filtered_stocks(
            venue=venue,
            offer=offer,
            time=datetime.time(2, 0, 0),
        )

        # Then
        assert stocks.count() == 3

    @time_machine.travel("2020-06-20 01:00:00")
    def test_filtered_stock_by_time_find_summer_and_winter_time_when_launch_in_summer(
        self,
    ):
        # Given
        beginning_datetime_1 = datetime.datetime(2021, 3, 13, 11, 0, 0)
        beginning_datetime_2 = datetime.datetime(2021, 3, 14, 10, 0, 0)
        beginning_datetime_3 = datetime.datetime(2021, 3, 15, 10, 0, 0)

        venue = offerers_factories.VenueFactory(timezone="America/Miquelon", departementCode="97", postalCode="97500")

        offer = factories.OfferFactory(venue=venue)
        factories.EventStockFactory(offer=offer, beginningDatetime=beginning_datetime_1)
        factories.EventStockFactory(
            offer=offer,
            beginningDatetime=beginning_datetime_2,
        )
        factories.EventStockFactory(
            offer=offer,
            beginningDatetime=beginning_datetime_3,
        )

        # When
        stocks = repository.get_filtered_stocks(
            venue=venue,
            offer=offer,
            time=datetime.time(10, 0, 0),
        )

        # Then
        assert stocks.count() == 3

    def test_filtered_stocks_query_by_default(self):
        # Given
        beginning_datetime = datetime.datetime(2020, 10, 15, 0, 0, 0)
        offer = factories.OfferFactory()
        first_stock = factories.EventStockFactory(offer=offer, beginningDatetime=beginning_datetime)
        second_stock = factories.EventStockFactory(
            offer=offer,
            beginningDatetime=beginning_datetime + datetime.timedelta(seconds=1),
        )
        third_stock = factories.EventStockFactory(
            offer=offer,
            beginningDatetime=beginning_datetime + datetime.timedelta(seconds=2),
        )

        # When
        stocks = repository.get_filtered_stocks(venue=offer.venue, offer=offer)

        # Then
        assert stocks.count() == 3
        assert stocks[0] == first_stock
        assert stocks[1] == second_stock
        assert stocks[2] == third_stock

    def test_stock_pagination_limit_per_page(self):
        # Given
        beginning_datetime = datetime.datetime(2020, 10, 15, 0, 0, 0)
        stocks_limit_per_page = 1
        current_page = 2
        offer = factories.OfferFactory()
        factories.EventStockFactory(
            offer=offer,
            beginningDatetime=beginning_datetime - datetime.timedelta(seconds=1),
        )
        factories.EventStockFactory(offer=offer, beginningDatetime=beginning_datetime)
        factories.EventStockFactory(
            offer=offer,
            beginningDatetime=beginning_datetime + datetime.timedelta(seconds=30),
        )

        # When
        filtered_stocks = repository.get_filtered_stocks(
            venue=offer.venue,
            offer=offer,
            order_by="BEGINNING_DATETIME",
        )
        stocks = repository.get_paginated_stocks(
            stocks_query=filtered_stocks,
            stocks_limit_per_page=stocks_limit_per_page,
            page=current_page,
        )

        # Then
        assert stocks.count() == 1

    def test_order_stocks_by_beginning_datetime_desc(self):
        # Given
        beginning_datetime = datetime.datetime(2020, 10, 15, 12, 0, 0)
        same_hour_other_day = datetime.datetime(2020, 10, 16, 12, 0, 0)
        same_hour_other_minutes_other_day = datetime.datetime(2020, 10, 16, 12, 45, 0)
        same_day_other_hour = datetime.datetime(2020, 10, 15, 0, 0, 0)
        same_day_same_hour_other_minutes = datetime.datetime(2020, 10, 15, 12, 45, 0)

        offer = factories.OfferFactory()
        stock1 = factories.EventStockFactory(offer=offer, beginningDatetime=beginning_datetime)
        stock2 = factories.EventStockFactory(offer=offer, beginningDatetime=same_hour_other_day)
        stock3 = factories.EventStockFactory(offer=offer, beginningDatetime=same_hour_other_minutes_other_day)
        stock4 = factories.EventStockFactory(offer=offer, beginningDatetime=same_day_other_hour)
        stock5 = factories.EventStockFactory(offer=offer, beginningDatetime=same_day_same_hour_other_minutes)

        # When
        stocks = repository.get_filtered_stocks(
            venue=offer.venue,
            offer=offer,
            order_by="BEGINNING_DATETIME",
            order_by_desc=True,
        )

        # Then
        assert stocks[0] == stock3
        assert stocks[1] == stock2
        assert stocks[2] == stock5
        assert stocks[3] == stock1
        assert stocks[4] == stock4

    def test_order_stocks_by_date(self):
        beginning_datetime = datetime.datetime(2020, 10, 15, 12, 0, 0)
        same_hour_other_day = datetime.datetime(2020, 10, 16, 12, 0, 0)
        same_hour_other_minutes_other_day = datetime.datetime(2020, 10, 16, 12, 45, 0)
        same_day_other_hour = datetime.datetime(2020, 10, 15, 0, 0, 0)
        same_day_same_hour_other_minutes = datetime.datetime(2020, 10, 15, 12, 45, 0)

        offer = factories.OfferFactory()
        stock1 = factories.EventStockFactory(offer=offer, beginningDatetime=beginning_datetime)
        stock2 = factories.EventStockFactory(offer=offer, beginningDatetime=same_hour_other_day)
        stock3 = factories.EventStockFactory(offer=offer, beginningDatetime=same_hour_other_minutes_other_day)
        stock4 = factories.EventStockFactory(offer=offer, beginningDatetime=same_day_other_hour)
        stock5 = factories.EventStockFactory(offer=offer, beginningDatetime=same_day_same_hour_other_minutes)

        # When
        stocks = repository.get_filtered_stocks(
            venue=offer.venue,
            offer=offer,
            order_by="DATE",
        )

        # Then
        assert stocks.count() == 5
        assert stocks[0] == stock1
        assert stocks[1] == stock4
        assert stocks[2] == stock5
        assert stocks[3] == stock2
        assert stocks[4] == stock3

    def test_order_stocks_by_time_desc(self):
        # Given
        beginning_datetime = datetime.datetime(2020, 10, 15, 12, 0, 0)
        same_hour_other_day = datetime.datetime(2020, 10, 16, 12, 0, 0)
        same_hour_other_minutes_other_day = datetime.datetime(2020, 10, 16, 12, 45, 0)
        same_day_other_hour = datetime.datetime(2020, 10, 15, 0, 0, 0)
        same_day_same_hour_other_minutes = datetime.datetime(2020, 10, 15, 12, 45, 0)

        offer = factories.OfferFactory()
        stock1 = factories.EventStockFactory(offer=offer, beginningDatetime=beginning_datetime)
        stock2 = factories.EventStockFactory(offer=offer, beginningDatetime=same_hour_other_day)
        stock3 = factories.EventStockFactory(offer=offer, beginningDatetime=same_hour_other_minutes_other_day)
        stock4 = factories.EventStockFactory(offer=offer, beginningDatetime=same_day_other_hour)
        stock5 = factories.EventStockFactory(offer=offer, beginningDatetime=same_day_same_hour_other_minutes)

        # When
        stocks = repository.get_filtered_stocks(
            venue=offer.venue,
            offer=offer,
            order_by="TIME",
            order_by_desc=True,
        )

        # Then
        assert stocks.count() == 5
        assert stocks[0] == stock5
        assert stocks[1] == stock3
        assert stocks[2] == stock2
        assert stocks[3] == stock1
        assert stocks[4] == stock4

    def test_order_stocks_by_price_category_id(self):
        # Given
        offer = factories.OfferFactory()
        price_cat1 = factories.PriceCategoryFactory(offer=offer)
        price_cat2 = factories.PriceCategoryFactory(offer=offer)

        stock1 = factories.EventStockFactory(offer=offer, priceCategory=price_cat1)
        stock2 = factories.EventStockFactory(offer=offer, priceCategory=price_cat2)
        stock3 = factories.EventStockFactory(offer=offer, priceCategory=price_cat1)

        # When
        stocks = repository.get_filtered_stocks(
            venue=offer.venue,
            offer=offer,
            order_by="PRICE_CATEGORY_ID",
        )

        # Then
        assert stocks[0] == stock1
        assert stocks[1] == stock3
        assert stocks[2] == stock2

    def test_order_stocks_by_booking_limit(self):
        # Given
        booking_limit_datetime = datetime.datetime(2020, 10, 15, 12, 0, 0)
        same_hour_other_day = datetime.datetime(2020, 10, 16, 12, 0, 0)
        same_hour_other_minutes_other_day = datetime.datetime(2020, 10, 16, 12, 45, 0)
        same_day_other_hour = datetime.datetime(2020, 10, 15, 0, 0, 0)
        same_day_same_hour_other_minutes = datetime.datetime(2020, 10, 15, 12, 45, 0)

        offer = factories.OfferFactory()
        stock1 = factories.EventStockFactory(offer=offer, bookingLimitDatetime=booking_limit_datetime)
        stock2 = factories.EventStockFactory(offer=offer, bookingLimitDatetime=same_hour_other_day)
        stock3 = factories.EventStockFactory(offer=offer, bookingLimitDatetime=same_hour_other_minutes_other_day)
        stock4 = factories.EventStockFactory(offer=offer, bookingLimitDatetime=same_day_other_hour)
        stock5 = factories.EventStockFactory(offer=offer, bookingLimitDatetime=same_day_same_hour_other_minutes)

        # When
        stocks = repository.get_filtered_stocks(
            venue=offer.venue,
            offer=offer,
            order_by="BOOKING_LIMIT_DATETIME",
        )

        # Then
        assert stocks[0] == stock4
        assert stocks[1] == stock1
        assert stocks[2] == stock5
        assert stocks[3] == stock2
        assert stocks[4] == stock3

    def test_order_stocks_by_remaining_quantity_desc(self):
        # Given
        offer = factories.OfferFactory()
        stock1 = factories.EventStockFactory(offer=offer, quantity=5, dnBookedQuantity=1)
        stock2 = factories.EventStockFactory(offer=offer, quantity=6, dnBookedQuantity=3)
        stock3 = factories.EventStockFactory(offer=offer, quantity=50, dnBookedQuantity=5)

        # When
        stocks = repository.get_filtered_stocks(
            venue=offer.venue,
            offer=offer,
            order_by="REMAINING_QUANTITY",
            order_by_desc=True,
        )

        # Then
        assert stocks[0] == stock3
        assert stocks[1] == stock1
        assert stocks[2] == stock2

    def test_order_stocks_by_dn_booked_quantity(self):
        offer = factories.OfferFactory()
        stock1 = factories.EventStockFactory(offer=offer, quantity=5, dnBookedQuantity=20)
        stock2 = factories.EventStockFactory(offer=offer, quantity=6, dnBookedQuantity=21)
        stock3 = factories.EventStockFactory(offer=offer, quantity=50, dnBookedQuantity=5)

        # When
        stocks = repository.get_filtered_stocks(
            venue=offer.venue,
            offer=offer,
            order_by="DN_BOOKED_QUANTITY",
        )

        # Then
        assert stocks[0] == stock3
        assert stocks[1] == stock1
        assert stocks[2] == stock2


@pytest.mark.usefixtures("db_session")
class GetOfferPriceCategoriesFiltersTest:
    def test_should_return_all_price_categories_if_no_id_at_provider_given(self):
        offer = factories.OfferFactory()
        price_category_1 = factories.PriceCategoryFactory(offer=offer)
        price_category_2 = factories.PriceCategoryFactory(offer=offer)

        # When
        price_categories = repository.get_offer_price_categories(offer.id)

        # Then
        assert set(price_categories) == {price_category_1, price_category_2}

    def test_should_return_all_price_categories_of_given_event(self):
        offer = factories.OfferFactory()
        price_category_1 = factories.PriceCategoryFactory(offer=offer)
        price_category_2 = factories.PriceCategoryFactory(offer=offer)
        offer2 = factories.OfferFactory()
        factories.PriceCategoryFactory(offer=offer2)  # should not appear in result

        # When
        price_categories = repository.get_offer_price_categories(offer.id)

        # Then
        assert set(price_categories) == {price_category_1, price_category_2}

    def test_should_filter_by_id_at_provider(self):
        offer = factories.OfferFactory()
        factories.PriceCategoryFactory(offer=offer, idAtProvider="GutenMorgen")
        price_category_2 = factories.PriceCategoryFactory(offer=offer, idAtProvider="bonjour")
        price_category_3 = factories.PriceCategoryFactory(offer=offer, idAtProvider="hello")

        # When
        price_categories = repository.get_offer_price_categories(offer.id, id_at_provider_list=["bonjour", "hello"])

        # Then
        assert set(price_categories) == {price_category_2, price_category_3}

    def test_should_return_no_result(self):
        offer = factories.OfferFactory()
        factories.PriceCategoryFactory(offer=offer, idAtProvider="GutenMorgen")
        factories.PriceCategoryFactory(offer=offer, idAtProvider="bonjour")
        factories.PriceCategoryFactory(offer=offer, idAtProvider="hello")

        # When
        price_categories = repository.get_offer_price_categories(offer.id, id_at_provider_list=[])

        # Then
        assert len(price_categories.all()) == 0


@pytest.mark.usefixtures("db_session")
class GetHeadlineOfferFiltersTest:
    def test_get_inactive_headline_offers_basic(self):
        inactive_offer = factories.OfferFactory(isActive=False)
        inactive_offer_headline_offer = factories.HeadlineOfferFactory(offer=inactive_offer)

        active_offer = factories.OfferFactory(isActive=True)
        factories.StockFactory(offer=active_offer)
        # active offer headline offer:
        factories.HeadlineOfferFactory(offer=active_offer)

        finished_timespan = (
            datetime.datetime.utcnow() - datetime.timedelta(days=20),
            datetime.datetime.utcnow() - datetime.timedelta(days=10),
        )
        # alreeady inactive offer headline offer:
        factories.HeadlineOfferFactory(offer=active_offer, timespan=finished_timespan)

        another_active_offer = factories.OfferFactory(isActive=True)
        timespan_finishing_in_the_future = (
            datetime.datetime.utcnow() - datetime.timedelta(days=3),
            datetime.datetime.utcnow() + datetime.timedelta(days=3),
        )
        # soon to be inactive offer headline offer:
        factories.HeadlineOfferFactory(offer=another_active_offer, timespan=timespan_finishing_in_the_future)

        headline_offer_query_result = repository.get_inactive_headline_offers()
        assert headline_offer_query_result == [inactive_offer_headline_offer]

    def test_get_inactive_headline_offers_empty_result(self):
        offer = factories.OfferFactory(isActive=True)
        factories.HeadlineOfferFactory(offer=offer)

        headline_offer_query_result = repository.get_inactive_headline_offers()
        assert headline_offer_query_result == []

    def test_get_inactive_headline_offers_should_not_return_already_deactivated_headline_offer(
        self,
    ):
        inactive_offer = factories.OfferFactory(isActive=False)
        inactive_offer_headline_offer = factories.HeadlineOfferFactory(offer=inactive_offer)

        finished_timespan = (
            datetime.datetime.utcnow() - datetime.timedelta(days=20),
            datetime.datetime.utcnow() - datetime.timedelta(days=10),
        )
        # already inactive headline offer
        factories.HeadlineOfferFactory(offer=inactive_offer, timespan=finished_timespan)

        another_inactive_offer = factories.OfferFactory(isActive=False)
        timespan_finishing_in_the_future = (
            datetime.datetime.utcnow() - datetime.timedelta(days=3),
            datetime.datetime.utcnow() + datetime.timedelta(days=3),
        )
        headline_offer_finishing_in_the_future_but_offer_is_inactive = factories.HeadlineOfferFactory(
            offer=another_inactive_offer, timespan=timespan_finishing_in_the_future
        )

        headline_offer_query_result = sorted(
            repository.get_inactive_headline_offers(),
            key=lambda headline_offer: headline_offer.id,
        )

        assert headline_offer_query_result == sorted(
            [
                inactive_offer_headline_offer,
                headline_offer_finishing_in_the_future_but_offer_is_inactive,
            ],
            key=lambda headline_offer: headline_offer.id,
        )

    def test_get_inactive_headline_offers_without_images(self):
        offer = factories.OfferFactory(isActive=True)
        headline_offer_without_mediation = factories.HeadlineOfferFactory(offer=offer, without_mediation=True)

        finished_timespan = (
            datetime.datetime.utcnow() - datetime.timedelta(days=20),
            datetime.datetime.utcnow() - datetime.timedelta(days=10),
        )
        # already inactive headline offer without mediation
        factories.HeadlineOfferFactory(offer=offer, timespan=finished_timespan, without_mediation=True)

        headline_offer_query_result = repository.get_inactive_headline_offers()
        assert headline_offer_query_result == [headline_offer_without_mediation]

    def test_get_offerer_active_headline_offer_even_not_yet_disabled_by_cron_for_active_offer(
        self,
    ):
        offer = factories.OfferFactory(isActive=True)
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        headline_offer = factories.HeadlineOfferFactory(offer=offer, venue=venue)
        headline_offer_query_result = repository.get_current_headline_offer(user_offerer.offerer.id)
        assert headline_offer_query_result == headline_offer

    def test_get_offerer_active_headline_offer_even_not_yet_disabled_by_cron_for_inactive_offer(
        self,
    ):
        offer = factories.OfferFactory(isActive=True)
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        headline_offer = factories.HeadlineOfferFactory(offer=offer, venue=venue, without_mediation=True)
        headline_offer_query_result = repository.get_current_headline_offer(user_offerer.offerer.id)
        assert headline_offer_query_result == headline_offer


@pytest.mark.usefixtures("db_session")
class GetActiveOfferByVenueIdAndEanTest:
    EAN = "0000000000001"

    def test_existing_offer_is_found(self):
        offer = factories.ThingOfferFactory(ean=self.EAN)
        res = repository.get_active_offer_by_venue_id_and_ean(offer.venueId, offer.ean)

        assert res == offer

    def test_existing_offer_amongst_many_others_is_found(self):
        main_venue = offerers_factories.VenueFactory()
        another_venue = offerers_factories.VenueFactory()

        offer = factories.ThingOfferFactory(venue=main_venue, ean=self.EAN)
        factories.ThingOfferFactory(venue=main_venue, ean=self.EAN, isActive=False)
        factories.ThingOfferFactory(venue=main_venue, ean="0000000000002")

        factories.ThingOfferFactory(venue=another_venue, ean=self.EAN)
        factories.ThingOfferFactory(venue=another_venue, ean="0000000000002")

        res = repository.get_active_offer_by_venue_id_and_ean(offer.venueId, offer.ean)

        assert res == offer

    def test_most_recent_offer_is_returned_if_many_amongst_venue_shares_same_ean(self, caplog):
        def past_date(delta):
            today = datetime.datetime.now(datetime.timezone.utc)
            return today - datetime.timedelta(days=delta)

        venue = offerers_factories.VenueFactory()
        offers = [
            factories.ThingOfferFactory(venue=venue, ean=self.EAN, dateCreated=past_date(1)),
            factories.ThingOfferFactory(venue=venue, ean=self.EAN, dateCreated=past_date(2)),
            factories.ThingOfferFactory(venue=venue, ean=self.EAN, dateCreated=past_date(3)),
        ]

        with caplog.at_level(logging.WARNING):
            res = repository.get_active_offer_by_venue_id_and_ean(venue.id, self.EAN)

        assert any(log.message == "EAN shared by more than one offer across a venue" for log in caplog.records)

        assert res == offers[0]

    def test_offer_from_another_venue_raises_an_error(self):
        another_venue = offerers_factories.VenueFactory()
        offer = factories.ThingOfferFactory(ean=self.EAN)

        with pytest.raises(exceptions.OfferNotFound):
            repository.get_active_offer_by_venue_id_and_ean(another_venue.id, offer.ean)

    def test_unknown_ean_raises_an_error(self):
        offer = factories.ThingOfferFactory(ean=self.EAN)

        with pytest.raises(exceptions.OfferNotFound):
            repository.get_active_offer_by_venue_id_and_ean(offer.venueId, "0000000000002")

    def test_inactive_offer_raises_an_error(self):
        offer = factories.ThingOfferFactory(ean=self.EAN, isActive=False)

        with pytest.raises(exceptions.OfferNotFound):
            repository.get_active_offer_by_venue_id_and_ean(offer.venueId, offer.ean)


@pytest.mark.usefixtures("db_session")
@patch(
    "pcapi.models.db.session.delete",
    side_effect=(sa_exc.IntegrityError(None, None, None), None),
)
def test_handles_offer_creation_while_product_merging(delete_mock):
    to_keep = factories.ProductFactory()
    to_delete = factories.ProductFactory()

    kept_product = repository.merge_products(to_keep, to_delete)

    assert delete_mock.call_count == 2
    assert kept_product == to_keep


@pytest.mark.usefixtures("db_session")
class GetUnbookableUnbookedOldOfferIdsTest:
    @property
    def a_year_ago(self):
        return datetime.date.today() - datetime.timedelta(days=366)

    def test_get_unbookable_unbooked_old_offer_id(self):
        offer = factories.OfferFactory(dateCreated=self.a_year_ago, dateUpdated=self.a_year_ago)

        ids = list(repository.get_unbookable_unbooked_old_offer_ids())
        assert ids == [offer.id]

    def test_get_old_offer_with_an_expired_stock_with_quantity_is_matched(self):
        offer = factories.StockFactory(
            quantity=10,
            bookingLimitDatetime=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=2),
            offer__dateCreated=self.a_year_ago,
            offer__dateUpdated=self.a_year_ago,
        ).offer

        ids = list(repository.get_unbookable_unbooked_old_offer_ids())
        assert ids == [offer.id]

    def test_get_old_offer_with_an_ongoing_stock_without_any_quantity_is_matched(self):
        offer = factories.StockFactory(
            quantity=0,
            offer__dateCreated=self.a_year_ago,
            offer__dateUpdated=self.a_year_ago,
        ).offer

        ids = list(repository.get_unbookable_unbooked_old_offer_ids())
        assert ids == [offer.id]

    def test_get_old_offer_with_a_soft_deleted_stock_is_matched(self):
        offer = factories.StockFactory(
            isSoftDeleted=True,
            quantity=10,
            offer__dateCreated=self.a_year_ago,
            offer__dateUpdated=self.a_year_ago,
        ).offer

        ids = list(repository.get_unbookable_unbooked_old_offer_ids())
        assert ids == [offer.id]

    def test_get_old_offer_with_an_ongoing_stock_is_ignored(self):
        factories.StockFactory(offer__dateCreated=self.a_year_ago, offer__dateUpdated=self.a_year_ago)
        assert not list(repository.get_unbookable_unbooked_old_offer_ids())

    def test_get_old_offer_with_ongoing_and_unbookable_stocks_is_ignored(self):
        offer = factories.OfferFactory(dateCreated=self.a_year_ago, dateUpdated=self.a_year_ago)

        factories.StockFactory(offer=offer)
        factories.StockFactory(offer=offer, isSoftDeleted=True)

        assert not list(repository.get_unbookable_unbooked_old_offer_ids())

    def test_get_old_offer_with_unbookable_and_bookable_stocks_and_a_booking_is_ignored(
        self,
    ):
        offer = factories.OfferFactory(dateCreated=self.a_year_ago, dateUpdated=self.a_year_ago)

        # unbookable stock with an old booking
        bookings_factories.UsedBookingFactory(stock__isSoftDeleted=True, stock__offer=offer)

        # bookable stock
        factories.StockFactory(offer=offer)

        assert not list(repository.get_unbookable_unbooked_old_offer_ids())

    def test_get_old_offer_with_a_booking_is_ignored(self):
        bookings_factories.BookingFactory(
            stock__offer__dateCreated=self.a_year_ago,
            stock__offer__dateUpdated=self.a_year_ago,
        )

        assert not list(repository.get_unbookable_unbooked_old_offer_ids())

    def test_get_old_offer_with_a_cancelled_booking_is_ignored(self):
        bookings_factories.CancelledBookingFactory(
            stock__offer__dateCreated=self.a_year_ago,
            stock__offer__dateUpdated=self.a_year_ago,
        )

        assert not list(repository.get_unbookable_unbooked_old_offer_ids())

    def test_get_recent_offer_without_stocks_nor_bookings_is_ignored(self):
        factories.OfferFactory()
        assert not list(repository.get_unbookable_unbooked_old_offer_ids())

    def test_recent_or_booked_offers_are_filtered(self):
        offer = factories.OfferFactory(dateCreated=self.a_year_ago, dateUpdated=self.a_year_ago)

        factories.OfferFactory()
        bookings_factories.BookingFactory(
            stock__offer__dateCreated=self.a_year_ago,
            stock__offer__dateUpdated=self.a_year_ago,
        )

        ids = list(repository.get_unbookable_unbooked_old_offer_ids())
        assert ids == [offer.id]

    def test_legit_offer_with_id_outside_of_asked_range_is_ignored(self):
        offer = factories.OfferFactory(dateCreated=self.a_year_ago, dateUpdated=self.a_year_ago)

        ids = repository.get_unbookable_unbooked_old_offer_ids(offer.id + 1, offer.id + 10)
        assert not list(ids)


@pytest.mark.usefixtures("clean_database")
def test_lock_stocks(app):
    venue = offerers_factories.VenueFactory()
    stock = factories.StockFactory(offer__venue=venue)

    engine = sqla.create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
    session_factory = sa_orm.sessionmaker(bind=engine)
    Session = sa_orm.scoped_session(session_factory)
    session = Session()

    # Ensure the new session can see the stock
    assert session.query(models.Stock).filter(models.Stock.id == stock.id).count() == 1

    repository.lock_stocks_for_venue(venue.id)

    # simulate a booking lock
    with pytest.raises(sa_exc.OperationalError):
        session.query(models.Stock).filter(models.Stock.id == stock.id).with_for_update(
            nowait=True,
        ).all()
