import pytest
import requests_mock

from pcapi.core.categories import subcategories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.offers.models import Offer
from pcapi.core.testing import override_settings
import pcapi.core.users.factories as users_factories
from pcapi.utils.human_ids import dehumanize
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    def test_create_event_offer(self, app):
        # Given
        venue = offers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        # When
        data = {
            "venueId": humanize(venue.id),
            "bookingEmail": "offer@example.com",
            "durationMinutes": 60,
            "name": "La pièce de théâtre",
            "subcategoryId": subcategories.SPECTACLE_REPRESENTATION.id,
            "extraData": {"toto": "text"},
            "externalTicketOfficeUrl": "http://example.net",
            "audioDisabilityCompliant": False,
            "mentalDisabilityCompliant": True,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
        }
        client = TestClient(app.test_client()).with_session_auth("user@example.com")
        response = client.post("/offers", json=data)

        # Then
        assert response.status_code == 201
        offer_id = dehumanize(response.json["id"])
        offer = Offer.query.get(offer_id)
        assert offer.bookingEmail == "offer@example.com"
        assert offer.subcategoryId == subcategories.SPECTACLE_REPRESENTATION.id
        assert offer.extraData == {"toto": "text"}
        assert offer.externalTicketOfficeUrl == "http://example.net"
        assert offer.venue == venue
        assert offer.product.durationMinutes == 60
        assert offer.product.owningOfferer == offerer
        assert offer.motorDisabilityCompliant == False
        assert offer.visualDisabilityCompliant == False
        assert offer.audioDisabilityCompliant == False
        assert offer.mentalDisabilityCompliant == True

    def when_creating_new_thing_offer(self, app):
        # Given
        venue = offers_factories.VirtualVenueFactory()
        offerer = venue.managingOfferer
        offers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        # When
        client = TestClient(app.test_client()).with_session_auth("user@example.com")
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
        response = client.post("/offers", json=data)

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

    def test_create_valid_educational_offer(self, app):
        # Given
        venue = offers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        # When
        data = {
            "venueId": humanize(venue.id),
            "bookingEmail": "offer@example.com",
            "durationMinutes": 60,
            "name": "La pièce de théâtre",
            "subcategoryId": subcategories.SPECTACLE_REPRESENTATION.id,
            "extraData": {"toto": "text"},
            "externalTicketOfficeUrl": "http://example.net",
            "audioDisabilityCompliant": False,
            "mentalDisabilityCompliant": True,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
            "isEducational": True,
        }
        client = TestClient(app.test_client()).with_session_auth("user@example.com")
        response = client.post("/offers", json=data)

        # Then
        assert response.status_code == 201
        offer_id = dehumanize(response.json["id"])
        offer = Offer.query.get(offer_id)
        assert offer.isEducational

    @override_settings(ADAGE_API_URL="https://adage-api-url")
    @override_settings(ADAGE_API_KEY="adage-api-key")
    @override_settings(ADAGE_BACKEND="pcapi.core.educational.adage_backends.adage.AdageHttpClient")
    def test_create_valid_educational_offer_with_new_route(self, app):
        # Given
        venue = offers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        # When
        data = {
            "offererId": humanize(offerer.id),
            "venueId": humanize(venue.id),
            "bookingEmail": "offer@example.com",
            "durationMinutes": 60,
            "name": "La pièce de théâtre",
            "subcategoryId": subcategories.SPECTACLE_REPRESENTATION.id,
            "extraData": {
                "students": ["Collège - 4e"],
                "contactEmail": "toto@toto.com",
                "contactPhone": "0600000000",
                "offerVenue": {"addressType": "other", "otherAddress": "", "venueId": ""},
            },
            "audioDisabilityCompliant": False,
            "mentalDisabilityCompliant": True,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
        }
        client = TestClient(app.test_client()).with_session_auth("user@example.com")
        with requests_mock.Mocker() as request_mock:
            request_mock.get(
                f"https://adage-api-url/v1/partenaire-culturel/{offerer.siren}",
                request_headers={
                    "X-omogen-api-key": "adage-api-key",
                },
                status_code=200,
                json=[
                    {
                        "id": "125334",
                        "siret": "18004623700012",
                        "regionId": "1",
                        "academieId": "25",
                        "statutId": "2",
                        "labelId": "4",
                        "typeId": "4",
                        "communeId": "75101",
                        "libelle": "Musée du Louvre",
                        "adresse": "Rue de Rivoli",
                        "siteWeb": "https://www.louvre.fr/",
                        "latitude": "48.861863",
                        "longitude": "2.338081",
                        "actif": "1",
                        "dateModification": "2021-09-01 00:00:00",
                        "statutLibelle": "Établissement public",
                        "labelLibelle": "Musée de France",
                        "typeIcone": "museum",
                        "typeLibelle": "Musée, domaine ou monument",
                        "communeLibelle": "PARIS  1ER ARRONDISSEMENT",
                        "domaines": "Architecture|Arts visuels, arts plastiques, arts appliqués|Patrimoine et archéologie|Photographie",
                    }
                ],
            )

            response = client.post("/offers/educational", json=data)

        # Then
        assert response.status_code == 201
        offer_id = dehumanize(response.json["id"])
        offer = Offer.query.get(offer_id)
        assert offer.isEducational
        assert offer.bookingEmail == "offer@example.com"
        assert offer.subcategoryId == subcategories.SPECTACLE_REPRESENTATION.id
        assert offer.venue == venue
        assert offer.product.name == "La pièce de théâtre"
        assert offer.product.owningOfferer == offerer
        assert offer.audioDisabilityCompliant == False
        assert offer.mentalDisabilityCompliant == True
        assert offer.motorDisabilityCompliant == False
        assert offer.visualDisabilityCompliant == False
        assert offer.extraData == {
            "students": ["Collège - 4e"],
            "contactEmail": "toto@toto.com",
            "contactPhone": "0600000000",
            "offerVenue": {"addressType": "other", "otherAddress": "", "venueId": ""},
            "isShowcase": False,
        }


@pytest.mark.usefixtures("db_session")
class Returns400Test:
    def test_fail_if_venue_is_not_found(self, app):
        # Given
        offers_factories.UserOffererFactory(user__email="user@example.com")

        # When
        client = TestClient(app.test_client()).with_session_auth("user@example.com")
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
        response = client.post("/offers", json=data)

        # Then
        assert response.status_code == 404
        assert response.json["global"] == ["Aucun objet ne correspond à cet identifiant dans notre base de données"]

    def test_fail_if_name_too_long(self, app):
        # Given
        venue = offers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        # When
        data = {
            "venueId": humanize(venue.id),
            "name": "too long" * 30,
            "subcategoryId": subcategories.SPECTACLE_REPRESENTATION.id,
        }
        client = TestClient(app.test_client()).with_session_auth("user@example.com")
        response = client.post("/offers", json=data)

        # Then
        assert response.status_code == 400
        assert response.json["name"] == ["Le titre de l’offre doit faire au maximum 90 caractères."]

    def test_fail_if_unknown_subcategory(self, app):
        # Given
        venue = offers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        # When
        data = {
            "venueId": humanize(venue.id),
            "name": "An unacceptable name",
            "subcategoryId": "TOTO",
        }
        client = TestClient(app.test_client()).with_session_auth("user@example.com")
        response = client.post("/offers", json=data)

        # Then
        assert response.status_code == 400
        assert response.json["subcategory"] == ["La sous-catégorie de cette offre est inconnue"]

    def test_fail_if_inactive_subcategory(self, app):
        # Given
        venue = offers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        # When
        data = {
            "venueId": humanize(venue.id),
            "name": "A cool offer name",
            "subcategoryId": "OEUVRE_ART",
        }
        client = TestClient(app.test_client()).with_session_auth("user@example.com")
        response = client.post("/offers", json=data)

        # Then
        assert response.status_code == 400
        assert response.json["subcategory"] == [
            "Une offre ne peut être créée ou éditée en utilisant cette sous-catégorie"
        ]

    def test_fail_when_educational_and_non_eligible_subcategory(self, app):
        # Given
        venue = offers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        # When
        data = {
            "venueId": humanize(venue.id),
            "name": "An cool educational name",
            "subcategoryId": "SUPPORT_PHYSIQUE_FILM",
            "isEducational": True,
        }
        client = TestClient(app.test_client()).with_session_auth("user@example.com")
        response = client.post("/offers", json=data)

        # Then
        assert response.status_code == 400
        assert response.json["offer"] == ["Cette catégorie d'offre n'est pas éligible aux offres éducationnelles"]

    def test_fail_when_educational_and_duo(self, app):
        # Given
        venue = offers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        # When
        data = {
            "venueId": humanize(venue.id),
            "name": "An unacceptable name",
            "subcategoryId": "SEANCE_CINE",
            "isEducational": True,
            "isDuo": True,
        }
        client = TestClient(app.test_client()).with_session_auth("user@example.com")
        response = client.post("/offers", json=data)

        # Then
        assert response.status_code == 400
        assert response.json["offer"] == ["Une offre ne peut être à la fois 'duo' et 'éducationnelle'."]

    def test_fail_when_offer_subcategory_is_offline_only_and_venue_is_virtuel(self, app):
        # Given
        venue = offers_factories.VirtualVenueFactory()
        offerer = venue.managingOfferer
        offers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

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
        client = TestClient(app.test_client()).with_session_auth("user@example.com")
        response = client.post("/offers", json=data)

        # Then
        assert response.status_code == 400
        assert response.json["url"] == ["Une offre de sous-catégorie Achat instrument ne peut pas être numérique"]

    def should_fail_when_url_has_no_scheme(self, app):
        # Given
        venue = offers_factories.VirtualVenueFactory()
        offerer = venue.managingOfferer
        offers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        # When
        client = TestClient(app.test_client()).with_session_auth("user@example.com")
        data = {
            "venueId": humanize(venue.id),
            "name": "Les lièvres pas malins",
            "subcategoryId": subcategories.JEU_EN_LIGNE.id,
            "url": "missing.something",
        }
        response = client.post("/offers", json=data)

        # Then
        assert response.status_code == 400
        assert response.json["url"] == ['L\'URL doit commencer par "http://" ou "https://"']

    def should_fail_when_externalTicketOfficeUrl_has_no_scheme(self, app):
        # Given
        venue = offers_factories.VirtualVenueFactory()
        offerer = venue.managingOfferer
        offers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        # When
        client = TestClient(app.test_client()).with_session_auth("user@example.com")
        data = {
            "venueId": humanize(venue.id),
            "name": "Les lièvres pas malins",
            "subcategoryId": subcategories.JEU_EN_LIGNE.id,
            "externalTicketOfficeUrl": "missing.something",
        }
        response = client.post("/offers", json=data)

        # Then
        assert response.status_code == 400
        assert response.json["externalTicketOfficeUrl"] == ['L\'URL doit commencer par "http://" ou "https://"']

    def should_fail_when_url_has_no_host(self, app):
        # Given
        venue = offers_factories.VirtualVenueFactory()
        offerer = venue.managingOfferer
        offers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        # When
        client = TestClient(app.test_client()).with_session_auth("user@example.com")
        data = {
            "venueId": humanize(venue.id),
            "name": "Les lièvres pas malins",
            "subcategoryId": subcategories.JEU_EN_LIGNE.id,
            "url": "https://missing",
        }
        response = client.post("/offers", json=data)

        # Then
        assert response.status_code == 400
        assert response.json["url"] == ['L\'URL doit terminer par une extension (ex. ".fr")']

    def should_fail_when_externalTicketOfficeUrl_has_no_host(self, app):
        # Given
        venue = offers_factories.VirtualVenueFactory()
        offerer = venue.managingOfferer
        offers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        # When
        client = TestClient(app.test_client()).with_session_auth("user@example.com")
        data = {
            "venueId": humanize(venue.id),
            "name": "Les lièvres pas malins",
            "subcategoryId": subcategories.JEU_EN_LIGNE.id,
            "externalTicketOfficeUrl": "https://missing",
        }
        response = client.post("/offers", json=data)

        # Then
        assert response.status_code == 400
        assert response.json["externalTicketOfficeUrl"] == ['L\'URL doit terminer par une extension (ex. ".fr")']

    def test_create_educational_offer_with_wrong_extra_data(self, app, client):
        # Given
        venue = offers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        # When
        data = {
            "offererId": humanize(offerer.id),
            "venueId": humanize(venue.id),
            "bookingEmail": "offer@example.com",
            "durationMinutes": 60,
            "name": "La pièce de théâtre",
            "subcategoryId": subcategories.SPECTACLE_REPRESENTATION.id,
            "extraData": {
                "students": ["Collège - 4e"],
            },
            "audioDisabilityCompliant": False,
            "mentalDisabilityCompliant": True,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
        }

        with requests_mock.Mocker() as request_mock:
            request_mock.get(
                f"https://adage-api-url/v1/partenaire-culturel/{offerer.siren}",
                request_headers={
                    "X-omogen-api-key": "adage-api-key",
                },
                status_code=200,
                json=[
                    {
                        "id": "125334",
                        "siret": "18004623700012",
                        "regionId": "1",
                        "academieId": "25",
                        "statutId": "2",
                        "labelId": "4",
                        "typeId": "4",
                        "communeId": "75101",
                        "libelle": "Musée du Louvre",
                        "adresse": "Rue de Rivoli",
                        "siteWeb": "https://www.louvre.fr/",
                        "latitude": "48.861863",
                        "longitude": "2.338081",
                        "actif": "1",
                        "dateModification": "2021-09-01 00:00:00",
                        "statutLibelle": "Établissement public",
                        "labelLibelle": "Musée de France",
                        "typeIcone": "museum",
                        "typeLibelle": "Musée, domaine ou monument",
                        "communeLibelle": "PARIS  1ER ARRONDISSEMENT",
                        "domaines": "Architecture|Arts visuels, arts plastiques, arts appliqués|Patrimoine et archéologie|Photographie",
                    }
                ],
            )

            client.with_session_auth("user@example.com")
            response = client.post("/offers/educational", json=data)

        # Then
        assert response.status_code == 400


@pytest.mark.usefixtures("db_session")
class Returns403Test:
    def when_user_is_not_attached_to_offerer(self, app):
        # Given
        users_factories.ProFactory(email="user@example.com")
        venue = offers_factories.VirtualVenueFactory()

        # When
        client = TestClient(app.test_client()).with_session_auth("user@example.com")
        data = {
            "venueId": humanize(venue.id),
            "audioDisabilityCompliant": True,
            "mentalDisabilityCompliant": False,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
        }
        response = client.post("/offers", json=data)

        # Then
        assert response.status_code == 403
        assert response.json["global"] == [
            "Vous n'avez pas les droits d'accès suffisant pour accéder à cette information."
        ]

    @override_settings(ADAGE_API_URL="https://adage-api-url")
    @override_settings(ADAGE_API_KEY="adage-api-key")
    @override_settings(ADAGE_BACKEND="pcapi.core.educational.adage_backends.adage.AdageHttpClient")
    def when_offerer_cannot_create_educational_offer(self, app):
        # Given
        venue = offers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        # When
        data = {
            "offererId": humanize(offerer.id),
            "venueId": humanize(venue.id),
            "bookingEmail": "offer@example.com",
            "durationMinutes": 60,
            "name": "La pièce de théâtre",
            "subcategoryId": subcategories.SPECTACLE_REPRESENTATION.id,
            "extraData": {
                "students": ["Collège - 4e"],
                "contactEmail": "toto@toto.com",
                "contactPhone": "0600000000",
                "offerVenue": {"addressType": "other", "otherAddress": "", "venueId": ""},
            },
            "audioDisabilityCompliant": False,
            "mentalDisabilityCompliant": True,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
        }
        client = TestClient(app.test_client()).with_session_auth("user@example.com")
        with requests_mock.Mocker() as request_mock:
            request_mock.get(
                f"https://adage-api-url/v1/partenaire-culturel/{offerer.siren}",
                request_headers={
                    "X-omogen-api-key": "adage-api-key",
                },
                status_code=404,
            )

            response = client.post("/offers/educational", json=data)

        # Then
        assert response.status_code == 403
        offers = Offer.query.all()
        assert len(offers) == 0
