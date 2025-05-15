import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.offers.models as offer_models
import pcapi.core.users.factories as users_factories
from pcapi.core.bookings import factories as booking_factory
from pcapi.core.token import SecureToken
from pcapi.core.token.serialization import ConnectAsInternalModel
from pcapi.models import db


@pytest.mark.usefixtures("db_session")
class Returns204Test:
    def test_delete_multiple_stocks_by_offer_id(self, client):
        # Given
        offer = offers_factories.OfferFactory()
        user = users_factories.UserFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offer.venue.managingOfferer)

        batch_stocks = offers_factories.StockFactory.create_batch(3, offer=offer)
        booking_1 = booking_factory.BookingFactory(stock=batch_stocks[0])
        booking_2 = booking_factory.BookingFactory(stock=batch_stocks[1])
        data = {"ids_to_delete": [stock.id for stock in batch_stocks]}

        # When
        response = client.with_session_auth(user.email).post(f"/offers/{offer.id}/stocks/delete", json=data)

        # Then
        assert response.status_code == 204
        assert all(stock.isSoftDeleted for stock in db.session.query(offer_models.Stock).all())
        assert booking_1.cancellationUser == user
        assert booking_2.cancellationUser == user

    def test_delete_multiple_stocks_by_offer_id_with_connect_as(self, client):
        # Given
        offer = offers_factories.OfferFactory()
        user = users_factories.ProFactory()
        user_offerer = offerers_factories.UserOffererFactory(user=user, offerer=offer.venue.managingOfferer)

        batch_stocks = offers_factories.StockFactory.create_batch(3, offer=offer)
        booking_1 = booking_factory.BookingFactory(stock=batch_stocks[0])
        booking_2 = booking_factory.BookingFactory(stock=batch_stocks[1])
        data = {"ids_to_delete": [stock.id for stock in batch_stocks]}
        admin = users_factories.AdminFactory(email="admin@example.com")
        secure_token = SecureToken(
            data=ConnectAsInternalModel(
                redirect_link="https://example.com",
                user_id=user_offerer.user.id,
                internal_admin_email=admin.email,
                internal_admin_id=admin.id,
            ).dict(),
        )

        response_token = client.get(f"/users/connect-as/{secure_token.token}")
        assert response_token.status_code == 302

        # When
        response = client.with_session_auth(user.email).post(f"/offers/{offer.id}/stocks/delete", json=data)

        # Then
        assert response.status_code == 204
        assert all(stock.isSoftDeleted for stock in db.session.query(offer_models.Stock).all())
        assert booking_1.cancellationUser == admin
        assert booking_2.cancellationUser == admin

    def test_delete_unaccessible_stocks(self, client):
        # Given
        offer = offers_factories.OfferFactory()
        another_offer = offers_factories.OfferFactory()
        user = users_factories.UserFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offer.venue.managingOfferer)

        another_offer_stocks = offers_factories.StockFactory.create_batch(3, offer=another_offer)

        # When
        response = client.with_session_auth(user.email).post(
            f"/offers/{offer.id}/stocks/delete", json={"ids_to_delete": [stock.id for stock in another_offer_stocks]}
        )

        # Then
        assert response.status_code == 204

        assert all(not stock.isSoftDeleted for stock in db.session.query(offer_models.Stock).all())


@pytest.mark.usefixtures("db_session")
class Returns401Test:
    def test_delete_stocks_not_connected(self, client):
        # Given
        offer = offers_factories.OfferFactory()
        user = users_factories.UserFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offer.venue.managingOfferer)
        stock = offers_factories.StockFactory(offer=offer)
        data = {"ids_to_delete": [stock.id]}

        # When
        response = client.post(f"/offers/{offer.id}/stocks/delete", json=data)

        # Then
        assert response.status_code == 401


@pytest.mark.usefixtures("db_session")
class Returns403Test:
    def test_delete_stocks_when_current_user_has_no_rights_on_offer(self, client):
        # given
        offer = offers_factories.OfferFactory()
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)
        stock = offers_factories.StockFactory(offer=offer)
        data = {"ids_to_delete": [stock.id]}

        # when
        response = client.with_session_auth(pro.email).post(f"/offers/{offer.id}/stocks/delete", json=data)

        # then
        assert response.status_code == 403
