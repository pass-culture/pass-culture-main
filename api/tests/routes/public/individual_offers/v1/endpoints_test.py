import base64
import datetime
import decimal
import pathlib
from unittest import mock

import freezegun
import pytest

from pcapi import settings
from pcapi.core import testing
from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.models import offer_mixin
from pcapi.utils import human_ids

import tests
from tests import conftest
from tests.routes import image_data


ACCESSIBILITY_FIELDS = {
    "audioDisabilityCompliant": True,
    "mentalDisabilityCompliant": True,
    "motorDisabilityCompliant": True,
    "visualDisabilityCompliant": True,
}


class PostProductTest:
    @pytest.mark.usefixtures("db_session")
    def test_physical_product_minimal_body(self, client):
        api_key = offerers_factories.ApiKeyFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=api_key.offerer)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products",
            json={
                "categoryRelatedFields": {"category": "LIVRE_PAPIER"},
                "accessibility": ACCESSIBILITY_FIELDS,
                "location": {"type": "physical", "venueId": venue.id},
                "name": "Le champ des possibles",
            },
        )

        assert response.status_code == 200
        created_offer = offers_models.Offer.query.one()
        assert created_offer.name == "Le champ des possibles"
        assert created_offer.venue == venue
        assert created_offer.subcategoryId == "LIVRE_PAPIER"
        assert created_offer.audioDisabilityCompliant is True
        assert created_offer.lastProvider.name == "Individual Offers public API"
        assert created_offer.mentalDisabilityCompliant is True
        assert created_offer.motorDisabilityCompliant is True
        assert created_offer.visualDisabilityCompliant is True
        assert not created_offer.isDuo
        assert created_offer.extraData == {}
        assert created_offer.bookingEmail is None
        assert created_offer.description is None
        assert created_offer.status == offer_mixin.OfferStatus.SOLD_OUT

        assert response.json == {
            "bookingEmail": None,
            "categoryRelatedFields": {"author": None, "category": "LIVRE_PAPIER", "isbn": None},
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
            "location": {"type": "physical", "venueId": venue.id},
            "name": "Le champ des possibles",
            "status": "SOLD_OUT",
            "stock": None,
        }

    @pytest.mark.usefixtures("db_session")
    @freezegun.freeze_time("2022-01-01 12:00:00")
    def test_offer_creation_with_full_body(self, client, clear_tests_assets_bucket):
        api_key = offerers_factories.ApiKeyFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=api_key.offerer)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products",
            json={
                "enableDoubleBookings": False,
                "bookingEmail": "spam@example.com",
                "categoryRelatedFields": {
                    "author": "Maurice",
                    "category": "SUPPORT_PHYSIQUE_MUSIQUE",
                    "musicType": "JAZZ-FUSION",
                    "performer": "Pink Pâtisserie",
                    "stageDirector": "Alfred",  # field not applicable
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
                "location": {"type": "physical", "venueId": venue.id},
                "name": "Le champ des possibles",
                "stock": {
                    "bookingLimitDatetime": "2022-01-01T00:00:00+04:00",
                    "price": 1234,
                    "quantity": 3,
                },
            },
        )

        assert response.status_code == 200
        created_offer = offers_models.Offer.query.one()
        assert created_offer.name == "Le champ des possibles"
        assert created_offer.venue == venue
        assert created_offer.subcategoryId == "SUPPORT_PHYSIQUE_MUSIQUE"
        assert created_offer.audioDisabilityCompliant is True
        assert created_offer.lastProvider.name == "Individual Offers public API"
        assert created_offer.mentalDisabilityCompliant is True
        assert created_offer.motorDisabilityCompliant is False
        assert created_offer.visualDisabilityCompliant is False
        assert created_offer.isDuo is False
        assert created_offer.extraData == {
            "author": "Maurice",
            "musicType": "501",
            "musicSubType": "511",
            "performer": "Pink Pâtisserie",
        }
        assert created_offer.bookingEmail == "spam@example.com"
        assert created_offer.description == "Enregistrement pour la nuit des temps"
        assert created_offer.externalTicketOfficeUrl == "https://maposaic.com"
        assert created_offer.status == offer_mixin.OfferStatus.EXPIRED
        assert created_offer.withdrawalDetails == "A retirer au 6ème sous-sol du parking de la gare entre minuit et 2"

        created_stock = offers_models.Stock.query.one()
        assert created_stock.price == decimal.Decimal("12.34")
        assert created_stock.quantity == 3
        assert created_stock.offer == created_offer
        assert created_stock.bookingLimitDatetime == datetime.datetime(2021, 12, 31, 20, 0, 0)

        created_mediation = offers_models.Mediation.query.one()
        assert created_mediation.offer == created_offer
        assert created_offer.image.url == created_mediation.thumbUrl
        assert (
            created_offer.image.url
            == f"{settings.OBJECT_STORAGE_URL}/thumbs/mediations/{human_ids.humanize(created_mediation.id)}"
        )

        assert response.json == {
            "bookingEmail": "spam@example.com",
            "categoryRelatedFields": {
                "author": "Maurice",
                "category": "SUPPORT_PHYSIQUE_MUSIQUE",
                "musicType": "JAZZ-FUSION",
                "performer": "Pink Pâtisserie",
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
            "image": {
                "credit": "Jean-Crédit Photo",
                "url": f"http://localhost/storage/thumbs/mediations/{human_ids.humanize(created_mediation.id)}",
            },
            "itemCollectionDetails": "A retirer au 6ème sous-sol du parking de la gare entre minuit et 2",
            "location": {"type": "physical", "venueId": venue.id},
            "name": "Le champ des possibles",
            "status": "EXPIRED",
            "stock": {
                "bookedQuantity": 0,
                "bookingLimitDatetime": "2021-12-31T20:00:00Z",
                "price": 1234,
                "quantity": 3,
            },
        }

    @pytest.mark.usefixtures("db_session")
    def test_unlimited_quantity(self, client):
        api_key = offerers_factories.ApiKeyFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=api_key.offerer)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products",
            json={
                "categoryRelatedFields": {"category": "SUPPORT_PHYSIQUE_FILM"},
                "accessibility": ACCESSIBILITY_FIELDS,
                "location": {"type": "physical", "venueId": venue.id},
                "name": "Le champ des possibles",
                "stock": {
                    "bookedQuantity": 0,
                    "price": 1,
                    "quantity": "unlimited",
                },
            },
        )

        assert response.status_code == 200
        created_offer = offers_models.Offer.query.one()
        assert created_offer.name == "Le champ des possibles"
        assert created_offer.status == offer_mixin.OfferStatus.ACTIVE

        created_stock = offers_models.Stock.query.one()
        assert created_stock.price == decimal.Decimal("0.01")
        assert created_stock.quantity == None
        assert created_stock.offer == created_offer

    @pytest.mark.usefixtures("db_session")
    def test_price_must_be_integer_strict(self, client):
        api_key = offerers_factories.ApiKeyFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=api_key.offerer)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products",
            json={
                "categoryRelatedFields": {"category": "SUPPORT_PHYSIQUE_FILM"},
                "accessibility": ACCESSIBILITY_FIELDS,
                "location": {"type": "physical", "venueId": venue.id},
                "name": "Le champ des possibles",
                "stock": {
                    "price": 12.34,
                    "quantity": "unlimited",
                },
            },
        )

        assert response.status_code == 400
        assert response.json == {"stock.price": ["Saisissez un nombre valide"]}

    @pytest.mark.usefixtures("db_session")
    def test_price_must_be_positive(self, client):
        api_key = offerers_factories.ApiKeyFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=api_key.offerer)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products",
            json={
                "categoryRelatedFields": {"category": "SUPPORT_PHYSIQUE_FILM"},
                "accessibility": ACCESSIBILITY_FIELDS,
                "location": {"type": "physical", "venueId": venue.id},
                "name": "Le champ des possibles",
                "stock": {
                    "price": -1200,
                    "quantity": "unlimited",
                },
            },
        )

        assert response.status_code == 400
        assert response.json == {"stock.price": ["Value must be positive"]}

    @pytest.mark.usefixtures("db_session")
    def test_quantity_must_be_positive(self, client):
        api_key = offerers_factories.ApiKeyFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=api_key.offerer)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products",
            json={
                "categoryRelatedFields": {"category": "SUPPORT_PHYSIQUE_FILM"},
                "accessibility": ACCESSIBILITY_FIELDS,
                "location": {"type": "physical", "venueId": venue.id},
                "name": "Le champ des possibles",
                "stock": {
                    "price": 1200,
                    "quantity": -1,
                },
            },
        )

        assert response.status_code == 400
        assert response.json == {"stock.quantity": ["Value must be positive"]}

    @pytest.mark.usefixtures("db_session")
    def test_is_duo_not_applicable(self, client):
        api_key = offerers_factories.ApiKeyFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=api_key.offerer)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products",
            json={
                "enableDoubleBookings": True,
                "categoryRelatedFields": {"category": "SPECTACLE_ENREGISTRE", "showType": "HUMOUR-VENTRILOQUE"},
                "accessibility": ACCESSIBILITY_FIELDS,
                "location": {"type": "physical", "venueId": venue.id},
                "name": "Le champ des possibles",
            },
        )
        assert response.status_code == 400
        assert offers_models.Offer.query.one_or_none() is None
        assert response.json == {"enableDoubleBookings": ["the category chosen does not allow double bookings"]}

    @pytest.mark.usefixtures("db_session")
    @testing.override_features(WIP_ENABLE_OFFER_CREATION_API_V1=False)
    def test_api_disabled(self, client):
        api_key = offerers_factories.ApiKeyFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=api_key.offerer)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products",
            json={
                "categoryRelatedFields": {"category": "LIVRE_PAPIER"},
                "accessibility": ACCESSIBILITY_FIELDS,
                "location": {"type": "physical", "venueId": venue.id},
                "name": "Le champ des possibles",
            },
        )

        assert response.status_code == 400
        assert offers_models.Offer.query.first() is None
        assert response.json == {"global": ["This API is not enabled"]}

    @pytest.mark.usefixtures("db_session")
    def test_digital_product(self, client):
        api_key = offerers_factories.ApiKeyFactory()
        venue = offerers_factories.VirtualVenueFactory(managingOfferer=api_key.offerer)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products",
            json={
                "categoryRelatedFields": {"category": "VOD"},
                "accessibility": ACCESSIBILITY_FIELDS,
                "location": {"type": "digital", "url": "https://example.com"},
                "name": "Le champ des possibles",
            },
        )

        assert response.status_code == 200
        created_offer = offers_models.Offer.query.one()
        assert created_offer.name == "Le champ des possibles"
        assert created_offer.venue == venue
        assert created_offer.subcategoryId == "VOD"
        assert created_offer.audioDisabilityCompliant is True
        assert created_offer.mentalDisabilityCompliant is True
        assert created_offer.motorDisabilityCompliant is True
        assert created_offer.visualDisabilityCompliant is True
        assert created_offer.url == "https://example.com"
        assert created_offer.extraData == {}

        assert response.json == {
            "bookingEmail": None,
            "categoryRelatedFields": {"category": "VOD"},
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
            "location": {"type": "digital", "url": "https://example.com"},
            "name": "Le champ des possibles",
            "status": "SOLD_OUT",
            "stock": None,
        }

    @pytest.mark.usefixtures("db_session")
    def test_extra_data_deserialization(self, client):
        api_key = offerers_factories.ApiKeyFactory()
        offerers_factories.VirtualVenueFactory(managingOfferer=api_key.offerer)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products",
            json={
                "categoryRelatedFields": {
                    "author": "Maurice",
                    "category": "CINE_VENTE_DISTANCE",
                    "stageDirector": "Alfred",
                    "isbn": "1234567891123",  # this field is not applicable and not added to extraData
                },
                "accessibility": ACCESSIBILITY_FIELDS,
                "location": {"type": "digital", "url": "https://example.com"},
                "name": "Le champ des possibles",
            },
        )

        assert response.status_code == 200
        created_offer = offers_models.Offer.query.one()

        assert created_offer.extraData == {"author": "Maurice", "stageDirector": "Alfred"}

        assert response.json["categoryRelatedFields"] == {
            "author": "Maurice",
            "category": "CINE_VENTE_DISTANCE",
            "stageDirector": "Alfred",
            "visa": None,
        }

    @pytest.mark.usefixtures("db_session")
    def test_physical_product_attached_to_digital_venue(self, client):
        api_key = offerers_factories.ApiKeyFactory()
        venue = offerers_factories.VirtualVenueFactory(managingOfferer=api_key.offerer)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products",
            json={
                "categoryRelatedFields": {"category": "SUPPORT_PHYSIQUE_MUSIQUE", "musicType": "CHANSON_VARIETE-OTHER"},
                "accessibility": ACCESSIBILITY_FIELDS,
                "location": {"type": "physical", "venueId": venue.id},
                "name": "Le champ des possibles",
            },
        )

        assert response.status_code == 400
        assert response.json == {"venue": ['Une offre physique ne peut être associée au lieu "Offre numérique"']}
        assert offers_models.Offer.query.first() is None

    @pytest.mark.usefixtures("db_session")
    def test_physical_product_with_digital_category(self, client):
        api_key = offerers_factories.ApiKeyFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=api_key.offerer)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products",
            json={
                "categoryRelatedFields": {"category": "CINE_VENTE_DISTANCE"},
                "accessibility": ACCESSIBILITY_FIELDS,
                "location": {"type": "physical", "venueId": venue.id},
                "name": "Le champ des possibles",
            },
        )

        assert response.status_code == 400
        assert response.json == {
            "subcategory": ['Une offre de catégorie CINE_VENTE_DISTANCE doit contenir un champ "url"']
        }
        assert offers_models.Offer.query.first() is None

    @pytest.mark.usefixtures("db_session")
    def test_right_isbn_format(self, client):
        api_key = offerers_factories.ApiKeyFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=api_key.offerer)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products",
            json={
                "categoryRelatedFields": {"category": "LIVRE_AUDIO_PHYSIQUE", "isbn": "1234567891123"},
                "accessibility": ACCESSIBILITY_FIELDS,
                "location": {"type": "physical", "venueId": venue.id},
                "name": "Le champ des possibles",
            },
        )

        assert response.status_code == 200
        created_offer = offers_models.Offer.query.one()

        assert created_offer.extraData == {"isbn": "1234567891123"}
        assert response.json["categoryRelatedFields"] == {
            "author": None,
            "category": "LIVRE_AUDIO_PHYSIQUE",
            "isbn": "1234567891123",
        }

    @pytest.mark.usefixtures("db_session")
    def test_wrong_isbn_format(self, client):
        api_key = offerers_factories.ApiKeyFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=api_key.offerer)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products",
            json={
                "categoryRelatedFields": {"category": "LIVRE_AUDIO_PHYSIQUE", "isbn": "123456789"},
                "accessibility": ACCESSIBILITY_FIELDS,
                "location": {"type": "physical", "venueId": venue.id},
                "name": "Le champ des possibles",
            },
        )

        assert response.status_code == 400
        assert response.json == {
            "categoryRelatedFields.LIVRE_AUDIO_PHYSIQUE.isbn": ['string does not match regex "^(\\d){13}$"']
        }
        assert offers_models.Offer.query.first() is None

    @pytest.mark.usefixtures("db_session")
    def test_event_category_not_accepted(self, client):
        api_key = offerers_factories.ApiKeyFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=api_key.offerer)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products",
            json={
                "categoryRelatedFields": {"category": "EVENEMENT_JEU"},
                "accessibility": ACCESSIBILITY_FIELDS,
                "location": {"type": "physical", "venueId": venue.id},
                "name": "Le champ des possibles",
            },
        )

        assert response.status_code == 400
        assert "categoryRelatedFields" in response.json
        assert offers_models.Offer.query.first() is None

    @pytest.mark.usefixtures("db_session")
    def test_venue_allowed(self, client):
        offerers_factories.ApiKeyFactory()
        not_allowed_venue = offerers_factories.VenueFactory()

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products",
            json={
                "categoryRelatedFields": {"category": "LIVRE_AUDIO_PHYSIQUE"},
                "accessibility": ACCESSIBILITY_FIELDS,
                "location": {"type": "physical", "venueId": not_allowed_venue.id},
                "name": "Le champ des possibles",
            },
        )

        assert response.status_code == 404
        assert response.json == {"venueId": ["There is no venue with this id associated to your API key"]}
        assert offers_models.Offer.query.first() is None

    @conftest.clean_database
    @mock.patch("pcapi.core.offers.api.create_thumb", side_effect=Exception)
    # this test needs "clean_database" instead of "db_session" fixture because with the latter, the mediation would still be present in databse
    def test_no_objects_saved_on_image_error(self, create_thumb_mock, client):
        api_key = offerers_factories.ApiKeyFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=api_key.offerer)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products",
            json={
                "categoryRelatedFields": {"category": "LIVRE_PAPIER"},
                "accessibility": ACCESSIBILITY_FIELDS,
                "location": {"type": "physical", "venueId": venue.id},
                "name": "Le champ des possibles",
                "image": {"file": image_data.GOOD_IMAGE},
                "stock": {"quantity": 1, "price": 100},
            },
        )

        assert response.status_code == 500
        assert response.json == {}

        assert offers_models.Offer.query.first() is None
        assert offers_models.Stock.query.first() is None

    @conftest.clean_database
    def test_image_too_small(self, client):
        api_key = offerers_factories.ApiKeyFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=api_key.offerer)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products",
            json={
                "categoryRelatedFields": {"category": "LIVRE_PAPIER"},
                "accessibility": ACCESSIBILITY_FIELDS,
                "location": {"type": "physical", "venueId": venue.id},
                "name": "Le champ des possibles",
                "image": {"file": image_data.WRONG_IMAGE_SIZE},
                "stock": {"quantity": 1, "price": 100},
            },
        )

        assert response.status_code == 400
        assert response.json == {"imageFile": "The image is too small. It must be It must be above 400x600 pixels."}

        assert offers_models.Offer.query.first() is None
        assert offers_models.Stock.query.first() is None

    @conftest.clean_database
    def test_bad_image_ratio(self, client):
        api_key = offerers_factories.ApiKeyFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=api_key.offerer)

        image_bytes = (pathlib.Path(tests.__path__[0]) / "files" / "mouette_square.jpg").read_bytes()
        encoded_bytes = base64.b64encode(image_bytes)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products",
            json={
                "categoryRelatedFields": {"category": "LIVRE_PAPIER"},
                "accessibility": ACCESSIBILITY_FIELDS,
                "location": {"type": "physical", "venueId": venue.id},
                "name": "Le champ des possibles",
                "image": {"file": encoded_bytes.decode()},
                "stock": {"quantity": 1, "price": 100},
            },
        )

        assert response.status_code == 400
        assert response.json == {"imageFile": "Bad image ratio: expected 0.66, found 1.0"}

        assert offers_models.Offer.query.first() is None
        assert offers_models.Stock.query.first() is None

    @pytest.mark.usefixtures("db_session")
    def test_stock_booking_limit_without_timezone(self, client):
        api_key = offerers_factories.ApiKeyFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=api_key.offerer)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products",
            json={
                "categoryRelatedFields": {"category": "LIVRE_PAPIER"},
                "accessibility": ACCESSIBILITY_FIELDS,
                "location": {"type": "physical", "venueId": venue.id},
                "name": "Le champ des possibles",
                "stock": {"bookingLimitDatetime": "2021-01-01T00:00:00", "price": 10, "quantity": 10},
            },
        )

        assert response.status_code == 400

        assert response.json == {
            "stock.bookingLimitDatetime": ["The datetime must be timezone-aware."],
        }

    @pytest.mark.usefixtures("db_session")
    def test_show_type_deserialization(self, client):
        api_key = offerers_factories.ApiKeyFactory()
        offerers_factories.VirtualVenueFactory(managingOfferer=api_key.offerer)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products",
            json={
                "categoryRelatedFields": {"category": "SPECTACLE_ENREGISTRE", "showType": "OPERA-GRAND_OPERA"},
                "accessibility": ACCESSIBILITY_FIELDS,
                "location": {"type": "digital", "url": "https://la-flute-en-chantier.fr"},
                "name": "La flûte en chantier",
            },
        )

        assert response.status_code == 200
        created_offer = offers_models.Offer.query.one()
        assert created_offer.extraData == {"showSubType": "1512", "showType": "1510"}


class PostEventTest:
    @pytest.mark.usefixtures("db_session")
    def test_event_minimal_body(self, client):
        api_key = offerers_factories.ApiKeyFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=api_key.offerer)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/events",
            json={
                "categoryRelatedFields": {"category": "RENCONTRE"},
                "accessibility": ACCESSIBILITY_FIELDS,
                "location": {"type": "physical", "venueId": venue.id},
                "name": "Le champ des possibles",
            },
        )

        assert response.status_code == 200
        created_offer = offers_models.Offer.query.one()
        assert created_offer.name == "Le champ des possibles"
        assert created_offer.venue == venue
        assert created_offer.subcategoryId == "RENCONTRE"
        assert created_offer.audioDisabilityCompliant is True
        assert created_offer.lastProvider.name == "Individual Offers public API"
        assert created_offer.mentalDisabilityCompliant is True
        assert created_offer.motorDisabilityCompliant is True
        assert created_offer.visualDisabilityCompliant is True
        assert not created_offer.isDuo
        assert created_offer.extraData == {}
        assert created_offer.bookingEmail is None
        assert created_offer.description is None
        assert created_offer.status == offer_mixin.OfferStatus.SOLD_OUT
        assert created_offer.withdrawalDetails is None
        assert created_offer.withdrawalType is None
        assert created_offer.withdrawalDelay is None

    @pytest.mark.usefixtures("db_session")
    @freezegun.freeze_time("2022-01-01 12:00:00")
    def test_event_creation_with_full_body(self, client, clear_tests_assets_bucket):
        api_key = offerers_factories.ApiKeyFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=api_key.offerer)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/events",
            json={
                "enableDoubleBookings": True,
                "bookingEmail": "nicoj@example.com",
                "categoryRelatedFields": {
                    "author": "Ray Charles",
                    "category": "CONCERT",
                    "musicType": "ELECTRO-HOUSE",
                    "performer": "Nicolas Jaar",
                    "stageDirector": "Alfred",  # field not applicable
                },
                "description": "Space is only noise if you can see",
                "eventDuration": 120,
                "accessibility": {
                    "audioDisabilityCompliant": False,
                    "mentalDisabilityCompliant": True,
                    "motorDisabilityCompliant": True,
                    "visualDisabilityCompliant": True,
                },
                "externalTicketOfficeUrl": "https://maposaic.com",
                "image": {
                    "credit": "Jean-Crédit Photo",
                    "file": image_data.GOOD_IMAGE,
                },
                "itemCollectionDetails": "A retirer au 6ème sous-sol du parking de la gare entre minuit et 2",
                "location": {"type": "physical", "venueId": venue.id},
                "name": "Nicolas Jaar dans ton salon",
                "ticketCollection": {"way": "by_email", "daysBeforeEvent": 1},
            },
        )

        assert response.status_code == 200
        created_offer = offers_models.Offer.query.one()
        assert created_offer.lastProvider.name == "Individual Offers public API"
        assert created_offer.name == "Nicolas Jaar dans ton salon"
        assert created_offer.venue == venue
        assert created_offer.subcategoryId == "CONCERT"
        assert created_offer.audioDisabilityCompliant is False
        assert created_offer.mentalDisabilityCompliant is True
        assert created_offer.motorDisabilityCompliant is True
        assert created_offer.visualDisabilityCompliant is True
        assert created_offer.isDuo is True
        assert created_offer.extraData == {
            "author": "Ray Charles",
            "musicType": "880",
            "musicSubType": "894",
            "performer": "Nicolas Jaar",
        }
        assert created_offer.bookingEmail == "nicoj@example.com"
        assert created_offer.description == "Space is only noise if you can see"
        assert created_offer.externalTicketOfficeUrl == "https://maposaic.com"
        assert created_offer.status == offer_mixin.OfferStatus.SOLD_OUT
        assert created_offer.withdrawalDetails == "A retirer au 6ème sous-sol du parking de la gare entre minuit et 2"
        assert created_offer.withdrawalType == offers_models.WithdrawalTypeEnum.BY_EMAIL
        assert created_offer.withdrawalDelay == 86400

        created_mediation = offers_models.Mediation.query.one()
        assert created_mediation.offer == created_offer
        assert created_offer.image.url == created_mediation.thumbUrl
        assert (
            created_offer.image.url
            == f"{settings.OBJECT_STORAGE_URL}/thumbs/mediations/{human_ids.humanize(created_mediation.id)}"
        )

        assert response.json == {
            "accessibility": {
                "audioDisabilityCompliant": False,
                "mentalDisabilityCompliant": True,
                "motorDisabilityCompliant": True,
                "visualDisabilityCompliant": True,
            },
            "bookingEmail": "nicoj@example.com",
            "categoryRelatedFields": {
                "author": "Ray Charles",
                "category": "CONCERT",
                "musicType": "ELECTRO-HOUSE",
                "performer": "Nicolas Jaar",
            },
            "description": "Space is only noise if you can see",
            "enableDoubleBookings": True,
            "eventDuration": 120,
            "externalTicketOfficeUrl": "https://maposaic.com",
            "id": created_offer.id,
            "image": {
                "credit": "Jean-Crédit Photo",
                "url": f"http://localhost/storage/thumbs/mediations/{human_ids.humanize(created_mediation.id)}",
            },
            "itemCollectionDetails": "A retirer au 6ème sous-sol du parking de la gare entre minuit et 2",
            "location": {"type": "physical", "venueId": venue.id},
            "name": "Nicolas Jaar dans ton salon",
            "status": "SOLD_OUT",
            "ticketCollection": {"daysBeforeEvent": 1, "way": "by_email"},
        }

    @pytest.mark.usefixtures("db_session")
    def test_event_without_ticket(self, client):
        api_key = offerers_factories.ApiKeyFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=api_key.offerer)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/events",
            json={
                "categoryRelatedFields": {"category": "FESTIVAL_ART_VISUEL"},
                "accessibility": ACCESSIBILITY_FIELDS,
                "location": {"type": "physical", "venueId": venue.id},
                "name": "Le champ des possibles",
                "ticketCollection": None,
            },
        )

        assert response.status_code == 200
        created_offer = offers_models.Offer.query.one()
        assert created_offer.withdrawalType == offers_models.WithdrawalTypeEnum.NO_TICKET

    @pytest.mark.usefixtures("db_session")
    def test_event_with_on_site_ticket(self, client):
        api_key = offerers_factories.ApiKeyFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=api_key.offerer)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/events",
            json={
                "categoryRelatedFields": {"category": "FESTIVAL_ART_VISUEL"},
                "accessibility": ACCESSIBILITY_FIELDS,
                "location": {"type": "physical", "venueId": venue.id},
                "name": "Le champ des possibles",
                "ticketCollection": {"way": "on_site", "minutesBeforeEvent": 30},
            },
        )

        assert response.status_code == 200
        created_offer = offers_models.Offer.query.one()
        assert created_offer.withdrawalType == offers_models.WithdrawalTypeEnum.ON_SITE
        assert created_offer.withdrawalDelay == 30 * 60

    @pytest.mark.usefixtures("db_session")
    def test_event_with_email_ticket(self, client):
        api_key = offerers_factories.ApiKeyFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=api_key.offerer)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/events",
            json={
                "categoryRelatedFields": {"category": "FESTIVAL_ART_VISUEL"},
                "accessibility": ACCESSIBILITY_FIELDS,
                "location": {"type": "physical", "venueId": venue.id},
                "name": "Le champ des possibles",
                "ticketCollection": {"way": "by_email", "daysBeforeEvent": 3},
            },
        )

        assert response.status_code == 200
        created_offer = offers_models.Offer.query.one()
        assert created_offer.withdrawalType == offers_models.WithdrawalTypeEnum.BY_EMAIL
        assert created_offer.withdrawalDelay == 3 * 24 * 3600

    @pytest.mark.usefixtures("db_session")
    def test_error_when_ticket_specified_but_not_applicable(self, client):
        api_key = offerers_factories.ApiKeyFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=api_key.offerer)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/events",
            json={
                "categoryRelatedFields": {"category": "EVENEMENT_PATRIMOINE"},
                "accessibility": ACCESSIBILITY_FIELDS,
                "location": {"type": "physical", "venueId": venue.id},
                "name": "Le champ des possibles",
                "ticketCollection": {"way": "on_site", "minutesBeforeEvent": 30},
            },
        )

        assert response.status_code == 400
        assert offers_models.Offer.query.count() == 0
        assert response.json == {
            "offer": ["Une offre qui n'a pas de ticket retirable ne peut pas avoir un type de retrait renseigné"]
        }


class PostDatesTest:
    @pytest.mark.usefixtures("db_session")
    def test_new_dates_are_added(self, client):
        api_key = offerers_factories.ApiKeyFactory()
        event_offer = offers_factories.EventOfferFactory(venue__managingOfferer=api_key.offerer)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            f"/public/offers/v1/events/{event_offer.id}/dates",
            json={
                "dates": [
                    {
                        "beginningDatetime": "2022-02-01T12:00:00+02:00",
                        "bookingLimitDatetime": "2022-01-15T13:00:00Z",
                        "price": 8899,
                        "quantity": 10,
                    },
                    {
                        "beginningDatetime": "2022-03-01T12:00:00+02:00",
                        "bookingLimitDatetime": "2022-01-15T13:00:00Z",
                        "price": 0,
                        "quantity": "unlimited",
                    },
                ],
            },
        )

        assert response.status_code == 200
        created_stocks = offers_models.Stock.query.filter(offers_models.Stock.offerId == event_offer.id).all()
        assert len(created_stocks) == 2
        first_stock = next(
            stock for stock in created_stocks if stock.beginningDatetime == datetime.datetime(2022, 2, 1, 10, 0, 0)
        )
        assert first_stock.price == decimal.Decimal("88.99")
        assert first_stock.quantity == 10
        second_stock = next(
            stock for stock in created_stocks if stock.beginningDatetime == datetime.datetime(2022, 3, 1, 10, 0, 0)
        )
        assert second_stock.price == decimal.Decimal("0")
        assert second_stock.quantity is None

        assert response.json == {
            "dates": [
                {
                    "beginningDatetime": "2022-02-01T10:00:00",
                    "bookedQuantity": 0,
                    "bookingLimitDatetime": "2022-01-15T13:00:00",
                    "id": first_stock.id,
                    "price": 8899,
                    "quantity": 10,
                },
                {
                    "beginningDatetime": "2022-03-01T10:00:00",
                    "bookedQuantity": 0,
                    "bookingLimitDatetime": "2022-01-15T13:00:00",
                    "id": second_stock.id,
                    "price": 0,
                    "quantity": "unlimited",
                },
            ],
        }

    @pytest.mark.usefixtures("db_session")
    def test_invalid_offer_id(self, client):
        offerers_factories.ApiKeyFactory()

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/events/quinze/dates",
            json={
                "additionalDates": [
                    {
                        "beginningDatetime": "2022-02-01T12:00:00+02:00",
                        "bookingLimitDatetime": "2022-01-15T13:00:00Z",
                        "price": 8899,
                        "quantity": 10,
                    }
                ]
            },
        )

        assert response.status_code == 404

    @pytest.mark.usefixtures("db_session")
    def test_404_for_other_offerer_offer(self, client):
        offerers_factories.ApiKeyFactory()
        event_offer = offers_factories.EventOfferFactory()

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            f"/public/offers/v1/events/{event_offer.id}/dates",
            json={
                "dates": [
                    {
                        "beginningDatetime": "2022-02-01T12:00:00+02:00",
                        "bookingLimitDatetime": "2022-01-15T13:00:00Z",
                        "price": 8899,
                        "quantity": 10,
                    },
                ],
            },
        )
        assert response.status_code == 404
        assert response.json == {"event_id": ["The event could not be found"]}

    @pytest.mark.usefixtures("db_session")
    def test_404_for_product_offer(self, client):
        api_key = offerers_factories.ApiKeyFactory()
        product_offer = offers_factories.ThingOfferFactory(venue__managingOfferer=api_key.offerer)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            f"/public/offers/v1/events/{product_offer.id}/dates",
            json={
                "dates": [
                    {
                        "beginningDatetime": "2022-02-01T12:00:00+02:00",
                        "bookingLimitDatetime": "2022-01-15T13:00:00Z",
                        "price": 8899,
                        "quantity": 10,
                    },
                ],
            },
        )
        assert response.status_code == 404
        assert response.json == {"event_id": ["The event could not be found"]}


class GetProductTest:
    @pytest.mark.usefixtures("db_session")
    def test_product_without_stock(self, client):
        api_key = offerers_factories.ApiKeyFactory()
        product_offer = offers_factories.ThingOfferFactory(
            venue__managingOfferer=api_key.offerer,
            description="Un livre de contrepèterie",
            name="Vieux motard que jamais",
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            f"/public/offers/v1/products/{product_offer.id}"
        )

        assert response.status_code == 200
        assert response.json == {
            "bookingEmail": None,
            "categoryRelatedFields": {"category": "SUPPORT_PHYSIQUE_FILM"},
            "description": "Un livre de contrepèterie",
            "accessibility": {
                "audioDisabilityCompliant": False,
                "mentalDisabilityCompliant": False,
                "motorDisabilityCompliant": False,
                "visualDisabilityCompliant": False,
            },
            "enableDoubleBookings": False,
            "externalTicketOfficeUrl": None,
            "id": product_offer.id,
            "image": None,
            "itemCollectionDetails": None,
            "location": {"type": "physical", "venueId": product_offer.venueId},
            "name": "Vieux motard que jamais",
            "status": "SOLD_OUT",
            "stock": None,
        }

    @pytest.mark.usefixtures("db_session")
    def test_product_with_stock_and_image(self, client):
        api_key = offerers_factories.ApiKeyFactory()
        product_offer = offers_factories.ThingOfferFactory(venue__managingOfferer=api_key.offerer)
        offers_factories.StockFactory(offer=product_offer, isSoftDeleted=True)
        bookable_stock = offers_factories.StockFactory(
            offer=product_offer, price=12.34, quantity=10, bookingLimitDatetime=datetime.datetime(2022, 1, 15, 13, 0, 0)
        )
        bookings_factories.BookingFactory(stock=bookable_stock)
        mediation = offers_factories.MediationFactory(offer=product_offer, credit="Ph. Oto")
        product_offer_id = product_offer.id

        num_query = 1  # feature flag WIP_ENABLE_OFFER_CREATION_API_V1
        num_query += 1  # retrieve API key
        num_query += 1  # retrieve offer

        with testing.assert_num_queries(3):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
                f"/public/offers/v1/products/{product_offer_id}"
            )

        assert response.status_code == 200
        assert response.json["stock"] == {
            "price": 1234,
            "quantity": 10,
            "bookedQuantity": 1,
            "bookingLimitDatetime": "2022-01-15T13:00:00Z",
        }
        assert response.json["image"] == {
            "credit": "Ph. Oto",
            "url": f"http://localhost/storage/thumbs/mediations/{human_ids.humanize(mediation.id)}",
        }
        assert response.json["status"] == "EXPIRED"

    @pytest.mark.usefixtures("db_session")
    def test_404_when_requesting_an_event(self, client):
        api_key = offerers_factories.ApiKeyFactory()
        event_offer = offers_factories.EventOfferFactory(venue__managingOfferer=api_key.offerer)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            f"/public/offers/v1/products/{event_offer.id}"
        )

        assert response.status_code == 404
        assert response.json == {"product_id": ["The product offer could not be found"]}


class GetEventTest:
    @pytest.mark.usefixtures("db_session")
    def test_404_when_requesting_a_product(self, client):
        api_key = offerers_factories.ApiKeyFactory()
        event_offer = offers_factories.ThingOfferFactory(venue__managingOfferer=api_key.offerer)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            f"/public/offers/v1/events/{event_offer.id}"
        )

        assert response.status_code == 404
        assert response.json == {"event_id": ["The event offer could not be found"]}

    @pytest.mark.usefixtures("db_session")
    def test_get_event(self, client):
        api_key = offerers_factories.ApiKeyFactory()
        product = offers_factories.ProductFactory(thumbCount=1)
        event_offer = offers_factories.EventOfferFactory(
            subcategoryId=subcategories.SEANCE_CINE.id,
            venue__managingOfferer=api_key.offerer,
            description="Un livre de contrepèterie",
            name="Vieux motard que jamais",
            product=product,
        )
        event_offer_id = event_offer.id

        num_query = 1  # feature flag WIP_ENABLE_OFFER_CREATION_API_V1
        num_query += 1  # retrieve API key
        num_query += 1  # retrieve offer

        with testing.assert_num_queries(3):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
                f"/public/offers/v1/events/{event_offer_id}"
            )

        assert response.status_code == 200
        assert response.json == {
            "accessibility": {
                "audioDisabilityCompliant": False,
                "mentalDisabilityCompliant": False,
                "motorDisabilityCompliant": False,
                "visualDisabilityCompliant": False,
            },
            "bookingEmail": None,
            "categoryRelatedFields": {"author": None, "category": "SEANCE_CINE", "stageDirector": None, "visa": None},
            "description": "Un livre de contrepèterie",
            "enableDoubleBookings": False,
            "externalTicketOfficeUrl": None,
            "eventDuration": None,
            "id": event_offer.id,
            "image": {
                "credit": None,
                "url": f"http://localhost/storage/thumbs/products/{human_ids.humanize(product.id)}",
            },
            "itemCollectionDetails": None,
            "location": {"type": "physical", "venueId": event_offer.venueId},
            "name": "Vieux motard que jamais",
            "status": "SOLD_OUT",
            "ticketCollection": None,
        }

    @pytest.mark.usefixtures("db_session")
    def test_ticket_collection_by_email(self, client):
        api_key = offerers_factories.ApiKeyFactory()
        event_offer = offers_factories.EventOfferFactory(
            venue__managingOfferer=api_key.offerer,
            withdrawalType=offers_models.WithdrawalTypeEnum.BY_EMAIL,
            withdrawalDelay=259201,  # 3 days + 1 second
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            f"/public/offers/v1/events/{event_offer.id}"
        )

        assert response.status_code == 200
        assert response.json["ticketCollection"] == {"daysBeforeEvent": 3, "way": "by_email"}

    @pytest.mark.usefixtures("db_session")
    def test_ticket_collection_on_site(self, client):
        api_key = offerers_factories.ApiKeyFactory()
        event_offer = offers_factories.EventOfferFactory(
            venue__managingOfferer=api_key.offerer,
            withdrawalType=offers_models.WithdrawalTypeEnum.ON_SITE,
            withdrawalDelay=1801,  # 30 minutes + 1 second
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            f"/public/offers/v1/events/{event_offer.id}"
        )

        assert response.status_code == 200
        assert response.json["ticketCollection"] == {"minutesBeforeEvent": 30, "way": "on_site"}

    @pytest.mark.usefixtures("db_session")
    def test_ticket_collection_no_ticket(self, client):
        api_key = offerers_factories.ApiKeyFactory()
        event_offer = offers_factories.EventOfferFactory(
            venue__managingOfferer=api_key.offerer,
            withdrawalType=offers_models.WithdrawalTypeEnum.NO_TICKET,
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            f"/public/offers/v1/events/{event_offer.id}"
        )

        assert response.status_code == 200
        assert response.json["ticketCollection"] is None


class GetEventDatesTest:
    @freezegun.freeze_time("2023-01-01 12:00:00")
    @pytest.mark.usefixtures("db_session")
    def test_event_with_dates(self, client):
        api_key = offerers_factories.ApiKeyFactory()
        event_offer = offers_factories.EventOfferFactory(venue__managingOfferer=api_key.offerer)
        offers_factories.StockFactory(offer=event_offer, isSoftDeleted=True)
        bookable_stock = offers_factories.EventStockFactory(
            offer=event_offer,
            price=12.34,
            quantity=10,
            bookingLimitDatetime=datetime.datetime(2023, 1, 15, 13, 0, 0),
            beginningDatetime=datetime.datetime(2023, 1, 15, 13, 0, 0),
        )
        stock_without_booking = offers_factories.EventStockFactory(
            offer=event_offer,
            price=12.34,
            quantity=2,
            bookingLimitDatetime=datetime.datetime(2023, 1, 15, 13, 0, 0),
            beginningDatetime=datetime.datetime(2023, 1, 15, 13, 0, 0),
        )
        offers_factories.EventStockFactory(offer=event_offer, isSoftDeleted=True)  # deleted stock, not returned
        bookings_factories.BookingFactory(stock=bookable_stock)

        with testing.assert_no_duplicated_queries():
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
                f"/public/offers/v1/events/{event_offer.id}/dates"
            )

        assert response.status_code == 200
        assert response.json["dates"] == [
            {
                "beginningDatetime": "2023-01-15T13:00:00Z",
                "bookedQuantity": 1,
                "bookingLimitDatetime": "2023-01-15T13:00:00Z",
                "id": bookable_stock.id,
                "price": 1234,
                "quantity": 10,
            },
            {
                "beginningDatetime": "2023-01-15T13:00:00Z",
                "bookedQuantity": 0,
                "bookingLimitDatetime": "2023-01-15T13:00:00Z",
                "id": stock_without_booking.id,
                "price": 1234,
                "quantity": 2,
            },
        ]
        assert (
            response.json["pagination"]["pagesLinks"]["current"]
            == f"http://localhost/public/offers/v1/events/{event_offer.id}/dates?page=1&limit=50"
        )

    @pytest.mark.usefixtures("db_session")
    def test_event_without_dates(self, client):
        api_key = offerers_factories.ApiKeyFactory()
        event_offer = offers_factories.EventOfferFactory(venue__managingOfferer=api_key.offerer)
        offers_factories.EventStockFactory(offer=event_offer, isSoftDeleted=True)  # deleted stock, not returned

        with testing.assert_no_duplicated_queries():
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
                f"/public/offers/v1/events/{event_offer.id}/dates"
            )

        assert response.status_code == 200
        assert response.json == {
            "dates": [],
            "pagination": {
                "currentPage": 1,
                "itemsCount": 0,
                "itemsTotal": 0,
                "lastPage": 1,
                "limitPerPage": 50,
                "pagesLinks": {
                    "current": f"http://localhost/public/offers/v1/events/{event_offer.id}/dates?page=1&limit=50",
                    "first": f"http://localhost/public/offers/v1/events/{event_offer.id}/dates?page=1&limit=50",
                    "last": f"http://localhost/public/offers/v1/events/{event_offer.id}/dates?page=1&limit=50",
                    "next": None,
                    "previous": None,
                },
            },
        }

    @pytest.mark.usefixtures("db_session")
    def test_404_when_page_is_too_high(self, client):
        api_key = offerers_factories.ApiKeyFactory()
        event_offer = offers_factories.EventOfferFactory(venue__managingOfferer=api_key.offerer)
        offers_factories.EventStockFactory(offer=event_offer)  # deleted stock, not returned

        with testing.assert_no_duplicated_queries():
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
                f"/public/offers/v1/events/{event_offer.id}/dates?page=2&limit=50"
            )

        assert response.status_code == 404
        assert response.json == {
            "page": "The page you requested does not exist. The maximum page for the specified limit is 1"
        }


class GetProductsTest:
    ENDPOINT_URL = "http://localhost/public/offers/v1/products"

    @pytest.mark.usefixtures("db_session")
    def test_get_first_page(self, client):
        api_key = offerers_factories.ApiKeyFactory()
        offers = offers_factories.ThingOfferFactory.create_batch(12, venue__managingOfferer=api_key.offerer)

        with testing.assert_no_duplicated_queries():
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
                "/public/offers/v1/products?limit=5"
            )

        assert response.status_code == 200
        assert response.json["pagination"] == {
            "currentPage": 1,
            "itemsCount": 5,
            "itemsTotal": 12,
            "lastPage": 3,
            "limitPerPage": 5,
            "pagesLinks": {
                "current": f"{self.ENDPOINT_URL}?page=1&limit=5",
                "first": f"{self.ENDPOINT_URL}?page=1&limit=5",
                "last": f"{self.ENDPOINT_URL}?page=3&limit=5",
                "next": f"{self.ENDPOINT_URL}?page=2&limit=5",
                "previous": None,
            },
        }
        assert [product["id"] for product in response.json["products"]] == [offer.id for offer in offers[0:5]]

    @pytest.mark.usefixtures("db_session")
    def test_get_last_page(self, client):
        api_key = offerers_factories.ApiKeyFactory()
        offers = offers_factories.ThingOfferFactory.create_batch(12, venue__managingOfferer=api_key.offerer)

        with testing.assert_no_duplicated_queries():
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
                "/public/offers/v1/products?limit=5&page=3"
            )

        assert response.status_code == 200
        assert response.json["pagination"] == {
            "currentPage": 3,
            "itemsCount": 2,
            "itemsTotal": 12,
            "lastPage": 3,
            "limitPerPage": 5,
            "pagesLinks": {
                "current": f"{self.ENDPOINT_URL}?page=3&limit=5",
                "first": f"{self.ENDPOINT_URL}?page=1&limit=5",
                "last": f"{self.ENDPOINT_URL}?page=3&limit=5",
                "next": None,
                "previous": f"{self.ENDPOINT_URL}?page=2&limit=5",
            },
        }
        assert [product["id"] for product in response.json["products"]] == [offer.id for offer in offers[10:12]]

    @pytest.mark.usefixtures("db_session")
    def test_404_when_the_page_is_too_high(self, client):
        offerers_factories.ApiKeyFactory()

        with testing.assert_no_duplicated_queries():
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
                "/public/offers/v1/products?limit=5&page=2"
            )

        assert response.status_code == 404
        assert response.json == {
            "page": "The page you requested does not exist. The maximum page for the " "specified limit is 1"
        }

    @pytest.mark.usefixtures("db_session")
    def test_200_for_first_page_if_no_items(self, client):
        offerers_factories.ApiKeyFactory()

        with testing.assert_no_duplicated_queries():
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
                "/public/offers/v1/products?limit=5"
            )

        assert response.status_code == 200
        assert response.json == {
            "pagination": {
                "currentPage": 1,
                "itemsCount": 0,
                "itemsTotal": 0,
                "limitPerPage": 5,
                "lastPage": 1,
                "pagesLinks": {
                    "current": f"{self.ENDPOINT_URL}?page=1&limit=5",
                    "first": f"{self.ENDPOINT_URL}?page=1&limit=5",
                    "last": f"{self.ENDPOINT_URL}?page=1&limit=5",
                    "next": None,
                    "previous": None,
                },
            },
            "products": [],
        }

    @pytest.mark.usefixtures("db_session")
    def test_400_when_limit_is_too_high(self, client):
        offerers_factories.ApiKeyFactory()

        with testing.assert_no_duplicated_queries():
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
                "/public/offers/v1/products?limit=51"
            )

        assert response.status_code == 400
        assert response.json == {"limit": ["ensure this value is less than or equal to 50"]}

    @pytest.mark.usefixtures("db_session")
    def test_get_filterd_venue_offer(self, client):
        api_key = offerers_factories.ApiKeyFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=api_key.offerer)
        offer = offers_factories.ThingOfferFactory(venue=venue)
        offers_factories.ThingOfferFactory(venue__managingOfferer=api_key.offerer)  # offer attached to other venue

        with testing.assert_no_duplicated_queries():
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
                f"/public/offers/v1/products?venueId={venue.id}"
            )

        assert response.status_code == 200
        assert response.json["pagination"] == {
            "currentPage": 1,
            "itemsCount": 1,
            "itemsTotal": 1,
            "lastPage": 1,
            "limitPerPage": 50,
            "pagesLinks": {
                "current": f"http://localhost/public/offers/v1/products?venueId={venue.id}&page=1&limit=50",
                "first": f"http://localhost/public/offers/v1/products?venueId={venue.id}&page=1&limit=50",
                "last": f"http://localhost/public/offers/v1/products?venueId={venue.id}&page=1&limit=50",
                "next": None,
                "previous": None,
            },
        }
        assert [product["id"] for product in response.json["products"]] == [offer.id]


class GetEventsTest:
    ENDPOINT_URL = "http://localhost/public/offers/v1/events"

    @pytest.mark.usefixtures("db_session")
    def test_get_first_page(self, client):
        api_key = offerers_factories.ApiKeyFactory()
        offers = offers_factories.EventOfferFactory.create_batch(12, venue__managingOfferer=api_key.offerer)
        offers_factories.ThingOfferFactory.create_batch(3, venue__managingOfferer=api_key.offerer)  # not returned

        with testing.assert_no_duplicated_queries():
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
                "/public/offers/v1/events?limit=5"
            )

        assert response.status_code == 200
        assert response.json["pagination"] == {
            "currentPage": 1,
            "itemsCount": 5,
            "itemsTotal": 12,
            "lastPage": 3,
            "limitPerPage": 5,
            "pagesLinks": {
                "current": f"{self.ENDPOINT_URL}?page=1&limit=5",
                "first": f"{self.ENDPOINT_URL}?page=1&limit=5",
                "last": f"{self.ENDPOINT_URL}?page=3&limit=5",
                "next": f"{self.ENDPOINT_URL}?page=2&limit=5",
                "previous": None,
            },
        }
        assert [event["id"] for event in response.json["events"]] == [offer.id for offer in offers[0:5]]
