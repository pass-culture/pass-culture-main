from decimal import Decimal

import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.users.factories as users_factories
from pcapi.core.categories import subcategories
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import WithdrawalTypeEnum
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationStatus


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    def test_created_offer_should_be_inactive(self, client):
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        # When
        data = {
            "venueId": venue.id,
            "name": "Celeste",
            "subcategoryId": subcategories.LIVRE_PAPIER.id,
            "mentalDisabilityCompliant": True,
            "audioDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
            "motorDisabilityCompliant": False,
        }
        response = client.with_session_auth("user@example.com").post("/offers", json=data)
        offer_id = response.json["id"]
        offer = db.session.query(Offer).get(offer_id)
        response_dict = response.json
        assert offer.isActive is False
        assert response_dict["venue"]["id"] == offer.venue.id
        assert response_dict["name"] == "Celeste"
        assert response_dict["id"] == offer.id
        assert not offer.product

    def test_create_event_offer(self, client):
        # Given
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        # When
        data = {
            "venueId": venue.id,
            "bookingContact": "offer@example.com",
            "bookingEmail": "offer@example.com",
            "durationMinutes": 60,
            "name": "La pièce de théâtre",
            "subcategoryId": subcategories.SPECTACLE_REPRESENTATION.id,
            "withdrawalType": "no_ticket",
            "extraData": {"toto": "text", "showType": 200, "showSubType": 201},
            "externalTicketOfficeUrl": "http://example.net",
            "audioDisabilityCompliant": False,
            "mentalDisabilityCompliant": True,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
        }
        response = client.with_session_auth("user@example.com").post("/offers", json=data)

        # Then
        assert response.status_code == 201
        offer_id = response.json["id"]
        offer = db.session.query(Offer).get(offer_id)
        assert offer.bookingContact == "offer@example.com"
        assert offer.bookingEmail == "offer@example.com"
        assert offer.publicationDate is None
        assert offer.subcategoryId == subcategories.SPECTACLE_REPRESENTATION.id
        assert offer.extraData == {"showType": 200, "showSubType": 201}
        assert offer.externalTicketOfficeUrl == "http://example.net"
        assert offer.venue == venue
        assert offer.motorDisabilityCompliant is False
        assert offer.visualDisabilityCompliant is False
        assert offer.audioDisabilityCompliant is False
        assert offer.mentalDisabilityCompliant is True
        assert offer.validation == OfferValidationStatus.DRAFT
        assert offer.isActive is False
        assert offer.offererAddress.id == venue.offererAddressId
        assert not offer.futureOffer
        assert offer.offererAddress == venue.offererAddress

    @pytest.mark.parametrize("oa_label", [None, "some place"])
    def test_create_event_offer_with_existing_offerer_address(self, oa_label, client):
        # Given
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        # Match the BAN API response
        offerer_address = offerers_factories.OffererAddressFactory(
            offerer=offerer,
            address__banId="75101_9575_00003",
            address__city="Paris",
            address__departmentCode="75",
            address__inseeCode="75056",
            address__isManualEdition=False,
            address__latitude=Decimal("48.87171"),
            address__longitude=Decimal("2.308289"),
            address__postalCode="75001",
            address__street="3 Rue de Valois",
            address__timezone="Europe/Paris",
        )
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        # When
        data = {
            "venueId": venue.id,
            "bookingContact": "offer@example.com",
            "bookingEmail": "offer@example.com",
            "durationMinutes": 60,
            "name": "La pièce de théâtre",
            "subcategoryId": subcategories.SPECTACLE_REPRESENTATION.id,
            "withdrawalType": "no_ticket",
            "extraData": {"toto": "text", "showType": 200, "showSubType": 201},
            "externalTicketOfficeUrl": "http://example.net",
            "audioDisabilityCompliant": False,
            "mentalDisabilityCompliant": True,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
            "address": {
                "city": offerer_address.address.city,
                "inseeCode": offerer_address.address.inseeCode,
                "label": oa_label,
                "latitude": offerer_address.address.latitude,
                "longitude": offerer_address.address.longitude,
                "postalCode": offerer_address.address.postalCode,
                "street": offerer_address.address.street,
                "banId": offerer_address.address.banId,
            },
        }
        response = client.with_session_auth("user@example.com").post("/offers", json=data)

        # Then
        assert response.status_code == 201
        offer_id = response.json["id"]
        offer = db.session.query(Offer).get(offer_id)
        assert offer.offererAddress.address == offerer_address.address
        assert offer.offererAddress.label == oa_label
        assert not offer.offererAddress.address.isManualEdition

    @pytest.mark.parametrize("oa_label", [None, "some place"])
    def test_create_event_offer_with_non_existing_offerer_address(self, oa_label, client):
        # Given
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerer_address = offerers_factories.OffererAddressFactory(offerer=offerer)
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        # When
        data = {
            "venueId": venue.id,
            "bookingContact": "offer@example.com",
            "bookingEmail": "offer@example.com",
            "durationMinutes": 60,
            "name": "La pièce de théâtre",
            "subcategoryId": subcategories.SPECTACLE_REPRESENTATION.id,
            "withdrawalType": "no_ticket",
            "extraData": {"toto": "text", "showType": 200, "showSubType": 201},
            "externalTicketOfficeUrl": "http://example.net",
            "audioDisabilityCompliant": False,
            "mentalDisabilityCompliant": True,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
            "address": {
                "city": "Paris",
                "label": oa_label,
                "latitude": "48.87171",
                "longitude": "2.308289",
                "postalCode": "75001",
                "street": "3 Rue de Valois",
            },
        }
        response = client.with_session_auth("user@example.com").post("/offers", json=data)

        # Then
        assert response.status_code == 201
        offer_id = response.json["id"]
        offer = db.session.query(Offer).get(offer_id)
        assert offer.offererAddress.address != offerer_address.address
        assert offer.offererAddress.label == oa_label
        assert not offer.offererAddress.address.isManualEdition

    @pytest.mark.parametrize("oa_label", [None, "some place"])
    def test_create_event_offer_with_manual_offerer_address(self, oa_label, client):
        # Given
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        # When
        data = {
            "venueId": venue.id,
            "bookingContact": "offer@example.com",
            "bookingEmail": "offer@example.com",
            "durationMinutes": 60,
            "name": "La pièce de théâtre",
            "subcategoryId": subcategories.SPECTACLE_REPRESENTATION.id,
            "withdrawalType": "no_ticket",
            "extraData": {"toto": "text", "showType": 200, "showSubType": 201},
            "externalTicketOfficeUrl": "http://example.net",
            "audioDisabilityCompliant": False,
            "mentalDisabilityCompliant": True,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
            "address": {
                "city": "Paris",
                "label": oa_label,
                "latitude": "48.87171",
                "longitude": "2.308289",
                "postalCode": "75001",
                "street": "3 Rue de Valois",
                "isManualEdition": True,
            },
        }
        response = client.with_session_auth("user@example.com").post("/offers", json=data)

        # Then
        assert response.status_code == 201
        offer_id = response.json["id"]
        offer = db.session.query(Offer).get(offer_id)
        assert offer.offererAddress.address.isManualEdition
        assert offer.offererAddress.label == oa_label
        assert not offer.offererAddress.address.banId
        assert offer.offererAddress.address.isManualEdition is True

    def when_creating_new_thing_offer(self, client):
        # Given
        venue = offerers_factories.VirtualVenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        # When
        data = {
            "venueId": venue.id,
            "bookingEmail": "offer@example.com",
            "name": "Les lièvres pas malins",
            "subcategoryId": subcategories.JEU_EN_LIGNE.id,
            "url": "http://example.com/offer",
            "externalTicketOfficeUrl": "http://example.net",
            "audioDisabilityCompliant": True,
            "mentalDisabilityCompliant": False,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
        }
        response = client.with_session_auth("user@example.com").post("/offers", json=data)

        # Then
        assert response.status_code == 201
        offer_id = response.json["id"]
        offer = db.session.query(Offer).get(offer_id)
        assert offer.bookingEmail == "offer@example.com"
        assert offer.subcategoryId == subcategories.JEU_EN_LIGNE.id
        assert offer.venue == venue
        assert offer.externalTicketOfficeUrl == "http://example.net"
        assert offer.url == "http://example.com/offer"
        assert offer.isDigital
        assert offer.isNational
        assert offer.motorDisabilityCompliant is False
        assert offer.visualDisabilityCompliant is False
        assert offer.audioDisabilityCompliant is True
        assert offer.mentalDisabilityCompliant is False
        assert offer.offererAddress is None

    def test_create_offer_with_ean(self, client):
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")
        ean = "1234567890112"
        data = {
            "venueId": venue.id,
            "name": "Les lièvres pas malins",
            "subcategoryId": subcategories.LIVRE_PAPIER.id,
            "extraData": {
                "ean": ean,
            },
            "audioDisabilityCompliant": True,
            "mentalDisabilityCompliant": False,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
        }
        response = client.with_session_auth("user@example.com").post("/offers", json=data)

        assert response.status_code == 201
        assert response.json["extraData"]["ean"] == ean
        assert "ean" not in response.json

        offer_id = response.json["id"]
        offer = db.session.query(Offer).get(offer_id)
        assert offer.subcategoryId == subcategories.LIVRE_PAPIER.id
        assert offer.venue == venue
        assert offer.ean == "1234567890112"
        assert "ean" not in offer.extraData

    def test_withdrawable_event_offer_can_have_no_ticket_to_withdraw(self, client):
        # Given
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        # When
        data = {
            "venueId": venue.id,
            "name": "La pièce de théâtre",
            "subcategoryId": subcategories.CONCERT.id,
            "bookingContact": "booking@conta.ct",
            "withdrawalDetails": "Veuillez récuperer vos billets à l'accueil :)",
            "withdrawalType": "no_ticket",
            "extraData": {"gtl_id": "07000000"},
            "mentalDisabilityCompliant": False,
            "audioDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
            "motorDisabilityCompliant": False,
        }
        response = client.with_session_auth("user@example.com").post("/offers", json=data)

        # Then
        offer_id = response.json["id"]
        offer = db.session.query(Offer).get(offer_id)
        assert offer.withdrawalDetails == "Veuillez récuperer vos billets à l'accueil :)"
        assert offer.withdrawalType == WithdrawalTypeEnum.NO_TICKET


@pytest.mark.usefixtures("db_session")
class Returns400Test:
    @staticmethod
    def _get_default_json(venue_id: int, subcategory_id: str) -> dict:
        return {
            "venueId": venue_id,
            "name": "Mon offre",
            "subcategoryId": subcategory_id,
            "mentalDisabilityCompliant": False,
            "audioDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
            "motorDisabilityCompliant": False,
        }

    def test_fail_if_venue_is_not_found(self, client):
        # Given
        offerers_factories.UserOffererFactory(user__email="user@example.com")

        # When
        data = {
            "venueId": 1,
            "bookingEmail": "offer@example.com",
            "name": "Les lièvres pas malins",
            "subcategoryId": subcategories.JEU_EN_LIGNE.id,
            "url": "http://example.com/offer",
            "audioDisabilityCompliant": True,
            "mentalDisabilityCompliant": False,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
        }
        response = client.with_session_auth("user@example.com").post("/offers", json=data)

        # Then
        assert response.status_code == 404

    @pytest.mark.parametrize(
        "input_json,expected_json",
        [
            ({"name": "too long" * 30}, {"name": ["Le titre de l’offre doit faire au maximum 90 caractères."]}),
            (
                {
                    "name": "Le Visible et l'invisible - Suivi de notes de travail - 9782070286256",
                    "subcategoryId": subcategories.LIVRE_PAPIER.id,
                },
                {"name": ["Le titre d'une offre ne peut contenir l'EAN"]},
            ),
            (
                {"subcategoryId": subcategories.ACHAT_INSTRUMENT.id, "url": "http://legrandj.eu"},
                {"url": ['Une offre de sous-catégorie "Achat instrument" ne peut contenir un champ `url`']},
            ),
            ({"url": "missing.something"}, {"url": ['L\'URL doit commencer par "http://" ou "https://"']}),
            ({"url": "https://missing"}, {"url": ['L\'URL doit terminer par une extension (ex. ".fr")']}),
            (
                {"externalTicketOfficeUrl": "missing.something"},
                {"externalTicketOfficeUrl": ['L\'URL doit commencer par "http://" ou "https://"']},
            ),
            (
                {"externalTicketOfficeUrl": "https://missing"},
                {"externalTicketOfficeUrl": ['L\'URL doit terminer par une extension (ex. ".fr")']},
            ),
            ({"subcategoryId": "ART_PRIMITIF"}, {"subcategory": ["La sous-catégorie de cette offre est inconnue"]}),
            (
                {"subcategoryId": "OEUVRE_ART"},
                {"subcategory": ["Une offre ne peut être créée ou éditée en utilisant cette sous-catégorie"]},
            ),
            (
                {"subcategoryId": subcategories.FESTIVAL_ART_VISUEL.id},
                {"offer": ["Une offre qui a un ticket retirable doit avoir un type de retrait renseigné"]},
            ),
            (
                {"subcategoryId": subcategories.FESTIVAL_ART_VISUEL.id, "withdrawalType": "no_ticket"},
                {"offer": ["Une offre qui a un ticket retirable doit avoir l'email du contact de réservation"]},
            ),
            (
                {"subcategoryId": subcategories.FESTIVAL_ART_VISUEL.id, "withdrawalType": "in_app"},
                {"withdrawalType": ["Withdrawal type cannot be in_app for manually created offers"]},
            ),
        ],
    )
    def test_fail_if_json_incorrect(self, client, input_json, expected_json):
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        data = self._get_default_json(venue.id, subcategories.SPECTACLE_REPRESENTATION.id)
        data.update(input_json)

        response = client.with_session_auth("user@example.com").post("/offers", json=data)

        assert response.status_code == 400
        assert response.json == expected_json


@pytest.mark.usefixtures("db_session")
class Returns403Test:
    def test_when_user_is_not_attached_to_offerer(self, client):
        # Given
        users_factories.ProFactory(email="user@example.com")
        venue = offerers_factories.VirtualVenueFactory()

        # When
        data = {
            "venueId": venue.id,
            "subcategoryId": subcategories.JEU_EN_LIGNE.id,
            "audioDisabilityCompliant": True,
            "mentalDisabilityCompliant": False,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
            "name": "Les orphelins",
        }
        response = client.with_session_auth("user@example.com").post("/offers", json=data)

        # Then
        assert response.status_code == 403
        assert response.json["global"] == [
            "Vous n'avez pas les droits d'accès suffisants pour accéder à cette information."
        ]
