import pytest

from pcapi.core.categories import subcategories_v2 as subcategories
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import WithdrawalTypeEnum
import pcapi.core.users.factories as users_factories
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
        offer = Offer.query.get(offer_id)
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
        offer = Offer.query.get(offer_id)
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
        offer = Offer.query.get(offer_id)
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

        data = {
            "venueId": venue.id,
            "name": "Les lièvres pas malins",
            "subcategoryId": subcategories.LIVRE_PAPIER.id,
            "extraData": {
                "ean": "1234567890112",
            },
            "audioDisabilityCompliant": True,
            "mentalDisabilityCompliant": False,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
        }
        response = client.with_session_auth("user@example.com").post("/offers", json=data)

        assert response.status_code == 201
        offer_id = response.json["id"]
        offer = Offer.query.get(offer_id)
        assert offer.subcategoryId == subcategories.LIVRE_PAPIER.id
        assert offer.venue == venue
        assert offer.extraData["ean"] == "1234567890112"

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
        offer = Offer.query.get(offer_id)
        assert offer.withdrawalDetails == "Veuillez récuperer vos billets à l'accueil :)"
        assert offer.withdrawalType == WithdrawalTypeEnum.NO_TICKET


@pytest.mark.usefixtures("db_session")
class Returns400Test:
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

    def test_fail_if_name_too_long(self, client):
        # Given
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        # When
        data = {
            "venueId": venue.id,
            "name": "too long" * 30,
            "subcategoryId": subcategories.SPECTACLE_REPRESENTATION.id,
            "withdrawalType": "no_ticket",
            "mentalDisabilityCompliant": False,
            "audioDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
            "motorDisabilityCompliant": False,
        }
        response = client.with_session_auth("user@example.com").post("/offers", json=data)

        # Then
        assert response.status_code == 400
        assert response.json["name"] == ["Le titre de l’offre doit faire au maximum 90 caractères."]

    def test_fail_if_unknown_subcategory(self, client):
        # Given
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        # When
        data = {
            "venueId": venue.id,
            "name": "An unacceptable name",
            "subcategoryId": "TOTO",
            "mentalDisabilityCompliant": False,
            "audioDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
            "motorDisabilityCompliant": False,
        }
        response = client.with_session_auth("user@example.com").post("/offers", json=data)

        # Then
        assert response.status_code == 400
        assert response.json["subcategory"] == ["La sous-catégorie de cette offre est inconnue"]

    @pytest.mark.parametrize("subcategory_id", ["OEUVRE_ART", "BON_ACHAT_INSTRUMENT"])
    def test_fail_if_inactive_subcategory(self, client, subcategory_id):
        # Given
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        # When
        data = {
            "venueId": venue.id,
            "name": "A cool offer name",
            "subcategoryId": subcategory_id,
            "mentalDisabilityCompliant": False,
            "audioDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
            "motorDisabilityCompliant": False,
        }
        response = client.with_session_auth("user@example.com").post("/offers", json=data)

        # Then
        assert response.status_code == 400
        assert response.json["subcategory"] == [
            "Une offre ne peut être créée ou éditée en utilisant cette sous-catégorie"
        ]

    def test_fail_when_offer_subcategory_is_offline_only_and_venue_is_virtuel(self, client):
        # Given
        venue = offerers_factories.VirtualVenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        # When
        data = {
            "subcategoryId": subcategories.ACHAT_INSTRUMENT.id,
            "name": "Le grand jeu",
            "url": "http://legrandj.eu",
            "venueId": venue.id,
            "audioDisabilityCompliant": True,
            "mentalDisabilityCompliant": False,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
        }
        response = client.with_session_auth("user@example.com").post("/offers", json=data)

        # Then
        assert response.status_code == 400
        assert response.json["url"] == ["Une offre de sous-catégorie Achat instrument ne peut pas être numérique"]

    def should_fail_when_url_has_no_scheme(self, client):
        # Given
        venue = offerers_factories.VirtualVenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        # When
        data = {
            "venueId": venue.id,
            "name": "Les lièvres pas malins",
            "subcategoryId": subcategories.JEU_EN_LIGNE.id,
            "url": "missing.something",
            "mentalDisabilityCompliant": False,
            "audioDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
            "motorDisabilityCompliant": False,
        }
        response = client.with_session_auth("user@example.com").post("/offers", json=data)

        # Then
        assert response.status_code == 400
        assert response.json["url"] == ['L\'URL doit commencer par "http://" ou "https://"']

    def should_fail_when_externalTicketOfficeUrl_has_no_scheme(self, client):
        # Given
        venue = offerers_factories.VirtualVenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        # When
        data = {
            "venueId": venue.id,
            "name": "Les lièvres pas malins",
            "subcategoryId": subcategories.JEU_EN_LIGNE.id,
            "externalTicketOfficeUrl": "missing.something",
            "mentalDisabilityCompliant": False,
            "audioDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
            "motorDisabilityCompliant": False,
        }
        response = client.with_session_auth("user@example.com").post("/offers", json=data)

        # Then
        assert response.status_code == 400
        assert response.json["externalTicketOfficeUrl"] == ['L\'URL doit commencer par "http://" ou "https://"']

    def should_fail_when_url_has_no_host(self, client):
        # Given
        venue = offerers_factories.VirtualVenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        # When
        data = {
            "venueId": venue.id,
            "name": "Les lièvres pas malins",
            "subcategoryId": subcategories.JEU_EN_LIGNE.id,
            "url": "https://missing",
            "mentalDisabilityCompliant": False,
            "audioDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
            "motorDisabilityCompliant": False,
        }
        response = client.with_session_auth("user@example.com").post("/offers", json=data)

        # Then
        assert response.status_code == 400
        assert response.json["url"] == ['L\'URL doit terminer par une extension (ex. ".fr")']

    def should_fail_when_externalTicketOfficeUrl_has_no_host(self, client):
        # Given
        venue = offerers_factories.VirtualVenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        # When
        data = {
            "venueId": venue.id,
            "name": "Les lièvres pas malins",
            "subcategoryId": subcategories.JEU_EN_LIGNE.id,
            "externalTicketOfficeUrl": "https://missing",
            "mentalDisabilityCompliant": False,
            "audioDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
            "motorDisabilityCompliant": False,
        }
        response = client.with_session_auth("user@example.com").post("/offers", json=data)

        # Then
        assert response.status_code == 400
        assert response.json["externalTicketOfficeUrl"] == ['L\'URL doit terminer par une extension (ex. ".fr")']

    def test_non_withdrawable_event_offer_cant_have_withdrawal(self, client):
        # Given
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        # When
        data = {
            "venueId": venue.id,
            "name": "Dofus",
            "subcategoryId": subcategories.JEU_EN_LIGNE.id,
            "withdrawalType": "no_ticket",
            "mentalDisabilityCompliant": False,
            "audioDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
            "motorDisabilityCompliant": False,
        }
        response = client.with_session_auth("user@example.com").post("/offers", json=data)

        # Then
        assert response.status_code == 400

    def test_withdrawable_event_offer_must_have_booking_contact(self, client):
        # Given
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        # When
        data = {
            "venueId": venue.id,
            "name": "Vernissage",
            "subcategoryId": subcategories.FESTIVAL_ART_VISUEL.id,
            "mentalDisabilityCompliant": False,
            "audioDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
            "motorDisabilityCompliant": False,
        }
        response = client.with_session_auth("user@example.com").post("/offers", json=data)

        # Then
        assert response.status_code == 400

    def test_withdrawalable_event_cannot_be_in_app_mode(self, client):
        venue = offerers_factories.VenueFactory()
        offerers_factories.UserOffererFactory(offerer=venue.managingOfferer, user__email="user@example.com")
        # When
        data = {
            "venueId": venue.id,
            "name": "Vernissage",
            "subcategoryId": subcategories.CONCERT.id,
            "mentalDisabilityCompliant": False,
            "audioDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
            "motorDisabilityCompliant": False,
            "withdrawalType": "in_app",
        }
        response = client.with_session_auth("user@example.com").post("/offers", json=data)

        assert response.status_code == 400
        assert response.json == {"withdrawalType": ["Withdrawal type cannot be in_app for manually created offers"]}


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
