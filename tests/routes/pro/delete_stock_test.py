from pcapi.core.bookings.factories import BookingFactory
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.offers.models import OfferValidationStatus
import pcapi.core.users.factories as users_factories
from pcapi.notifications.push import testing as push_testing
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


class Returns200Test:
    def when_current_user_has_rights_on_offer(self, app, db_session):
        # given
        offer = offers_factories.OfferFactory()
        offers_factories.UserOffererFactory(
            user__email="pro@example.com",
            offerer=offer.venue.managingOfferer,
        )
        stock = offers_factories.StockFactory(offer=offer)
        booking = BookingFactory(stock=stock)

        # when
        client = TestClient(app.test_client()).with_auth("pro@example.com")
        response = client.delete(f"/stocks/{humanize(stock.id)}")

        # then
        assert response.status_code == 200
        assert response.json == {"id": humanize(stock.id)}
        assert stock.isSoftDeleted
        assert push_testing.requests[-1] == {
            "group_id": "Cancel_booking",
            "message": {
                "body": f"""Ta commande "{offer.name}" a été annulée par l'offreur.""",
                "title": "Commande annulée",
            },
            "user_ids": [booking.userId],
        }


class Returns400Test:
    def when_stock_is_on_an_offer_from_titelive_provider(self, app, db_session):
        # given
        provider = offerers_factories.AllocineProviderFactory(localClass="TiteLiveThings")
        offer = offers_factories.OfferFactory(lastProvider=provider, idAtProviders="1")
        stock = offers_factories.StockFactory(offer=offer)

        user = users_factories.AdminFactory()

        # when
        client = TestClient(app.test_client()).with_auth(user.email)
        response = client.delete(f"/stocks/{humanize(stock.id)}")

        # then
        assert response.status_code == 400
        assert response.json["global"] == ["Les offres importées ne sont pas modifiables"]

    def test_delete_non_approved_offer_fails(self, app, db_session):
        pending_validation_offer = offers_factories.OfferFactory(validation=OfferValidationStatus.PENDING)
        stock = offers_factories.StockFactory(offer=pending_validation_offer)
        user = users_factories.AdminFactory()

        client = TestClient(app.test_client()).with_auth(user.email)
        response = client.delete(f"/stocks/{humanize(stock.id)}")

        assert response.status_code == 400
        assert response.json["global"] == ["Les offres refusées ou en attente de validation ne sont pas modifiables"]


class Returns403Test:
    def when_current_user_has_no_rights_on_offer(self, app, db_session):
        # given
        user = users_factories.UserFactory(email="notadmin@example.com")
        stock = offers_factories.StockFactory()

        # when
        client = TestClient(app.test_client()).with_auth(user.email)
        response = client.delete(f"/stocks/{humanize(stock.id)}")

        # then
        assert response.status_code == 403
