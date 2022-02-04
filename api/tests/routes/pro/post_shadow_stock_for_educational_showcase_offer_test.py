from datetime import datetime

import pytest

from pcapi.core.offers import factories as offer_factories
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
from pcapi.utils.human_ids import dehumanize
from pcapi.utils.human_ids import humanize


pytestmark = pytest.mark.usefixtures("db_session")


class Return200Test:
    def test_create_valid_shadow_stock_for_educational_offer(self, client):
        # Given
        offer = offer_factories.EducationalEventOfferFactory(extraData={"isShowcase": False})
        offer_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )
        print("OFFER ID", offer.id)

        # When
        stock_payload = {
            "educationalPriceDetail": "Détail du prix",
        }

        client.with_session_auth("user@example.com")
        response = client.post(f"/offers/educational/{humanize(offer.id)}/shadow-stock", json=stock_payload)

        # Then
        assert response.status_code == 201
        response_dict = response.json
        created_stock = Stock.query.get(dehumanize(response_dict["id"]))
        updated_offer = Offer.query.get(offer.id)
        assert offer.id == created_stock.offerId
        assert created_stock.educationalPriceDetail == "Détail du prix"
        assert created_stock.beginningDatetime == datetime(2030, 1, 1)
        assert created_stock.bookingLimitDatetime == datetime(2030, 1, 1)
        assert created_stock.price == 1
        assert created_stock.numberOfTickets == 1
        assert created_stock.educationalPriceDetail == "Détail du prix"
        assert updated_offer.extraData["isShowcase"] == True


class Return400Test:
    def test_create_educational_shadow_stocks_should_not_be_available_if_user_not_linked_to_offerer(self, app, client):
        # Given
        offer = offer_factories.EducationalEventOfferFactory(extraData={"isShowcase": False})
        offer_factories.UserOffererFactory(
            user__email="user@example.com",
        )

        # When
        stock_payload = {
            "educationalPriceDetail": "Détail du prix",
        }

        client.with_session_auth("user@example.com")
        response = client.post(f"/offers/educational/{humanize(offer.id)}/shadow-stock", json=stock_payload)
        updated_offer = Offer.query.get(offer.id)
        # Then
        assert response.status_code == 403
        assert response.json == {
            "global": ["Vous n'avez pas les droits d'accès suffisant pour accéder à cette information."]
        }
        assert updated_offer.extraData["isShowcase"] == False

    def should_not_accept_payload_with_price_details_with_more_than_1000_caracters(self, app, client):
        # Given
        offer = offer_factories.EducationalEventOfferFactory(extraData={"isShowcase": False})
        offer_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        stock_payload = {
            "educationalPriceDetail": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer sodales commodo tellus, at dictum odio vulputate nec. Donec iaculis rutrum nunc. Nam euismod, odio vel iaculis tincidunt, enim ante iaculis purus, ac vehicula ex lacus sit amet nisl. Aliquam et diam tellus. Curabitur in pharetra augue. Nunc scelerisque lectus non diam efficitur, eu porta neque vestibulum. Nullam elementum purus ac ligula viverra tincidunt. Etiam tincidunt metus nec nibh tempor tincidunt. Pellentesque ac ipsum purus. Duis vestibulum mollis nisi a vulputate. Nullam malesuada eros eu convallis rhoncus. Maecenas eleifend ex at posuere maximus. Suspendisse faucibus egestas dolor, sit amet dignissim odio condimentum vitae. Pellentesque ultricies eleifend nisi, quis pellentesque nisi faucibus finibus. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Suspendisse potenti. Aliquam convallis diam nisl, eget ullamcorper odio convallis ac. Ut quis nulla fringilla, commodo tellus ut.",
        }

        client.with_session_auth("user@example.com")
        response = client.post(f"/offers/educational/{humanize(offer.id)}/shadow-stock", json=stock_payload)

        updated_offer = Offer.query.get(offer.id)

        # Then
        assert response.status_code == 400
        assert response.json == {"educationalPriceDetail": ["Le détail du prix ne doit pas excéder 1000 caractères."]}
        assert updated_offer.extraData["isShowcase"] == False

    def should_not_allow_multiple_stocks(self, client):
        # Given
        offer = offer_factories.EducationalEventStockFactory(offer__extraData={"isShowcase": False}).offer
        offer_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        stock_payload = {
            "educationalPriceDetail": "Détail du prix",
        }

        client.with_session_auth("user@example.com")
        response = client.post(f"/offers/educational/{humanize(offer.id)}/shadow-stock", json=stock_payload)

        updated_offer = Offer.query.get(offer.id)

        # Then
        assert response.status_code == 400
        assert response.json == {"code": "EDUCATIONAL_STOCK_ALREADY_EXISTS"}
        assert updated_offer.extraData["isShowcase"] == False
