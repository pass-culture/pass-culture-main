from datetime import datetime
from datetime import timedelta

import pytest

from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers.repository import get_paginated_offers_for_offerer_venue_and_keywords
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
    def should_return_a_number_of_page_as_an_integer(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)
        venue = create_venue(offerer)
        offer1 = create_offer_with_thing_product(venue)
        offer2 = create_offer_with_thing_product(venue)
        offer3 = create_offer_with_thing_product(venue)
        repository.save(user_offerer, offer1, offer2, offer3)
        requested_page = 1
        requested_offers_per_page = 2

        # When
        paginated_offers = get_paginated_offers_for_offerer_venue_and_keywords(
            user_id=user.id,
            user_is_admin=user.isAdmin,
            offers_per_page=requested_offers_per_page,
            page=requested_page,
        )

        # Then
        assert isinstance(paginated_offers, PaginatedOffersRecap)
        assert paginated_offers.total_pages == 2

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
    def should_return_offers_of_given_venue(self, app):
        user_offerer = offers_factories.UserOffererFactory()
        offer_for_requested_venue = offers_factories.OfferFactory(venue__managingOfferer=user_offerer.offerer)
        offer_for_other_venue = offers_factories.OfferFactory(venue__managingOfferer=user_offerer.offerer)

        # when
        paginated_offers = get_paginated_offers_for_offerer_venue_and_keywords(
            user_id=user_offerer.user.id,
            user_is_admin=user_offerer.user.isAdmin,
            venue_id=offer_for_requested_venue.venue.id,
            page=1,
            offers_per_page=10,
        )

        # then
        offers_id = [offer.identifier for offer in paginated_offers.offers]
        assert Identifier(offer_for_requested_venue.id) in offers_id
        assert Identifier(offer_for_other_venue.id) not in offers_id

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

    @pytest.mark.usefixtures("db_session")
    def test_returns_offers_filtered_by_offerer_id_when_provided(self, app: object):
        # given
        pro_user = create_user()
        wanted_offerer = create_offerer()
        unwanted_offerer = create_offerer(siren="981237")
        create_user_offerer(pro_user, wanted_offerer)
        create_user_offerer(pro_user, unwanted_offerer)
        venue_from_wanted_offerer = create_venue(wanted_offerer)
        venue_from_unwanted_offerer = create_venue(unwanted_offerer, siret="12345678912387")
        offer_from_wanted_offerer = create_offer_with_thing_product(
            venue=venue_from_wanted_offerer, thing_name="Returned offer"
        )
        offer_from_unwanted_offerer = create_offer_with_thing_product(
            venue=venue_from_unwanted_offerer, thing_name="Not returned offer"
        )

        repository.save(offer_from_wanted_offerer, offer_from_unwanted_offerer)

        # When
        paginated_offers = get_paginated_offers_for_offerer_venue_and_keywords(
            user_id=pro_user.id,
            user_is_admin=pro_user.isAdmin,
            page=1,
            offers_per_page=1,
            offerer_id=wanted_offerer.id,
        )

        # then
        assert paginated_offers.total_offers == 1
        assert paginated_offers.offers[0].name == offer_from_wanted_offerer.name

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
        assert paginated_offers.total_offers == 1
        assert paginated_offers.offers[0].identifier.persisted == manually_created_offer.id

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
        assert paginated_offers.total_offers == 1
        assert paginated_offers.offers[0].identifier.persisted == imported_offer.id

    class StatusFiltersTest:
        def setup_method(self):
            self.offerer = create_offerer()
            venue = create_venue(self.offerer)
            self.pro = create_user()
            self.user_offerer = create_user_offerer(self.pro, self.offerer)

            self.inactive_thing_offer_with_stock_with_remaining_quantity = create_offer_with_thing_product(
                venue, is_active=False
            )
            self.inactive_thing_offer_without_remaining_quantity = create_offer_with_thing_product(
                venue, is_active=False
            )
            self.inactive_thing_offer_without_stock = create_offer_with_thing_product(venue, is_active=False)
            self.inactive_expired_event_offer = create_offer_with_event_product(venue, is_active=False)
            self.active_thing_offer_with_one_stock_with_remaining_quantity = create_offer_with_thing_product(
                venue, is_active=True
            )
            self.active_thing_offer_with_all_stocks_without_quantity = create_offer_with_thing_product(
                venue, is_active=True
            )
            self.active_event_offer_with_stock_in_the_future_without_quantity = create_offer_with_event_product(
                venue=venue
            )
            self.active_event_offer_with_one_stock_in_the_future_with_remaining_quantity = (
                create_offer_with_event_product(venue=venue)
            )
            self.sold_old_thing_offer_with_all_stocks_empty = create_offer_with_thing_product(venue)
            self.sold_out_event_offer_with_all_stocks_in_the_future_with_zero_remaining_quantity = (
                create_offer_with_event_product(venue=venue)
            )
            self.sold_out_thing_offer_without_stock = create_offer_with_thing_product(venue)
            self.sold_out_event_offer_without_stock = create_offer_with_event_product(venue=venue)
            self.expired_event_offer_with_stock_in_the_past_without_quantity = create_offer_with_event_product(
                venue=venue
            )
            self.expired_event_offer_with_all_stocks_in_the_past_with_remaining_quantity = (
                create_offer_with_event_product(venue=venue)
            )
            self.expired_event_offer_with_all_stocks_in_the_past_with_zero_remaining_quantity = (
                create_offer_with_event_product(venue=venue)
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
                user_id=self.pro.id, user_is_admin=self.pro.isAdmin, offers_per_page=20, page=1, status="active"
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
            assert Identifier(self.sold_out_event_offer_without_stock.id) not in offer_ids
            assert Identifier(self.expired_event_offer_with_stock_in_the_past_without_quantity.id) not in offer_ids
            assert (
                Identifier(self.expired_event_offer_with_all_stocks_in_the_past_with_remaining_quantity.id)
                not in offer_ids
            )
            assert (
                Identifier(self.expired_event_offer_with_all_stocks_in_the_past_with_zero_remaining_quantity.id)
                not in offer_ids
            )

        @pytest.mark.usefixtures("db_session")
        def should_return_only_inactive_offers_when_requesting_inactive_status(self, app):
            # given
            self.save_data_set()

            # when
            paginated_offers = get_paginated_offers_for_offerer_venue_and_keywords(
                user_id=self.pro.id, user_is_admin=self.pro.isAdmin, offers_per_page=20, page=1, status="inactive"
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
            assert Identifier(self.sold_out_event_offer_without_stock.id) not in offer_ids
            assert Identifier(self.expired_event_offer_with_stock_in_the_past_without_quantity.id) not in offer_ids
            assert (
                Identifier(self.expired_event_offer_with_all_stocks_in_the_past_with_remaining_quantity.id)
                not in offer_ids
            )
            assert (
                Identifier(self.expired_event_offer_with_all_stocks_in_the_past_with_zero_remaining_quantity.id)
                not in offer_ids
            )

        @pytest.mark.usefixtures("db_session")
        def should_return_only_sold_out_offers_when_requesting_sold_out_status(self, app):
            # given
            self.save_data_set()

            # when
            paginated_offers = get_paginated_offers_for_offerer_venue_and_keywords(
                user_id=self.pro.id, user_is_admin=self.pro.isAdmin, offers_per_page=20, page=1, status="soldOut"
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
            assert Identifier(self.sold_out_event_offer_without_stock.id) in offer_ids
            assert Identifier(self.expired_event_offer_with_stock_in_the_past_without_quantity.id) not in offer_ids
            assert (
                Identifier(self.expired_event_offer_with_all_stocks_in_the_past_with_remaining_quantity.id)
                not in offer_ids
            )
            assert (
                Identifier(self.expired_event_offer_with_all_stocks_in_the_past_with_zero_remaining_quantity.id)
                not in offer_ids
            )

        @pytest.mark.usefixtures("db_session")
        def should_return_offers_with_no_stocks_when_requesting_sold_out_status(self, app):
            # given
            self.save_data_set()

            # when
            paginated_offers = get_paginated_offers_for_offerer_venue_and_keywords(
                user_id=self.pro.id, user_is_admin=self.pro.isAdmin, offers_per_page=20, page=1, status="soldOut"
            )

            # then
            offer_ids = [offer.identifier for offer in paginated_offers.offers]
            assert Identifier(self.sold_out_thing_offer_without_stock.id) in offer_ids
            assert Identifier(self.active_thing_offer_with_all_stocks_without_quantity.id) not in offer_ids

        @pytest.mark.usefixtures("db_session")
        def should_return_offers_with_no_remaining_quantity_and_no_bookings_when_requesting_sold_out_status(self, app):
            # given
            self.save_data_set()

            # when
            paginated_offers = get_paginated_offers_for_offerer_venue_and_keywords(
                user_id=self.pro.id, user_is_admin=self.pro.isAdmin, offers_per_page=20, page=1, status="soldOut"
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
                user_id=self.pro.id, user_is_admin=self.pro.isAdmin, offers_per_page=20, page=1, status="soldOut"
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
                user_id=self.pro.id, user_is_admin=self.pro.isAdmin, offers_per_page=20, page=1, status="soldOut"
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
                user_id=self.pro.id, user_is_admin=self.pro.isAdmin, offers_per_page=20, page=1, status="expired"
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
            assert Identifier(self.sold_out_event_offer_without_stock.id) not in offer_ids
            assert Identifier(self.expired_event_offer_with_stock_in_the_past_without_quantity.id) in offer_ids
            assert (
                Identifier(self.expired_event_offer_with_all_stocks_in_the_past_with_remaining_quantity.id) in offer_ids
            )
            assert (
                Identifier(self.expired_event_offer_with_all_stocks_in_the_past_with_zero_remaining_quantity.id)
                in offer_ids
            )

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
                offers_per_page=20,
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
            assert Identifier(self.sold_out_event_offer_without_stock.id) not in offer_ids
            assert Identifier(sold_out_offer_on_other_venue.id) in offer_ids
