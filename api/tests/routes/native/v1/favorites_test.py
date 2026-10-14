import concurrent.futures
import time
from datetime import UTC
from datetime import datetime
from datetime import timedelta
from decimal import Decimal
from unittest import mock

import pytest
import sqlalchemy as sa

import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.artist import factories as artist_factories
from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.categories import subcategories
from pcapi.core.discoveries import models as discoveries_models
from pcapi.core.external.batch import models as batch_models
from pcapi.core.external.batch import testing as push_testing
from pcapi.core.favorites import factories as favorite_factories
from pcapi.core.favorites.models import FavoriteOffer
from pcapi.core.favorites.repository import get_favorites_for
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import factories as users_factories
from pcapi.core.users import testing as users_testing
from pcapi.models import db
from pcapi.models.validation_status_mixin import ValidationStatus
from pcapi.utils import date as date_utils
from pcapi.utils.human_ids import humanize


pytestmark = pytest.mark.usefixtures("db_session")

FAVORITES_URL = "/native/v1/me/favorites"


class CulturalFavoritesTest:
    @pytest.mark.parametrize("target", ["offer", "work", "artist"])
    def test_database_rejects_duplicate_target(self, target):
        user = users_factories.UserFactory()
        targets = {
            "offer": offers_factories.OfferFactory(),
            "work": discoveries_models.Work(title="Work", media_type=discoveries_models.WorkMediaType.BOOK),
            "artist": artist_factories.ArtistFactory(),
        }
        db.session.add(FavoriteOffer(user=user, **{target: targets[target]}))
        db.session.flush()

        with pytest.raises(sa.exc.IntegrityError), db.session.begin_nested():
            db.session.add(FavoriteOffer(user=user, **{target: targets[target]}))
            db.session.flush()

    @pytest.mark.parametrize("case", ["none", "multiple", "origin_without_work"])
    def test_database_rejects_invalid_target(self, case):
        user = users_factories.UserFactory()
        artist = artist_factories.ArtistFactory()
        offer = offers_factories.OfferFactory()
        favorite = FavoriteOffer(user=user)
        if case == "multiple":
            favorite.offer = offer
            favorite.artist = artist
        elif case == "origin_without_work":
            favorite.artist = artist
            favorite.offer_origin = offer

        with pytest.raises(sa.exc.IntegrityError), db.session.begin_nested():
            db.session.add(favorite)
            db.session.flush()

    @pytest.mark.parametrize("target", ["work", "artist", "offer_product", "offer_direct"])
    def test_create_and_repeat(self, client, target):
        user = users_factories.UserFactory()
        offer = None
        if target == "artist":
            artist = artist_factories.ArtistFactory()
            payload = {"artistId": artist.id}
        else:
            work = discoveries_models.Work(title="A work", media_type=discoveries_models.WorkMediaType.BOOK)
            db.session.add(work)
            db.session.flush()
            if target == "work":
                payload = {"workId": work.id}
            else:
                if target == "offer_product":
                    product = offers_factories.ProductFactory(work=work, subcategoryId=subcategories.LIVRE_PAPIER.id)
                    offer = offers_factories.OfferFactory(product=product)
                else:
                    offer = offers_factories.OfferFactory()
                    work.offer = offer
                offers_factories.StockFactory(offer=offer, price=12)
                payload = {"offerId": offer.id}
        client.with_token(user)

        response = client.post(FAVORITES_URL, json=payload)
        repeated = client.post(FAVORITES_URL, json=payload)

        assert response.status_code == repeated.status_code == 200
        assert repeated.json == response.json
        assert response.json["createdAt"]
        if target in ("work", "artist"):
            assert not any(
                event.get("event_name") == batch_models.BatchEvent.HAS_ADDED_OFFER_TO_FAVORITES.value
                for event in push_testing.requests
            )
        assert db.session.query(FavoriteOffer).filter_by(userId=user.id).count() == 1
        favorite = db.session.query(FavoriteOffer).filter_by(userId=user.id).one()
        if target == "artist":
            assert response.json["artist"]["id"] == artist.id
            assert response.json["work"] is None
            assert response.json["offer"] is None
        else:
            assert response.json["work"]["id"] == work.id
            assert response.json["artist"] is None
            assert favorite.offerId is None
            if offer is not None:
                assert response.json["offer"]["id"] == offer.id
                assert response.json["offer"]["price"] == 1200
                assert favorite.offer_origin_id == offer.id
            else:
                assert response.json["offer"] is None
        listing = client.get(FAVORITES_URL)
        assert listing.status_code == 200
        assert listing.json["nbFavorites"] == 1
        assert listing.json["favorites"] == [response.json]

    @pytest.mark.parametrize("work_first", [False, True])
    def test_offers_for_same_work_share_one_favorite(self, client, work_first):
        work = discoveries_models.Work(title="One work", media_type=discoveries_models.WorkMediaType.BOOK)
        product = offers_factories.ProductFactory(work=work)
        first_offer = offers_factories.OfferFactory(product=product)
        second_offer = offers_factories.OfferFactory(product=product)
        user = users_factories.UserFactory()
        client.with_token(user)
        first_payload = {"workId": work.id} if work_first else {"offerId": first_offer.id}
        first = client.post(FAVORITES_URL, json=first_payload)
        assert first.status_code == 200
        from_offer = client.post(FAVORITES_URL, json={"offerId": first_offer.id})
        assert from_offer.status_code == 200
        repeated = client.post(FAVORITES_URL, json={"offerId": second_offer.id})

        assert repeated.status_code == 200
        assert repeated.json["id"] == first.json["id"]
        assert repeated.json["createdAt"] == first.json["createdAt"]
        assert repeated.json["offer"]["id"] == first_offer.id
        assert db.session.query(FavoriteOffer).filter_by(userId=user.id).count() == 1

    @pytest.mark.parametrize(
        "payload",
        [
            {},
            {"offerId": None},
            {"workId": 1, "offerId": 1},
            {"artistId": "artist", "workId": 1},
            {"artistId": "artist", "offerId": 1},
            {"workId": 0},
            {"artistId": ""},
        ],
    )
    def test_invalid_target_returns_400(self, client, payload):
        client.with_token(users_factories.UserFactory())

        assert client.post(FAVORITES_URL, json=payload).status_code == 400
        assert db.session.query(FavoriteOffer).count() == 0

    @pytest.mark.parametrize("payload", [{"workId": 999999}, {"artistId": "missing"}])
    def test_unknown_target_returns_404(self, client, payload):
        client.with_token(users_factories.UserFactory())

        assert client.post(FAVORITES_URL, json=payload).status_code == 404

    @pytest.mark.settings(MAX_FAVORITES=1)
    def test_global_limit_allows_duplicate_but_not_new_target(self, client):
        user = users_factories.UserFactory()
        artist = artist_factories.ArtistFactory()
        work = discoveries_models.Work(title="Work", media_type=discoveries_models.WorkMediaType.BOOK)
        db.session.add(FavoriteOffer(user=user, work=work))
        db.session.flush()
        client.with_token(user)

        assert client.post(FAVORITES_URL, json={"workId": work.id}).status_code == 200
        response = client.post(FAVORITES_URL, json={"artistId": artist.id})

        assert response.status_code == 400
        assert response.json == {"code": "MAX_FAVORITES_REACHED"}
        assert db.session.query(FavoriteOffer).filter_by(userId=user.id).count() == 1

    @pytest.mark.settings(MAX_FAVORITES=0)
    def test_no_limit_and_user_isolation(self, client):
        artist = artist_factories.ArtistFactory()
        first_user = users_factories.UserFactory()
        second_user = users_factories.UserFactory()
        first = client.with_token(first_user).post(FAVORITES_URL, json={"artistId": artist.id})
        second = client.with_token(second_user).post(FAVORITES_URL, json={"artistId": artist.id})

        assert first.status_code == second.status_code == 200
        assert first.json["id"] != second.json["id"]
        assert client.delete(f"{FAVORITES_URL}/{first.json['id']}").status_code == 404
        assert client.delete(f"{FAVORITES_URL}/{second.json['id']}").status_code == 204

    def test_mixed_list_is_sorted_by_creation_date(self, client):
        user = users_factories.UserFactory()
        offer_favorite = favorite_factories.FavoriteOfferFactory(user=user, dateCreated=datetime(2026, 1, 3))
        work = discoveries_models.Work(title="Work", media_type=discoveries_models.WorkMediaType.BOOK)
        work_favorite = FavoriteOffer(user=user, work=work, dateCreated=datetime(2026, 1, 1))
        artist_favorite = FavoriteOffer(
            user=user, artist=artist_factories.ArtistFactory(), dateCreated=datetime(2026, 1, 2)
        )
        db.session.add_all([work_favorite, artist_favorite])
        db.session.flush()

        response = client.with_token(user).get(FAVORITES_URL)

        assert response.status_code == 200
        assert response.json["nbFavorites"] == 3
        assert response.json["page"] == 1
        assert [favorite["id"] for favorite in response.json["favorites"]] == [
            offer_favorite.id,
            artist_favorite.id,
            work_favorite.id,
        ]

    def test_historical_offer_favorite_is_not_converted(self, client):
        user = users_factories.UserFactory()
        work = discoveries_models.Work(title="Work", media_type=discoveries_models.WorkMediaType.BOOK)
        offer = offers_factories.OfferFactory(product=offers_factories.ProductFactory(work=work))
        historical = favorite_factories.FavoriteOfferFactory(user=user, offer=offer)

        response = client.with_token(user).post(FAVORITES_URL, json={"offerId": offer.id})

        assert response.status_code == 200
        assert response.json["id"] == historical.id
        assert response.json["offer"]["id"] == offer.id
        assert response.json["work"] is None
        assert response.json["artist"] is None

    @pytest.mark.parametrize("action", ["unpublish", "delete"])
    def test_work_remains_when_origin_offer_is_unavailable(self, client, action):
        user = users_factories.UserFactory()
        work = discoveries_models.Work(title="Work", media_type=discoveries_models.WorkMediaType.BOOK)
        offer = offers_factories.OfferFactory()
        favorite = FavoriteOffer(user=user, work=work, offer_origin=offer)
        db.session.add(favorite)
        db.session.flush()
        favorite_id, work_id = favorite.id, work.id
        if action == "delete":
            db.session.execute(sa.delete(offers_models.Offer).where(offers_models.Offer.id == offer.id))
        else:
            offer.publicationDatetime = None
        db.session.flush()
        db.session.expire_all()

        response = client.with_token(user).get(FAVORITES_URL)

        assert response.status_code == 200
        assert response.json["nbFavorites"] == 1
        assert response.json["favorites"][0]["id"] == favorite_id
        assert response.json["favorites"][0]["work"]["id"] == work_id
        assert response.json["favorites"][0]["offer"] is None


class GetTest:
    class Returns200Test:
        expected_num_queries = 1  # user
        expected_num_queries += 1  # favorites

        def when_user_is_logged_in_but_has_no_favorites(self, client):
            # Given
            user = users_factories.UserFactory()

            # When
            client = client.with_token(user)
            with assert_num_queries(self.expected_num_queries):
                response = client.get(FAVORITES_URL)
                assert response.status_code == 200

            # Then
            assert response.json == {"page": 1, "nbFavorites": 0, "favorites": []}

        def when_user_is_logged_in_and_has_favorite_offers(self, client):
            # Given
            # 13h time delta should make this runnable everywhere on earth: it
            # should always be > now()
            start = datetime.now(UTC).replace(tzinfo=None) + timedelta(hours=13)
            day_before_start = start - timedelta(days=1)
            day_after_start = start + timedelta(days=1)
            user = users_factories.UserFactory()
            offerer = offerers_factories.OffererFactory()
            venue = offerers_factories.VenueFactory(managingOfferer=offerer, publicName="Le Petit Rintintin")

            # Event offer with 1 expired stock, 2 futures ones and a mediation
            offer1 = offers_factories.EventOfferFactory(venue=venue, bookingAllowedDatetime=day_before_start)
            offers_factories.MediationFactory(offer=offer1, thumbCount=1, credit="Pour hurlevent !")
            favorite1 = favorite_factories.FavoriteOfferFactory(offer=offer1, user=user)
            # should be ignored because of the date in the past
            offers_factories.EventStockFactory(offer=offer1, beginningDatetime=day_before_start, price=10)
            # 2 valid stocks (different dates and prices)
            offers_factories.EventStockFactory(offer=offer1, beginningDatetime=start, price=30)
            offers_factories.EventStockFactory(offer=offer1, beginningDatetime=day_after_start, price=20)

            # Event offer with soft deleted stock and product's image
            offer2 = offers_factories.EventOfferFactory(venue=venue)
            mediation = offers_factories.MediationFactory(offer=offer2, thumbCount=666)
            favorite2 = favorite_factories.FavoriteOfferFactory(offer=offer2, user=user)
            offers_factories.EventStockFactory(offer=offer2, beginningDatetime=start, price=20, isSoftDeleted=True)
            offers_factories.EventStockFactory(offer=offer2, beginningDatetime=day_after_start, price=50)

            # Thing offer with no date
            offer3 = offers_factories.ThingOfferFactory(
                venue=venue, subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id
            )
            favorite3 = favorite_factories.FavoriteOfferFactory(offer=offer3, user=user)
            offers_factories.ThingStockFactory(offer=offer3, price=10)

            # Event offer with passed reservation date
            offer4 = offers_factories.EventOfferFactory(venue=venue)
            offers_factories.MediationFactory(offer=offer4)
            favorite4 = favorite_factories.FavoriteOfferFactory(offer=offer4, user=user)
            stock4 = offers_factories.EventStockFactory(
                offer=offer4, beginningDatetime=date_utils.get_naive_utc_now() + timedelta(minutes=30), price=50
            )
            assert stock4.bookingLimitDatetime < date_utils.get_naive_utc_now()

            # Event offer in the past
            offer5 = offers_factories.EventOfferFactory(venue=venue)
            offers_factories.MediationFactory(offer=offer5)
            favorite5 = favorite_factories.FavoriteOfferFactory(offer=offer5, user=user)
            offers_factories.EventStockFactory(offer=offer5, beginningDatetime=day_before_start, price=50)

            # Event offer with two times the same date / price
            offer6 = offers_factories.EventOfferFactory(venue=venue)
            favorite6 = favorite_factories.FavoriteOfferFactory(offer=offer6, user=user)
            offers_factories.EventStockFactory(offer=offer6, beginningDatetime=day_after_start, price=30)
            offers_factories.EventStockFactory(offer=offer6, beginningDatetime=day_after_start, price=30)

            client.with_token(user)

            # When
            with assert_num_queries(self.expected_num_queries):
                response = client.get(FAVORITES_URL)

            # Then
            assert response.status_code == 200
            favorites = response.json["favorites"]
            assert len(favorites) == 6

            # We have 2 valid stocks with different dates/prices and one mediation
            assert favorites[5]["id"] == favorite1.id
            assert favorites[5]["offer"]["id"] == offer1.id
            assert favorites[5]["offer"]["price"] is None
            assert favorites[5]["offer"]["startPrice"] == 2000
            assert favorites[5]["offer"]["date"] is None
            assert favorites[5]["offer"]["bookingAllowedDatetime"] == date_utils.format_into_utc_date(day_before_start)
            assert favorites[5]["offer"]["startDate"] == date_utils.format_into_utc_date(start)
            assert favorites[5]["offer"]["image"]["credit"] == "Pour hurlevent !"
            assert favorites[5]["offer"]["image"]["url"] == "http://localhost/storage/thumbs/mediations/%s" % (
                humanize(offer1.activeMediation.id)
            )
            assert favorites[5]["offer"]["expenseDomains"] == ["all"]
            assert favorites[5]["offer"]["subcategoryId"] == "SEANCE_CINE"
            assert favorites[5]["offer"]["venueName"] == "Le Petit Rintintin"

            # Only stock2b is valid and product has a thumb
            assert favorites[4]["id"] == favorite2.id
            assert favorites[4]["offer"]["id"] == offer2.id
            assert favorites[4]["offer"]["price"] == 5000
            assert favorites[4]["offer"]["startPrice"] is None
            assert favorites[4]["offer"]["date"] == date_utils.format_into_utc_date(day_after_start)
            assert favorites[4]["offer"]["startDate"] is None
            assert favorites[4]["offer"]["image"]["credit"] is None
            assert (
                favorites[4]["offer"]["image"]["url"]
                == f"http://localhost/storage/thumbs/mediations/{humanize(mediation.id)}_665"
            )
            assert favorites[4]["offer"]["expenseDomains"] == ["all"]
            assert favorites[4]["offer"]["subcategoryId"] == "SEANCE_CINE"
            assert favorites[4]["offer"]["venueName"] == "Le Petit Rintintin"

            # No date
            assert favorites[3]["id"] == favorite3.id
            assert favorites[3]["offer"]["id"] == offer3.id
            assert favorites[3]["offer"]["price"] == 1000
            assert favorites[3]["offer"]["startPrice"] is None
            assert favorites[3]["offer"]["date"] is None
            assert favorites[3]["offer"]["startDate"] is None
            assert favorites[3]["offer"]["image"] is None
            assert favorites[3]["offer"]["subcategoryId"] == "SUPPORT_PHYSIQUE_FILM"
            assert set(favorites[3]["offer"]["expenseDomains"]) == {"physical", "all"}
            assert favorites[3]["offer"]["venueName"] == "Le Petit Rintintin"

            # Offer in the future but past the booking limit
            assert favorites[2]["id"] == favorite4.id
            assert favorites[2]["offer"]["id"] == offer4.id
            assert favorites[2]["offer"]["price"] is None
            assert favorites[2]["offer"]["startPrice"] is None
            assert favorites[2]["offer"]["date"] is None
            assert favorites[2]["offer"]["startDate"] is None
            assert (
                favorites[2]["offer"]["image"]["url"]
                == f"http://localhost/storage/thumbs/mediations/{humanize(offer4.activeMediation.id)}"
            )
            assert favorites[2]["offer"]["expenseDomains"] == ["all"]
            assert favorites[2]["offer"]["subcategoryId"] == "SEANCE_CINE"
            assert favorites[2]["offer"]["venueName"] == "Le Petit Rintintin"

            # Offer in the past, favorite should appear but no price/date are valid
            assert favorites[1]["id"] == favorite5.id
            assert favorites[1]["offer"]["id"] == offer5.id
            assert favorites[1]["offer"]["price"] is None
            assert favorites[1]["offer"]["startPrice"] is None
            assert favorites[1]["offer"]["date"] is None
            assert favorites[1]["offer"]["startDate"] is None
            assert (
                favorites[1]["offer"]["image"]["url"]
                == f"http://localhost/storage/thumbs/mediations/{humanize(offer5.activeMediation.id)}"
            )
            assert favorites[1]["offer"]["expenseDomains"] == ["all"]
            assert favorites[1]["offer"]["subcategoryId"] == "SEANCE_CINE"
            assert favorites[1]["offer"]["venueName"] == "Le Petit Rintintin"

            # best price/same date twice should appear as single price/date
            assert favorites[0]["id"] == favorite6.id
            assert favorites[0]["offer"]["price"] == 3000
            assert favorites[0]["offer"]["startPrice"] is None
            assert favorites[0]["offer"]["date"] == date_utils.format_into_utc_date(day_after_start)
            assert favorites[0]["offer"]["startDate"] is None
            assert favorites[0]["offer"]["image"] is None
            assert favorites[0]["offer"]["expenseDomains"] == ["all"]
            assert favorites[0]["offer"]["subcategoryId"] == "SEANCE_CINE"
            assert favorites[0]["offer"]["venueName"] == "Le Petit Rintintin"

        def test_do_not_display_deactivated_favorites(self, client):
            # Given
            user = users_factories.UserFactory()
            active_offer = offers_factories.EventOfferFactory()
            favorite_factories.FavoriteOfferFactory(offer=active_offer, user=user)
            inactive_offer = offers_factories.EventOfferFactory(publicationDatetime=None)
            favorite_factories.FavoriteOfferFactory(offer=inactive_offer, user=user)

            # When
            client = client.with_token(user)
            with assert_num_queries(self.expected_num_queries):
                response = client.get(FAVORITES_URL)
                assert response.status_code == 200

            # Then
            assert response.json["nbFavorites"] == 1
            assert len(response.json["favorites"]) == 1
            assert response.json["favorites"][0]["offer"]["id"] == active_offer.id

        def test_offer_venue_name_is_public_name_for_non_digital_offer(self, client):
            user = users_factories.UserFactory()
            offerer = offerers_factories.OffererFactory(name="Pathé Gaumont")
            venue = offerers_factories.VenueFactory(managingOfferer=offerer, publicName="Ciné Pathé")
            offer = offers_factories.EventOfferFactory(venue=venue)
            favorite_factories.FavoriteOfferFactory(offer=offer, user=user)

            response = client.with_token(user).get(FAVORITES_URL)
            favorites = response.json["favorites"]

            assert favorites[0]["offer"]["venueName"] == "Ciné Pathé"

        def test_offer_venue_name_is_offerer_name_for_digital_offer(self, client):
            user = users_factories.UserFactory()
            offerer = offerers_factories.OffererFactory(name="Pathé Gaumont")
            venue = offerers_factories.VenueFactory(managingOfferer=offerer, publicName="Ciné Pathé")
            offer = offers_factories.DigitalOfferFactory(venue=venue)
            favorite_factories.FavoriteOfferFactory(offer=offer, user=user)

            client = client.with_token(user)

            with assert_num_queries(self.expected_num_queries):
                response = client.get(FAVORITES_URL)

            favorites = response.json["favorites"]

            assert favorites[0]["offer"]["venueName"] == "Pathé Gaumont"

        def test_expired_offer(self, client):
            # Given
            today = date_utils.get_naive_utc_now() + timedelta(hours=3)  # offset a bit to make sure it's > now()
            yesterday = today - timedelta(days=1)
            tomorow = today + timedelta(days=1)
            user = users_factories.BeneficiaryFactory()
            offerer = offerers_factories.OffererFactory()
            venue = offerers_factories.VenueFactory(managingOfferer=offerer)

            # Event offer future stock
            offer1 = offers_factories.EventOfferFactory(venue=venue)
            favorite1 = favorite_factories.FavoriteOfferFactory(offer=offer1, user=user)
            offers_factories.EventStockFactory(offer=offer1, beginningDatetime=tomorow, price=10)

            # Thing offer with no date
            offer2 = offers_factories.ThingOfferFactory(venue=venue)
            favorite2 = favorite_factories.FavoriteOfferFactory(offer=offer2, user=user)
            offers_factories.ThingStockFactory(offer=offer2, price=10)

            # Thing offer with past booking stock
            offer3 = offers_factories.ThingOfferFactory(venue=venue)
            favorite3 = favorite_factories.FavoriteOfferFactory(offer=offer3, user=user)
            offers_factories.ThingStockFactory(offer=offer3, bookingLimitDatetime=yesterday, price=10)

            # Event offer with stock in the future but past booking
            offer4 = offers_factories.EventOfferFactory(venue=venue)
            favorite4 = favorite_factories.FavoriteOfferFactory(offer=offer4, user=user)
            offers_factories.EventStockFactory(
                offer=offer4, beginningDatetime=today, bookingLimitDatetime=yesterday, price=10
            )

            # Event offer with soft deleted stock
            offer5 = offers_factories.EventOfferFactory(venue=venue)
            favorite5 = favorite_factories.FavoriteOfferFactory(offer=offer5, user=user)
            offers_factories.EventStockFactory(
                offer=offer5, beginningDatetime=tomorow, quantity=1, price=10, isSoftDeleted=True
            )

            # Event offer with booked stock
            offer6 = offers_factories.EventOfferFactory(venue=venue)
            favorite6 = favorite_factories.FavoriteOfferFactory(offer=offer6, user=user)
            stock6 = offers_factories.EventStockFactory(offer=offer6, beginningDatetime=tomorow, quantity=1, price=10)
            bookings_factories.BookingFactory(stock=stock6, user=user)

            client.with_token(user)

            # When
            with assert_num_queries(self.expected_num_queries):
                response = client.get(FAVORITES_URL)

            # Then
            assert response.status_code == 200
            favorites = response.json["favorites"]
            count = 6
            assert len(favorites) == count

            favorites.reverse()

            assert [fav["id"] for fav in favorites] == [
                favorite1.id,
                favorite2.id,
                favorite3.id,
                favorite4.id,
                favorite5.id,
                favorite6.id,
            ]
            assert [fav["offer"]["isExpired"] for fav in favorites] == [
                False,
                False,
                True,
                True,
                False,
                False,
            ]
            assert [fav["offer"]["isSoldOut"] for fav in favorites] == [
                False,
                False,
                False,
                False,
                True,
                True,
            ]
            assert [fav["offer"]["isReleased"] for fav in favorites] == [
                True,
                True,
                True,
                True,
                True,
                True,
            ]

        def test_uses_offerer_address_if_available(self, client):
            # Given
            user = users_factories.UserFactory()
            offerer_address = offerers_factories.OfferLocationFactory()
            offer = offers_factories.OfferFactory(offererAddress=offerer_address)
            client.with_token(user)
            # When

            client.post(FAVORITES_URL, json={"offerId": offer.id})
            with assert_num_queries(self.expected_num_queries):
                response = client.get(FAVORITES_URL)

            # Then
            assert response.status_code == 200
            assert response.json["favorites"][0]["offer"]["coordinates"] == {
                "latitude": float(offerer_address.address.latitude),
                "longitude": float(offerer_address.address.longitude),
            }
            assert response.json["favorites"][0]["offer"]["venueName"] == offerer_address.label

    class Returns401Test:
        def when_user_is_not_logged_in(self, client):
            # When
            with assert_num_queries(0):
                response = client.get(FAVORITES_URL)

            # Then
            assert response.status_code == 401


class CreateFavoriteTest:
    def when_user_creates_a_favorite(self, client):
        # Given
        user = users_factories.UserFactory()
        offer = offers_factories.EventOfferFactory(
            name="This is a long event name that has a space at the sixty-first character"
        )
        earliest_stock = offers_factories.EventStockFactory(offer=offer, price=Decimal("10.1"), quantity=None)
        offers_factories.EventStockFactory(beginningDatetime=earliest_stock.beginningDatetime + timedelta(days=30))

        # When
        response = client.with_token(user).post(FAVORITES_URL, json={"offerId": offer.id})

        # Then
        assert response.status_code == 200, response.data
        assert db.session.query(FavoriteOffer).count() == 1
        favorite = db.session.query(FavoriteOffer).first()
        assert favorite.dateCreated
        assert favorite.userId == user.id
        assert response.json["id"] == favorite.id
        assert response.json["offer"]["price"] == 1010

        expected_push_counts = (
            1  # for user attribute update in android
            + 1  # for user attribute update in iOS
            + 1  # for favorite tracking
        )
        assert len(push_testing.requests) == expected_push_counts
        assert len(users_testing.brevo_requests) == 1
        brevo_data = users_testing.brevo_requests[0]
        assert brevo_data["attributes"]["LAST_FAVORITE_CREATION_DATE"] is not None

        favorite_creation_tracking_event = next(
            event
            for event in push_testing.requests
            if event.get("event_name") == batch_models.BatchEvent.HAS_ADDED_OFFER_TO_FAVORITES.value
        )
        event_payload = favorite_creation_tracking_event["event_payload"]
        assert event_payload["event_date"] == earliest_stock.beginningDatetime.isoformat(timespec="seconds")
        assert event_payload["offer_name"] == "This is a long event name that has a space at the sixty-first..."
        assert all(value is not None for value in event_payload.values())

    def when_user_creates_a_favorite_twice(self, client):
        # Given
        user = users_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        offer1 = offers_factories.EventOfferFactory(venue=venue)
        assert db.session.query(FavoriteOffer).count() == 0

        client.with_token(user)

        # When
        response = client.post(FAVORITES_URL, json={"offerId": offer1.id})
        assert response.status_code == 200
        response = client.post(FAVORITES_URL, json={"offerId": offer1.id})

        # Then
        assert response.status_code == 200
        assert db.session.query(FavoriteOffer).count() == 1

        expected_push_counts = (
            1  # for user attribute update in android
            + 1  # for user attribute update in iOS
            + 1  # for favorite tracking
        )
        assert len(push_testing.requests) == expected_push_counts
        assert len(users_testing.brevo_requests) == 1
        brevo_data = users_testing.brevo_requests[0]
        assert brevo_data["attributes"]["LAST_FAVORITE_CREATION_DATE"] is not None

    @pytest.mark.settings(MAX_FAVORITES=1)
    def when_user_creates_one_favorite_above_the_limit(self, client):
        user = users_factories.UserFactory()
        offer = offers_factories.EventOfferFactory()
        assert db.session.query(FavoriteOffer).count() == 0

        client.with_token(user)

        response = client.post(FAVORITES_URL, json={"offerId": offer.id})

        assert response.status_code == 200, response.data
        assert db.session.query(FavoriteOffer).count() == 1

        response = client.post(FAVORITES_URL, json={"offerId": offer.id})

        assert response.status_code == 200, response.data
        other_offer = offers_factories.EventOfferFactory()
        response = client.post(FAVORITES_URL, json={"offerId": other_offer.id})

        assert response.status_code == 400, response.data
        assert response.json == {"code": "MAX_FAVORITES_REACHED"}
        assert db.session.query(FavoriteOffer).count() == 1

    def test_offer_does_not_exist(self, client):
        user = users_factories.UserFactory()

        # When
        response = client.with_token(user).post(FAVORITES_URL, json={"offerId": 0})

        # Then
        assert response.status_code == 404
        assert db.session.query(FavoriteOffer).count() == 0

    def test_offer_is_deactivated(self, client):
        user = users_factories.UserFactory()
        offer = offers_factories.EventOfferFactory(publicationDatetime=None)

        # When
        response = client.with_token(user).post(FAVORITES_URL, json={"offerId": offer.id})

        # Then
        assert response.status_code == 404
        assert db.session.query(FavoriteOffer).count() == 0

    @pytest.mark.parametrize(
        "validation_status, status_code, count",
        (
            (offers_models.OfferValidationStatus.APPROVED, 200, 1),
            (offers_models.OfferValidationStatus.DRAFT, 404, 0),
            (offers_models.OfferValidationStatus.PENDING, 404, 0),
            (offers_models.OfferValidationStatus.REJECTED, 404, 0),
        ),
    )
    def test_offer_is_not_approved(self, client, validation_status, status_code, count):
        user = users_factories.UserFactory()
        offer = offers_factories.EventOfferFactory(validation=validation_status)

        # When
        response = client.with_token(user).post(FAVORITES_URL, json={"offerId": offer.id})

        # Then
        assert response.status_code == status_code
        assert db.session.query(FavoriteOffer).count() == count

    @pytest.mark.parametrize(
        "validation_status, status_code, count",
        (
            (ValidationStatus.NEW, 404, 0),
            (ValidationStatus.PENDING, 404, 0),
            (ValidationStatus.VALIDATED, 200, 1),
            (ValidationStatus.REJECTED, 404, 0),
            (ValidationStatus.DELETED, 404, 0),
            (ValidationStatus.CLOSED, 404, 0),
        ),
    )
    def test_offerer_is_not_validated(self, client, validation_status, status_code, count):
        user = users_factories.UserFactory()
        offer = offers_factories.EventOfferFactory(venue__managingOfferer__validationStatus=validation_status)

        # When
        response = client.with_token(user).post(FAVORITES_URL, json={"offerId": offer.id})

        # Then
        assert response.status_code == status_code
        assert db.session.query(FavoriteOffer).count() == count

    @pytest.mark.usefixtures("clean_database")
    def test_create_favorite_concurrently(self, client, app, settings):
        user = users_factories.BeneficiaryGrant18Factory()
        offer = offers_factories.ThingOfferFactory()
        offer_id = offer.id
        client_with_user = client.with_token(user)

        def add_to_favorite(position):
            def slow_get_favorites(*args, **kwargs):
                time.sleep(position % 2)
                # return the mocked function's return value
                return mock.DEFAULT

            with (
                mock.patch("pcapi.core.favorites.api.update_external_user") as update_external_user_mock,
                mock.patch(
                    "pcapi.core.favorites.api.track_offer_added_to_favorites_event",
                ) as track_offer_added_to_favorites_event_mock,
                mock.patch(
                    "pcapi.routes.native.v1.favorites.get_favorites_for", wraps=get_favorites_for
                ) as get_favorites_for_mock,
            ):
                # Use the app context in the new thread
                app.app_context().push()
                # Simulate a slow db transaction so we can get the race condition
                get_favorites_for_mock.side_effect = slow_get_favorites
                # Allow lock_timeout to be sure that the db transaction is waiting while another transaction is inserting the same row
                db.session.execute(sa.text("SET LOCAL lock_timeout='3s'"))
                try:
                    response = client_with_user.post(FAVORITES_URL, json={"offerId": offer_id})
                finally:
                    db.session.execute(sa.text(f"SET LOCAL lock_timeout='{settings.DATABASE_LOCK_TIMEOUT}'"))
            return (
                response.status_code,
                update_external_user_mock.call_count,
                track_offer_added_to_favorites_event_mock.call_count,
            )

        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = []
            for i in range(3):
                futures.append(executor.submit(add_to_favorite, i))
            results = [future.result() for future in futures]

        # all returned status codes should be == 200. update_external_user and track_offer_added_to_favorites_event should be called once
        assert set(results) == {(200, 1, 1), (200, 0, 0)}
        assert (
            db.session.query(FavoriteOffer)
            .filter(FavoriteOffer.offerId == offer_id, FavoriteOffer.userId == user.id)
            .count()
            == 1
        )


class DeleteTest:
    class Returns204Test:
        def when_user_delete_its_favorite(self, client):
            # Given
            user = users_factories.UserFactory()
            offerer = offerers_factories.OffererFactory()
            venue = offerers_factories.VenueFactory(managingOfferer=offerer)
            offer = offers_factories.ThingOfferFactory(venue=venue)
            favorite = favorite_factories.FavoriteOfferFactory(offer=offer, user=user)
            assert db.session.query(FavoriteOffer).count() == 1

            # When
            response = client.with_token(user).delete(f"{FAVORITES_URL}/{favorite.id}")

            # Then
            assert response.status_code == 204
            assert db.session.query(FavoriteOffer).count() == 0

        def when_user_delete_another_user_favorite(self, client):
            # Given
            user = users_factories.UserFactory()
            other_beneficiary = users_factories.BeneficiaryGrant18Factory()
            offerer = offerers_factories.OffererFactory()
            venue = offerers_factories.VenueFactory(managingOfferer=offerer)
            offer = offers_factories.ThingOfferFactory(venue=venue)
            favorite = favorite_factories.FavoriteOfferFactory(offer=offer, user=other_beneficiary)
            assert db.session.query(FavoriteOffer).count() == 1

            # When
            response = client.with_token(user).delete(f"{FAVORITES_URL}/{favorite.id}")

            # Then
            assert response.status_code == 404
            assert db.session.query(FavoriteOffer).count() == 1

        def when_user_delete_non_existent_favorite(self, client):
            # Given
            user = users_factories.UserFactory()

            # When
            response = client.with_token(user).delete(f"{FAVORITES_URL}/1203481310")

            # Then
            assert response.status_code == 404
