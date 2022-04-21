from datetime import datetime

from freezegun import freeze_time
import pytest

from pcapi.core.educational.factories import CollectiveOfferFactory
from pcapi.core.educational.factories import CollectiveStockFactory
import pcapi.core.offerers.factories as offerers_factories
from pcapi.utils.human_ids import humanize


pytestmark = pytest.mark.usefixtures("db_session")


@freeze_time("2020-11-17 15:00:00")
class Return200Test:
    def test_get_educational_stock(self, client):
        # Given
        stock = CollectiveStockFactory(
            beginningDatetime=datetime(2021, 12, 18),
            price=1200,
            numberOfTickets=32,
            bookingLimitDatetime=datetime(2021, 12, 1),
            priceDetail="Détail du prix",
        )
        offerers_factories.UserOffererFactory(
            user__email="user@example.com", offerer=stock.collectiveOffer.venue.managingOfferer
        )

        client.with_session_auth("user@example.com")
        response = client.get(f"/collective/offers/{humanize(stock.collectiveOffer.id)}/stock")

        # Then
        assert response.status_code == 200
        assert response.json == {
            "id": humanize(stock.id),
            "beginningDatetime": "2021-12-18T00:00:00Z",
            "bookingLimitDatetime": "2021-12-01T00:00:00Z",
            "price": 1200.0,
            "numberOfTickets": 32,
            "isEducationalStockEditable": True,
            "educationalPriceDetail": "Détail du prix",
            "stockId": None,
        }


@freeze_time("2020-11-17 15:00:00")
class Return403Test:
    def test_get_collective_stock_should_not_be_possible_when_user_not_linked_to_offerer(self, app, client):
        stock = CollectiveStockFactory(
            beginningDatetime=datetime(2021, 12, 18),
            price=1200,
            numberOfTickets=32,
            bookingLimitDatetime=datetime(2021, 12, 1),
            priceDetail="Détail du prix",
        )
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
        )

        client.with_session_auth("user@example.com")
        response = client.get(f"/collective/offers/{humanize(stock.collectiveOffer.id)}/stock")

        # Then
        assert response.status_code == 403
        assert response.json == {
            "global": ["Vous n'avez pas les droits d'accès suffisant pour accéder à cette information."]
        }


@freeze_time("2020-11-17 15:00:00")
class Return404Test:
    def test_get_collective_stock_when_no_stock_exists_for_offer(self, app, client):
        offer = CollectiveOfferFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        client.with_session_auth("user@example.com")
        response = client.get(f"/collective/offers/{humanize(offer.id)}/stock")

        # Then
        assert response.status_code == 404
        assert response.json == {"stock": ["Aucun stock trouvé à partir de cette offre"]}
