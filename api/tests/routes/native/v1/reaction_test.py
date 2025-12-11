import datetime
from operator import itemgetter

import pytest

from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.categories import subcategories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.reactions.models import ReactionTypeEnum
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import factories as users_factories
from pcapi.utils import date as date_utils
from pcapi.utils.date import format_into_utc_date


pytestmark = pytest.mark.usefixtures("db_session")


class PostReactionTest:
    num_queries_base = 1  # select user
    num_queries_base += 1  # select booking, stock, offer

    num_queries_success = num_queries_base + 1  # select reaction
    num_queries_success += 1  # Insert reaction
    num_queries_success_with_product = num_queries_success + 1  # update product likes count

    num_queries_failure = num_queries_base + 2  # rollback x2

    def test_should_be_logged_in_to_post_reaction(self, client):
        with assert_num_queries(0):
            response = client.post("/native/v1/reaction", json={})
            assert response.status_code == 400

    def test_offer_not_found(self, client):
        user = users_factories.BeneficiaryFactory()
        client.with_token(user)

        with assert_num_queries(self.num_queries_failure):
            response = client.post("/native/v1/reaction", json={"offerId": 1, "reactionType": "LIKE"})
            assert response.status_code == 400

    def test_post_new_like_reaction(self, client):
        user = users_factories.BeneficiaryFactory()
        offer = offers_factories.ThingOfferFactory(subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE_VINYLE.id)
        bookings_factories.UsedBookingFactory(
            user=user, stock__offer=offer, dateUsed=date_utils.get_naive_utc_now() - datetime.timedelta(hours=25)
        )
        client.with_token(user)

        offer_id = offer.id
        with assert_num_queries(self.num_queries_success):
            response = client.post("/native/v1/reaction", json={"offerId": offer_id, "reactionType": "LIKE"})
            assert response.status_code == 204

        reaction = user.reactions[0]

        assert reaction.reactionType == ReactionTypeEnum.LIKE

    def test_post_new_dislike_reaction(self, client):
        user = users_factories.BeneficiaryFactory()
        offer = offers_factories.ThingOfferFactory(subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE_VINYLE.id)
        bookings_factories.UsedBookingFactory(
            user=user, stock__offer=offer, dateUsed=date_utils.get_naive_utc_now() - datetime.timedelta(hours=25)
        )
        client.with_token(user)

        offer_id = offer.id
        with assert_num_queries(self.num_queries_success):
            response = client.post("/native/v1/reaction", json={"offerId": offer_id, "reactionType": "DISLIKE"})
            assert response.status_code == 204

    def test_edit_reaction(self, client):
        user = users_factories.BeneficiaryFactory()
        offer = offers_factories.ThingOfferFactory(subcategoryId=subcategories.LIVRE_PAPIER.id)
        bookings_factories.UsedBookingFactory(
            user=user, stock__offer=offer, dateUsed=date_utils.get_naive_utc_now() - datetime.timedelta(hours=25)
        )
        client.with_token(user)

        offer_id = offer.id
        with assert_num_queries(self.num_queries_success):
            response = client.post("/native/v1/reaction", json={"offerId": offer_id, "reactionType": "LIKE"})
            assert response.status_code == 204
        reaction = user.reactions[0]

        offer_id = offer.id

        assert reaction.reactionType == ReactionTypeEnum.LIKE

        response = client.post("/native/v1/reaction", json={"offerId": offer_id, "reactionType": "DISLIKE"})
        reaction = user.reactions[0]

        assert response.status_code == 204
        assert reaction.reactionType == ReactionTypeEnum.DISLIKE

    def test_post_reaction_to_product(self, client):
        user = users_factories.BeneficiaryFactory()
        product = offers_factories.ProductFactory()
        offer = offers_factories.OfferFactory(product=product)
        bookings_factories.UsedBookingFactory(
            user=user, stock__offer=offer, dateUsed=date_utils.get_naive_utc_now() - datetime.timedelta(hours=25)
        )
        client.with_token(user)

        offer_id = offer.id
        with assert_num_queries(self.num_queries_success_with_product):
            response = client.post("/native/v1/reaction", json={"offerId": offer_id, "reactionType": "LIKE"})
            assert response.status_code == 204

        assert product.likesCount == 1

        response = client.post("/native/v1/reaction", json={"offerId": offer_id, "reactionType": "DISLIKE"})
        reaction = user.reactions[0]

        assert reaction.reactionType == ReactionTypeEnum.DISLIKE
        assert reaction.product == product
        assert reaction.product.likesCount == 0

    def test_post_bulk_reaction(self, client):
        user = users_factories.BeneficiaryFactory()
        offer = offers_factories.ThingOfferFactory(subcategoryId=subcategories.LIVRE_PAPIER.id)
        other_offer = offers_factories.ThingOfferFactory(subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id)
        bookings_factories.UsedBookingFactory(
            user=user, stock__offer=offer, dateUsed=date_utils.get_naive_utc_now() - datetime.timedelta(hours=25)
        )
        bookings_factories.UsedBookingFactory(
            user=user, stock__offer=other_offer, dateUsed=date_utils.get_naive_utc_now() - datetime.timedelta(days=25)
        )
        client.with_token(user)

        offer_id = offer.id
        other_offer_id = other_offer.id

        with assert_num_queries(self.num_queries_success):
            response = client.post(
                "/native/v1/reaction",
                json={
                    "reactions": [
                        {"offerId": offer_id, "reactionType": "LIKE"},
                        {"offerId": other_offer_id, "reactionType": "LIKE"},
                    ]
                },
            )
            assert response.status_code == 204

        reaction = user.reactions[0]
        assert reaction.reactionType == ReactionTypeEnum.LIKE

        reaction = user.reactions[1]
        assert reaction.reactionType == ReactionTypeEnum.LIKE

    def test_user_did_not_booked(self, client):
        user = users_factories.BeneficiaryFactory()
        offer = offers_factories.ThingOfferFactory(subcategoryId=subcategories.LIVRE_PAPIER.id)
        bookings_factories.UsedBookingFactory(
            # booking from someone else
            stock__offer=offer,
            dateUsed=date_utils.get_naive_utc_now() - datetime.timedelta(hours=25),
        )
        client.with_token(user)

        offer_id = offer.id
        with assert_num_queries(self.num_queries_failure):
            response = client.post("/native/v1/reaction", json={"offerId": offer_id, "reactionType": "LIKE"})
            assert response.status_code == 400
            assert response.json["code"] == "OFFER_NOT_BOOKED"

        assert not user.reactions

    def test_user_canceled_booking(self, client):
        user = users_factories.BeneficiaryFactory()
        offer = offers_factories.ThingOfferFactory(subcategoryId=subcategories.LIVRE_PAPIER.id)
        bookings_factories.CancelledBookingFactory(user=user, stock__offer=offer)
        client.with_token(user)

        offer_id = offer.id
        with assert_num_queries(self.num_queries_failure):
            response = client.post("/native/v1/reaction", json={"offerId": offer_id, "reactionType": "LIKE"})
            assert response.status_code == 400
            assert response.json["code"] == "OFFER_NOT_BOOKED"

        assert not user.reactions

    def test_booking_not_used(self, client):
        user = users_factories.BeneficiaryFactory()
        offer = offers_factories.ThingOfferFactory(subcategoryId=subcategories.LIVRE_PAPIER.id)
        bookings_factories.BookingFactory(user=user, stock__offer=offer)
        client.with_token(user)

        offer_id = offer.id
        with assert_num_queries(self.num_queries_failure):
            response = client.post("/native/v1/reaction", json={"offerId": offer_id, "reactionType": "LIKE"})
            assert response.status_code == 400
            assert response.json["code"] == "CAN_NOT_REACT"

        assert not user.reactions

    def test_booking_not_eligible(self, client):
        user = users_factories.BeneficiaryFactory()
        offer = offers_factories.OfferFactory(subcategoryId=subcategories.ATELIER_PRATIQUE_ART.id)
        bookings_factories.BookingFactory(user=user, stock__offer=offer)
        client.with_token(user)

        offer_id = offer.id
        with assert_num_queries(self.num_queries_failure):
            response = client.post("/native/v1/reaction", json={"offerId": offer_id, "reactionType": "LIKE"})
            assert response.status_code == 400
            assert response.json["code"] == "CAN_NOT_REACT"

        assert not user.reactions


class GetAvailableReactionTest:
    def test_should_be_logged_in_to_get_available_reactions(self, client):
        with assert_num_queries(0):
            response = client.get("/native/v1/reaction/available")
        assert response.status_code == 401

    def test_get_available_reactions_empty_if_no_booking(self, client):
        user = users_factories.BeneficiaryFactory()
        client.with_token(user)

        with assert_num_queries(2):
            # SELECT user, booking
            response = client.get("/native/v1/reaction/available")

        assert response.status_code == 200
        assert response.json == {"numberOfReactableBookings": 0, "bookings": []}

    def test_handles_multiple_eligible_offers(self, client):
        """Rules for eligible bookings:
        - User has used the booking
        - Offer is in a category that allows reactions
        - Booking has been used in the past (depending on the subcategory)
        - No reaction has been posted for this booking
        """
        user_1 = users_factories.BeneficiaryFactory()
        user_2 = users_factories.BeneficiaryFactory()

        offer_1 = offers_factories.OfferFactory(subcategoryId=subcategories.SEANCE_CINE.id)
        offer_2 = offers_factories.OfferFactory(subcategoryId=subcategories.LIVRE_PAPIER.id)
        offer_3 = offers_factories.OfferFactory(subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id)
        offer_4 = offers_factories.OfferFactory(subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE_VINYLE.id)
        offer_5 = offers_factories.OfferFactory(subcategoryId=subcategories.ABO_PRESSE_EN_LIGNE.id)

        a_little_more_than_24h_ago = date_utils.get_naive_utc_now() - datetime.timedelta(hours=25)
        a_little_more_than_31d_ago = date_utils.get_naive_utc_now() - datetime.timedelta(days=32)
        a_lot_more_than_31d_ago = date_utils.get_naive_utc_now() - datetime.timedelta(days=60)

        # Booking eligible to reactions from user
        booking_offer_1 = bookings_factories.UsedBookingFactory(
            user=user_1, stock__offer=offer_1, dateUsed=a_little_more_than_24h_ago
        )
        booking_offer_2 = bookings_factories.UsedBookingFactory(
            user=user_1, stock__offer=offer_2, dateUsed=a_little_more_than_31d_ago
        )
        booking_offer_3 = bookings_factories.UsedBookingFactory(
            user=user_1, stock__offer=offer_3, dateUsed=a_lot_more_than_31d_ago
        )
        booking_offer_4 = bookings_factories.UsedBookingFactory(
            user=user_1, stock__offer=offer_4, dateUsed=a_little_more_than_31d_ago
        )
        # Bookings not eligible to reactions: other users / unauthorized subcategories
        bookings_factories.BookingFactory(user=user_1, stock__offer=offer_2)
        bookings_factories.UsedBookingFactory(user=user_2, stock__offer=offer_2, dateUsed=a_lot_more_than_31d_ago)
        bookings_factories.UsedBookingFactory(user=user_1, stock__offer=offer_5, dateUsed=a_lot_more_than_31d_ago)

        med_1 = offers_factories.MediationFactory(offer=offer_1)
        client.with_token(user_1)

        with assert_num_queries(2):
            # SELECT user, booking
            response = client.get("/native/v1/reaction/available")

        assert response.status_code == 200
        response_bookings = response.json.get("bookings")
        response_number_of_reactable_bookings = response.json.get("numberOfReactableBookings")
        expected_bookings = [
            {
                "image": med_1.thumbUrl,
                "dateUsed": format_into_utc_date(booking_offer_1.dateUsed),
                "name": offer_1.name,
                "offerId": offer_1.id,
                "subcategoryId": offer_1.subcategoryId,
            },
            {
                "image": None,
                "dateUsed": format_into_utc_date(booking_offer_2.dateUsed),
                "name": offer_2.name,
                "offerId": offer_2.id,
                "subcategoryId": offer_2.subcategoryId,
            },
            {
                "image": None,
                "dateUsed": format_into_utc_date(booking_offer_4.dateUsed),
                "name": offer_4.name,
                "offerId": offer_4.id,
                "subcategoryId": offer_4.subcategoryId,
            },
            {
                "image": None,
                "dateUsed": format_into_utc_date(booking_offer_3.dateUsed),
                "name": offer_3.name,
                "offerId": offer_3.id,
                "subcategoryId": offer_3.subcategoryId,
            },
        ]

        sorting_key = itemgetter("name")
        expected_bookings.sort(key=sorting_key)
        response_bookings.sort(key=sorting_key)
        assert response_bookings == expected_bookings
        assert response_number_of_reactable_bookings == 4
