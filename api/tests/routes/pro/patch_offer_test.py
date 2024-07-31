from datetime import datetime
from decimal import Decimal
from unittest.mock import patch

import pytest

from pcapi.connectors.api_adresse import AddressInfo
import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.categories import subcategories_v2 as subcategories
import pcapi.core.mails.testing as mails_testing
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import OfferValidationStatus
from pcapi.core.offers.models import WithdrawalTypeEnum
import pcapi.core.users.factories as users_factories
from pcapi.utils.date import format_into_utc_date


pytestmark = pytest.mark.usefixtures("db_session")


class Returns200Test:
    def test_patch_offer(self, client):
        # Given
        user_offerer = offerers_factories.UserOffererFactory(user__email="user@example.com")
        venue = offerers_factories.VirtualVenueFactory(managingOfferer=user_offerer.offerer)
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.ABO_PLATEFORME_VIDEO.id,
            venue=venue,
            name="New name",
            url="test@test.com",
            description="description",
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
        assert response.json["id"] == offer.id
        assert response.json["venue"]["id"] == offer.venue.id

        updated_offer = Offer.query.get(offer.id)
        assert updated_offer.name == "New name"
        assert updated_offer.externalTicketOfficeUrl == "http://example.net"
        assert updated_offer.mentalDisabilityCompliant
        assert updated_offer.subcategoryId == subcategories.ABO_PLATEFORME_VIDEO.id
        assert not updated_offer.product

    @pytest.mark.parametrize(
        "label, offer_has_oa, address_update_exist",
        [
            ["label", True, True],
            ["label", False, True],
            ["label", False, False],
            ["label", True, False],
            [None, True, True],
            [None, False, True],
            [None, False, False],
            [None, True, False],
        ],
    )
    @patch("pcapi.connectors.api_adresse.get_address")
    def test_patch_offer_with_address(self, get_address_mock, label, offer_has_oa, address_update_exist, client):
        # Given
        user_offerer = offerers_factories.UserOffererFactory(user__email="user@example.com")
        venue = offerers_factories.VirtualVenueFactory(managingOfferer=user_offerer.offerer)
        oa = None
        if offer_has_oa:
            oa = offerers_factories.OffererAddressFactory(offerer=user_offerer.offerer)
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.ABO_PLATEFORME_VIDEO.id,
            venue=venue,
            name="New name",
            url="test@test.com",
            description="description",
            offererAddress=oa,
        )
        if address_update_exist:
            existant_oa = offerers_factories.OffererAddressFactory(
                offerer=user_offerer.offerer,
                label=label,
                address__street="1 rue de la paix",
                address__city="Paris",
                address__banId="75102_7560_00001",
                address__postalCode="75102",
                address__latitude=48.8566,
                address__longitude=2.3522,
            )

        # When
        data = {
            "name": "New name",
            "externalTicketOfficeUrl": "http://example.net",
            "mentalDisabilityCompliant": True,
            "address": {
                "street": "1 rue de la paix",
                "city": "Paris",
                "postalCode": "75102",
                "latitude": 48.8566,
                "longitude": 2.3522,
                "label": label,
            },
        }
        get_address_mock.return_value = AddressInfo(
            street="1 rue de la paix",
            city="Paris",
            citycode="75102",
            postcode="75102",
            latitude=48.8566,
            longitude=2.3522,
            score=0.9,
            id="75102_7560_00001",
            label=label if label else "",
        )
        response = client.with_session_auth("user@example.com").patch(f"/offers/{offer.id}", json=data)
        assert response.status_code == 200
        assert response.json["id"] == offer.id
        updated_offer = Offer.query.get(offer.id)
        address = updated_offer.offererAddress.address
        if address_update_exist:
            assert updated_offer.offererAddress == existant_oa
        assert updated_offer.offererAddress.label == label
        assert address.street == "1 rue de la paix"
        assert address.city == "Paris"
        assert address.postalCode == "75102"
        assert address.latitude == Decimal("48.85660")
        assert address.longitude == Decimal("2.3522")

    def test_withdrawal_can_be_updated(self, client):
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.CONCERT.id,
            bookingContact="booking@conta.ct",
            name="New name",
        )
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

    def test_withdrawal_update_send_email_to_each_related_booker(self, client):
        # given
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.CONCERT.id,
            bookingContact="booking@conta.ct",
            name="New name",
        )
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

        outbox = sorted(mails_testing.outbox, key=lambda mail: mail["params"]["OFFER_TOKEN"])
        bookings.sort(key=lambda b: b.activationCode.code if getattr(b, "activationCode") else b.token)
        assert [mail["To"] for mail in outbox] == [b.user.email for b in bookings]
        assert [mail["params"]["USER_FIRST_NAME"] for mail in outbox] == [b.user.firstName for b in bookings]
        assert [mail["params"]["OFFER_NAME"] for mail in outbox] == [b.stock.offer.name for b in bookings]
        assert [mail["params"]["OFFER_TOKEN"] for mail in outbox] == [
            b.activationCode.code if b.activationCode else b.token for b in bookings
        ]
        assert [mail["params"]["OFFER_WITHDRAWAL_DELAY"] for mail in outbox] == [None] * 3
        assert [mail["params"]["OFFER_WITHDRAWAL_DETAILS"] for mail in outbox] == ["conditions de retrait"] * 3
        assert [mail["params"]["OFFER_WITHDRAWAL_TYPE"] for mail in outbox] == ["no_ticket"] * 3
        assert [mail["params"]["OFFERER_NAME"] for mail in outbox] == [offer.venue.managingOfferer.name] * 3
        assert [mail["params"]["VENUE_ADDRESS"] for mail in outbox] == [
            f"{offer.venue.street} {offer.venue.postalCode} {offer.venue.city}"
        ] * 3

    def test_withdrawal_update_does_not_send_email_if_not_specified_so(self, client):
        # given
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.CONCERT.id,
            bookingContact="booking@conta.ct",
            name="New name",
        )
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
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.CARTE_MUSEE.id,
            name="New name",
            url="test@test.com",
            description="description",
        )
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        data = {
            "dateCreated": format_into_utc_date(datetime(2019, 1, 1)),
            "dateModifiedAtLastProvider": format_into_utc_date(datetime(2019, 1, 1)),
            "id": 1,
            "idAtProviders": 1,
            "lastProviderId": 1,
            "thumbCount": 2,
            "subcategoryId": subcategories.LIVRE_PAPIER,
        }
        response = client.with_session_auth("user@example.com").patch(f"offers/{offer.id}", json=data)

        # Then
        assert response.status_code == 400
        assert response.json["lastProviderId"] == ["Vous ne pouvez pas changer cette information"]
        forbidden_keys = {
            "dateCreated",
            "dateModifiedAtLastProvider",
            "id",
            "idAtProviders",
            "lastProviderId",
            "thumbCount",
            "subcategoryId",
        }
        for key in forbidden_keys:
            assert key in response.json

    def should_fail_when_url_has_no_scheme(self, app, client):
        # Given
        virtual_venue = offerers_factories.VirtualVenueFactory()
        offer = offers_factories.OfferFactory(
            venue=virtual_venue,
            subcategoryId=subcategories.CARTE_MUSEE.id,
            name="New name",
            url="test@test.com",
            description="description",
        )
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
        offer = offers_factories.OfferFactory(
            venue=virtual_venue,
            subcategoryId=subcategories.CARTE_MUSEE.id,
            name="New name",
            url="test@test.com",
            description="description",
        )
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
        offer = offers_factories.OfferFactory(
            venue=virtual_venue,
            name="New name",
            subcategoryId=subcategories.CARTE_MUSEE.id,
            url="test@test.com",
            description="description",
        )
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
        offer = offers_factories.OfferFactory(
            venue=virtual_venue,
            name="New name",
            subcategoryId=subcategories.CARTE_MUSEE.id,
            url="test@test.com",
            description="description",
        )
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
        offer = offers_factories.OfferFactory(
            validation=OfferValidationStatus.PENDING,
            name="New name",
            subcategoryId=subcategories.CARTE_MUSEE.id,
            url="test@test.com",
            description="description",
        )
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

    def test_reuse_unchanged_withdrawal(self, client):
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.CONCERT.id,
            withdrawalType=WithdrawalTypeEnum.BY_EMAIL,
            withdrawalDelay=60 * 15,
            bookingContact="booking@conta.ct",
            name="New name",
            url="test@test.com",
            description="description",
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

    def test_booking_contact_is_checked_when_changed(self, client):
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.CONCERT.id,
            withdrawalType=WithdrawalTypeEnum.BY_EMAIL,
            withdrawalDelay=60 * 15,
            bookingContact="booking@conta.ct",
            name="New name",
            url="test@test.com",
            description="description",
        )
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        data = {"bookingContact": None}
        response = client.with_session_auth("user@example.com").patch(f"offers/{offer.id}", json=data)

        assert response.status_code == 400
        assert response.json["offer"] == [
            "Une offre qui a un ticket retirable doit avoir l'email du contact de réservation"
        ]


class Returns403Test:
    def when_user_is_not_attached_to_offerer(self, app, client):
        # Given
        offer = offers_factories.OfferFactory(
            name="Old name",
            subcategoryId=subcategories.CARTE_MUSEE.id,
            url="test@test.com",
            description="description",
        )
        offerers_factories.UserOffererFactory(user__email="user@example.com")

        # When
        data = {"name": "New name"}
        response = client.with_session_auth("user@example.com").patch(f"/offers/{offer.id}", json=data)

        # Then
        assert response.status_code == 403
        assert response.json["global"] == [
            "Vous n'avez pas les droits d'accès suffisants pour accéder à cette information."
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
