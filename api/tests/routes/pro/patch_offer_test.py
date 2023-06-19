from datetime import datetime

import pytest

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.categories import subcategories
import pcapi.core.mails.testing as mails_testing
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import OfferValidationStatus
from pcapi.core.offers.models import WithdrawalTypeEnum
from pcapi.core.testing import override_features
import pcapi.core.users.factories as users_factories
from pcapi.routes.serialization import serialize


pytestmark = pytest.mark.usefixtures("db_session")


class Returns200Test:
    def test_patch_offer(self, app, client):
        # Given
        user_offerer = offerers_factories.UserOffererFactory(user__email="user@example.com")
        product = offers_factories.ProductFactory(owningOfferer=user_offerer.offerer)
        offer = offers_factories.OfferFactory(
            subcategoryId="SEANCE_CINE", venue__managingOfferer=user_offerer.offerer, product=product
        )

        # When
        data = {
            "name": "New name",
            "externalTicketOfficeUrl": "http://example.net",
            "mentalDisabilityCompliant": True,
        }
        response = client.with_session_auth("user@example.com").patch(f"/offers/{offer.id}", json=data)

        # Then
        assert response.status_code == 200
        assert response.json["nonHumanizedId"] == offer.id
        assert response.json["venue"]["nonHumanizedId"] == offer.venue.id

        updated_offer = Offer.query.get(offer.id)
        assert updated_offer.name == "New name"
        assert updated_offer.externalTicketOfficeUrl == "http://example.net"
        assert updated_offer.mentalDisabilityCompliant
        assert updated_offer.subcategoryId == "SEANCE_CINE"
        assert updated_offer.product.name == "New name"

    def test_withdrawal_can_be_updated(self, client):
        offer = offers_factories.OfferFactory(subcategoryId=subcategories.CONCERT.id)
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        data = {
            "withdrawalDetails": "Veuillez récuperer vos billets à l'accueil :)",
            "withdrawalType": "no_ticket",
        }
        response = client.with_session_auth("user@example.com").patch(f"/offers/{offer.id}", json=data)

        assert response.status_code == 200
        offer = Offer.query.get(offer.id)
        assert offer.withdrawalDetails == "Veuillez récuperer vos billets à l'accueil :)"
        assert offer.withdrawalType == WithdrawalTypeEnum.NO_TICKET

    @override_features(WIP_ENABLE_WITHDRAWAL_UPDATED_MAIL=True)
    def test_withdrawal_update_send_email_to_each_related_booker(self, client):
        # given
        offer = offers_factories.OfferFactory(subcategoryId=subcategories.CONCERT.id)
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)
        stock = offers_factories.StockFactory(offer=offer)
        bookings = [bookings_factories.BookingFactory(stock=stock) for _ in range(3)]

        data = {
            "withdrawalDetails": "conditions de retrait",
            "withdrawalType": "no_ticket",
            "shouldSendMail": "true",
        }

        # when
        response = client.with_session_auth("user@example.com").patch(f"/offers/{offer.id}", json=data)

        # then
        assert response.status_code == 200
        assert len(mails_testing.outbox) == 3

        outbox = sorted(mails_testing.outbox, key=lambda mail: mail.sent_data["params"]["OFFER_TOKEN"])
        bookings.sort(key=lambda b: b.activationCode.code if getattr(b, "activationCode") else b.token)
        assert [mail.sent_data["To"] for mail in outbox] == [b.user.email for b in bookings]
        assert [mail.sent_data["params"]["USER_FIRST_NAME"] for mail in outbox] == [b.user.firstName for b in bookings]
        assert [mail.sent_data["params"]["OFFER_NAME"] for mail in outbox] == [b.stock.offer.name for b in bookings]
        assert [mail.sent_data["params"]["OFFER_TOKEN"] for mail in outbox] == [
            b.activationCode.code if b.activationCode else b.token for b in bookings
        ]
        assert [mail.sent_data["params"]["OFFER_WITHDRAWAL_DELAY"] for mail in outbox] == [None] * 3
        assert [mail.sent_data["params"]["OFFER_WITHDRAWAL_DETAILS"] for mail in outbox] == [
            "conditions de retrait"
        ] * 3
        assert [mail.sent_data["params"]["OFFER_WITHDRAWAL_TYPE"] for mail in outbox] == ["no_ticket"] * 3
        assert [mail.sent_data["params"]["OFFERER_NAME"] for mail in outbox] == [offer.venue.managingOfferer.name] * 3
        assert [mail.sent_data["params"]["VENUE_ADDRESS"] for mail in outbox] == [
            f"{offer.venue.address} {offer.venue.postalCode} {offer.venue.city}"
        ] * 3

    @override_features(WIP_ENABLE_WITHDRAWAL_UPDATED_MAIL=True)
    def test_withdrawal_update_does_not_send_email_if_not_specified_so(self, client):
        # given
        offer = offers_factories.OfferFactory(subcategoryId=subcategories.CONCERT.id)
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)
        stock = offers_factories.StockFactory(offer=offer)
        _ = [bookings_factories.BookingFactory(stock=stock) for _ in range(3)]

        data = {
            "withdrawalDetails": "conditions de retrait",
            "withdrawalType": "no_ticket",
            "shouldSendMail": "false",
        }

        # when
        response = client.with_session_auth("user@example.com").patch(f"/offers/{offer.id}", json=data)

        # then
        assert response.status_code == 200
        assert len(mails_testing.outbox) == 0


class Returns400Test:
    def when_trying_to_patch_forbidden_attributes(self, app, client):
        # Given
        offer = offers_factories.OfferFactory()
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        data = {
            "dateCreated": serialize(datetime(2019, 1, 1)),
            "dateModifiedAtLastProvider": serialize(datetime(2019, 1, 1)),
            "id": 1,
            "idAtProviders": 1,
            "lastProviderId": 1,
            "owningOffererId": "AA",
            "thumbCount": 2,
            "subcategoryId": subcategories.LIVRE_PAPIER,
        }
        response = client.with_session_auth("user@example.com").patch(f"offers/{offer.id}", json=data)

        # Then
        assert response.status_code == 400
        assert response.json["owningOffererId"] == ["Vous ne pouvez pas changer cette information"]
        forbidden_keys = {
            "dateCreated",
            "dateModifiedAtLastProvider",
            "id",
            "idAtProviders",
            "lastProviderId",
            "owningOffererId",
            "thumbCount",
            "subcategoryId",
        }
        for key in forbidden_keys:
            assert key in response.json

    def should_fail_when_url_has_no_scheme(self, app, client):
        # Given
        virtual_venue = offerers_factories.VirtualVenueFactory()
        offer = offers_factories.OfferFactory(venue=virtual_venue)
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        data = {
            "name": "Les lièvres pas malins",
            "url": "missing.something",
        }
        response = client.with_session_auth("user@example.com").patch(f"offers/{offer.id}", json=data)

        # Then
        assert response.status_code == 400
        assert response.json["url"] == ['L\'URL doit commencer par "http://" ou "https://"']

    def should_fail_when_externalTicketOfficeUrl_has_no_scheme(self, app, client):
        # Given
        virtual_venue = offerers_factories.VirtualVenueFactory()
        offer = offers_factories.OfferFactory(venue=virtual_venue)
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        data = {
            "name": "Les lièvres pas malins",
            "externalTicketOfficeUrl": "missing.something",
        }
        response = client.with_session_auth("user@example.com").patch(f"offers/{offer.id}", json=data)

        # Then
        assert response.status_code == 400
        assert response.json["externalTicketOfficeUrl"] == ['L\'URL doit commencer par "http://" ou "https://"']

    def should_fail_when_url_has_no_host(self, app, client):
        # Given
        virtual_venue = offerers_factories.VirtualVenueFactory()
        offer = offers_factories.OfferFactory(venue=virtual_venue)
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        data = {
            "name": "Les lièvres pas malins",
            "url": "https://missing",
        }
        response = client.with_session_auth("user@example.com").patch(f"offers/{offer.id}", json=data)

        # Then
        assert response.status_code == 400
        assert response.json["url"] == ['L\'URL doit terminer par une extension (ex. ".fr")']

    def should_fail_when_externalTicketOfficeUrl_has_no_host(self, app, client):
        # Given
        virtual_venue = offerers_factories.VirtualVenueFactory()
        offer = offers_factories.OfferFactory(venue=virtual_venue)
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        data = {
            "name": "Les lièvres pas malins",
            "externalTicketOfficeUrl": "https://missing",
        }
        response = client.with_session_auth("user@example.com").patch(f"offers/{offer.id}", json=data)

        # Then
        assert response.status_code == 400
        assert response.json["externalTicketOfficeUrl"] == ['L\'URL doit terminer par une extension (ex. ".fr")']

    def test_patch_non_approved_offer_fails(self, app, client):
        offer = offers_factories.OfferFactory(validation=OfferValidationStatus.PENDING)
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        data = {
            "visualDisabilityCompliant": True,
        }
        response = client.with_session_auth("user@example.com").patch(f"/offers/{offer.id}", json=data)

        assert response.status_code == 400
        assert response.json["global"] == ["Les offres refusées ou en attente de validation ne sont pas modifiables"]

    def test_withdrawal_is_checked_when_changed(self, client):
        offer = offers_factories.OfferFactory(subcategoryId=subcategories.JEU_EN_LIGNE.id)
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        data = {
            "withdrawalType": "no_ticket",
        }
        response = client.with_session_auth("user@example.com").patch(f"offers/{offer.id}", json=data)

        assert response.status_code == 400
        assert response.json["offer"] == [
            "Une offre qui n'a pas de ticket retirable ne peut pas avoir un type de retrait renseigné"
        ]

    def test_reuse_unchanged_withdrawal(self, client):
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.CONCERT.id, withdrawalType=WithdrawalTypeEnum.BY_EMAIL, withdrawalDelay=60 * 15
        )
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        data = {
            "withdrawalType": "no_ticket",
        }
        response = client.with_session_auth("user@example.com").patch(f"offers/{offer.id}", json=data)

        assert response.status_code == 400
        assert response.json["offer"] == [
            "Il ne peut pas y avoir de délai de retrait lorsqu'il s'agit d'un évènement sans ticket"
        ]


class Returns403Test:
    def when_user_is_not_attached_to_offerer(self, app, client):
        # Given
        offer = offers_factories.OfferFactory(name="Old name")
        offerers_factories.UserOffererFactory(user__email="user@example.com")

        # When
        data = {"name": "New name"}
        response = client.with_session_auth("user@example.com").patch(f"/offers/{offer.id}", json=data)

        # Then
        assert response.status_code == 403
        assert response.json["global"] == [
            "Vous n'avez pas les droits d'accès suffisant pour accéder à cette information."
        ]
        assert Offer.query.get(offer.id).name == "Old name"


class Returns404Test:
    def test_returns_404_if_offer_does_not_exist(self, app, client):
        # given
        users_factories.UserFactory(email="user@example.com")

        # when
        response = client.with_session_auth("user@example.com").patch("/offers/12345", json={})

        # then
        assert response.status_code == 404
