from freezegun import freeze_time
import pytest

import pcapi.core.educational.factories as educational_factories
import pcapi.core.educational.models as educational_models
import pcapi.core.offerers.factories as offerers_factories
from pcapi.utils.human_ids import dehumanize
from pcapi.utils.human_ids import humanize


pytestmark = pytest.mark.usefixtures("db_session")


class Return200Test:
    @freeze_time("2020-11-17 15:00:00")
    def test_create_valid_stock_for_collective_offer(self, client):
        # Given
        domain = educational_factories.EducationalDomainFactory(name="Yet Another Domain")
        offer = educational_factories.CollectiveOfferTemplateFactory(educational_domains=[domain])
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        stock_payload = {
            "offerId": humanize(offer.id),
            "beginningDatetime": "2022-01-17T22:00:00Z",
            "bookingLimitDatetime": "2021-12-31T20:00:00Z",
            "totalPrice": 1500,
            "numberOfTickets": 38,
            "educationalPriceDetail": "Détail du prix",
        }

        client.with_session_auth("user@example.com")
        response = client.patch(
            f"/collective/offers-template/{humanize(offer.id)}/to-collective-offer/", json=stock_payload
        )

        # Then
        assert response.status_code == 201
        response_dict = response.json
        created_stock = educational_models.CollectiveStock.query.get(dehumanize(response_dict["id"]))
        collective_offer = educational_models.CollectiveOffer.query.filter_by(
            id=dehumanize(response_dict["offerId"])
        ).one()
        assert collective_offer is not None
        assert collective_offer.domains == [domain]
        assert educational_models.CollectiveOfferTemplate.query.filter_by(id=offer.id).one_or_none() is None
        assert created_stock.price == 1500
        assert created_stock.priceDetail == "Détail du prix"


class Return400Test:
    @freeze_time("2020-11-17 15:00:00")
    def test_create_educational_stocks_should_not_be_available_if_user_not_linked_to_offerer(self, app, client):
        # Given
        offer = educational_factories.CollectiveOfferTemplateFactory()
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
        )

        # When
        stock_payload = {
            "offerId": humanize(offer.id),
            "beginningDatetime": "2022-01-17T22:00:00Z",
            "bookingLimitDatetime": "2021-12-31T20:00:00Z",
            "totalPrice": 1500,
            "numberOfTickets": 38,
        }

        client.with_session_auth("user@example.com")
        response = client.patch(
            f"/collective/offers-template/{humanize(offer.id)}/to-collective-offer/", json=stock_payload
        )

        # Then
        assert response.status_code == 403
        assert response.json == {
            "global": ["Vous n'avez pas les droits d'accès suffisant pour accéder à cette information."]
        }
        assert educational_models.CollectiveOfferTemplate.query.filter_by(id=offer.id).one_or_none()

    @freeze_time("2020-11-17 15:00:00")
    def should_not_allow_number_of_tickets_to_be_negative_on_creation(self, app, client):
        # Given
        offer = educational_factories.CollectiveOfferTemplateFactory()
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        stock_payload = {
            "offerId": humanize(offer.id),
            "beginningDatetime": "2022-01-17T22:00:00Z",
            "bookingLimitDatetime": "2021-12-31T20:00:00Z",
            "totalPrice": 1500,
            "numberOfTickets": -1,
        }

        client.with_session_auth("user@example.com")
        response = client.patch(
            f"/collective/offers-template/{humanize(offer.id)}/to-collective-offer/", json=stock_payload
        )

        # Then
        assert response.status_code == 400
        assert response.json == {"numberOfTickets": ["Le nombre de places ne peut pas être négatif."]}
        assert educational_models.CollectiveOfferTemplate.query.filter_by(id=offer.id).one_or_none()

    @freeze_time("2020-11-17 15:00:00")
    def should_not_allow_price_to_be_negative_on_creation(self, app, client):
        # Given
        offer = educational_factories.CollectiveOfferTemplateFactory()
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        stock_payload = {
            "offerId": humanize(offer.id),
            "beginningDatetime": "2022-01-17T22:00:00Z",
            "bookingLimitDatetime": "2021-12-31T20:00:00Z",
            "totalPrice": -1500,
            "numberOfTickets": 30,
        }

        client.with_session_auth("user@example.com")
        response = client.patch(
            f"/collective/offers-template/{humanize(offer.id)}/to-collective-offer/", json=stock_payload
        )

        # Then
        assert response.status_code == 400
        assert response.json == {"totalPrice": ["Le prix ne peut pas être négatif."]}
        assert educational_models.CollectiveOfferTemplate.query.filter_by(id=offer.id).one_or_none()

    @freeze_time("2020-11-17 15:00:00")
    def should_not_accept_payload_with_bookingLimitDatetime_after_beginningDatetime(self, app, client):
        # Given
        offer = educational_factories.CollectiveOfferTemplateFactory()
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        stock_payload = {
            "offerId": humanize(offer.id),
            "beginningDatetime": "2022-01-17T22:00:00Z",
            "bookingLimitDatetime": "2022-01-18T20:00:00Z",
            "totalPrice": 1500,
            "numberOfTickets": 30,
        }

        client.with_session_auth("user@example.com")
        response = client.patch(
            f"/collective/offers-template/{humanize(offer.id)}/to-collective-offer/", json=stock_payload
        )

        # Then
        assert response.status_code == 400
        assert response.json == {
            "bookingLimitDatetime": [
                "La date limite de réservation ne peut être postérieure à la date de début de l'évènement"
            ]
        }
        assert educational_models.CollectiveOfferTemplate.query.filter_by(id=offer.id).one_or_none()

    @freeze_time("2020-11-17 15:00:00")
    def should_not_accept_payload_with_price_details_with_more_than_1000_caracters(self, app, client):
        # Given
        offer = educational_factories.CollectiveOfferTemplateFactory()
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        stock_payload = {
            "offerId": humanize(offer.id),
            "beginningDatetime": "2022-01-17T22:00:00Z",
            "bookingLimitDatetime": "2021-12-31T20:00:00Z",
            "totalPrice": 1500,
            "numberOfTickets": 38,
            "educationalPriceDetail": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer sodales commodo tellus, at dictum odio vulputate nec. Donec iaculis rutrum nunc. Nam euismod, odio vel iaculis tincidunt, enim ante iaculis purus, ac vehicula ex lacus sit amet nisl. Aliquam et diam tellus. Curabitur in pharetra augue. Nunc scelerisque lectus non diam efficitur, eu porta neque vestibulum. Nullam elementum purus ac ligula viverra tincidunt. Etiam tincidunt metus nec nibh tempor tincidunt. Pellentesque ac ipsum purus. Duis vestibulum mollis nisi a vulputate. Nullam malesuada eros eu convallis rhoncus. Maecenas eleifend ex at posuere maximus. Suspendisse faucibus egestas dolor, sit amet dignissim odio condimentum vitae. Pellentesque ultricies eleifend nisi, quis pellentesque nisi faucibus finibus. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Suspendisse potenti. Aliquam convallis diam nisl, eget ullamcorper odio convallis ac. Ut quis nulla fringilla, commodo tellus ut.",
        }

        client.with_session_auth("user@example.com")
        response = client.patch(
            f"/collective/offers-template/{humanize(offer.id)}/to-collective-offer/", json=stock_payload
        )

        # Then
        assert response.status_code == 400
        assert response.json == {"educationalPriceDetail": ["Le détail du prix ne doit pas excéder 1000 caractères."]}
        assert educational_models.CollectiveOfferTemplate.query.filter_by(id=offer.id).one_or_none()
