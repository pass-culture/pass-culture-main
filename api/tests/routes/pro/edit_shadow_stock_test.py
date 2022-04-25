from datetime import datetime

import pytest

import pcapi.core.educational.factories as educational_factories
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.offers.models import Stock
from pcapi.utils.human_ids import humanize


pytestmark = pytest.mark.usefixtures("db_session")


class Return200Test:
    def test_edit_shadow_stock(self, client):
        # Given
        stock = offers_factories.EducationalEventShadowStockFactory(
            educationalPriceDetail="Détail du prix",
        )
        educational_factories.CollectiveOfferTemplateFactory(offerId=stock.offerId)
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=stock.offer.venue.managingOfferer)

        # When
        stock_edition_payload = {
            "educationalPriceDetail": "Nouvelle description du prix",
        }

        client.with_session_auth("user@example.com")
        response = client.patch(f"/stocks/shadow/{humanize(stock.id)}", json=stock_edition_payload)

        # Then
        assert response.status_code == 200
        edited_stock = Stock.query.get(stock.id)
        assert edited_stock.beginningDatetime == stock.beginningDatetime
        assert edited_stock.bookingLimitDatetime == stock.bookingLimitDatetime
        assert edited_stock.price == stock.price
        assert edited_stock.numberOfTickets == stock.numberOfTickets
        assert edited_stock.educationalPriceDetail == "Nouvelle description du prix"

    def test_edit_shadow_stock_with_no_payload(self, client):
        # Given
        stock = offers_factories.EducationalEventShadowStockFactory(
            educationalPriceDetail="Détail du prix",
        )
        educational_factories.CollectiveOfferTemplateFactory(offerId=stock.offerId)
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=stock.offer.venue.managingOfferer)

        # When
        stock_edition_payload = {}

        client.with_session_auth("user@example.com")
        response = client.patch(f"/stocks/shadow/{humanize(stock.id)}", json=stock_edition_payload)

        # Then
        assert response.status_code == 200
        edited_stock = Stock.query.get(stock.id)
        assert edited_stock.beginningDatetime == stock.beginningDatetime
        assert edited_stock.bookingLimitDatetime == stock.bookingLimitDatetime
        assert edited_stock.price == stock.price
        assert edited_stock.numberOfTickets == stock.numberOfTickets
        assert edited_stock.educationalPriceDetail == "Détail du prix"


class Return403Test:
    def test_edit_educational_stocks_should_not_be_possible_when_user_not_linked_to_offerer(self, app, client):
        stock = offers_factories.EducationalEventShadowStockFactory(
            educationalPriceDetail="Détail du prix",
        )
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
        )
        educational_factories.CollectiveOfferTemplateFactory(offerId=stock.offerId)

        # When
        stock_edition_payload = {
            "educationalPriceDetail": "Nouvelle description du prix",
        }

        client.with_session_auth("user@example.com")
        response = client.patch(f"/stocks/shadow/{humanize(stock.id)}", json=stock_edition_payload)

        # Then
        assert response.status_code == 403
        assert response.json == {
            "global": ["Vous n'avez pas les droits d'accès suffisant pour accéder à cette information."]
        }


class Return400Test:
    def should_raise_error_when_educational_price_detail_length_is_greater_than_1000(self, app, client):
        # Given
        stock = offers_factories.EducationalEventShadowStockFactory(
            educationalPriceDetail="Détail du prix",
        )
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=stock.offer.venue.managingOfferer)
        educational_factories.CollectiveOfferTemplateFactory(offerId=stock.offerId)

        # When
        stock_edition_payload = {
            "educationalPriceDetail": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer sodales commodo tellus, at dictum odio vulputate nec. Donec iaculis rutrum nunc. Nam euismod, odio vel iaculis tincidunt, enim ante iaculis purus, ac vehicula ex lacus sit amet nisl. Aliquam et diam tellus. Curabitur in pharetra augue. Nunc scelerisque lectus non diam efficitur, eu porta neque vestibulum. Nullam elementum purus ac ligula viverra tincidunt. Etiam tincidunt metus nec nibh tempor tincidunt. Pellentesque ac ipsum purus. Duis vestibulum mollis nisi a vulputate. Nullam malesuada eros eu convallis rhoncus. Maecenas eleifend ex at posuere maximus. Suspendisse faucibus egestas dolor, sit amet dignissim odio condimentum vitae. Pellentesque ultricies eleifend nisi, quis pellentesque nisi faucibus finibus. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Suspendisse potenti. Aliquam convallis diam nisl, eget ullamcorper odio convallis ac. Ut quis nulla fringilla, commodo tellus ut.",
        }

        client.with_session_auth("user@example.com")
        response = client.patch(f"/stocks/shadow/{humanize(stock.id)}", json=stock_edition_payload)

        # Then
        assert response.status_code == 400
        assert response.json == {"educationalPriceDetail": ["Le détail du prix ne doit pas excéder 1000 caractères."]}

    def should_raise_error_when_offer_is_not_showcase(self, app, client):
        # Given
        stock = offers_factories.EducationalEventStockFactory(
            beginningDatetime=datetime(2021, 12, 18),
            price=1200,
            numberOfTickets=32,
            bookingLimitDatetime=datetime(2021, 12, 1),
            educationalPriceDetail="Détail du prix",
            offer__extraData={
                "students": [
                    "CAP - 1re ann\u00e9e",
                    "CAP - 2e ann\u00e9e",
                    "Lyc\u00e9e - Seconde",
                    "Lyc\u00e9e - Premi\u00e8re",
                ],
                "offerVenue": {
                    "addressType": "other",
                    "otherAddress": "1 rue des polissons, Paris 75017",
                    "venueId": "",
                },
                "contactEmail": "miss.rond@point.com",
                "contactPhone": "01010100101",
                "isShowcase": False,
            },
        )
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=stock.offer.venue.managingOfferer)
        educational_factories.CollectiveOfferTemplateFactory(offerId=stock.offerId)

        # When
        stock_edition_payload = {
            "educationalPriceDetail": "Nouvelle description du prix",
        }

        client.with_session_auth("user@example.com")
        response = client.patch(f"/stocks/shadow/{humanize(stock.id)}", json=stock_edition_payload)

        # Then
        assert response.status_code == 400
        assert response.json == {"code": "OFFER_IS_NOT_SHOWCASE"}
