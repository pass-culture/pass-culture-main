import datetime

import pytest

from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings import models as bookings_models
import pcapi.core.categories.subcategories_v2 as subcategories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.reactions.factories import ReactionFactory
from pcapi.core.reactions.models import ReactionTypeEnum
from pcapi.core.testing import assert_num_queries
from pcapi.core.testing import override_settings
from pcapi.core.users import factories as users_factories
from pcapi.utils.date import format_into_utc_date


pytestmark = pytest.mark.usefixtures("db_session")


class PostReactionTest:
    def test_should_be_logged_in_to_post_reaction(self, client):
        with assert_num_queries(0):
            response = client.post("/native/v1/reaction", json={})
        assert response.status_code == 400

    def test_post_new_like_reaction(self, client):
        user = users_factories.BeneficiaryFactory()
        offer = offers_factories.OfferFactory()
        client.with_token(user.email)

        with assert_num_queries(4):
            # SELECT offer, user, reaction
            # INSERT reaction
            response = client.post("/native/v1/reaction", json={"offerId": offer.id, "reactionType": "LIKE"})
        reaction = user.reactions[0]

        assert response.status_code == 204
        assert reaction.reactionType == ReactionTypeEnum.LIKE

    def test_post_new_dislike_reaction(self, client):
        user = users_factories.BeneficiaryFactory()
        offer = offers_factories.OfferFactory()
        client.with_token(user.email)

        with assert_num_queries(4):
            # SELECT offer, user, reaction
            # INSERT reaction
            response = client.post("/native/v1/reaction", json={"offerId": offer.id, "reactionType": "DISLIKE"})
        reaction = user.reactions[0]

        assert response.status_code == 204
        assert reaction.reactionType == ReactionTypeEnum.DISLIKE

    def test_edit_reaction(self, client):
        user = users_factories.BeneficiaryFactory()
        offer = offers_factories.OfferFactory()
        client.with_token(user.email)

        with assert_num_queries(4):
            # SELECT offer, user, reaction
            # INSERT reaction
            response = client.post("/native/v1/reaction", json={"offerId": offer.id, "reactionType": "LIKE"})
        reaction = user.reactions[0]

        assert response.status_code == 204
        assert reaction.reactionType == ReactionTypeEnum.LIKE

        response = client.post("/native/v1/reaction", json={"offerId": offer.id, "reactionType": "DISLIKE"})
        reaction = user.reactions[0]

        assert response.status_code == 204
        assert reaction.reactionType == ReactionTypeEnum.DISLIKE

    def test_post_reaction_to_product(self, client):
        user = users_factories.BeneficiaryFactory()
        product = offers_factories.ProductFactory()
        offer = offers_factories.OfferFactory(product=product)
        client.with_token(user.email)

        with assert_num_queries(4):
            # SELECT offer, user, reaction
            # INSERT reaction
            response = client.post("/native/v1/reaction", json={"offerId": offer.id, "reactionType": "LIKE"})
        reaction = user.reactions[0]

        assert response.status_code == 204
        assert reaction.reactionType == ReactionTypeEnum.LIKE
        assert reaction.product == product


class GetAvailableReactionTest:
    def test_should_be_logged_in_to_get_available_reactions(self, client):
        with assert_num_queries(0):
            response = client.get("/native/v1/reaction/available")
        assert response.status_code == 401

    def test_get_available_reactions_empty_if_no_booking(self, client):
        user = users_factories.BeneficiaryFactory()
        client.with_token(user.email)

        with assert_num_queries(2):
            # SELECT user, booking
            response = client.get("/native/v1/reaction/available")

        assert response.status_code == 200
        assert response.json == {"bookings": []}

    def test_get_available_reactions_returns_eligible_booking_used(self, client):
        """Rules for eligible bookings:
        - User has used the booking
        - Offer is in a category that allows reactions (SEANCE_CINE only for now - 2024-07-12)
        - Booking has been used at least 24 hours ago
        - No reaction has been posted for this booking
        """
        user = users_factories.BeneficiaryFactory()

        cine_offer_1 = offers_factories.OfferFactory(subcategoryId=subcategories.SEANCE_CINE.id)
        cine_offer_2 = offers_factories.OfferFactory(subcategoryId=subcategories.SEANCE_CINE.id)
        cine_offer_3 = offers_factories.OfferFactory(subcategoryId=subcategories.SEANCE_CINE.id)
        cine_offer_4 = offers_factories.OfferFactory(subcategoryId=subcategories.SEANCE_CINE.id)
        not_a_cine_offer = offers_factories.OfferFactory(subcategoryId=subcategories.LIVRE_PAPIER.id)

        # Not eligible: offer subcategory is not eligible for reactions (yet)
        bookings_factories.UsedBookingFactory(user=user, stock__offer=not_a_cine_offer)
        # Not eligible: booking has not been used
        bookings_factories.BookingFactory(
            user=user, status=bookings_models.BookingStatus.CONFIRMED, stock__offer=cine_offer_1
        )
        # Not eligible: booking has been used less than 24 hours ago
        less_than_24h_ago = datetime.datetime.utcnow() - datetime.timedelta(hours=23)
        bookings_factories.UsedBookingFactory(user=user, stock__offer=cine_offer_2, dateUsed=less_than_24h_ago)
        # Not eligible: reaction has already been posted
        more_than_24h_ago = datetime.datetime.utcnow() - datetime.timedelta(hours=25)
        bookings_factories.UsedBookingFactory(user=user, stock__offer=cine_offer_3, dateUsed=more_than_24h_ago)
        ReactionFactory(user=user, offer=cine_offer_3)

        # Eligible
        eligible_booking = bookings_factories.UsedBookingFactory(
            user=user, stock__offer=cine_offer_4, dateUsed=more_than_24h_ago
        )

        client.with_token(user.email)
        with assert_num_queries(2):
            # SELECT user, booking
            response = client.get("/native/v1/reaction/available")

        assert response.status_code == 200
        assert response.json == {
            "bookings": [
                {
                    "image": eligible_booking.stock.offer.image,
                    "dateUsed": format_into_utc_date(eligible_booking.dateUsed),
                    "name": eligible_booking.stock.offer.name,
                }
            ]
        }

    def test_get_available_reactions_takes_product_reaction_into_account(self, client):
        user = users_factories.BeneficiaryFactory()

        product = offers_factories.ProductFactory()
        product_offer_1 = offers_factories.OfferFactory(product=product, subcategoryId=subcategories.SEANCE_CINE.id)
        product_offer_2 = offers_factories.OfferFactory(product=product, subcategoryId=subcategories.SEANCE_CINE.id)

        # User booked and reacted to the product_offer_1
        more_than_24h_ago = datetime.datetime.utcnow() - datetime.timedelta(hours=25)
        bookings_factories.UsedBookingFactory(user=user, stock__offer=product_offer_1, dateUsed=more_than_24h_ago)
        ReactionFactory(user=user, product=product)

        # User booked the product_offer_2, linked to the same product
        bookings_factories.UsedBookingFactory(user=user, stock__offer=product_offer_2, dateUsed=more_than_24h_ago)

        client.with_token(user.email)

        with assert_num_queries(2):
            # SELECT user, booking
            response = client.get("/native/v1/reaction/available")

        assert response.status_code == 200
        assert response.json == {"bookings": []}

    def test_handles_multiple_eligible_offers(self, client):
        user = users_factories.BeneficiaryFactory()

        cine_offer_1 = offers_factories.OfferFactory(subcategoryId=subcategories.SEANCE_CINE.id)
        cine_offer_2 = offers_factories.OfferFactory(subcategoryId=subcategories.SEANCE_CINE.id)

        a_little_more_than_24h_ago = datetime.datetime.utcnow() - datetime.timedelta(hours=25)
        a_lot_more_than_24h_ago = datetime.datetime.utcnow() - datetime.timedelta(hours=48)
        booking_yesterday = bookings_factories.UsedBookingFactory(
            user=user, stock__offer=cine_offer_1, dateUsed=a_little_more_than_24h_ago
        )
        booking_longer_ago = bookings_factories.UsedBookingFactory(
            user=user, stock__offer=cine_offer_2, dateUsed=a_lot_more_than_24h_ago
        )

        client.with_token(user.email)

        with assert_num_queries(2):
            # SELECT user, booking
            response = client.get("/native/v1/reaction/available")

        assert response.status_code == 200
        assert response.json == {
            "bookings": [
                {
                    "image": booking_yesterday.stock.offer.image,
                    "dateUsed": format_into_utc_date(booking_yesterday.dateUsed),
                    "name": booking_yesterday.stock.offer.name,
                },
                {
                    "image": booking_longer_ago.stock.offer.image,
                    "dateUsed": format_into_utc_date(booking_longer_ago.dateUsed),
                    "name": booking_longer_ago.stock.offer.name,
                },
            ]
        }

    def test_available_bookings_displayed_according_to_an_env_var(self, client):
        # Instead of 24h, we want to display bookings that have been used 30s ago, for testing environments
        user = users_factories.BeneficiaryFactory()

        cine_offer = offers_factories.OfferFactory(subcategoryId=subcategories.SEANCE_CINE.id)
        around_30s_ago = datetime.datetime.utcnow() - datetime.timedelta(seconds=32)
        booking = bookings_factories.UsedBookingFactory(user=user, stock__offer=cine_offer, dateUsed=around_30s_ago)

        client.with_token(user.email)
        with override_settings(SUGGEST_REACTION_COOLDOWN_IN_SECONDS=24 * 3600):
            with assert_num_queries(2):
                # SELECT user, booking
                response = client.get("/native/v1/reaction/available")

            assert response.status_code == 200
            assert response.json == {"bookings": []}

        with override_settings(SUGGEST_REACTION_COOLDOWN_IN_SECONDS=30):
            with assert_num_queries(2):
                # SELECT user, booking
                response = client.get("/native/v1/reaction/available")

            assert response.status_code == 200
            assert response.json == {
                "bookings": [
                    {
                        "image": booking.stock.offer.image,
                        "dateUsed": format_into_utc_date(booking.dateUsed),
                        "name": booking.stock.offer.name,
                    }
                ]
            }
