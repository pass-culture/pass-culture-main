import pytest

from pcapi.core.categories import subcategories
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import WithdrawalTypeEnum
from pcapi.core.testing import override_features
import pcapi.core.users.factories as users_factories
from pcapi.utils.human_ids import dehumanize
from pcapi.utils.human_ids import humanize


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    @override_features(OFFER_FORM_SUMMARY_PAGE=True)
    def test_created_offer_should_be_inactive(self, client):
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        # When
        data = {
            "venueId": humanize(venue.id),
            "name": "Celeste",
            "subcategoryId": subcategories.JEU_EN_LIGNE.id,
            "mentalDisabilityCompliant": True,
        }
        response = client.with_session_auth("user@example.com").post("/offers", json=data)
        offer_id = dehumanize(response.json["id"])
        offer = Offer.query.get(offer_id)
        assert offer.isActive == False

    def test_create_event_offer(self, client):
        # Given
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        # When
        data = {
            "venueId": humanize(venue.id),
            "bookingEmail": "offer@example.com",
            "durationMinutes": 60,
            "name": "La pièce de théâtre",
            "subcategoryId": subcategories.SPECTACLE_REPRESENTATION.id,
            "withdrawalType": "no_ticket",
            "extraData": {"toto": "text", "showType": 200},
            "externalTicketOfficeUrl": "http://example.net",
            "audioDisabilityCompliant": False,
            "mentalDisabilityCompliant": True,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
        }
        response = client.with_session_auth("user@example.com").post("/offers", json=data)

        # Then
        assert response.status_code == 201
        offer_id = dehumanize(response.json["id"])
        offer = Offer.query.get(offer_id)
        assert offer.bookingEmail == "offer@example.com"
        assert offer.subcategoryId == subcategories.SPECTACLE_REPRESENTATION.id
        assert offer.extraData == {"toto": "text", "showType": 200}
        assert offer.externalTicketOfficeUrl == "http://example.net"
        assert offer.venue == venue
        assert offer.product.durationMinutes == 60
        assert offer.product.owningOfferer == offerer
        assert offer.motorDisabilityCompliant == False
        assert offer.visualDisabilityCompliant == False
        assert offer.audioDisabilityCompliant == False
        assert offer.mentalDisabilityCompliant == True
        assert offer.isActive == True

    def when_creating_new_thing_offer(self, client):
        # Given
        venue = offerers_factories.VirtualVenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        # When
        data = {
            "venueId": humanize(venue.id),
            "bookingEmail": "offer@example.com",
            "mediaUrls": ["http://example.com/media"],
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
        offer_id = dehumanize(response.json["id"])
        offer = Offer.query.get(offer_id)
        assert offer.bookingEmail == "offer@example.com"
        assert offer.subcategoryId == subcategories.JEU_EN_LIGNE.id
        assert offer.venue == venue
        assert offer.product.name == "Les lièvres pas malins"
        assert offer.product.url == "http://example.com/offer"
        assert offer.externalTicketOfficeUrl == "http://example.net"
        assert offer.url == "http://example.com/offer"
        assert offer.isDigital
        assert offer.isNational
        assert offer.product.isNational
        assert offer.product.owningOfferer == offerer
        assert offer.motorDisabilityCompliant == False
        assert offer.visualDisabilityCompliant == False
        assert offer.audioDisabilityCompliant == True
        assert offer.mentalDisabilityCompliant == False

    def test_create_valid_collective_offer_in_old_offer_model(self, client):
        # Given
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        # When
        data = {
            "venueId": humanize(venue.id),
            "bookingEmail": "offer@example.com",
            "durationMinutes": 60,
            "name": "La pièce de théâtre",
            "subcategoryId": subcategories.SPECTACLE_REPRESENTATION.id,
            "withdrawalType": "no_ticket",
            "extraData": {"toto": "text", "showType": 300},
            "externalTicketOfficeUrl": "http://example.net",
            "audioDisabilityCompliant": False,
            "mentalDisabilityCompliant": True,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
            "isEducational": True,
        }
        response = client.with_session_auth("user@example.com").post("/offers", json=data)

        # Then
        assert response.status_code == 201
        offer_id = dehumanize(response.json["id"])
        offer = Offer.query.get(offer_id)
        assert offer.isEducational

    def test_withdrawable_event_offer_can_have_no_ticket_to_withdraw(self, client):
        # Given
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        # When
        data = {
            "venueId": humanize(venue.id),
            "name": "La pièce de théâtre",
            "subcategoryId": subcategories.CONCERT.id,
            "withdrawalDetails": "Veuillez récuperer vos billets à l'accueil :)",
            "withdrawalType": "no_ticket",
            "extraData": {"musicType": 300},
        }
        response = client.with_session_auth("user@example.com").post("/offers", json=data)

        # Then
        offer_id = dehumanize(response.json["id"])
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
            "venueId": humanize(1),
            "bookingEmail": "offer@example.com",
            "mediaUrls": ["http://example.com/media"],
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
        assert response.json["global"] == ["Aucun objet ne correspond à cet identifiant dans notre base de données"]

    def test_fail_if_name_too_long(self, client):
        # Given
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        # When
        data = {
            "venueId": humanize(venue.id),
            "name": "too long" * 30,
            "subcategoryId": subcategories.SPECTACLE_REPRESENTATION.id,
            "withdrawalType": "no_ticket",
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
            "venueId": humanize(venue.id),
            "name": "An unacceptable name",
            "subcategoryId": "TOTO",
        }
        response = client.with_session_auth("user@example.com").post("/offers", json=data)

        # Then
        assert response.status_code == 400
        assert response.json["subcategory"] == ["La sous-catégorie de cette offre est inconnue"]

    def test_fail_if_inactive_subcategory(self, client):
        # Given
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        # When
        data = {
            "venueId": humanize(venue.id),
            "name": "A cool offer name",
            "subcategoryId": "OEUVRE_ART",
        }
        response = client.with_session_auth("user@example.com").post("/offers", json=data)

        # Then
        assert response.status_code == 400
        assert response.json["subcategory"] == [
            "Une offre ne peut être créée ou éditée en utilisant cette sous-catégorie"
        ]

    def test_fail_when_educational_and_non_eligible_subcategory(self, client):
        # Given
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        # When
        data = {
            "venueId": humanize(venue.id),
            "name": "An cool educational name",
            "subcategoryId": "SUPPORT_PHYSIQUE_FILM",
            "isEducational": True,
        }
        response = client.with_session_auth("user@example.com").post("/offers", json=data)

        # Then
        assert response.status_code == 400
        assert response.json["offer"] == ["Cette catégorie d'offre n'est pas éligible aux offres éducationnelles"]

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
            "mediaUrls": ["http://media.url"],
            "venueId": humanize(venue.id),
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
            "venueId": humanize(venue.id),
            "name": "Les lièvres pas malins",
            "subcategoryId": subcategories.JEU_EN_LIGNE.id,
            "url": "missing.something",
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
            "venueId": humanize(venue.id),
            "name": "Les lièvres pas malins",
            "subcategoryId": subcategories.JEU_EN_LIGNE.id,
            "externalTicketOfficeUrl": "missing.something",
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
            "venueId": humanize(venue.id),
            "name": "Les lièvres pas malins",
            "subcategoryId": subcategories.JEU_EN_LIGNE.id,
            "url": "https://missing",
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
            "venueId": humanize(venue.id),
            "name": "Les lièvres pas malins",
            "subcategoryId": subcategories.JEU_EN_LIGNE.id,
            "externalTicketOfficeUrl": "https://missing",
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
            "venueId": humanize(venue.id),
            "name": "Dofus",
            "subcategoryId": subcategories.JEU_EN_LIGNE.id,
            "withdrawalType": "no_ticket",
        }
        response = client.with_session_auth("user@example.com").post("/offers", json=data)

        # Then
        assert response.status_code == 400


@pytest.mark.usefixtures("db_session")
class Returns403Test:
    def test_when_user_is_not_attached_to_offerer(self, client):
        # Given
        users_factories.ProFactory(email="user@example.com")
        venue = offerers_factories.VirtualVenueFactory()

        # When
        data = {
            "venueId": humanize(venue.id),
            "subcategoryId": subcategories.JEU_EN_LIGNE.id,
            "audioDisabilityCompliant": True,
            "mentalDisabilityCompliant": False,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
        }
        response = client.with_session_auth("user@example.com").post("/offers", json=data)

        # Then
        assert response.status_code == 403
        assert response.json["global"] == [
            "Vous n'avez pas les droits d'accès suffisant pour accéder à cette information."
        ]
