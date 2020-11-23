from datetime import datetime
from datetime import timedelta

import pytest

from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers.repository import find_online_activation_stock
from pcapi.core.offers.repository import get_paginated_offers_for_offerer_venue_and_keywords
from pcapi.core.users import factories as users_factories
from pcapi.domain.identifier.identifier import Identifier
from pcapi.domain.pro_offers.paginated_offers_recap import PaginatedOffersRecap
from pcapi.model_creators.generic_creators import create_booking
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_provider
from pcapi.model_creators.generic_creators import create_user
from pcapi.model_creators.generic_creators import create_user_offerer
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_offer_with_event_product
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.model_creators.specific_creators import create_product_with_event_type
from pcapi.model_creators.specific_creators import create_product_with_thing_type
from pcapi.model_creators.specific_creators import create_stock_from_offer
from pcapi.models import ThingType
from pcapi.repository import repository


class PaginatedOfferSQLRepositoryTest:
    @pytest.mark.usefixtures("db_session")
    def should_return_paginated_offers_with_details_of_pagination_and_offers_of_requested_page(self, app):
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
        paginated_offers = get_paginated_offers_for_offerer_venue_and_keywords(
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
    def should_return_offers_sorted_by_id_desc(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)
        venue = create_venue(offerer)
        offer1 = create_offer_with_thing_product(venue)
        offer2 = create_offer_with_thing_product(venue)
        repository.save(user_offerer, offer1, offer2)

        # When
        paginated_offers = get_paginated_offers_for_offerer_venue_and_keywords(
            user_id=user.id, user_is_admin=user.isAdmin, page=1, offers_per_page=10
        )

        # Then
        assert paginated_offers.offers[0].identifier.persisted > paginated_offers.offers[1].identifier.persisted

    @pytest.mark.usefixtures("db_session")
    def should_return_offers_of_given_type(self, app):
        user_offerer = offers_factories.UserOffererFactory()
        requested_offer = offers_factories.OfferFactory(
            type=str(ThingType.AUDIOVISUEL), venue__managingOfferer=user_offerer.offerer
        )
        other_offer = offers_factories.OfferFactory(
            type=str(ThingType.JEUX), venue__managingOfferer=user_offerer.offerer
        )

        paginated_offers = get_paginated_offers_for_offerer_venue_and_keywords(
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
    def should_return_offers_matching_searched_name(self, app):
        user = create_user()
        offerer = create_offerer(siren="123456789")
        user_offerer = create_user_offerer(user=user, offerer=offerer)

        product_event = create_product_with_event_type(event_name="Rencontre avec Jacques Martin")
        product_thing = create_product_with_thing_type(thing_name="Belle du Seigneur", author_name="Jacqueline Rencon")
        requested_venue = create_venue(
            offerer=offerer,
            name="Bataclan",
            city="Paris",
            siret=offerer.siren + "12345",
        )
        other_venue = create_venue(
            offerer=offerer,
            name="Librairie la Rencontre des jachères",
            city="Saint Denis",
            siret=offerer.siren + "54321",
        )
        offer_matching_requested_name = create_offer_with_event_product(venue=requested_venue, product=product_event)
        offer_not_matching_requested_name = create_offer_with_thing_product(venue=other_venue, product=product_thing)
        repository.save(
            user_offerer,
            offer_matching_requested_name,
            offer_not_matching_requested_name,
        )

        # when
        paginated_offers = get_paginated_offers_for_offerer_venue_and_keywords(
            user_id=user.id,
            user_is_admin=user.isAdmin,
            name_keywords="Jac rencon",
            page=1,
            offers_per_page=10,
        )

        # then
        offers_id = [offer.identifier for offer in paginated_offers.offers]
        assert Identifier(offer_matching_requested_name.id) in offers_id
        assert Identifier(offer_not_matching_requested_name.id) not in offers_id
        assert paginated_offers.total_offers == 1

    @pytest.mark.usefixtures("db_session")
    def test_returns_offers_filtered_by_manual_creation_mode_when_provided(self, app: object):
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
        paginated_offers = get_paginated_offers_for_offerer_venue_and_keywords(
            user_id=pro_user.id, user_is_admin=pro_user.isAdmin, page=1, offers_per_page=1, creation_mode="manual"
        )

        # then
        assert paginated_offers.offers[0].identifier.persisted == manually_created_offer.id
        assert paginated_offers.total_offers == 1

    @pytest.mark.usefixtures("db_session")
    def test_returns_offers_filtered_by_imported_creation_mode_when_provided(self, app: object):
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
        paginated_offers = get_paginated_offers_for_offerer_venue_and_keywords(
            user_id=pro_user.id, user_is_admin=pro_user.isAdmin, page=1, offers_per_page=1, creation_mode="imported"
        )

        # then
        assert paginated_offers.offers[0].identifier.persisted == imported_offer.id
        assert paginated_offers.total_offers == 1

    class WhenUserIsAdmin:
        @pytest.mark.usefixtures("db_session")
        def should_return_offers_of_given_venue_when_user_is_not_attached_to_its_offerer(self, app):
            # given
            admin = users_factories.UserFactory(canBookFreeOffers=False, isAdmin=True)
            offer_for_requested_venue = offers_factories.OfferFactory()
            offer_for_other_venue = offers_factories.OfferFactory()

            # when
            paginated_offers = get_paginated_offers_for_offerer_venue_and_keywords(
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
            admin = users_factories.UserFactory(canBookFreeOffers=False, isAdmin=True)
            admin_attachment_to_offerer = offers_factories.UserOffererFactory(user=admin)
            offer_for_requested_venue = offers_factories.OfferFactory(
                venue__managingOfferer=admin_attachment_to_offerer.offerer
            )
            offer_for_other_venue = offers_factories.OfferFactory(
                venue__managingOfferer=admin_attachment_to_offerer.offerer
            )

            # when
            paginated_offers = get_paginated_offers_for_offerer_venue_and_keywords(
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
        def should_return_offers_of_given_offerer_when_user_is_not_attached_to_it(self, app: object):
            # given
            admin = users_factories.UserFactory(canBookFreeOffers=False, isAdmin=True)
            offer_for_requested_offerer = offers_factories.OfferFactory()
            offer_for_other_offerer = offers_factories.OfferFactory()

            # When
            paginated_offers = get_paginated_offers_for_offerer_venue_and_keywords(
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
        def should_return_offers_of_given_offerer_when_user_is_attached_to_it(self, app: object):
            # given
            admin = users_factories.UserFactory(canBookFreeOffers=False, isAdmin=True)
            admin_attachment_to_requested_offerer = offers_factories.UserOffererFactory(user=admin)
            admin_attachment_to_other_offerer = offers_factories.UserOffererFactory(user=admin)
            offer_for_requested_offerer = offers_factories.OfferFactory(
                venue__managingOfferer=admin_attachment_to_requested_offerer.offerer
            )
            offer_for_other_offerer = offers_factories.OfferFactory(
                venue__managingOfferer=admin_attachment_to_other_offerer.offerer
            )

            # When
            paginated_offers = get_paginated_offers_for_offerer_venue_and_keywords(
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
            admin = users_factories.UserFactory(canBookFreeOffers=False, isAdmin=False)
            offer_for_requested_venue = offers_factories.OfferFactory()
            offer_for_other_venue = offers_factories.OfferFactory()

            # when
            paginated_offers = get_paginated_offers_for_offerer_venue_and_keywords(
                user_id=admin.id,
                user_is_admin=admin.isAdmin,
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
            pro = users_factories.UserFactory(canBookFreeOffers=False, isAdmin=False)
            pro_attachment_to_offerer = offers_factories.UserOffererFactory(user=pro)
            offer_for_requested_venue = offers_factories.OfferFactory(
                venue__managingOfferer=pro_attachment_to_offerer.offerer
            )
            offer_for_other_venue = offers_factories.OfferFactory(
                venue__managingOfferer=pro_attachment_to_offerer.offerer
            )

            # when
            paginated_offers = get_paginated_offers_for_offerer_venue_and_keywords(
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
        def should_not_return_offers_of_given_offerer_when_user_is_not_attached_to_it(self, app: object):
            # given
            pro = users_factories.UserFactory(canBookFreeOffers=False, isAdmin=False)
            offer_for_requested_offerer = offers_factories.OfferFactory()
            offer_for_other_offerer = offers_factories.OfferFactory()

            # When
            paginated_offers = get_paginated_offers_for_offerer_venue_and_keywords(
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
        def should_return_offers_of_given_offerer_when_user_is_attached_to_it(self, app: object):
            # given
            pro = users_factories.UserFactory(canBookFreeOffers=False, isAdmin=False)
            pro_attachment_to_requested_offerer = offers_factories.UserOffererFactory(user=pro)
            pro_attachment_to_other_offerer = offers_factories.UserOffererFactory(user=pro)
            offer_for_requested_offerer = offers_factories.OfferFactory(
                venue__managingOfferer=pro_attachment_to_requested_offerer.offerer
            )
            offer_for_other_offerer = offers_factories.OfferFactory(
                venue__managingOfferer=pro_attachment_to_other_offerer.offerer
            )

            # When
            paginated_offers = get_paginated_offers_for_offerer_venue_and_keywords(
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

    class StatusFiltersTest:
        def setup_method(self):
            self.offerer = create_offerer()
            self.venue = create_venue(self.offerer)
            self.pro = create_user()
            self.user_offerer = create_user_offerer(self.pro, self.offerer)

            self.inactive_thing_offer_with_stock_with_remaining_quantity = create_offer_with_thing_product(
                self.venue, is_active=False, description="inactive_thing_offer_with_stock_with_remaining_quantity"
            )
            self.inactive_thing_offer_without_remaining_quantity = create_offer_with_thing_product(
                self.venue, is_active=False, description="inactive_thing_offer_without_remaining_quantity"
            )
            self.inactive_thing_offer_without_stock = create_offer_with_thing_product(
                self.venue, is_active=False, description="inactive_thing_offer_without_stock"
            )
            self.inactive_expired_event_offer = create_offer_with_event_product(
                self.venue, is_active=False, description="inactive_expired_event_offer"
            )
            self.active_thing_offer_with_one_stock_with_remaining_quantity = create_offer_with_thing_product(
                self.venue, is_active=True, description="active_thing_offer_with_one_stock_with_remaining_quantity"
            )
            self.active_thing_offer_with_all_stocks_without_quantity = create_offer_with_thing_product(
                self.venue, is_active=True, description="active_thing_offer_with_all_stocks_without_quantity"
            )
            self.active_event_offer_with_stock_in_the_future_without_quantity = create_offer_with_event_product(
                venue=self.venue, description="active_event_offer_with_stock_in_the_future_without_quantity"
            )
            self.active_event_offer_with_one_stock_in_the_future_with_remaining_quantity = (
                create_offer_with_event_product(
                    venue=self.venue,
                    description="active_event_offer_with_one_stock_in_the_future_with_remaining_quantity",
                )
            )
            self.sold_old_thing_offer_with_all_stocks_empty = create_offer_with_thing_product(
                self.venue, description="sold_old_thing_offer_with_all_stocks_empty"
            )
            self.sold_out_event_offer_with_all_stocks_in_the_future_with_zero_remaining_quantity = (
                create_offer_with_event_product(
                    venue=self.venue,
                    description="sold_out_event_offer_with_all_stocks_in_the_future_with_zero_remaining_quantity",
                )
            )
            self.sold_out_thing_offer_without_stock = create_offer_with_thing_product(
                self.venue, description="sold_out_thing_offer_without_stock"
            )
            self.sold_out_event_offer_without_stock = create_offer_with_event_product(
                venue=self.venue, description="sold_out_event_offer_without_stock"
            )
            self.sold_out_event_offer_with_only_one_stock_soft_deleted = create_offer_with_event_product(
                venue=self.venue, description="sold_out_event_offer_with_only_one_stock_soft_deleted"
            )
            self.expired_event_offer_with_stock_in_the_past_without_quantity = create_offer_with_event_product(
                venue=self.venue, description="expired_event_offer_with_stock_in_the_past_without_quantity"
            )
            self.expired_event_offer_with_all_stocks_in_the_past_with_remaining_quantity = (
                create_offer_with_event_product(
                    venue=self.venue,
                    description="expired_event_offer_with_all_stocks_in_the_past_with_remaining_quantity",
                )
            )
            self.expired_event_offer_with_all_stocks_in_the_past_with_zero_remaining_quantity = (
                create_offer_with_event_product(
                    venue=self.venue,
                    description="expired_event_offer_with_all_stocks_in_the_past_with_zero_remaining_quantity",
                )
            )
            self.expired_thing_offer_with_a_stock_expired_with_remaining_quantity = create_offer_with_event_product(
                venue=self.venue,
                description="expired_thing_offer_with_a_stock_expired_with_remaining_quantity",
            )
            self.expired_thing_offer_with_a_stock_expired_with_zero_remaining_quantity = (
                create_offer_with_event_product(
                    venue=self.venue,
                    description="expired_thing_offer_with_a_stock_expired_with_zero_remaining_quantity",
                )
            )

        def save_data_set(self):
            five_days_ago = datetime.now() - timedelta(days=5)
            in_five_days = datetime.now() + timedelta(days=5)
            beneficiary = create_user(email="jane.doe@example.com")
            stock_1 = create_stock_from_offer(self.sold_old_thing_offer_with_all_stocks_empty, quantity=0)
            stock_2 = create_stock_from_offer(
                self.active_thing_offer_with_one_stock_with_remaining_quantity, quantity=5
            )
            stock_3 = create_stock_from_offer(
                self.active_thing_offer_with_one_stock_with_remaining_quantity, quantity=0
            )
            stock_4 = create_stock_from_offer(self.active_thing_offer_with_all_stocks_without_quantity, quantity=None)
            stock_5 = create_stock_from_offer(
                self.expired_event_offer_with_stock_in_the_past_without_quantity,
                beginning_datetime=five_days_ago,
                booking_limit_datetime=five_days_ago,
                quantity=None,
            )
            stock_17 = create_stock_from_offer(
                self.expired_event_offer_with_stock_in_the_past_without_quantity,
                beginning_datetime=in_five_days,
                booking_limit_datetime=in_five_days,
                quantity=None,
                soft_deleted=True,
            )
            stock_6 = create_stock_from_offer(
                self.active_event_offer_with_stock_in_the_future_without_quantity,
                beginning_datetime=in_five_days,
                booking_limit_datetime=in_five_days,
                quantity=None,
            )
            stock_7 = create_stock_from_offer(
                self.expired_event_offer_with_all_stocks_in_the_past_with_remaining_quantity,
                beginning_datetime=five_days_ago,
                booking_limit_datetime=five_days_ago,
                quantity=5,
            )
            stock_8 = create_stock_from_offer(
                self.expired_event_offer_with_all_stocks_in_the_past_with_remaining_quantity,
                beginning_datetime=five_days_ago,
                booking_limit_datetime=five_days_ago,
                quantity=4,
            )
            stock_9 = create_stock_from_offer(
                self.active_event_offer_with_one_stock_in_the_future_with_remaining_quantity,
                beginning_datetime=in_five_days,
                booking_limit_datetime=in_five_days,
                quantity=1,
            )
            stock_10 = create_stock_from_offer(
                self.active_event_offer_with_one_stock_in_the_future_with_remaining_quantity,
                beginning_datetime=in_five_days,
                booking_limit_datetime=in_five_days,
                quantity=0,
            )
            stock_11 = create_stock_from_offer(
                self.expired_event_offer_with_all_stocks_in_the_past_with_zero_remaining_quantity,
                beginning_datetime=five_days_ago,
                booking_limit_datetime=five_days_ago,
                quantity=0,
            )
            stock_12 = create_stock_from_offer(
                self.expired_event_offer_with_all_stocks_in_the_past_with_zero_remaining_quantity,
                beginning_datetime=five_days_ago,
                booking_limit_datetime=five_days_ago,
                quantity=0,
            )
            stock_13 = create_stock_from_offer(
                self.sold_out_event_offer_with_all_stocks_in_the_future_with_zero_remaining_quantity,
                beginning_datetime=five_days_ago,
                booking_limit_datetime=five_days_ago,
                quantity=5,
            )
            stock_14 = create_stock_from_offer(
                self.sold_out_event_offer_with_all_stocks_in_the_future_with_zero_remaining_quantity,
                beginning_datetime=in_five_days,
                booking_limit_datetime=in_five_days,
                quantity=1,
                price=0,
            )
            stock_15 = create_stock_from_offer(self.inactive_thing_offer_with_stock_with_remaining_quantity, quantity=4)
            stock_16 = create_stock_from_offer(
                self.active_event_offer_with_stock_in_the_future_without_quantity,
                beginning_datetime=five_days_ago,
                booking_limit_datetime=five_days_ago,
                quantity=None,
            )
            stock_18 = create_stock_from_offer(
                self.inactive_expired_event_offer,
                beginning_datetime=five_days_ago,
                booking_limit_datetime=five_days_ago,
                quantity=None,
            )
            stock_19 = create_stock_from_offer(self.inactive_thing_offer_without_remaining_quantity, quantity=0)
            stock_20 = create_stock_from_offer(
                self.sold_out_event_offer_with_only_one_stock_soft_deleted, quantity=10, soft_deleted=True
            )
            stock_21 = create_stock_from_offer(
                self.expired_thing_offer_with_a_stock_expired_with_remaining_quantity,
                booking_limit_datetime=five_days_ago,
                quantity=4,
            )
            stock_22 = create_stock_from_offer(
                self.expired_thing_offer_with_a_stock_expired_with_zero_remaining_quantity,
                booking_limit_datetime=five_days_ago,
                quantity=0,
            )
            booking = create_booking(user=beneficiary, stock=stock_14)
            booking_cancelled = create_booking(user=beneficiary, stock=stock_9, is_cancelled=True)
            stocks = [
                stock_1,
                stock_2,
                stock_3,
                stock_4,
                stock_5,
                stock_6,
                stock_7,
                stock_8,
                stock_10,
                stock_11,
                stock_12,
                stock_13,
                stock_15,
                stock_16,
                stock_17,
                stock_18,
                stock_19,
                stock_20,
                stock_21,
                stock_22,
            ]

            repository.save(
                self.user_offerer,
                self.inactive_thing_offer_without_stock,
                self.sold_out_thing_offer_without_stock,
                self.sold_out_event_offer_without_stock,
                *stocks,
                booking,
                booking_cancelled,
            )

        @pytest.mark.usefixtures("db_session")
        def should_return_only_active_offers_when_requesting_active_status(self, app):
            self.save_data_set()

            # when
            paginated_offers = get_paginated_offers_for_offerer_venue_and_keywords(
                user_id=self.pro.id, user_is_admin=self.pro.isAdmin, offers_per_page=5, page=1, status="active"
            )

            # then
            offer_ids = [offer.identifier for offer in paginated_offers.offers]
            assert Identifier(self.active_thing_offer_with_one_stock_with_remaining_quantity.id) in offer_ids
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
            assert paginated_offers.total_offers == 4

        @pytest.mark.usefixtures("db_session")
        def should_return_only_inactive_offers_when_requesting_inactive_status(self, app):
            # given
            self.save_data_set()

            # when
            paginated_offers = get_paginated_offers_for_offerer_venue_and_keywords(
                user_id=self.pro.id, user_is_admin=self.pro.isAdmin, offers_per_page=5, page=1, status="inactive"
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
        def should_return_only_sold_out_offers_when_requesting_sold_out_status(self, app):
            # given
            self.save_data_set()

            # when
            paginated_offers = get_paginated_offers_for_offerer_venue_and_keywords(
                user_id=self.pro.id, user_is_admin=self.pro.isAdmin, offers_per_page=5, page=1, status="soldOut"
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
            assert paginated_offers.total_offers == 5

        @pytest.mark.usefixtures("db_session")
        def should_return_offers_with_no_stocks_when_requesting_sold_out_status(self, app):
            # given
            self.save_data_set()

            # when
            paginated_offers = get_paginated_offers_for_offerer_venue_and_keywords(
                user_id=self.pro.id, user_is_admin=self.pro.isAdmin, offers_per_page=5, page=1, status="soldOut"
            )

            # then
            offer_ids = [offer.identifier for offer in paginated_offers.offers]
            assert Identifier(self.sold_out_thing_offer_without_stock.id) in offer_ids
            assert Identifier(self.sold_out_event_offer_with_only_one_stock_soft_deleted.id) in offer_ids

        @pytest.mark.usefixtures("db_session")
        def should_return_offers_with_no_remaining_quantity_and_no_bookings_when_requesting_sold_out_status(self, app):
            # given
            self.save_data_set()

            # when
            paginated_offers = get_paginated_offers_for_offerer_venue_and_keywords(
                user_id=self.pro.id, user_is_admin=self.pro.isAdmin, offers_per_page=5, page=1, status="soldOut"
            )

            # then
            offer_ids = [offer.identifier for offer in paginated_offers.offers]
            assert Identifier(self.sold_old_thing_offer_with_all_stocks_empty.id) in offer_ids

        @pytest.mark.usefixtures("db_session")
        def should_return_offers_with_no_remaining_quantity_in_the_future_when_requesting_sold_out_status(self, app):
            # given
            self.save_data_set()

            # when
            paginated_offers = get_paginated_offers_for_offerer_venue_and_keywords(
                user_id=self.pro.id, user_is_admin=self.pro.isAdmin, offers_per_page=5, page=1, status="soldOut"
            )

            # then
            offer_ids = [offer.identifier for offer in paginated_offers.offers]
            assert (
                Identifier(self.sold_out_event_offer_with_all_stocks_in_the_future_with_zero_remaining_quantity.id)
                in offer_ids
            )

        @pytest.mark.usefixtures("db_session")
        def should_exclude_offers_with_cancelled_bookings_when_requesting_sold_out_status(self, app):
            # given
            self.save_data_set()

            # when
            paginated_offers = get_paginated_offers_for_offerer_venue_and_keywords(
                user_id=self.pro.id, user_is_admin=self.pro.isAdmin, offers_per_page=5, page=1, status="soldOut"
            )

            # then
            offer_ids = [offer.identifier for offer in paginated_offers.offers]
            assert (
                Identifier(self.active_event_offer_with_one_stock_in_the_future_with_remaining_quantity.id)
                not in offer_ids
            )

        @pytest.mark.usefixtures("db_session")
        def should_return_only_expired_offers_when_requesting_expired_status(self, app):
            # given
            self.save_data_set()

            # when
            paginated_offers = get_paginated_offers_for_offerer_venue_and_keywords(
                user_id=self.pro.id, user_is_admin=self.pro.isAdmin, offers_per_page=5, page=1, status="expired"
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
        def should_return_only_sold_out_offers_and_requested_venue_when_requesting_sold_out_status_and_specific_venue(
            self, app
        ):
            # given
            self.save_data_set()
            other_venue = create_venue(offerer=self.offerer, siret="12345678998765")
            sold_out_offer_on_other_venue = create_offer_with_thing_product(other_venue)
            repository.save(sold_out_offer_on_other_venue)

            # when
            paginated_offers = get_paginated_offers_for_offerer_venue_and_keywords(
                user_id=self.pro.id,
                user_is_admin=self.pro.isAdmin,
                offers_per_page=5,
                page=1,
                status="soldOut",
                venue_id=other_venue.id,
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
            assert Identifier(sold_out_offer_on_other_venue.id) in offer_ids
            assert paginated_offers.total_offers == 1

        @pytest.mark.usefixtures("db_session")
        def should_return_only_active_offer_on_specific_period_when_requesting_active_status_and_time_period(self, app):
            # given
            in_six_days = datetime.now() + timedelta(days=6)
            in_six_days_beginning = in_six_days.replace(hour=0, minute=0, second=0)
            in_six_days_ending = in_six_days.replace(hour=23, minute=59, second=59)
            active_event_in_six_days_offer = create_offer_with_event_product(venue=self.venue)
            stock = create_stock_from_offer(
                offer=active_event_in_six_days_offer,
                beginning_datetime=in_six_days,
                booking_limit_datetime=in_six_days,
                quantity=10,
            )
            self.save_data_set()
            repository.save(stock)

            # when
            paginated_offers = get_paginated_offers_for_offerer_venue_and_keywords(
                user_id=self.pro.id,
                user_is_admin=self.pro.isAdmin,
                offers_per_page=5,
                page=1,
                status="active",
                period_beginning_date=in_six_days_beginning.isoformat(),
                period_ending_date=in_six_days_ending.isoformat(),
            )

            # then
            offer_ids = [offer.identifier for offer in paginated_offers.offers]
            assert Identifier(active_event_in_six_days_offer.id) in offer_ids
            assert (
                Identifier(self.active_event_offer_with_one_stock_in_the_future_with_remaining_quantity.id)
                not in offer_ids
            )
            assert Identifier(self.active_event_offer_with_stock_in_the_future_without_quantity.id) not in offer_ids
            assert Identifier(self.active_thing_offer_with_all_stocks_without_quantity.id) not in offer_ids
            assert Identifier(self.active_thing_offer_with_one_stock_with_remaining_quantity.id) not in offer_ids
            assert paginated_offers.total_offers == 1


@pytest.mark.usefixtures("db_session")
def test_find_online_activation_stock(app):
    offers_factories.EventStockFactory()
    offers_factories.StockFactory(offer__type=str(ThingType.ACTIVATION), offer__venue__isVirtual=False)

    # assert find_online_activation_stock() is None

    activation_stock = offers_factories.StockFactory(
        offer__type=str(ThingType.ACTIVATION),
        offer__venue=offers_factories.VirtualVenueFactory(),
        offer__product__type=str(ThingType.ACTIVATION),
    )

    assert find_online_activation_stock() == activation_stock
