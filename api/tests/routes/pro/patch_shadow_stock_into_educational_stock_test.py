import pytest

from pcapi.core.offers import factories as offer_factories
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
from pcapi.utils.human_ids import dehumanize
from pcapi.utils.human_ids import humanize


pytestmark = pytest.mark.usefixtures("db_session")


class Return200Test:
    def test_create_valid_stock_for_educational_offer(self, app, client):
        # Given
        stock = offer_factories.EducationalEventStockFactory(
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
                "isShowcase": True,
            },
        )
        offer_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=stock.offer.venue.managingOfferer,
        )

        # When
        stock_payload = {
            "offerId": humanize(stock.offer.id),
            "beginningDatetime": "2022-01-17T22:00:00Z",
            "bookingLimitDatetime": "2021-12-31T20:00:00Z",
            "totalPrice": 1500,
            "numberOfTickets": 38,
            "educationalPriceDetail": "Détail du prix",
        }

        client.with_session_auth("user@example.com")
        response = client.patch(f"/stocks/shadow-to-educational/{humanize(stock.id)}", json=stock_payload)

        # Then
        assert response.status_code == 201
        response_dict = response.json
        created_stock = Stock.query.get(dehumanize(response_dict["id"]))
        shadow_stock = Stock.query.get(stock.id)
        assert stock.offer.id == created_stock.offerId
        assert shadow_stock.isSoftDeleted == True
        assert created_stock.price == 1500
        assert created_stock.educationalPriceDetail == "Détail du prix"
        updated_offer = Offer.query.get(stock.offer.id)
        assert updated_offer.extraData["isShowcase"] == False


class Return400Test:
    def test_create_educational_stocks_should_not_be_available_if_user_not_linked_to_offerer(self, app, client):
        # Given
        stock = offer_factories.EducationalEventStockFactory(
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
                "isShowcase": True,
            },
        )
        offer_factories.UserOffererFactory(
            user__email="user@example.com",
        )

        # When
        stock_payload = {
            "offerId": humanize(stock.offer.id),
            "beginningDatetime": "2022-01-17T22:00:00Z",
            "bookingLimitDatetime": "2021-12-31T20:00:00Z",
            "totalPrice": 1500,
            "numberOfTickets": 38,
        }

        client.with_session_auth("user@example.com")
        response = client.patch(f"/stocks/shadow-to-educational/{humanize(stock.id)}", json=stock_payload)

        # Then
        assert response.status_code == 403
        assert response.json == {
            "global": ["Vous n'avez pas les droits d'accès suffisant pour accéder à cette information."]
        }

    def should_not_allow_number_of_tickets_to_be_negative_on_creation(self, app, client):
        # Given
        stock = offer_factories.EducationalEventStockFactory(
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
                "isShowcase": True,
            },
        )
        offer_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=stock.offer.venue.managingOfferer,
        )

        # When
        stock_payload = {
            "offerId": humanize(stock.offer.id),
            "beginningDatetime": "2022-01-17T22:00:00Z",
            "bookingLimitDatetime": "2021-12-31T20:00:00Z",
            "totalPrice": 1500,
            "numberOfTickets": -1,
        }

        client.with_session_auth("user@example.com")
        response = client.patch(f"/stocks/shadow-to-educational/{humanize(stock.id)}", json=stock_payload)

        # Then
        assert response.status_code == 400
        assert response.json == {"numberOfTickets": ["Le nombre de places ne peut pas être négatif."]}

    def should_not_allow_price_to_be_negative_on_creation(self, app, client):
        # Given
        stock = offer_factories.EducationalEventStockFactory(
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
                "isShowcase": True,
            },
        )
        offer_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=stock.offer.venue.managingOfferer,
        )

        # When
        stock_payload = {
            "offerId": humanize(stock.offer.id),
            "beginningDatetime": "2022-01-17T22:00:00Z",
            "bookingLimitDatetime": "2021-12-31T20:00:00Z",
            "totalPrice": -1500,
            "numberOfTickets": 30,
        }

        client.with_session_auth("user@example.com")
        response = client.patch(f"/stocks/shadow-to-educational/{humanize(stock.id)}", json=stock_payload)

        # Then
        assert response.status_code == 400
        assert response.json == {"totalPrice": ["Le prix ne peut pas être négatif."]}

    def should_not_accept_payload_with_bookingLimitDatetime_after_beginningDatetime(self, app, client):
        # Given
        stock = offer_factories.EducationalEventStockFactory(
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
                "isShowcase": True,
            },
        )
        offer_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=stock.offer.venue.managingOfferer,
        )

        # When
        stock_payload = {
            "offerId": humanize(stock.offer.id),
            "beginningDatetime": "2022-01-17T22:00:00Z",
            "bookingLimitDatetime": "2022-01-18T20:00:00Z",
            "totalPrice": 1500,
            "numberOfTickets": 30,
        }

        client.with_session_auth("user@example.com")
        response = client.patch(f"/stocks/shadow-to-educational/{humanize(stock.id)}", json=stock_payload)

        # Then
        assert response.status_code == 400
        assert response.json == {
            "bookingLimitDatetime": [
                "La date limite de réservation ne peut être postérieure à la date de début de l'évènement"
            ]
        }

    def should_not_accept_payload_with_price_details_with_more_than_1000_caracters(self, app, client):
        # Given
        stock = offer_factories.EducationalEventStockFactory(
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
                "isShowcase": True,
            },
        )
        offer_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=stock.offer.venue.managingOfferer,
        )

        # When
        stock_payload = {
            "offerId": humanize(stock.offer.id),
            "beginningDatetime": "2022-01-17T22:00:00Z",
            "bookingLimitDatetime": "2021-12-31T20:00:00Z",
            "totalPrice": 1500,
            "numberOfTickets": 38,
            "educationalPriceDetail": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer sodales commodo tellus, at dictum odio vulputate nec. Donec iaculis rutrum nunc. Nam euismod, odio vel iaculis tincidunt, enim ante iaculis purus, ac vehicula ex lacus sit amet nisl. Aliquam et diam tellus. Curabitur in pharetra augue. Nunc scelerisque lectus non diam efficitur, eu porta neque vestibulum. Nullam elementum purus ac ligula viverra tincidunt. Etiam tincidunt metus nec nibh tempor tincidunt. Pellentesque ac ipsum purus. Duis vestibulum mollis nisi a vulputate. Nullam malesuada eros eu convallis rhoncus. Maecenas eleifend ex at posuere maximus. Suspendisse faucibus egestas dolor, sit amet dignissim odio condimentum vitae. Pellentesque ultricies eleifend nisi, quis pellentesque nisi faucibus finibus. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Suspendisse potenti. Aliquam convallis diam nisl, eget ullamcorper odio convallis ac. Ut quis nulla fringilla, commodo tellus ut.",
        }

        client.with_session_auth("user@example.com")
        response = client.patch(f"/stocks/shadow-to-educational/{humanize(stock.id)}", json=stock_payload)

        # Then
        assert response.status_code == 400
        assert response.json == {"educationalPriceDetail": ["Le détail du prix ne doit pas excéder 1000 caractères."]}

    def should_not_allow_stock_transformation_on_a_non_showcase_offer(self, client):
        # Given
        stock = offer_factories.EducationalEventStockFactory(
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
        offer_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=stock.offer.venue.managingOfferer,
        )

        # When
        stock_payload = {
            "offerId": humanize(stock.offer.id),
            "beginningDatetime": "2022-01-17T22:00:00Z",
            "bookingLimitDatetime": "2021-12-31T20:00:00Z",
            "totalPrice": 1500,
            "numberOfTickets": 38,
            "educationalPriceDetail": "Détail du prix",
        }

        client.with_session_auth("user@example.com")
        response = client.patch(f"/stocks/shadow-to-educational/{humanize(stock.id)}", json=stock_payload)

        # Then
        assert response.status_code == 400
        assert response.json == {"code": "OFFER_IS_NOT_SHOWCASE"}
