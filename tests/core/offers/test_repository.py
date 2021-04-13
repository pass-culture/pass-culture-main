from datetime import datetime
from datetime import timedelta

import pytest

import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.offers.models import OfferStatus
from pcapi.core.offers.models import OfferValidationStatus
from pcapi.core.offers.repository import check_stock_consistency
from pcapi.core.offers.repository import get_active_offers_count_for_venue
from pcapi.core.offers.repository import get_offers_by_ids
from pcapi.core.offers.repository import get_paginated_offers_for_filters
from pcapi.core.offers.repository import get_sold_out_offers_count_for_venue
from pcapi.core.users import factories as users_factories
from pcapi.domain.identifier.identifier import Identifier
from pcapi.domain.pro_offers.paginated_offers_recap import PaginatedOffersRecap
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_provider
from pcapi.model_creators.generic_creators import create_user
from pcapi.model_creators.generic_creators import create_user_offerer
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.models import ThingType
from pcapi.repository import repository


class PaginatedOfferForFiltersTest:
    @pytest.mark.usefixtures("db_session")
    def should_return_paginated_offers_with_details_of_pagination_and_offers_of_requested_page(self):
        # Given
        user = create_user()
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)
        venue = create_venue(offerer)
        offer1 = create_offer_with_thing_product(venue)
        offer2 = create_offer_with_thing_product(venue)
        repository.save(user_offerer, offer1, offer2)
        requested_page = 2
        requested_offers_per_page = 1

        # When
        paginated_offers = get_paginated_offers_for_filters(
            user_id=user.id,
            user_is_admin=user.isAdmin,
            offers_per_page=requested_offers_per_page,
            page=requested_page,
        )

        # Then
        assert isinstance(paginated_offers, PaginatedOffersRecap)
        assert paginated_offers.total_offers == 2
        assert paginated_offers.current_page == requested_page
        assert paginated_offers.total_pages == 2
        assert len(paginated_offers.offers) == 1
        assert paginated_offers.offers[0].identifier == Identifier(offer1.id)

    @pytest.mark.usefixtures("db_session")
    def should_return_offers_sorted_by_id_desc(self):
        # Given
        user = create_user()
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)
        venue = create_venue(offerer)
        offer1 = create_offer_with_thing_product(venue)
        offer2 = create_offer_with_thing_product(venue)
        repository.save(user_offerer, offer1, offer2)

        # When
        paginated_offers = get_paginated_offers_for_filters(
            user_id=user.id, user_is_admin=user.isAdmin, page=1, offers_per_page=10
        )

        # Then
        assert paginated_offers.offers[0].identifier.persisted > paginated_offers.offers[1].identifier.persisted

    @pytest.mark.usefixtures("db_session")
    def should_return_offers_of_given_type(self):
        user_offerer = offers_factories.UserOffererFactory()
        requested_offer = offers_factories.OfferFactory(
            type=str(ThingType.AUDIOVISUEL), venue__managingOfferer=user_offerer.offerer
        )
        other_offer = offers_factories.OfferFactory(
            type=str(ThingType.JEUX), venue__managingOfferer=user_offerer.offerer
        )

        paginated_offers = get_paginated_offers_for_filters(
            user_id=user_offerer.user.id,
            user_is_admin=user_offerer.user.isAdmin,
            type_id=str(ThingType.AUDIOVISUEL),
            page=1,
            offers_per_page=10,
        )

        # then
        offers_id = [offer.identifier for offer in paginated_offers.offers]
        assert Identifier(requested_offer.id) in offers_id
        assert Identifier(other_offer.id) not in offers_id
        assert paginated_offers.total_offers == 1

    @pytest.mark.usefixtures("db_session")
    def test_returns_offers_filtered_by_manual_creation_mode_when_provided(self):
        # given
        pro_user = create_user()
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
        paginated_offers = get_paginated_offers_for_filters(
            user_id=pro_user.id, user_is_admin=pro_user.isAdmin, page=1, offers_per_page=1, creation_mode="manual"
        )

        # then
        assert paginated_offers.offers[0].identifier.persisted == manually_created_offer.id
        assert paginated_offers.total_offers == 1

    @pytest.mark.usefixtures("db_session")
    def test_returns_offers_filtered_by_imported_creation_mode_when_provided(self):
        # given
        pro_user = create_user()
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
        paginated_offers = get_paginated_offers_for_filters(
            user_id=pro_user.id, user_is_admin=pro_user.isAdmin, page=1, offers_per_page=1, creation_mode="imported"
        )

        # then
        assert paginated_offers.offers[0].identifier.persisted == imported_offer.id
        assert paginated_offers.total_offers == 1

    @pytest.mark.usefixtures("db_session")
    def should_not_return_event_offers_with_only_deleted_stock_if_filtering_by_time_period(self):
        # given
        pro = users_factories.UserFactory(isAdmin=True)
        offer_in_requested_time_period = offers_factories.OfferFactory()
        offers_factories.EventStockFactory(
            offer=offer_in_requested_time_period, beginningDatetime=datetime(2020, 1, 2), isSoftDeleted=True
        )

        # When
        paginated_offers = get_paginated_offers_for_filters(
            user_id=pro.id,
            user_is_admin=pro.isAdmin,
            page=1,
            offers_per_page=1,
            period_beginning_date="2020-01-01T00:00:00",
        )

        # then
        offers_id = [offer.identifier for offer in paginated_offers.offers]
        assert Identifier(offer_in_requested_time_period.id) not in offers_id
        assert paginated_offers.total_offers == 0

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
        paginated_offers = get_paginated_offers_for_filters(
            user_id=admin.id,
            user_is_admin=admin.isAdmin,
            page=1,
            offers_per_page=10,
            period_beginning_date=period_beginning_date,
            period_ending_date=period_ending_date,
        )

        # then
        offers_id = [offer.identifier for offer in paginated_offers.offers]
        assert Identifier(offer_in_cayenne.id) in offers_id
        assert Identifier(offer_in_mayotte.id) in offers_id
        assert paginated_offers.total_offers == 2

    class WhenUserIsAdmin:
        @pytest.mark.usefixtures("db_session")
        def should_return_offers_of_given_venue_when_user_is_not_attached_to_its_offerer(self, app):
            # given
            admin = users_factories.UserFactory(isAdmin=True)
            offer_for_requested_venue = offers_factories.OfferFactory()
            offer_for_other_venue = offers_factories.OfferFactory()

            # when
            paginated_offers = get_paginated_offers_for_filters(
                user_id=admin.id,
                user_is_admin=admin.isAdmin,
                venue_id=offer_for_requested_venue.venue.id,
                page=1,
                offers_per_page=10,
            )

            # then
            offers_id = [offer.identifier for offer in paginated_offers.offers]
            assert Identifier(offer_for_requested_venue.id) in offers_id
            assert Identifier(offer_for_other_venue.id) not in offers_id
            assert paginated_offers.total_offers == 1

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
            paginated_offers = get_paginated_offers_for_filters(
                user_id=admin.id,
                user_is_admin=admin.isAdmin,
                venue_id=offer_for_requested_venue.venue.id,
                page=1,
                offers_per_page=10,
            )

            # then
            offers_id = [offer.identifier for offer in paginated_offers.offers]
            assert Identifier(offer_for_requested_venue.id) in offers_id
            assert Identifier(offer_for_other_venue.id) not in offers_id
            assert paginated_offers.total_offers == 1

        @pytest.mark.usefixtures("db_session")
        def should_return_offers_of_given_offerer_when_user_is_not_attached_to_it(self):
            # given
            admin = users_factories.UserFactory(isAdmin=True)
            offer_for_requested_offerer = offers_factories.OfferFactory()
            offer_for_other_offerer = offers_factories.OfferFactory()

            # When
            paginated_offers = get_paginated_offers_for_filters(
                user_id=admin.id,
                user_is_admin=admin.isAdmin,
                page=1,
                offers_per_page=1,
                offerer_id=offer_for_requested_offerer.venue.managingOffererId,
            )

            # then
            offers_id = [offer.identifier for offer in paginated_offers.offers]
            assert Identifier(offer_for_requested_offerer.id) in offers_id
            assert Identifier(offer_for_other_offerer.id) not in offers_id
            assert paginated_offers.total_offers == 1

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
            paginated_offers = get_paginated_offers_for_filters(
                user_id=admin.id,
                user_is_admin=admin.isAdmin,
                page=1,
                offers_per_page=1,
                offerer_id=offer_for_requested_offerer.venue.managingOffererId,
            )

            # then
            offers_id = [offer.identifier for offer in paginated_offers.offers]
            assert Identifier(offer_for_requested_offerer.id) in offers_id
            assert Identifier(offer_for_other_offerer.id) not in offers_id
            assert paginated_offers.total_offers == 1

    class WhenUserIsPro:
        @pytest.mark.usefixtures("db_session")
        def should_not_return_offers_of_given_venue_when_user_is_not_attached_to_its_offerer(self, app):
            # given
            pro = users_factories.UserFactory(isBeneficiary=False, isAdmin=False)
            offer_for_requested_venue = offers_factories.OfferFactory()
            offer_for_other_venue = offers_factories.OfferFactory()

            # when
            paginated_offers = get_paginated_offers_for_filters(
                user_id=pro.id,
                user_is_admin=pro.isAdmin,
                venue_id=offer_for_requested_venue.venue.id,
                page=1,
                offers_per_page=10,
            )

            # then
            offers_id = [offer.identifier for offer in paginated_offers.offers]
            assert Identifier(offer_for_requested_venue.id) not in offers_id
            assert Identifier(offer_for_other_venue.id) not in offers_id
            assert paginated_offers.total_offers == 0

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
            paginated_offers = get_paginated_offers_for_filters(
                user_id=pro.id,
                user_is_admin=pro.isAdmin,
                venue_id=offer_for_requested_venue.venue.id,
                page=1,
                offers_per_page=10,
            )

            # then
            offers_id = [offer.identifier for offer in paginated_offers.offers]
            assert Identifier(offer_for_requested_venue.id) in offers_id
            assert Identifier(offer_for_other_venue.id) not in offers_id
            assert paginated_offers.total_offers == 1

        @pytest.mark.usefixtures("db_session")
        def should_not_return_offers_of_given_offerer_when_user_is_not_attached_to_it(self):
            # given
            pro = users_factories.UserFactory(isBeneficiary=False, isAdmin=False)
            offer_for_requested_offerer = offers_factories.OfferFactory()
            offer_for_other_offerer = offers_factories.OfferFactory()

            # When
            paginated_offers = get_paginated_offers_for_filters(
                user_id=pro.id,
                user_is_admin=pro.isAdmin,
                page=1,
                offers_per_page=1,
                offerer_id=offer_for_requested_offerer.venue.managingOffererId,
            )

            # then
            offers_id = [offer.identifier for offer in paginated_offers.offers]
            assert Identifier(offer_for_requested_offerer.id) not in offers_id
            assert Identifier(offer_for_other_offerer.id) not in offers_id
            assert paginated_offers.total_offers == 0

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
            paginated_offers = get_paginated_offers_for_filters(
                user_id=pro.id,
                user_is_admin=pro.isAdmin,
                page=1,
                offers_per_page=1,
                offerer_id=offer_for_requested_offerer.venue.managingOffererId,
            )

            # then
            offers_id = [offer.identifier for offer in paginated_offers.offers]
            assert Identifier(offer_for_requested_offerer.id) in offers_id
            assert Identifier(offer_for_other_offerer.id) not in offers_id
            assert paginated_offers.total_offers == 1

    class NameFilterTest:
        @pytest.mark.usefixtures("db_session")
        def should_return_offer_which_name_equal_keyword_when_keyword_is_less_or_equal_than_3_letters(self, app):
            # given
            user_offerer = offers_factories.UserOffererFactory()
            expected_offer = offers_factories.OfferFactory(name="ocs", venue__managingOfferer=user_offerer.offerer)
            other_offer = offers_factories.OfferFactory(name="ocsir", venue__managingOfferer=user_offerer.offerer)

            # when
            paginated_offers = get_paginated_offers_for_filters(
                user_id=user_offerer.user.id,
                user_is_admin=user_offerer.user.isAdmin,
                name_keywords="ocs",
                page=1,
                offers_per_page=10,
            )

            # then
            offers_id = [offer.identifier for offer in paginated_offers.offers]
            assert Identifier(expected_offer.id) in offers_id
            assert Identifier(other_offer.id) not in offers_id
            assert paginated_offers.total_offers == 1

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
            paginated_offers = get_paginated_offers_for_filters(
                user_id=user_offerer.user.id,
                user_is_admin=user_offerer.user.isAdmin,
                name_keywords="seras-tu",
                page=1,
                offers_per_page=10,
            )

            # then
            offers_id = [offer.identifier for offer in paginated_offers.offers]
            assert Identifier(expected_offer.id) in offers_id
            assert Identifier(another_expected_offer.id) in offers_id
            assert Identifier(other_offer.id) not in offers_id
            assert paginated_offers.total_offers == 2

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
            paginated_offers = get_paginated_offers_for_filters(
                user_id=user_offerer.user.id,
                user_is_admin=user_offerer.user.isAdmin,
                name_keywords="mon océan",
                page=1,
                offers_per_page=10,
            )

            # then
            offers_id = [offer.identifier for offer in paginated_offers.offers]
            assert Identifier(expected_offer.id) in offers_id
            assert Identifier(another_expected_offer.id) in offers_id
            assert paginated_offers.total_offers == 2

        @pytest.mark.usefixtures("db_session")
        def should_be_accent_sensitive(self, app):
            # given
            user_offerer = offers_factories.UserOffererFactory()
            expected_offer = offers_factories.OfferFactory(name="ocean", venue__managingOfferer=user_offerer.offerer)
            other_offer = offers_factories.OfferFactory(name="océan", venue__managingOfferer=user_offerer.offerer)

            # when
            paginated_offers = get_paginated_offers_for_filters(
                user_id=user_offerer.user.id,
                user_is_admin=user_offerer.user.isAdmin,
                name_keywords="ocean",
                page=1,
                offers_per_page=10,
            )

            # then
            offers_id = [offer.identifier for offer in paginated_offers.offers]
            assert Identifier(expected_offer.id) in offers_id
            assert Identifier(other_offer.id) not in offers_id
            assert paginated_offers.total_offers == 1

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
            beneficiary = create_user(email="jane.doe@example.com")
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

        @pytest.mark.usefixtures("db_session")
        def should_return_only_active_offers_when_requesting_active_status(self):
            # given
            self.init_test_data()

            # when
            paginated_offers = get_paginated_offers_for_filters(
                user_id=self.pro.id, user_is_admin=self.pro.isAdmin, offers_per_page=5, page=1, status="ACTIVE"
            )

            # then
            offer_ids = [offer.identifier for offer in paginated_offers.offers]
            assert Identifier(self.active_thing_offer_with_one_stock_with_remaining_quantity.id) in offer_ids
            assert Identifier(self.active_event_in_six_days_offer.id) in offer_ids
            assert Identifier(self.active_thing_offer_with_all_stocks_without_quantity.id) in offer_ids
            assert Identifier(self.active_event_offer_with_stock_in_the_future_without_quantity.id) in offer_ids
            assert (
                Identifier(self.active_event_offer_with_one_stock_in_the_future_with_remaining_quantity.id) in offer_ids
            )
            assert Identifier(self.inactive_thing_offer_without_stock.id) not in offer_ids
            assert Identifier(self.inactive_thing_offer_with_stock_with_remaining_quantity.id) not in offer_ids
            assert Identifier(self.inactive_expired_event_offer.id) not in offer_ids
            assert Identifier(self.inactive_thing_offer_without_remaining_quantity.id) not in offer_ids
            assert Identifier(self.sold_out_thing_offer_without_stock.id) not in offer_ids
            assert Identifier(self.sold_old_thing_offer_with_all_stocks_empty.id) not in offer_ids
            assert (
                Identifier(self.sold_out_event_offer_with_all_stocks_in_the_future_with_zero_remaining_quantity.id)
                not in offer_ids
            )
            assert Identifier(self.sold_out_event_offer_with_only_one_stock_soft_deleted.id) not in offer_ids
            assert Identifier(self.sold_out_event_offer_without_stock.id) not in offer_ids
            assert Identifier(self.expired_event_offer_with_stock_in_the_past_without_quantity.id) not in offer_ids
            assert Identifier(self.expired_thing_offer_with_a_stock_expired_with_remaining_quantity.id) not in offer_ids
            assert (
                Identifier(self.expired_event_offer_with_all_stocks_in_the_past_with_remaining_quantity.id)
                not in offer_ids
            )
            assert (
                Identifier(self.expired_event_offer_with_all_stocks_in_the_past_with_zero_remaining_quantity.id)
                not in offer_ids
            )
            assert paginated_offers.total_offers == 5

        @pytest.mark.usefixtures("db_session")
        def should_return_only_inactive_offers_when_requesting_inactive_status(self):
            # given
            self.init_test_data()

            # when
            paginated_offers = get_paginated_offers_for_filters(
                user_id=self.pro.id, user_is_admin=self.pro.isAdmin, offers_per_page=5, page=1, status="INACTIVE"
            )

            # then
            offer_ids = [offer.identifier for offer in paginated_offers.offers]
            assert Identifier(self.active_thing_offer_with_one_stock_with_remaining_quantity.id) not in offer_ids
            assert Identifier(self.active_thing_offer_with_all_stocks_without_quantity.id) not in offer_ids
            assert Identifier(self.active_event_offer_with_stock_in_the_future_without_quantity.id) not in offer_ids
            assert (
                Identifier(self.active_event_offer_with_one_stock_in_the_future_with_remaining_quantity.id)
                not in offer_ids
            )
            assert Identifier(self.inactive_thing_offer_without_stock.id) in offer_ids
            assert Identifier(self.inactive_thing_offer_with_stock_with_remaining_quantity.id) in offer_ids
            assert Identifier(self.inactive_expired_event_offer.id) in offer_ids
            assert Identifier(self.inactive_thing_offer_without_remaining_quantity.id) in offer_ids
            assert Identifier(self.sold_out_thing_offer_without_stock.id) not in offer_ids
            assert Identifier(self.sold_old_thing_offer_with_all_stocks_empty.id) not in offer_ids
            assert (
                Identifier(self.sold_out_event_offer_with_all_stocks_in_the_future_with_zero_remaining_quantity.id)
                not in offer_ids
            )
            assert Identifier(self.sold_out_event_offer_with_only_one_stock_soft_deleted.id) not in offer_ids
            assert Identifier(self.sold_out_event_offer_without_stock.id) not in offer_ids
            assert Identifier(self.expired_event_offer_with_stock_in_the_past_without_quantity.id) not in offer_ids
            assert Identifier(self.expired_thing_offer_with_a_stock_expired_with_remaining_quantity.id) not in offer_ids
            assert (
                Identifier(self.expired_thing_offer_with_a_stock_expired_with_zero_remaining_quantity.id)
                not in offer_ids
            )
            assert (
                Identifier(self.expired_event_offer_with_all_stocks_in_the_past_with_remaining_quantity.id)
                not in offer_ids
            )
            assert (
                Identifier(self.expired_event_offer_with_all_stocks_in_the_past_with_zero_remaining_quantity.id)
                not in offer_ids
            )
            assert paginated_offers.total_offers == 4

        @pytest.mark.usefixtures("db_session")
        def should_return_only_sold_out_offers_when_requesting_sold_out_status(self):
            # given
            self.init_test_data()

            # when
            paginated_offers = get_paginated_offers_for_filters(
                user_id=self.pro.id, user_is_admin=self.pro.isAdmin, offers_per_page=10, page=1, status="SOLD_OUT"
            )

            # then
            offer_ids = [offer.identifier for offer in paginated_offers.offers]
            assert Identifier(self.active_thing_offer_with_one_stock_with_remaining_quantity.id) not in offer_ids
            assert Identifier(self.active_thing_offer_with_all_stocks_without_quantity.id) not in offer_ids
            assert Identifier(self.active_event_offer_with_stock_in_the_future_without_quantity.id) not in offer_ids
            assert (
                Identifier(self.active_event_offer_with_one_stock_in_the_future_with_remaining_quantity.id)
                not in offer_ids
            )
            assert Identifier(self.inactive_thing_offer_without_stock.id) not in offer_ids
            assert Identifier(self.inactive_thing_offer_with_stock_with_remaining_quantity.id) not in offer_ids
            assert Identifier(self.inactive_expired_event_offer.id) not in offer_ids
            assert Identifier(self.inactive_thing_offer_without_remaining_quantity.id) not in offer_ids
            assert Identifier(self.sold_out_thing_offer_without_stock.id) in offer_ids
            assert Identifier(self.sold_old_thing_offer_with_all_stocks_empty.id) in offer_ids
            assert (
                Identifier(self.sold_out_event_offer_with_all_stocks_in_the_future_with_zero_remaining_quantity.id)
                in offer_ids
            )
            assert Identifier(self.sold_out_event_offer_with_only_one_stock_soft_deleted.id) in offer_ids
            assert Identifier(self.sold_out_event_offer_without_stock.id) in offer_ids
            assert Identifier(self.sold_out_offer_on_other_venue.id) in offer_ids
            assert Identifier(self.expired_event_offer_with_stock_in_the_past_without_quantity.id) not in offer_ids
            assert Identifier(self.expired_thing_offer_with_a_stock_expired_with_remaining_quantity.id) not in offer_ids
            assert (
                Identifier(self.expired_thing_offer_with_a_stock_expired_with_zero_remaining_quantity.id)
                not in offer_ids
            )
            assert (
                Identifier(self.expired_event_offer_with_all_stocks_in_the_past_with_remaining_quantity.id)
                not in offer_ids
            )
            assert (
                Identifier(self.expired_event_offer_with_all_stocks_in_the_past_with_zero_remaining_quantity.id)
                not in offer_ids
            )
            assert paginated_offers.total_offers == 6

        @pytest.mark.usefixtures("db_session")
        def should_return_offers_with_no_stocks_when_requesting_sold_out_status(self):
            # given
            self.init_test_data()

            # when
            paginated_offers = get_paginated_offers_for_filters(
                user_id=self.pro.id, user_is_admin=self.pro.isAdmin, offers_per_page=5, page=1, status="SOLD_OUT"
            )

            # then
            offer_ids = [offer.identifier for offer in paginated_offers.offers]
            assert Identifier(self.sold_out_thing_offer_without_stock.id) in offer_ids
            assert Identifier(self.sold_out_event_offer_with_only_one_stock_soft_deleted.id) in offer_ids

        @pytest.mark.usefixtures("db_session")
        def should_return_offers_with_no_remaining_quantity_and_no_bookings_when_requesting_sold_out_status(self):
            # given
            self.init_test_data()

            # when
            paginated_offers = get_paginated_offers_for_filters(
                user_id=self.pro.id, user_is_admin=self.pro.isAdmin, offers_per_page=5, page=1, status="SOLD_OUT"
            )

            # then
            offer_ids = [offer.identifier for offer in paginated_offers.offers]
            assert Identifier(self.sold_old_thing_offer_with_all_stocks_empty.id) in offer_ids

        @pytest.mark.usefixtures("db_session")
        def should_return_offers_with_no_remaining_quantity_in_the_future_when_requesting_sold_out_status(self):
            # given
            self.init_test_data()

            # when
            paginated_offers = get_paginated_offers_for_filters(
                user_id=self.pro.id, user_is_admin=self.pro.isAdmin, offers_per_page=5, page=1, status="SOLD_OUT"
            )

            # then
            offer_ids = [offer.identifier for offer in paginated_offers.offers]
            assert (
                Identifier(self.sold_out_event_offer_with_all_stocks_in_the_future_with_zero_remaining_quantity.id)
                in offer_ids
            )

        @pytest.mark.usefixtures("db_session")
        def should_exclude_offers_with_cancelled_bookings_when_requesting_sold_out_status(self):
            # given
            self.init_test_data()

            # when
            paginated_offers = get_paginated_offers_for_filters(
                user_id=self.pro.id, user_is_admin=self.pro.isAdmin, offers_per_page=5, page=1, status="SOLD_OUT"
            )

            # then
            offer_ids = [offer.identifier for offer in paginated_offers.offers]
            assert (
                Identifier(self.active_event_offer_with_one_stock_in_the_future_with_remaining_quantity.id)
                not in offer_ids
            )

        @pytest.mark.usefixtures("db_session")
        def should_return_only_expired_offers_when_requesting_expired_status(self):
            # given
            self.init_test_data()

            # when
            paginated_offers = get_paginated_offers_for_filters(
                user_id=self.pro.id, user_is_admin=self.pro.isAdmin, offers_per_page=5, page=1, status="EXPIRED"
            )

            # then
            offer_ids = [offer.identifier for offer in paginated_offers.offers]
            assert Identifier(self.active_thing_offer_with_one_stock_with_remaining_quantity.id) not in offer_ids
            assert Identifier(self.active_thing_offer_with_all_stocks_without_quantity.id) not in offer_ids
            assert Identifier(self.active_event_offer_with_stock_in_the_future_without_quantity.id) not in offer_ids
            assert (
                Identifier(self.active_event_offer_with_one_stock_in_the_future_with_remaining_quantity.id)
                not in offer_ids
            )
            assert Identifier(self.inactive_thing_offer_without_stock.id) not in offer_ids
            assert Identifier(self.inactive_thing_offer_with_stock_with_remaining_quantity.id) not in offer_ids
            assert Identifier(self.inactive_expired_event_offer.id) not in offer_ids
            assert Identifier(self.inactive_thing_offer_without_remaining_quantity.id) not in offer_ids
            assert Identifier(self.sold_out_thing_offer_without_stock.id) not in offer_ids
            assert Identifier(self.sold_old_thing_offer_with_all_stocks_empty.id) not in offer_ids
            assert (
                Identifier(self.sold_out_event_offer_with_all_stocks_in_the_future_with_zero_remaining_quantity.id)
                not in offer_ids
            )
            assert Identifier(self.sold_out_event_offer_with_only_one_stock_soft_deleted.id) not in offer_ids
            assert Identifier(self.sold_out_event_offer_without_stock.id) not in offer_ids
            assert Identifier(self.expired_event_offer_with_stock_in_the_past_without_quantity.id) in offer_ids
            assert Identifier(self.expired_thing_offer_with_a_stock_expired_with_remaining_quantity.id) in offer_ids
            assert (
                Identifier(self.expired_thing_offer_with_a_stock_expired_with_zero_remaining_quantity.id) in offer_ids
            )
            assert (
                Identifier(self.expired_event_offer_with_all_stocks_in_the_past_with_remaining_quantity.id) in offer_ids
            )
            assert (
                Identifier(self.expired_event_offer_with_all_stocks_in_the_past_with_zero_remaining_quantity.id)
                in offer_ids
            )
            assert paginated_offers.total_offers == 5

        @pytest.mark.usefixtures("db_session")
        def should_return_only_awaiting_offers_when_requesting_awaiting_status(self):
            # given
            unexpired_booking_limit_date = datetime.utcnow() + timedelta(days=3)

            awaiting_offer = offers_factories.ThingOfferFactory(
                validation=OfferValidationStatus.AWAITING, name="Offre en attente"
            )
            offers_factories.StockFactory(bookingLimitDatetime=unexpired_booking_limit_date, offer=awaiting_offer)

            offer = offers_factories.OfferFactory(product__type=str(ThingType.INSTRUMENT))
            offers_factories.StockFactory(bookingLimitDatetime=unexpired_booking_limit_date, offer=offer)

            user = awaiting_offer.venue.managingOfferer

            # when
            paginated_offers = get_paginated_offers_for_filters(
                user_id=user.id, user_is_admin=True, offers_per_page=5, page=1, status="AWAITING"
            )

            # then
            assert len(paginated_offers.offers) == 1
            assert paginated_offers.offers[0].name == "Offre en attente"
            assert paginated_offers.offers[0].status == OfferStatus.AWAITING.name

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
            paginated_offers = get_paginated_offers_for_filters(
                user_id=user.id, user_is_admin=True, offers_per_page=5, page=1, status="REJECTED"
            )

            # then
            assert len(paginated_offers.offers) == 1
            assert paginated_offers.offers[0].name == "Offre rejetée"
            assert paginated_offers.offers[0].status == OfferStatus.REJECTED.name

        @pytest.mark.usefixtures("db_session")
        def should_return_only_sold_out_offers_and_requested_venue_when_requesting_sold_out_status_and_specific_venue(
            self,
        ):
            # given
            self.init_test_data()

            # when
            paginated_offers = get_paginated_offers_for_filters(
                user_id=self.pro.id,
                user_is_admin=self.pro.isAdmin,
                offers_per_page=5,
                page=1,
                status="SOLD_OUT",
                venue_id=self.other_venue.id,
            )

            # then
            offer_ids = [offer.identifier for offer in paginated_offers.offers]
            assert Identifier(self.sold_out_thing_offer_without_stock.id) not in offer_ids
            assert Identifier(self.sold_old_thing_offer_with_all_stocks_empty.id) not in offer_ids
            assert (
                Identifier(self.sold_out_event_offer_with_all_stocks_in_the_future_with_zero_remaining_quantity.id)
                not in offer_ids
            )
            assert Identifier(self.sold_out_event_offer_with_only_one_stock_soft_deleted.id) not in offer_ids
            assert Identifier(self.sold_out_event_offer_without_stock.id) not in offer_ids
            assert Identifier(self.sold_out_offer_on_other_venue.id) in offer_ids
            assert paginated_offers.total_offers == 1

        @pytest.mark.usefixtures("db_session")
        def should_return_only_active_offer_on_specific_period_when_requesting_active_status_and_time_period(self):
            # given
            self.init_test_data()

            in_six_days = datetime.now() + timedelta(days=6)
            in_six_days_beginning = in_six_days.replace(hour=0, minute=0, second=0)
            in_six_days_ending = in_six_days.replace(hour=23, minute=59, second=59)

            # when
            paginated_offers = get_paginated_offers_for_filters(
                user_id=self.pro.id,
                user_is_admin=self.pro.isAdmin,
                offers_per_page=5,
                page=1,
                status="ACTIVE",
                period_beginning_date=in_six_days_beginning.isoformat(),
                period_ending_date=in_six_days_ending.isoformat(),
            )

            # then
            offer_ids = [offer.identifier for offer in paginated_offers.offers]
            assert Identifier(self.active_event_in_six_days_offer.id) in offer_ids
            assert (
                Identifier(self.active_event_offer_with_one_stock_in_the_future_with_remaining_quantity.id)
                not in offer_ids
            )
            assert Identifier(self.active_event_offer_with_stock_in_the_future_without_quantity.id) not in offer_ids
            assert Identifier(self.active_thing_offer_with_all_stocks_without_quantity.id) not in offer_ids
            assert Identifier(self.active_thing_offer_with_one_stock_with_remaining_quantity.id) not in offer_ids
            assert paginated_offers.total_offers == 1


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
