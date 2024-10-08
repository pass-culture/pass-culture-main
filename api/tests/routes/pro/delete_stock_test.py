from pcapi.core.bookings import factories as bookings_factory
from pcapi.core.bookings.factories import BookingFactory
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.offers.models import OfferValidationStatus
from pcapi.core.testing import override_features
from pcapi.core.token import SecureToken
from pcapi.core.token.serialization import ConnectAsInternalModel
import pcapi.core.users.factories as users_factories
from pcapi.notifications.push import testing as push_testing


class Returns200Test:
    @override_features(WIP_DISABLE_CANCEL_BOOKING_NOTIFICATION=False)
    def when_current_user_has_rights_on_offer(self, client, db_session):
        # given
        offer = offers_factories.OfferFactory()
        user_offerer = offerers_factories.UserOffererFactory(
            user__email="pro@example.com",
            offerer=offer.venue.managingOfferer,
        )
        stock = offers_factories.StockFactory(offer=offer)
        booking = BookingFactory(stock=stock)

        # when
        response = client.with_session_auth("pro@example.com").delete(f"/stocks/{stock.id}")

        # then
        assert response.status_code == 200
        assert response.json == {"id": stock.id}
        assert stock.isSoftDeleted
        assert stock.bookings[0].cancellationUser == user_offerer.user
        assert push_testing.requests[-1] == {
            "group_id": "Cancel_booking",
            "message": {
                "body": f"""Ta commande "{offer.name}" a été annulée par l'offreur.""",
                "title": "Commande annulée",
            },
            "user_ids": [booking.userId],
            "can_be_asynchronously_retried": False,
        }

    @override_features(WIP_DISABLE_CANCEL_BOOKING_NOTIFICATION=True)
    def when_current_user_has_rights_on_offer_with_FF(self, client, db_session):
        # given
        offer = offers_factories.OfferFactory()
        user_offerer = offerers_factories.UserOffererFactory(
            user__email="pro@example.com",
            offerer=offer.venue.managingOfferer,
        )
        stock = offers_factories.StockFactory(offer=offer)
        booking = BookingFactory(stock=stock)

        # when
        response = client.with_session_auth("pro@example.com").delete(f"/stocks/{stock.id}")

        # then
        assert response.status_code == 200
        assert response.json == {"id": stock.id}
        assert stock.isSoftDeleted
        assert stock.bookings[0].cancellationUser == user_offerer.user
        cancel_notification_requests = [req for req in push_testing.requests if req.get("group_id") == "Cancel_booking"]
        assert len(cancel_notification_requests) == 0

    def when_current_user_is_connect_as(self, client, db_session):
        # given
        offer = offers_factories.OfferFactory()
        user_offerer = offerers_factories.UserOffererFactory(
            user__email="pro@example.com",
            offerer=offer.venue.managingOfferer,
        )
        stock = offers_factories.StockFactory(offer=offer, bookings=[bookings_factory.BookingFactory()])
        expected_redirect_link = "https://example.com"
        admin = users_factories.AdminFactory(email="admin@example.com")
        secure_token = SecureToken(
            data=ConnectAsInternalModel(
                redirect_link=expected_redirect_link,
                user_id=user_offerer.user.id,
                internal_admin_email=admin.email,
                internal_admin_id=admin.id,
            ).dict(),
        )
        client = client.with_session_auth(admin.email)
        response_token = client.get(f"/users/connect-as/{secure_token.token}")
        assert response_token.status_code == 302

        # when
        response = client.delete(f"/stocks/{stock.id}")

        # then
        assert response.status_code == 200
        assert response.json == {"id": stock.id}
        assert stock.isSoftDeleted
        assert stock.bookings[0].cancellationUser == admin


class Returns400Test:
    def test_delete_non_approved_offer_fails(self, client, db_session):
        pending_validation_offer = offers_factories.OfferFactory(validation=OfferValidationStatus.PENDING)
        stock = offers_factories.StockFactory(offer=pending_validation_offer)
        user = users_factories.AdminFactory()

        response = client.with_session_auth(user.email).delete(f"/stocks/{stock.id}")

        assert response.status_code == 400
        assert response.json["global"] == ["Les offres refusées ou en attente de validation ne sont pas modifiables"]


class Returns403Test:
    def when_current_user_has_no_rights_on_offer(self, client, db_session):
        # given
        pro = users_factories.ProFactory(email="notadmin@example.com")
        stock = offers_factories.StockFactory()

        # when
        response = client.with_session_auth(pro.email).delete(f"/stocks/{stock.id}")

        # then
        assert response.status_code == 403
