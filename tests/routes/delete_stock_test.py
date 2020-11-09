from datetime import datetime
from datetime import timedelta
from unittest.mock import patch

from freezegun import freeze_time

import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.models import Booking
from pcapi.models import EventType
from pcapi.models import Provider
from pcapi.models.feature import override_features
from pcapi.repository import repository
from pcapi.repository.provider_queries import get_provider_by_local_class
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


NOW = datetime(2020, 10, 15)


class Returns200:
    def when_current_user_has_rights_on_offer(self, app, db_session):
        # given
        offer = offers_factories.OfferFactory()
        user_offerer = offers_factories.UserOffererFactory(
            user__email="notadmin@example.com",
            offerer=offer.venue.managingOfferer,
        )

        stock = offers_factories.StockFactory(
            offer=offer,
            price=100,
            quantity=10,
            dateCreated=NOW,
            dateModified=NOW,
            dateModifiedAtLastProvider=NOW,
        )

        # when
        response = (
            TestClient(app.test_client())
            .with_auth("notadmin@example.com")
            .delete("/stocks/" + humanize(stock.id))
        )

        # then
        assert response.status_code == 200
        assert response.json == {"id": humanize(stock.id)}
        assert stock.isSoftDeleted is True

    def expect_bookings_to_be_cancelled(self, app, db_session):
        # given
        admin = users_factories.UserFactory(
            email="admin@email.com", isAdmin=True, canBookFreeOffers=False
        )
        stock = offers_factories.StockFactory(
            dateCreated=NOW,
            dateModified=NOW,
            dateModifiedAtLastProvider=NOW,
            price=0,
        )
        other_user = users_factories.UserFactory(email="consumer@test.com")
        booking1 = bookings_factories.BookingFactory(
            user=other_user, isCancelled=False, stock=stock
        )
        booking2 = bookings_factories.BookingFactory(
            user=other_user, isCancelled=False, stock=stock
        )

        # when
        response = (
            TestClient(app.test_client())
            .with_auth(admin.email)
            .delete("/stocks/" + humanize(stock.id))
        )

        # then
        assert response.status_code == 200
        bookings = Booking.query.filter_by(isCancelled=True).all()
        assert booking1 in bookings
        assert booking2 in bookings
        assert stock.isSoftDeleted is True

    @freeze_time("2020-10-15 00:00:00")
    def expect_booking_to_be_cancelled_when_stock_is_an_event_that_ended_less_than_two_days_ago(
        self, app, db_session
    ):
        # given
        admin = users_factories.UserFactory(
            email="admin@email.com", isAdmin=True, canBookFreeOffers=False
        )
        user = users_factories.UserFactory(email="consumer@test.com")
        stock = offers_factories.StockFactory(
            offer__product__type=str(EventType.JEUX),
            price=0,
            quantity=10,
            dateCreated=NOW - timedelta(days=7),
            dateModified=NOW - timedelta(days=7),
            dateModifiedAtLastProvider=NOW - timedelta(days=7),
            beginningDatetime=NOW - timedelta(hours=47),
            bookingLimitDatetime=NOW - timedelta(days=6),
        )
        booking = bookings_factories.BookingFactory(
            user=user, isCancelled=False, stock=stock
        )

        # when
        response = (
            TestClient(app.test_client())
            .with_auth(admin.email)
            .delete("/stocks/" + humanize(stock.id))
        )

        # then
        assert response.status_code == 200
        booking_from_db = Booking.query.filter_by(isCancelled=True).one()
        assert booking == booking_from_db
        assert stock.isSoftDeleted is True

    def when_stock_is_on_an_offer_from_allocine_provider(self, app, db_session):
        # Given
        allocine_provider = get_provider_by_local_class("AllocineStocks")

        user = users_factories.UserFactory(isAdmin=True, canBookFreeOffers=False)
        venue = offers_factories.VenueFactory()
        product = offers_factories.ProductFactory()
        idAtProviders = f"{product.idAtProviders}@{venue.siret}"

        offer = offers_factories.OfferFactory(
            product=product,
            venue=venue,
            lastProviderId=allocine_provider.id,
            lastProvider=allocine_provider,
            idAtProviders=idAtProviders,
        )
        stock = offers_factories.StockFactory(offer=offer, idAtProviders=idAtProviders)

        # When
        response = (
            TestClient(app.test_client())
            .with_auth(user.email)
            .delete("/stocks/" + humanize(stock.id))
        )

        # Then
        assert response.status_code == 200
        assert stock.isSoftDeleted is True

    @override_features(SYNCHRONIZE_ALGOLIA=True)
    @patch("pcapi.routes.stocks.redis.add_offer_id")
    def when_stock_is_deleted_expect_offer_id_to_be_added_to_redis(
        self, mock_redis, app, db_session
    ):
        # given
        user = users_factories.UserFactory(isAdmin=True, canBookFreeOffers=False)
        stock = offers_factories.StockFactory()

        # when
        response = (
            TestClient(app.test_client())
            .with_auth(user.email)
            .delete("/stocks/" + humanize(stock.id))
        )

        # then
        assert response.status_code == 200
        assert stock.isSoftDeleted is True
        mock_redis.assert_called_once_with(
            client=app.redis_client, offer_id=stock.offerId
        )


class Returns400:
    def when_stock_is_on_an_offer_from_titelive_provider(self, app, db_session):
        # given
        allocine_provider = get_provider_by_local_class("TiteLiveThings")

        user = users_factories.UserFactory(isAdmin=True, canBookFreeOffers=False)
        venue = offers_factories.VenueFactory()
        product = offers_factories.ProductFactory()
        idAtProviders = f"{product.idAtProviders}@{venue.siret}"

        offer = offers_factories.OfferFactory(
            product=product,
            venue=venue,
            lastProviderId=allocine_provider.id,
            lastProvider=allocine_provider,
            idAtProviders=idAtProviders,
        )
        stock = offers_factories.StockFactory(offer=offer, idAtProviders=idAtProviders)

        # when
        response = (
            TestClient(app.test_client())
            .with_auth(user.email)
            .delete("/stocks/" + humanize(stock.id))
        )

        # then
        assert response.status_code == 400
        assert response.json["global"] == [
            "Les offres importées ne sont pas modifiables"
        ]

    @freeze_time("2020-10-15 00:00:00")
    def when_stock_is_an_event_that_ended_more_than_two_days_ago(self, app, db_session):
        # given
        admin = users_factories.UserFactory(
            email="admin@email.com", isAdmin=True, canBookFreeOffers=False
        )
        user = users_factories.UserFactory(email="consumer@test.com")
        product = offers_factories.ProductFactory(type=str(EventType.JEUX))
        offer = offers_factories.OfferFactory(product=product)
        stock = offers_factories.StockFactory(
            offer=offer,
            price=0,
            quantity=10,
            dateCreated=NOW - timedelta(days=7),
            dateModified=NOW - timedelta(days=7),
            dateModifiedAtLastProvider=NOW - timedelta(days=7),
            beginningDatetime=NOW - timedelta(hours=49),
            bookingLimitDatetime=NOW - timedelta(days=6),
        )
        booking = bookings_factories.BookingFactory(
            user=user, isCancelled=False, stock=stock
        )

        # when
        response = (
            TestClient(app.test_client())
            .with_auth(admin.email)
            .delete("/stocks/" + humanize(stock.id))
        )

        # then
        assert response.status_code == 400
        assert response.json["global"] == [
            "L'événement s'est terminé il y a plus de deux jours, "
            "la suppression est impossible."
        ]


class Returns403:
    def when_current_user_has_no_rights_on_offer(self, app, db_session):
        # given
        user = users_factories.UserFactory(email="notadmin@example.com")
        offer = offers_factories.OfferFactory()

        user_offerer = offers_factories.UserOffererFactory(
            user__email="anotheruser@example.com",
            offerer=offer.venue.managingOfferer,
        )

        stock = offers_factories.StockFactory(
            offer=offer,
        )

        # when
        response = (
            TestClient(app.test_client())
            .with_auth(user.email)
            .delete("/stocks/" + humanize(stock.id))
        )

        # then
        assert response.status_code == 403
