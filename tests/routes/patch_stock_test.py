from datetime import datetime
from datetime import timedelta
from unittest.mock import patch

from freezegun import freeze_time

import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.models import EventType
from pcapi.models import Provider
from pcapi.models import StockSQLEntity
from pcapi.models import ThingType
from pcapi.models.feature import override_features
from pcapi.repository import repository
from pcapi.repository.provider_queries import get_provider_by_local_class
from pcapi.routes.serialization import serialize
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


class Returns200:
    def when_user_has_editor_rights_on_offerer(self, app, db_session):
        # given
        date_event = datetime(2020, 10, 15)

        offer = offers_factories.OfferFactory(product__type=str(EventType.JEUX))
        user_offerer = offers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        stock = offers_factories.StockFactory(
            offer=offer,
            price=100,
            quantity=10,
            dateCreated=date_event,
            dateModified=date_event,
            dateModifiedAtLastProvider=date_event,
        )

        humanized_stock_id = humanize(stock.id)

        # when
        request_update = (
            TestClient(app.test_client())
            .with_auth("user@example.com")
            .patch("/stocks/" + humanized_stock_id, json={"quantity": 5, "price": 20})
        )

        # then
        assert request_update.status_code == 200
        assert request_update.json == {"id": humanize(stock.id)}

        assert stock.quantity == 5
        assert stock.price == 20

    def when_user_is_admin(self, app, db_session):
        # given
        user = users_factories.UserFactory(canBookFreeOffers=False, isAdmin=True)
        stock = offers_factories.StockFactory(price=100, quantity=10)

        humanized_stock_id = humanize(stock.id)

        # when
        request_update = (
            TestClient(app.test_client())
            .with_auth(user.email)
            .patch("/stocks/" + humanized_stock_id, json={"quantity": 5, "price": 20})
        )

        # then
        assert request_update.status_code == 200
        assert stock.quantity == 5
        assert stock.price == 20

    def when_booking_limit_datetime_is_none_for_thing(self, app, db_session):
        # Given
        date_event = datetime(2020, 10, 15)

        user = users_factories.UserFactory(isAdmin=True, canBookFreeOffers=False)
        stock = offers_factories.StockFactory(
            offer__product__type=str(ThingType.AUDIOVISUEL),
            price=10,
            dateCreated=date_event,
            dateModified=date_event,
            dateModifiedAtLastProvider=date_event,
        )

        stock_id = stock.id

        data = {
            "price": 120,
            "offerId": humanize(stock.offer.id),
            "bookingLimitDatetime": None,
        }

        # When
        response = TestClient(app.test_client()).with_auth(user.email).patch("/stocks/" + humanize(stock.id), json=data)

        # Then
        assert response.status_code == 200
        assert response.json["id"] == humanize(stock.id)

        assert stock.bookingLimitDatetime == None
        assert stock.price == 120

    @override_features(SYNCHRONIZE_ALGOLIA=True)
    @patch("pcapi.routes.stocks.redis.add_offer_id")
    def when_stock_is_edited_expect_offer_id_to_be_added_to_redis(self, mock_redis, app, db_session):
        # given
        user = users_factories.UserFactory(isAdmin=True, canBookFreeOffers=False)
        stock = offers_factories.StockFactory(offer__product__type=str(EventType.JEUX), price=100, quantity=10)

        # when
        request_update = (
            TestClient(app.test_client())
            .with_auth(user.email)
            .patch("/stocks/" + humanize(stock.id), json={"quantity": 5, "price": 20})
        )

        # then
        assert request_update.status_code == 200
        mock_redis.assert_called_once_with(client=app.redis_client, offer_id=stock.offerId)

    def when_offer_come_from_allocine_provider_and_fields_updated_in_stock_are_editable(self, app, db_session):
        # given
        date_event = datetime(2020, 10, 15)

        allocine_provider = get_provider_by_local_class("AllocineStocks")

        user = users_factories.UserFactory(isAdmin=True, canBookFreeOffers=False)
        venue = offers_factories.VenueFactory()
        product = offers_factories.ProductFactory(type=str(ThingType.AUDIOVISUEL))
        idAtProviders = f"{product.idAtProviders}@{venue.siret}"

        offer = offers_factories.OfferFactory(
            product=product,
            venue=venue,
            lastProviderId=allocine_provider.id,
            lastProvider=allocine_provider,
            idAtProviders=idAtProviders,
        )
        stock = offers_factories.StockFactory(
            offer=offer,
            quantity=10,
            price=10,
            dateCreated=date_event,
            dateModified=date_event,
            dateModifiedAtLastProvider=date_event,
        )

        humanized_stock_id = humanize(stock.id)

        # when
        request_update = (
            TestClient(app.test_client())
            .with_auth(user.email)
            .patch(f"/stocks/{humanized_stock_id}", json={"quantity": 5, "price": 20})
        )

        # then
        assert request_update.status_code == 200

        assert stock.quantity == 5
        assert stock.price == 20

    @patch("pcapi.routes.stocks.send_raw_email")
    @patch("pcapi.routes.stocks.find_not_cancelled_bookings_by_stock")
    @freeze_time("2020-10-15 09:20:00")
    def when_stock_changes_date_and_should_send_email_to_users_with_correct_info(
        self, find_not_cancelled_bookings_by_stock, email_function, app, db_session
    ):
        # Given
        event_date = datetime.utcnow() + timedelta(days=1)

        user = users_factories.UserFactory()
        admin = users_factories.UserFactory(email="admin@email.fr", canBookFreeOffers=False, isAdmin=True)
        stock = offers_factories.StockFactory(
            offer__product__type=str(EventType.JEUX),
            price=0,
            beginningDatetime=event_date,
            bookingLimitDatetime=event_date,
        )
        booking = bookings_factories.BookingFactory(user=user, stock=stock)

        find_not_cancelled_bookings_by_stock.return_value = [booking]
        serialized_date = serialize(stock.beginningDatetime + timedelta(days=1) + timedelta(hours=3))

        # When
        request_update = (
            TestClient(app.test_client())
            .with_auth(admin.email)
            .patch(
                "/stocks/" + humanize(stock.id),
                json={"beginningDatetime": serialized_date},
            )
        )

        # Then
        assert request_update.status_code == 200
        assert email_function.call_count == 1
        data_email = email_function.call_args[1]
        assert data_email["data"]["Vars"]["event_date"] == "samedi 17 octobre 2020"
        assert data_email["data"]["Vars"]["event_hour"] == "14h20"

    @patch("pcapi.routes.stocks.have_beginning_date_been_modified")
    @patch("pcapi.routes.stocks.send_batch_stock_postponement_emails_to_users")
    def when_stock_date_has_not_been_changed_and_should_not_email_to_beneficiaries(
        self,
        mocked_send_batch_stock_postponement_emails_to_users,
        mocked_have_beginning_date_been_modified,
        app,
        db_session,
    ):
        # Given
        user = users_factories.UserFactory()
        admin = users_factories.UserFactory(email="admin@email.fr", canBookFreeOffers=False, isAdmin=True)
        stock = offers_factories.StockFactory(
            price=0,
        )
        booking = bookings_factories.BookingFactory(user=user, stock=stock)

        mocked_have_beginning_date_been_modified.return_value = False

        # When
        request_update = (
            TestClient(app.test_client())
            .with_auth(admin.email)
            .patch("/stocks/" + humanize(stock.id), json={"price": 20})
        )

        # Then
        assert request_update.status_code == 200
        mocked_have_beginning_date_been_modified.assert_called_once()
        mocked_send_batch_stock_postponement_emails_to_users.assert_not_called()


class Returns400:
    def when_wrong_type_for_quantity(self, app, db_session):
        # given
        user = users_factories.UserFactory(canBookFreeOffers=False, isAdmin=True)
        stock = offers_factories.StockFactory()

        # when
        response = (
            TestClient(app.test_client())
            .with_auth(user.email)
            .patch("/stocks/" + humanize(stock.id), json={"quantity": " "})
        )

        # then
        assert response.status_code == 400
        assert response.json == {"quantity": ["Saisissez un nombre valide"]}

    def when_booking_limit_datetime_after_beginning_datetime(self, app, db_session):
        # given
        event_date = datetime.utcnow() + timedelta(days=1)

        user = users_factories.UserFactory(canBookFreeOffers=False, isAdmin=True)
        stock = offers_factories.StockFactory(
            offer__product__type=str(EventType.JEUX),
            beginningDatetime=event_date,
            bookingLimitDatetime=event_date,
        )

        serialized_date = serialize(stock.beginningDatetime + timedelta(days=1))

        # when
        response = (
            TestClient(app.test_client())
            .with_auth(user.email)
            .patch(
                "/stocks/" + humanize(stock.id),
                json={"bookingLimitDatetime": serialized_date},
            )
        )

        # then
        assert response.status_code == 400
        assert response.json == {
            "bookingLimitDatetime": [
                "La date limite de réservation pour cette offre est postérieure à la date de début de l'évènement"
            ]
        }

    def when_quantity_below_existing_bookings_quantity(self, app, db_session):
        # given
        user = users_factories.UserFactory()
        admin = users_factories.UserFactory(email="admin@email.fr", canBookFreeOffers=False, isAdmin=True)
        stock = offers_factories.StockFactory(price=0, quantity=1)
        booking = bookings_factories.BookingFactory(user=user, stock=stock)

        # when
        response = (
            TestClient(app.test_client())
            .with_auth(admin.email)
            .patch("/stocks/" + humanize(stock.id), json={"quantity": 0})
        )

        # then
        assert response.status_code == 400
        assert response.json == {"quantity": ["Le stock total ne peut être inférieur au nombre de réservations"]}

    def when_booking_limit_datetime_is_none_for_event(self, app, db_session):
        # Given
        user = users_factories.UserFactory(canBookFreeOffers=False, isAdmin=True)
        stock = offers_factories.StockFactory(offer__product__type=str(EventType.JEUX))

        data = {
            "price": 0,
            "offerId": humanize(stock.offer.id),
            "bookingLimitDatetime": None,
        }

        # When
        response = TestClient(app.test_client()).with_auth(user.email).patch("/stocks/" + humanize(stock.id), json=data)

        # Then
        assert response.status_code == 400
        assert response.json == {"bookingLimitDatetime": ["Ce paramètre est obligatoire"]}

    def when_offer_come_from_titelive_provider(self, app, db_session):
        # given
        titelive_provider = get_provider_by_local_class("TiteLiveThings")

        user = users_factories.UserFactory(isAdmin=True, canBookFreeOffers=False)

        venue = offers_factories.VenueFactory()
        product = offers_factories.ProductFactory(type=str(ThingType.AUDIOVISUEL))
        idAtProviders = f"{product.idAtProviders}@{venue.siret}"

        offer = offers_factories.OfferFactory(
            product=product,
            venue=venue,
            lastProviderId=titelive_provider.id,
            lastProvider=titelive_provider,
            idAtProviders=idAtProviders,
        )
        stock = offers_factories.StockFactory(offer=offer, quantity=10, price=10)

        humanized_stock_id = humanize(stock.id)

        # when
        request_update = (
            TestClient(app.test_client())
            .with_auth(user.email)
            .patch("/stocks/" + humanized_stock_id, json={"quantity": 5})
        )

        # then
        assert request_update.status_code == 400
        assert request_update.json["global"] == ["Les offres importées ne sont pas modifiables"]

        assert stock.quantity == 10

    def when_update_allocine_offer_with_new_values_for_non_editable_fields(self, app, db_session):
        # given
        allocine_provider = get_provider_by_local_class("AllocineStocks")

        user = users_factories.UserFactory(isAdmin=True, canBookFreeOffers=False)
        venue = offers_factories.VenueFactory()
        product = offers_factories.ProductFactory(type=str(EventType.JEUX))
        idAtProviders = f"{product.idAtProviders}@{venue.siret}"

        offer = offers_factories.OfferFactory(
            product=product,
            venue=venue,
            lastProviderId=allocine_provider.id,
            lastProvider=allocine_provider,
            idAtProviders=idAtProviders,
        )
        stock = offers_factories.StockFactory(offer=offer, quantity=10, price=10, idAtProviders=idAtProviders)

        humanized_stock_id = humanize(stock.id)

        # when
        request_update = (
            TestClient(app.test_client())
            .with_auth(user.email)
            .patch(
                f"/stocks/{humanized_stock_id}",
                json={
                    "quantity": 5,
                    "price": 20,
                    "beginningDatetime": "2020-02-08T14:30:00Z",
                },
            )
        )

        # then
        assert request_update.status_code == 400
        assert request_update.json["global"] == ["Pour les offres importées, certains champs ne sont pas modifiables"]

        existing_stock = StockSQLEntity.query.one()
        assert existing_stock.quantity == 10


class Returns403:
    def when_user_has_no_rights(self, app, db_session):
        # given
        user = users_factories.UserFactory(email="wrong@example.com")
        offer = offers_factories.OfferFactory(product__type=str(ThingType.AUDIOVISUEL))
        user_offerer = offers_factories.UserOffererFactory(
            user__email="right@example.com", offerer=offer.venue.managingOfferer
        )
        stock = offers_factories.StockFactory(offer=offer, quantity=10, price=10)

        # when
        response = (
            TestClient(app.test_client())
            .with_auth(user.email)
            .patch("/stocks/" + humanize(stock.id), json={"quantity": 5})
        )

        # then
        assert response.status_code == 403
        assert response.json == {
            "global": ["Vous n'avez pas les droits d'accès suffisant pour accéder à cette information."]
        }
