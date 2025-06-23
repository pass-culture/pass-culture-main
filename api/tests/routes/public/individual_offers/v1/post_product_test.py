import base64
import datetime
import decimal
import pathlib
from unittest import mock

import pytest
import time_machine

from pcapi import settings
from pcapi.core.geography import factories as geography_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.models import db
from pcapi.models import offer_mixin
from pcapi.utils import date as date_utils
from pcapi.utils import human_ids

import tests
from tests.routes import image_data
from tests.routes.public.helpers import PublicAPIVenueEndpointHelper


ACCESSIBILITY_FIELDS = {
    "audioDisabilityCompliant": True,
    "mentalDisabilityCompliant": True,
    "motorDisabilityCompliant": True,
    "visualDisabilityCompliant": True,
}

now_datetime_with_tz = datetime.datetime.now(datetime.timezone.utc)


@pytest.mark.usefixtures("db_session")
class PostProductTest(PublicAPIVenueEndpointHelper):
    endpoint_url = "/public/offers/v1/products"
    endpoint_method = "post"

    @staticmethod
    def _get_base_payload(venue_id: int) -> dict:
        return {
            "location": {"type": "physical", "venueId": venue_id},
            "categoryRelatedFields": {
                "category": "SUPPORT_PHYSIQUE_FILM",
                "ean": "1234567891234",
            },
            "accessibility": ACCESSIBILITY_FIELDS,
            "name": "Le champ des possibles",
        }

    def test_should_raise_401_because_not_authenticated(self, client):
        response = client.post(self.endpoint_url, json={})
        assert response.status_code == 401

    def test_should_raise_404_because_has_no_access_to_venue(self, client):
        plain_api_key, _ = self.setup_provider()
        venue = self.setup_venue()
        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url, json=self._get_base_payload(venue.id)
        )
        assert response.status_code == 404

    def test_should_raise_404_because_venue_provider_is_inactive(self, client):
        plain_api_key, venue_provider = self.setup_inactive_venue_provider()
        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url, json=self._get_base_payload(venue_provider.venue.id)
        )
        assert response.status_code == 404

    @time_machine.travel(now_datetime_with_tz, tick=False)
    @mock.patch("pcapi.tasks.sendinblue_tasks.update_sib_pro_attributes_task")
    def test_physical_product_minimal_body(self, update_sib_pro_task_mock, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()

        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url, json=self._get_base_payload(venue_provider.venueId)
        )

        assert response.status_code == 200
        created_offer = db.session.query(offers_models.Offer).one()
        assert created_offer.name == "Le champ des possibles"
        assert created_offer.venue == venue_provider.venue
        assert created_offer.subcategoryId == "SUPPORT_PHYSIQUE_FILM"
        assert created_offer.audioDisabilityCompliant is True
        assert created_offer.lastProvider.name == venue_provider.provider.name
        assert created_offer.mentalDisabilityCompliant is True
        assert created_offer.motorDisabilityCompliant is True
        assert created_offer.visualDisabilityCompliant is True
        assert created_offer.publicationDatetime == now_datetime_with_tz.replace(tzinfo=None)
        assert created_offer.finalizationDatetime == now_datetime_with_tz.replace(tzinfo=None)
        assert not created_offer.bookingAllowedDatetime
        assert not created_offer.isDuo
        assert created_offer.bookingEmail is None
        assert created_offer.description is None
        assert created_offer.status == offer_mixin.OfferStatus.SOLD_OUT
        assert created_offer.offererAddress.id == venue_provider.venue.offererAddress.id

        assert response.json == {
            "bookingContact": None,
            "bookingEmail": None,
            "categoryRelatedFields": {
                "category": "SUPPORT_PHYSIQUE_FILM",
                "ean": "1234567891234",
            },
            "description": None,
            "accessibility": {
                "audioDisabilityCompliant": True,
                "mentalDisabilityCompliant": True,
                "motorDisabilityCompliant": True,
                "visualDisabilityCompliant": True,
            },
            "enableDoubleBookings": False,
            "externalTicketOfficeUrl": None,
            "id": created_offer.id,
            "image": None,
            "itemCollectionDetails": None,
            "location": {"type": "physical", "venueId": venue_provider.venue.id},
            "name": "Le champ des possibles",
            "status": "SOLD_OUT",
            "stock": None,
            "idAtProvider": None,
        }

    @time_machine.travel(now_datetime_with_tz, tick=False)
    def test_product_creation_with_full_body(self, client, clear_tests_assets_bucket):
        plain_api_key, venue_provider = self.setup_active_venue_provider()

        in_ten_minutes = datetime.datetime.utcnow().replace(second=0, microsecond=0) + datetime.timedelta(minutes=10)
        in_ten_minutes_in_non_utc_tz = date_utils.utc_datetime_to_department_timezone(in_ten_minutes, "973")
        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url,
            json={
                "location": {"type": "physical", "venueId": venue_provider.venue.id},
                "enableDoubleBookings": False,
                "bookingContact": "contact@example.com",
                "bookingEmail": "spam@example.com",
                "categoryRelatedFields": {
                    "category": "SUPPORT_PHYSIQUE_FILM",
                    "ean": "1234567891234",
                },
                "description": "Enregistrement pour la nuit des temps",
                "accessibility": {
                    "audioDisabilityCompliant": True,
                    "mentalDisabilityCompliant": True,
                    "motorDisabilityCompliant": False,
                    "visualDisabilityCompliant": False,
                },
                "externalTicketOfficeUrl": "https://maposaic.com",
                "image": {
                    "credit": "Jean-Crédit Photo",
                    "file": image_data.GOOD_IMAGE,
                },
                "itemCollectionDetails": "A retirer au 6ème sous-sol du parking de la gare entre minuit et 2",
                "name": "Le champ des possibles",
                "stock": {
                    "bookingLimitDatetime": in_ten_minutes_in_non_utc_tz.isoformat(),
                    "price": 1234,
                    "quantity": 3,
                },
                "id_at_provider": "l'id du provider",
            },
        )

        assert response.status_code == 200, response.json

        created_offer = db.session.query(offers_models.Offer).one()
        assert created_offer.name == "Le champ des possibles"
        assert created_offer.venue == venue_provider.venue
        assert created_offer.subcategoryId == "SUPPORT_PHYSIQUE_FILM"
        assert created_offer.audioDisabilityCompliant is True
        assert created_offer.lastProvider == venue_provider.provider
        assert created_offer.mentalDisabilityCompliant is True
        assert created_offer.motorDisabilityCompliant is False
        assert created_offer.visualDisabilityCompliant is False
        assert created_offer.publicationDatetime == now_datetime_with_tz.replace(tzinfo=None)
        assert created_offer.finalizationDatetime == now_datetime_with_tz.replace(tzinfo=None)
        assert not created_offer.bookingAllowedDatetime
        assert created_offer.isDuo is False
        assert created_offer.bookingEmail == "spam@example.com"
        assert created_offer.description == "Enregistrement pour la nuit des temps"
        assert created_offer.idAtProvider == "l'id du provider"
        assert created_offer.externalTicketOfficeUrl == "https://maposaic.com"
        assert created_offer.status == offer_mixin.OfferStatus.ACTIVE
        assert created_offer.withdrawalDetails == "A retirer au 6ème sous-sol du parking de la gare entre minuit et 2"
        assert created_offer.offererAddress.id == venue_provider.venue.offererAddress.id

        created_stock = db.session.query(offers_models.Stock).one()
        assert created_stock.price == decimal.Decimal("12.34")
        assert created_stock.quantity == 3
        assert created_stock.offer == created_offer
        assert created_stock.bookingLimitDatetime == in_ten_minutes

        created_mediation = db.session.query(offers_models.Mediation).one()
        assert created_mediation.offer == created_offer
        assert created_offer.image.url == created_mediation.thumbUrl
        assert (
            created_offer.image.url
            == f"{settings.OBJECT_STORAGE_URL}/thumbs/mediations/{human_ids.humanize(created_mediation.id)}"
        )

        assert response.json == {
            "bookingContact": "contact@example.com",
            "bookingEmail": "spam@example.com",
            "categoryRelatedFields": {
                "ean": "1234567891234",
                "category": "SUPPORT_PHYSIQUE_FILM",
            },
            "description": "Enregistrement pour la nuit des temps",
            "accessibility": {
                "audioDisabilityCompliant": True,
                "mentalDisabilityCompliant": True,
                "motorDisabilityCompliant": False,
                "visualDisabilityCompliant": False,
            },
            "enableDoubleBookings": False,
            "externalTicketOfficeUrl": "https://maposaic.com",
            "id": created_offer.id,
            "idAtProvider": "l'id du provider",
            "image": {
                "credit": "Jean-Crédit Photo",
                "url": f"http://localhost/storage/thumbs/mediations/{human_ids.humanize(created_mediation.id)}",
            },
            "itemCollectionDetails": "A retirer au 6ème sous-sol du parking de la gare entre minuit et 2",
            "location": {"type": "physical", "venueId": venue_provider.venue.id},
            "name": "Le champ des possibles",
            "status": "ACTIVE",
            "stock": {
                "bookedQuantity": 0,
                "bookingLimitDatetime": date_utils.format_into_utc_date(in_ten_minutes),
                "price": 1234,
                "quantity": 3,
            },
        }

    def test_unlimited_quantity(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()

        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url,
            json={
                "location": {"type": "physical", "venueId": venue_provider.venue.id},
                "categoryRelatedFields": {
                    "category": "SUPPORT_PHYSIQUE_FILM",
                    "ean": "1234567891234",
                },
                "accessibility": ACCESSIBILITY_FIELDS,
                "name": "Le champ des possibles",
                "stock": {
                    "bookedQuantity": 0,
                    "price": 1,
                    "quantity": "unlimited",
                },
            },
        )

        assert response.status_code == 200
        created_offer = db.session.query(offers_models.Offer).one()
        assert created_offer.name == "Le champ des possibles"
        assert created_offer.status == offer_mixin.OfferStatus.ACTIVE

        created_stock = db.session.query(offers_models.Stock).one()
        assert created_stock.price == decimal.Decimal("0.01")
        assert created_stock.quantity is None
        assert created_stock.offer == created_offer

    @pytest.mark.parametrize(
        "stock,expected_json",
        [
            ({"price": 12.34, "quantity": "unlimited"}, {"stock.price": ["value is not a valid integer"]}),
            (
                {"price": -1200, "quantity": "unlimited"},
                {"stock.price": ["ensure this value is greater than or equal to 0"]},
            ),
            (
                {"price": 1200, "quantity": -1},
                {"stock.quantity": ["ensure this value is greater than 0", "unexpected value; permitted: 'unlimited'"]},
            ),
        ],
    )
    def test_should_raise_400_because_of_incorrect_price_value(self, client, stock, expected_json):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        payload = self._get_base_payload(venue_provider.venueId)
        payload["stock"] = stock

        response = client.with_explicit_token(plain_api_key).post(self.endpoint_url, json=payload)

        assert response.status_code == 400
        assert response.json == expected_json

    def test_is_duo_not_applicable(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()

        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url,
            json={
                "location": {"type": "physical", "venueId": venue_provider.venue.id},
                "enableDoubleBookings": True,
                "categoryRelatedFields": {
                    "category": "SUPPORT_PHYSIQUE_FILM",
                    "ean": "1234567891234",
                },
                "accessibility": ACCESSIBILITY_FIELDS,
                "name": "Le champ des possibles",
            },
        )
        assert response.status_code == 400
        assert db.session.query(offers_models.Offer).one_or_none() is None
        assert response.json == {"enableDoubleBookings": ["the category chosen does not allow double bookings"]}

    def test_extra_data_deserialization(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()

        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url,
            json={
                "location": {"type": "physical", "venueId": venue_provider.venue.id},
                "categoryRelatedFields": {
                    "category": "SUPPORT_PHYSIQUE_FILM",
                    "ean": "1234567891234",
                },
                "accessibility": ACCESSIBILITY_FIELDS,
                "name": "Le champ des possibles",
            },
        )

        assert response.status_code == 200
        assert response.json["categoryRelatedFields"] == {"category": "SUPPORT_PHYSIQUE_FILM", "ean": "1234567891234"}
        created_offer = db.session.query(offers_models.Offer).one()
        assert created_offer.ean == "1234567891234"
        assert "ean" not in created_offer.extraData

    def test_event_with_custom_address(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        payload = self._get_base_payload(venue_provider.venueId)
        address = geography_factories.AddressFactory()
        offerer_address = offerers_factories.OffererAddressFactory(
            address=address,
            offerer=venue_provider.venue.managingOfferer,
            label="My beautiful address no one knows about",
        )
        payload["location"] = {
            "type": "address",
            "venueId": venue_provider.venueId,
            "addressId": address.id,
            "addressLabel": "My beautiful address no one knows about",
        }

        response = client.with_explicit_token(plain_api_key).post(self.endpoint_url, json=payload)
        assert response.status_code == 200
        assert response.json["location"]["addressId"] == address.id
        assert response.json["location"]["addressLabel"] == "My beautiful address no one knows about"
        created_offer = db.session.query(offers_models.Offer).one()
        assert created_offer.offererAddress == offerer_address

    def test_event_with_custom_address_should_create_offerer_address(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        payload = self._get_base_payload(venue_provider.venueId)
        address = geography_factories.AddressFactory()

        assert (
            not db.session.query(offerers_models.OffererAddress)
            .filter(
                offerers_models.OffererAddress.addressId == address.id,
                offerers_models.OffererAddress.label == "My beautiful address no one knows about",
            )
            .one_or_none()
        )

        payload["location"] = {
            "type": "address",
            "venueId": venue_provider.venueId,
            "addressId": address.id,
            "addressLabel": "My beautiful address no one knows about",
        }
        response = client.with_explicit_token(plain_api_key).post(self.endpoint_url, json=payload)
        assert response.status_code == 200
        created_offer = db.session.query(offers_models.Offer).one()
        offerer_address = (
            db.session.query(offerers_models.OffererAddress)
            .filter(
                offerers_models.OffererAddress.addressId == address.id,
                offerers_models.OffererAddress.label == "My beautiful address no one knows about",
            )
            .one()
        )
        assert created_offer.offererAddress == offerer_address

    def test_event_with_custom_address_should_raiser_404_because_address_does_not_exist(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider(provider_has_ticketing_urls=False)
        payload = self._get_base_payload(venue_provider.venueId)
        address = geography_factories.AddressFactory()
        not_existing_address_id = address.id + 1

        payload["location"] = {
            "type": "address",
            "venueId": venue_provider.venueId,
            "addressId": not_existing_address_id,
        }
        response = client.with_explicit_token(plain_api_key).post(self.endpoint_url, json=payload)
        assert response.status_code == 404
        assert response.json == {
            "location.AddressLocation.addressId": [f"There is no address with id {not_existing_address_id}"]
        }

    def test_event_category_not_accepted(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()

        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url,
            json={
                "location": {"type": "physical", "venueId": venue_provider.venue.id},
                "categoryRelatedFields": {"category": "EVENEMENT_JEU"},
                "accessibility": ACCESSIBILITY_FIELDS,
                "name": "Le champ des possibles",
            },
        )

        assert response.status_code == 400
        assert "categoryRelatedFields.category" in response.json
        assert db.session.query(offers_models.Offer).first() is None

    def test_offer_with_ean_in_name_is_not_accepted(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()

        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url,
            json={
                "location": {
                    "type": "digital",
                    "venueId": venue_provider.venue.id,
                    "url": "https://monebook.com/le-visible",
                },
                "categoryRelatedFields": {"category": "LIVRE_NUMERIQUE"},
                "accessibility": ACCESSIBILITY_FIELDS,
                "name": "Le Visible et l'invisible - Suivi de notes de travail - 9782070286256",
            },
        )

        assert response.status_code == 400
        assert response.json["name"] == ["Le titre d'une offre ne peut contenir l'EAN"]

    def test_offer_with_description_more_than_10000_characters_long_is_not_accepted(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()

        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url,
            json={
                "location": {
                    "type": "digital",
                    "venueId": venue_provider.venue.id,
                    "url": "https://monebook.com/le-visible",
                },
                "categoryRelatedFields": {"category": "LIVRE_NUMERIQUE"},
                "accessibility": ACCESSIBILITY_FIELDS,
                "name": "Jean Tartine est de retour",
                "description": "A" * 10_001,
            },
        )

        assert response.status_code == 400
        assert response.json["description"] == ["ensure this value has at most 10000 characters"]

    def test_venue_allowed(self, client):
        not_allowed_venue = offerers_factories.VenueFactory()
        plain_api_key, _ = self.setup_active_venue_provider()

        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url,
            json={
                "location": {"type": "physical", "venueId": not_allowed_venue.id},
                "categoryRelatedFields": {
                    "category": "SUPPORT_PHYSIQUE_FILM",
                    "ean": "1234567891234",
                },
                "accessibility": ACCESSIBILITY_FIELDS,
                "name": "Le champ des possibles",
            },
        )

        assert response.status_code == 404
        assert response.json == {"global": "Venue cannot be found"}
        assert db.session.query(offers_models.Offer).first() is None

    @pytest.mark.usefixtures("clean_database")
    @mock.patch("pcapi.core.offers.api.create_thumb", side_effect=Exception)
    # this test needs "clean_database" instead of "db_session" fixture because with the latter, the mediation would still be present in databse
    def test_no_objects_saved_on_image_error(self, create_thumb_mock, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()

        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url,
            json={
                "location": {"type": "physical", "venueId": venue_provider.venue.id},
                "stock": {"quantity": 1, "price": 100},
                "categoryRelatedFields": {
                    "category": "SUPPORT_PHYSIQUE_FILM",
                    "ean": "1234567891234",
                },
                "accessibility": ACCESSIBILITY_FIELDS,
                "name": "Le champ des possibles",
                "image": {"file": image_data.GOOD_IMAGE},
            },
        )

        assert response.status_code == 500
        assert response.json == {}

        assert db.session.query(offers_models.Offer).first() is None
        assert db.session.query(offers_models.Stock).first() is None

    @pytest.mark.usefixtures("clean_database")
    def test_image_too_small(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()

        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url,
            json={
                "location": {"type": "physical", "venueId": venue_provider.venue.id},
                "categoryRelatedFields": {
                    "category": "SUPPORT_PHYSIQUE_FILM",
                    "ean": "1234567891234",
                },
                "accessibility": ACCESSIBILITY_FIELDS,
                "name": "Le champ des possibles",
                "image": {"file": image_data.WRONG_IMAGE_SIZE},
                "stock": {"quantity": 1, "price": 100},
            },
        )

        assert response.status_code == 400
        assert response.json == {"imageFile": "The image is too small. It must be above 400x600 pixels."}

        assert db.session.query(offers_models.Offer).first() is None
        assert db.session.query(offers_models.Stock).first() is None

    @pytest.mark.usefixtures("clean_database")
    def test_bad_image_ratio(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()

        image_bytes = (pathlib.Path(tests.__path__[0]) / "files" / "mouette_square.jpg").read_bytes()
        encoded_bytes = base64.b64encode(image_bytes)

        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url,
            json={
                "location": {"type": "physical", "venueId": venue_provider.venue.id},
                "categoryRelatedFields": {
                    "category": "SUPPORT_PHYSIQUE_FILM",
                    "ean": "1234567891234",
                },
                "accessibility": ACCESSIBILITY_FIELDS,
                "name": "Le champ des possibles",
                "image": {"file": encoded_bytes.decode()},
                "stock": {"quantity": 1, "price": 100},
            },
        )

        assert response.status_code == 400
        assert response.json == {"imageFile": "Bad image ratio: expected 0.66, found 1.0"}

        assert db.session.query(offers_models.Offer).first() is None
        assert db.session.query(offers_models.Stock).first() is None

    def test_stock_booking_limit_without_timezone(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()

        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url,
            json={
                "location": {"type": "physical", "venueId": venue_provider.venue.id},
                "categoryRelatedFields": {
                    "category": "SUPPORT_PHYSIQUE_FILM",
                    "ean": "1234567891234",
                },
                "accessibility": ACCESSIBILITY_FIELDS,
                "name": "Le champ des possibles",
                "stock": {"bookingLimitDatetime": "2021-01-01T00:00:00", "price": 10, "quantity": 10},
            },
        )

        assert response.status_code == 400

        assert response.json == {
            "stock.bookingLimitDatetime": ["The datetime must be timezone-aware."],
        }

    def test_not_allowed_categories(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()

        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url,
            json={
                "location": {
                    "type": "digital",
                    "url": "https://la-flute-en-chantier.fr",
                    "venue_id": venue_provider.id,
                },
                "categoryRelatedFields": {"category": "CARTE_CINE_ILLIMITE", "showType": "OPERA-GRAND_OPERA"},
                "accessibility": ACCESSIBILITY_FIELDS,
                "name": "La flûte en chantier",
            },
        )

        assert response.status_code == 400
        assert response.json == {
            "categoryRelatedFields.category": [
                "unexpected value; permitted: 'ABO_BIBLIOTHEQUE'",
                "unexpected value; permitted: 'ABO_CONCERT'",
                "unexpected value; permitted: 'ABO_LIVRE_NUMERIQUE'",
                "unexpected value; permitted: 'ABO_MEDIATHEQUE'",
                "unexpected value; permitted: 'ABO_PLATEFORME_MUSIQUE'",
                "unexpected value; permitted: 'ABO_PLATEFORME_VIDEO'",
                "unexpected value; permitted: 'ABO_PRATIQUE_ART'",
                "unexpected value; permitted: 'ABO_PRESSE_EN_LIGNE'",
                "unexpected value; permitted: 'ABO_SPECTACLE'",
                "unexpected value; permitted: 'ACHAT_INSTRUMENT'",
                "unexpected value; permitted: 'APP_CULTURELLE'",
                "unexpected value; permitted: 'AUTRE_SUPPORT_NUMERIQUE'",
                "unexpected value; permitted: 'CARTE_JEUNES'",
                "unexpected value; permitted: 'CARTE_MUSEE'",
                "unexpected value; permitted: 'LIVRE_AUDIO_PHYSIQUE'",
                "unexpected value; permitted: 'LIVRE_NUMERIQUE'",
                "unexpected value; permitted: 'LOCATION_INSTRUMENT'",
                "unexpected value; permitted: 'PARTITION'",
                "unexpected value; permitted: 'PLATEFORME_PRATIQUE_ARTISTIQUE'",
                "unexpected value; permitted: 'PODCAST'",
                "unexpected value; permitted: 'PRATIQUE_ART_VENTE_DISTANCE'",
                "unexpected value; permitted: 'SPECTACLE_ENREGISTRE'",
                "unexpected value; permitted: 'SUPPORT_PHYSIQUE_FILM'",
                "unexpected value; permitted: 'TELECHARGEMENT_LIVRE_AUDIO'",
                "unexpected value; permitted: 'TELECHARGEMENT_MUSIQUE'",
                "unexpected value; permitted: 'VISITE_VIRTUELLE'",
                "unexpected value; permitted: 'VOD'",
            ],
            "categoryRelatedFields.ean": [
                "field required",
                "field required",
                "field required",
                "field required",
                "field required",
            ],
            "categoryRelatedFields.musicType": ["field required", "field required"],
        }
        assert db.session.query(offers_models.Offer).first() is None

    def test_books_are_not_allowed(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()

        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url,
            json={
                "location": {"type": "physical", "venueId": venue_provider.venue.id},
                "categoryRelatedFields": {
                    "category": "LIVRE_PAPIER",
                    "ean": "1234567890123",
                    "author": "Maurice",
                },
                "accessibility": ACCESSIBILITY_FIELDS,
                "name": "A qui mieux mieux",
            },
        )

        assert response.status_code == 400
        assert db.session.query(offers_models.Offer).count() == 0

    def test_create_allowed_product(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()

        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url,
            json={
                "location": {
                    "type": "digital",
                    "url": "https://la-flute-en-chantier.fr",
                    "venue_id": venue_provider.venue.id,
                },
                "categoryRelatedFields": {"category": "SPECTACLE_ENREGISTRE", "showType": "OPERA-GRAND_OPERA"},
                "accessibility": ACCESSIBILITY_FIELDS,
                "name": "La flûte en chantier",
            },
        )

        assert response.status_code == 200
        assert db.session.query(offers_models.Offer).count() == 1

    def test_unique_venue_and_id_at_provider_violation(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        auth_client = client.with_explicit_token(plain_api_key)

        offer = offers_factories.OfferFactory(venue=venue_provider.venue, idAtProvider="some_id")

        payload = self._get_base_payload(venue_provider.venue.id)
        payload["idAtProvider"] = offer.idAtProvider
        response = auth_client.post(self.endpoint_url, json=payload)

        assert response.status_code == 400
