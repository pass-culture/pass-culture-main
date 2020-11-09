from datetime import datetime
from datetime import timedelta
from unittest.mock import patch

import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.models import EventType
from pcapi.models import StockSQLEntity
from pcapi.models import ThingType
from pcapi.models.feature import override_features
from pcapi.repository import repository
from pcapi.repository.provider_queries import get_provider_by_local_class
from pcapi.routes.serialization import serialize
from pcapi.utils.date import DATE_ISO_FORMAT
from pcapi.utils.human_ids import dehumanize
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


class Returns201:
    @override_features(SYNCHRONIZE_ALGOLIA=True)
    @patch("pcapi.routes.stocks.redis.add_offer_id")
    def when_user_has_rights(self, mock_add_offer_id_to_redis, app, db_session):
        # Given
        offer = offers_factories.OfferFactory(product__type=str(ThingType.AUDIOVISUEL))
        user_offerer = offers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        stock_data = {"price": 1222, "offerId": humanize(offer.id)}

        # When
        response = (
            TestClient(app.test_client())
            .with_auth("user@example.com")
            .post("/stocks", json=stock_data)
        )

        # Then
        assert response.status_code == 201

        # This are variables we do not have control over with but we still want to check
        # the response body has the right format
        id = response.json["id"]
        assert type(id) == str

        stock = StockSQLEntity.query.filter_by(id=dehumanize(id)).first()
        assert stock.price == 1222
        assert stock.bookingLimitDatetime is None

        mock_add_offer_id_to_redis.assert_called()
        mock_args, mock_kwargs = mock_add_offer_id_to_redis.call_args
        assert mock_kwargs["offer_id"] == offer.id


class Returns400:
    def when_missing_offer_id(self, app, db_session):
        # Given
        user = users_factories.UserFactory()

        # When
        response = (
            TestClient(app.test_client())
            .with_auth(user.email)
            .post("/stocks", json={"price": 1222})
        )

        # Then
        assert response.status_code == 400
        assert response.json == {"offerId": ["Ce champ est obligatoire"]}

    def when_booking_limit_datetime_after_beginning_datetime(self, app, db_session):
        # Given
        user = users_factories.UserFactory(isAdmin=True, canBookFreeOffers=False)
        offer = offers_factories.OfferFactory(product__type=str(EventType.JEUX))

        beginningDatetime = datetime(2019, 2, 14)

        data = {
            "price": 1222,
            "offerId": humanize(offer.id),
            "beginningDatetime": serialize(beginningDatetime),
            "bookingLimitDatetime": serialize(beginningDatetime + timedelta(days=2)),
        }

        # When
        response = (
            TestClient(app.test_client())
            .with_auth(user.email)
            .post("/stocks", json=data)
        )

        # Then
        assert response.status_code == 400
        assert response.json == {
            "bookingLimitDatetime": [
                "La date limite de réservation pour cette offre est postérieure à la date de début de l'évènement"
            ]
        }

    def when_invalid_format_for_booking_limit_datetime(self, app, db_session):
        # Given
        user = users_factories.UserFactory(isAdmin=True, canBookFreeOffers=False)
        offer = offers_factories.OfferFactory(product__type=str(EventType.JEUX))

        data = {
            "price": 0,
            "offerId": humanize(offer.id),
            "beginningDatetime": "2020-10-11T00:00:00Z",
            "bookingLimitDatetime": "zbbopbjeo",
        }

        # When
        response = (
            TestClient(app.test_client())
            .with_auth(user.email)
            .post("/stocks", json=data)
        )

        # Then
        assert response.status_code == 400
        assert response.json == {"bookingLimitDatetime": ["Format de date invalide"]}

    def when_booking_limit_datetime_is_none_for_event(self, app, db_session):
        # Given
        user = users_factories.UserFactory(isAdmin=True, canBookFreeOffers=False)
        offer = offers_factories.OfferFactory(product__type=str(EventType.JEUX))

        beginningDatetime = datetime(2019, 2, 14)
        data = {
            "price": 0,
            "offerId": humanize(offer.id),
            "bookingLimitDatetime": None,
            "beginningDatetime": serialize(beginningDatetime),
        }

        # When
        response = (
            TestClient(app.test_client())
            .with_auth(user.email)
            .post("/stocks", json=data)
        )

        # Then
        assert response.status_code == 400
        assert response.json == {
            "bookingLimitDatetime": ["Ce paramètre est obligatoire"]
        }

    def when_setting_beginning_datetime_on_offer_with_thing(self, app, db_session):
        # Given
        user = users_factories.UserFactory(isAdmin=True, canBookFreeOffers=False)
        offer = offers_factories.OfferFactory(product__type=str(ThingType.AUDIOVISUEL))

        beginningDatetime = datetime(2019, 2, 14)

        data = {
            "price": 0,
            "offerId": humanize(offer.id),
            "beginningDatetime": serialize(beginningDatetime),
            "bookingLimitDatetime": serialize(beginningDatetime - timedelta(days=2)),
        }

        # When
        response = (
            TestClient(app.test_client())
            .with_auth(user.email)
            .post("/stocks", json=data)
        )

        # Then
        assert response.status_code == 400
        assert response.json == {
            "global": [
                "Impossible de mettre une date de début si l'offre ne porte pas sur un événement"
            ]
        }

    def when_stock_is_on_offer_coming_from_provider(self, app, db_session):
        # given
        tite_live_provider = get_provider_by_local_class("TiteLiveThings")

        user = users_factories.UserFactory()
        offerer = offers_factories.OffererFactory()
        venue = offers_factories.VenueFactory(managingOfferer=offerer)
        user_offerer = offers_factories.UserOffererFactory(user=user, offerer=offerer)
        product = offers_factories.ProductFactory(type=str(ThingType.AUDIOVISUEL))
        idAtProviders = f"{product.idAtProviders}@{venue.siret}"

        offer = offers_factories.OfferFactory(
            product=product,
            venue=venue,
            lastProviderId=tite_live_provider.id,
            lastProvider=tite_live_provider,
            idAtProviders=idAtProviders,
        )

        stock_data = {"price": 1222, "offerId": humanize(offer.id)}

        # When
        response = (
            TestClient(app.test_client())
            .with_auth(user.email)
            .post("/stocks", json=stock_data)
        )

        # Then
        assert response.status_code == 400
        assert response.json == {
            "global": ["Les offres importées ne sont pas modifiables"]
        }


class Returns403:
    def when_user_has_no_rights_and_creating_stock_from_offer_id(self, app, db_session):
        # Given
        user = users_factories.UserFactory(email="wrong@example.com")
        offer = offers_factories.OfferFactory(product__type=str(ThingType.AUDIOVISUEL))
        user_offerer = offers_factories.UserOffererFactory(
            user__email="right@example.com", offerer=offer.venue.managingOfferer
        )

        data = {"price": 1222, "offerId": humanize(offer.id)}

        # When
        response = (
            TestClient(app.test_client())
            .with_auth(user.email)
            .post("/stocks", json=data)
        )

        # Then
        assert response.status_code == 403
        assert response.json == {
            "global": [
                "Vous n'avez pas les droits d'accès suffisant pour accéder à cette information."
            ]
        }
