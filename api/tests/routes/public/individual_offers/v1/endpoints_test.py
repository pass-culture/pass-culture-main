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
from pcapi.core.bookings import models as bookings_models
from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
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


@pytest.mark.usefixtures("db_session")
class GetOffererVenuesTest:
    def test_get_offerer_venues(self, client):
        offerer = offerers_factories.OffererFactory(
            name="Offreur de fleurs", dateCreated=datetime.datetime(2022, 2, 22, 22, 22, 22), siren="123456789"
        )
        api_key = offerers_factories.ApiKeyFactory(offerer=offerer)
        digital_venue = offerers_factories.VirtualVenueFactory(
            managingOfferer=api_key.offerer,
            dateCreated=datetime.datetime(2023, 1, 16),
            name="Do you diji",
            publicName="Diji",
            venueTypeCode=offerers_models.VenueTypeCode.ARTISTIC_COURSE,
        )
        physical_venue = offerers_factories.VenueFactory(
            managingOfferer=api_key.offerer,
            dateCreated=datetime.datetime(2023, 1, 16, 1, 1, 1),
            name="Coiffeur Librairie",
            publicName="Tiff tuff",
            siret="12345678912345",
            venueTypeCode=offerers_models.VenueTypeCode.BOOKSTORE,
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            "/public/offers/v1/offerer_venues",
        )

        assert response.status_code == 200
        assert response.json["offerer"] == {
            "createdDatetime": "2022-02-22T22:22:22Z",
            "id": offerer.id,
            "name": "Offreur de fleurs",
            "siren": "123456789",
        }
        assert response.json["venues"] == [
            {
                "activityDomain": "ARTISTIC_COURSE",
                "createdDatetime": "2023-01-16T00:00:00Z",
                "publicName": "Diji",
                "id": digital_venue.id,
                "legalName": "Do you diji",
                "location": {"type": "digital"},
                "siret": None,
                "siretComment": None,
            },
            {
                "activityDomain": "BOOKSTORE",
                "createdDatetime": "2023-01-16T01:01:01Z",
                "publicName": "Tiff tuff",
                "id": physical_venue.id,
                "legalName": "Coiffeur Librairie",
                "location": {
                    "address": "1 boulevard Poissonnière",
                    "city": "Paris",
                    "postalCode": "75000",
                    "type": "physical",
                },
                "siret": "12345678912345",
                "siretComment": None,
            },
        ]

    def test_when_no_venues(self, client):
        offerer = offerers_factories.OffererFactory(
            name="Offreur sans fleurs", dateCreated=datetime.datetime(2022, 2, 22, 22, 22, 22), siren="123456789"
        )
        offerers_factories.ApiKeyFactory(offerer=offerer)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            "/public/offers/v1/offerer_venues",
        )
        assert response == 200
        assert response.json == {
            "offerer": {
                "createdDatetime": "2022-02-22T22:22:22Z",
                "id": offerer.id,
                "name": "Offreur sans fleurs",
                "siren": "123456789",
            },
            "venues": [],
        }


class PostProductTest:
    @pytest.mark.usefixtures("db_session")
    def test_physical_product_minimal_body(self, client):
        api_key = offerers_factories.ApiKeyFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=api_key.offerer)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products",
            json={
                "categoryRelatedFields": {"category": "LIVRE_AUDIO_PHYSIQUE"},
                "accessibility": ACCESSIBILITY_FIELDS,
                "location": {"type": "physical", "venueId": venue.id},
                "name": "Le champ des possibles",
            },
        )

        assert response.status_code == 200
        created_offer = offers_models.Offer.query.one()
        assert created_offer.name == "Le champ des possibles"
        assert created_offer.venue == venue
        assert created_offer.subcategoryId == "LIVRE_AUDIO_PHYSIQUE"
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
            "categoryRelatedFields": {"author": None, "category": "LIVRE_AUDIO_PHYSIQUE", "isbn": None},
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
                    "ean": "12345678",
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
            "ean": "12345678",
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
                "ean": "12345678",
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
                "categoryRelatedFields": {"category": "SUPPORT_PHYSIQUE_FILM", "ean": "12345678"},
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
                "categoryRelatedFields": {"category": "SUPPORT_PHYSIQUE_FILM", "ean": "12345678"},
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
                "categoryRelatedFields": {"category": "SUPPORT_PHYSIQUE_FILM", "ean": "12345678"},
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
                "categoryRelatedFields": {"category": "SUPPORT_PHYSIQUE_FILM", "ean": "12345678"},
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
                "categoryRelatedFields": {"category": "SPECTACLE_ENREGISTRE"},
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
                "categoryRelatedFields": {
                    "category": "SUPPORT_PHYSIQUE_MUSIQUE",
                    "ean": "12345678",
                    "musicType": "CHANSON_VARIETE-OTHER",
                },
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
                "categoryRelatedFields": {"category": "LIVRE_AUDIO_PHYSIQUE"},
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
                "categoryRelatedFields": {"category": "LIVRE_AUDIO_PHYSIQUE"},
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
                "categoryRelatedFields": {"category": "LIVRE_AUDIO_PHYSIQUE"},
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
                "categoryRelatedFields": {"category": "LIVRE_AUDIO_PHYSIQUE"},
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

    @pytest.mark.usefixtures("db_session")
    def test_books_are_not_allowed(self, client):
        api_key = offerers_factories.ApiKeyFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=api_key.offerer)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products",
            json={
                "categoryRelatedFields": {"category": "LIVRE_PAPIER"},
                "accessibility": ACCESSIBILITY_FIELDS,
                "location": {"type": "physical", "venueId": venue.id},
                "name": "A qui mieux mieux",
            },
        )

        assert response.status_code == 400
        assert offers_models.Offer.query.count() == 0


@pytest.mark.usefixtures("db_session")
class PostEventTest:
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


@pytest.mark.usefixtures("db_session")
class PostDatesTest:
    def test_new_dates_are_added(self, individual_offers_api_provider, client):
        api_key = offerers_factories.ApiKeyFactory()
        event_offer = offers_factories.EventOfferFactory(
            venue__managingOfferer=api_key.offerer, lastProvider=individual_offers_api_provider
        )

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


@pytest.mark.usefixtures("db_session")
class GetProductTest:
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
            "categoryRelatedFields": {"category": "SUPPORT_PHYSIQUE_FILM", "ean": None},
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

    def test_books_can_be_retrieved(self, client):
        api_key = offerers_factories.ApiKeyFactory()
        product_offer = offers_factories.ThingOfferFactory(
            venue__managingOfferer=api_key.offerer,
            subcategoryId=subcategories.LIVRE_PAPIER.id,
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            f"/public/offers/v1/products/{product_offer.id}"
        )

        assert response.status_code == 200
        assert response.json["categoryRelatedFields"] == {"author": None, "category": "LIVRE_PAPIER", "isbn": None}

    def test_product_with_not_selectable_category_can_be_retrieved(self, client):
        api_key = offerers_factories.ApiKeyFactory()
        product_offer = offers_factories.ThingOfferFactory(
            venue__managingOfferer=api_key.offerer,
            subcategoryId=subcategories.ABO_LUDOTHEQUE.id,
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            f"/public/offers/v1/products/{product_offer.id}"
        )

        assert response.status_code == 200
        assert response.json["categoryRelatedFields"] == {"category": "ABO_LUDOTHEQUE"}

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

    def test_404_when_requesting_an_event(self, client):
        api_key = offerers_factories.ApiKeyFactory()
        event_offer = offers_factories.EventOfferFactory(venue__managingOfferer=api_key.offerer)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            f"/public/offers/v1/products/{event_offer.id}"
        )

        assert response.status_code == 404
        assert response.json == {"product_id": ["The product offer could not be found"]}


@pytest.mark.usefixtures("db_session")
class GetEventTest:
    def test_404_when_requesting_a_product(self, client):
        api_key = offerers_factories.ApiKeyFactory()
        event_offer = offers_factories.ThingOfferFactory(venue__managingOfferer=api_key.offerer)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            f"/public/offers/v1/events/{event_offer.id}"
        )

        assert response.status_code == 404
        assert response.json == {"event_id": ["The event offer could not be found"]}

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

    def test_event_with_not_selectable_category_can_be_retrieved(self, client):
        api_key = offerers_factories.ApiKeyFactory()
        event_offer = offers_factories.EventOfferFactory(
            venue__managingOfferer=api_key.offerer,
            subcategoryId=subcategories.DECOUVERTE_METIERS.id,
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            f"/public/offers/v1/events/{event_offer.id}"
        )

        assert response.status_code == 200
        assert response.json["categoryRelatedFields"] == {"category": "DECOUVERTE_METIERS", "speaker": None}

    def test_get_show_offer_without_show_type(self, client):
        api_key = offerers_factories.ApiKeyFactory()
        event_offer = offers_factories.EventOfferFactory(
            subcategoryId=subcategories.SPECTACLE_REPRESENTATION.id,
            venue__managingOfferer=api_key.offerer,
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            f"/public/offers/v1/events/{event_offer.id}"
        )
        assert response.status_code == 200
        assert response.json["categoryRelatedFields"] == {
            "author": None,
            "category": "SPECTACLE_REPRESENTATION",
            "performer": None,
            "showType": None,
            "stageDirector": None,
        }

    def test_get_music_offer_without_music_type(self, client):
        api_key = offerers_factories.ApiKeyFactory()
        event_offer = offers_factories.EventOfferFactory(
            subcategoryId=subcategories.CONCERT.id,
            venue__managingOfferer=api_key.offerer,
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            f"/public/offers/v1/events/{event_offer.id}"
        )
        assert response.status_code == 200
        assert response.json["categoryRelatedFields"] == {
            "author": None,
            "category": "CONCERT",
            "performer": None,
            "musicType": None,
        }

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


@pytest.mark.usefixtures("db_session")
class GetEventDatesTest:
    @freezegun.freeze_time("2023-01-01 12:00:00")
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


@pytest.mark.usefixtures("db_session")
class GetProductsTest:
    ENDPOINT_URL = "http://localhost/public/offers/v1/products"

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

    def test_400_when_limit_is_too_high(self, client):
        offerers_factories.ApiKeyFactory()

        with testing.assert_no_duplicated_queries():
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
                "/public/offers/v1/products?limit=51"
            )

        assert response.status_code == 400
        assert response.json == {"limit": ["ensure this value is less than or equal to 50"]}

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


@pytest.mark.usefixtures("db_session")
class GetEventsTest:
    ENDPOINT_URL = "http://localhost/public/offers/v1/events"

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


@pytest.mark.usefixtures("db_session")
class PatchProductTest:
    def test_deactivate_offer(self, individual_offers_api_provider, client):
        api_key = offerers_factories.ApiKeyFactory()
        product_offer = offers_factories.ThingOfferFactory(
            venue__managingOfferer=api_key.offerer, isActive=True, lastProvider=individual_offers_api_provider
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/offers/v1/products/{product_offer.id}",
            json={"isActive": False},
        )

        assert response.status_code == 200
        assert response.json["status"] == "INACTIVE"
        assert product_offer.isActive is False

    def test_sets_field_to_none_and_leaves_other_unchanged(self, individual_offers_api_provider, client):
        api_key = offerers_factories.ApiKeyFactory()
        product_offer = offers_factories.ThingOfferFactory(
            venue__managingOfferer=api_key.offerer,
            withdrawalDetails="Des conditions de retrait sur la sellette",
            bookingEmail="notify@example.com",
            lastProvider=individual_offers_api_provider,
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/offers/v1/products/{product_offer.id}",
            json={"itemCollectionDetails": None},
        )

        assert response.status_code == 200
        assert response.json["itemCollectionDetails"] is None
        assert product_offer.withdrawalDetails is None
        assert product_offer.bookingEmail == "notify@example.com"

    def test_updates_booking_email(self, individual_offers_api_provider, client):
        api_key = offerers_factories.ApiKeyFactory()
        product_offer = offers_factories.ThingOfferFactory(
            venue__managingOfferer=api_key.offerer,
            bookingEmail="notify@example.com",
            lastProvider=individual_offers_api_provider,
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/offers/v1/products/{product_offer.id}",
            json={"bookingEmail": "spam@example.com"},
        )

        assert response.status_code == 200
        assert product_offer.bookingEmail == "spam@example.com"

    def test_sets_accessibility_partially(self, individual_offers_api_provider, client):
        api_key = offerers_factories.ApiKeyFactory()
        product_offer = offers_factories.ThingOfferFactory(
            venue__managingOfferer=api_key.offerer,
            audioDisabilityCompliant=True,
            mentalDisabilityCompliant=True,
            motorDisabilityCompliant=True,
            visualDisabilityCompliant=True,
            lastProvider=individual_offers_api_provider,
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/offers/v1/products/{product_offer.id}",
            json={"accessibility": {"audioDisabilityCompliant": False}},
        )

        assert response.status_code == 200
        assert response.json["accessibility"] == {
            "audioDisabilityCompliant": False,
            "mentalDisabilityCompliant": True,
            "motorDisabilityCompliant": True,
            "visualDisabilityCompliant": True,
        }
        assert product_offer.audioDisabilityCompliant is False
        assert product_offer.mentalDisabilityCompliant is True
        assert product_offer.motorDisabilityCompliant is True
        assert product_offer.visualDisabilityCompliant is True

    def test_update_extra_data_partially(self, individual_offers_api_provider, client):
        api_key = offerers_factories.ApiKeyFactory()
        product_offer = offers_factories.ThingOfferFactory(
            venue__managingOfferer=api_key.offerer,
            subcategoryId="SUPPORT_PHYSIQUE_MUSIQUE",
            extraData={
                "author": "Maurice",
                "musicType": "501",
                "musicSubType": "508",
                "performer": "Pink Pâtisserie",
            },
            lastProvider=individual_offers_api_provider,
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/offers/v1/products/{product_offer.id}",
            json={"categoryRelatedFields": {"category": "SUPPORT_PHYSIQUE_MUSIQUE", "musicType": "JAZZ-ACID_JAZZ"}},
        )
        assert response.status_code == 200
        assert response.json["categoryRelatedFields"] == {
            "author": "Maurice",
            "ean": None,
            "category": "SUPPORT_PHYSIQUE_MUSIQUE",
            "musicType": "JAZZ-ACID_JAZZ",
            "performer": "Pink Pâtisserie",
        }
        assert product_offer.extraData == {
            "author": "Maurice",
            "musicSubType": "502",
            "musicType": "501",
            "performer": "Pink Pâtisserie",
        }

    def test_create_stock(self, individual_offers_api_provider, client):
        api_key = offerers_factories.ApiKeyFactory()
        product_offer = offers_factories.ThingOfferFactory(
            venue__managingOfferer=api_key.offerer,
            lastProvider=individual_offers_api_provider,
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/offers/v1/products/{product_offer.id}",
            json={"stock": {"price": 1000, "quantity": 1}},
        )
        assert response.status_code == 200
        assert response.json["stock"] == {
            "bookedQuantity": 0,
            "bookingLimitDatetime": None,
            "price": 1000,
            "quantity": 1,
        }
        assert product_offer.activeStocks[0].quantity == 1
        assert product_offer.activeStocks[0].price == 10

    def test_update_stock_quantity(self, individual_offers_api_provider, client):
        api_key = offerers_factories.ApiKeyFactory()
        product_offer = offers_factories.ThingOfferFactory(
            venue__managingOfferer=api_key.offerer,
            lastProvider=individual_offers_api_provider,
        )
        stock = offers_factories.StockFactory(offer=product_offer, quantity=None, price=10)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/offers/v1/products/{product_offer.id}",
            json={"stock": {"quantity": 100}},
        )
        assert response.status_code == 200
        assert response.json["stock"] == {
            "bookedQuantity": 0,
            "bookingLimitDatetime": None,
            "price": 1000,
            "quantity": 100,
        }
        assert len(product_offer.activeStocks) == 1
        assert product_offer.activeStocks[0] == stock
        assert product_offer.activeStocks[0].quantity == 100

    def test_remove_stock_booking_limit_datetime(self, individual_offers_api_provider, client):
        api_key = offerers_factories.ApiKeyFactory()
        product_offer = offers_factories.ThingOfferFactory(
            venue__managingOfferer=api_key.offerer,
            lastProvider=individual_offers_api_provider,
        )
        stock = offers_factories.StockFactory(offer=product_offer, bookingLimitDatetime="2021-01-15T00:00:00Z")

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/offers/v1/products/{product_offer.id}",
            json={"stock": {"bookingLimitDatetime": None}},
        )
        assert response.status_code == 200
        assert response.json["stock"]["bookingLimitDatetime"] == None

        assert len(product_offer.activeStocks) == 1
        assert product_offer.activeStocks[0] == stock
        assert product_offer.activeStocks[0].bookingLimitDatetime == None

    def test_update_stock_booking_limit_datetime(self, individual_offers_api_provider, client):
        api_key = offerers_factories.ApiKeyFactory()
        product_offer = offers_factories.ThingOfferFactory(
            venue__managingOfferer=api_key.offerer,
            lastProvider=individual_offers_api_provider,
        )
        stock = offers_factories.StockFactory(offer=product_offer, bookingLimitDatetime=None)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/offers/v1/products/{product_offer.id}",
            json={"stock": {"bookingLimitDatetime": "2021-01-15T00:00:00Z"}},
        )
        assert response.status_code == 200
        assert response.json["stock"]["bookingLimitDatetime"] == "2021-01-15T00:00:00Z"

        assert len(product_offer.activeStocks) == 1
        assert product_offer.activeStocks[0] == stock
        assert product_offer.activeStocks[0].bookingLimitDatetime == datetime.datetime(2021, 1, 15, 0, 0, 0)

    def test_delete_stock(self, individual_offers_api_provider, client):
        api_key = offerers_factories.ApiKeyFactory()
        product_offer = offers_factories.ThingOfferFactory(
            venue__managingOfferer=api_key.offerer,
            lastProvider=individual_offers_api_provider,
        )
        stock = offers_factories.StockFactory(offer=product_offer, bookingLimitDatetime=None)
        confirmed_booking = bookings_factories.IndividualBookingFactory(
            stock=stock, status=bookings_models.BookingStatus.CONFIRMED
        )
        used_booking = bookings_factories.IndividualBookingFactory(
            stock=stock, status=bookings_models.BookingStatus.USED
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/offers/v1/products/{product_offer.id}",
            json={"stock": None},
        )
        assert response.status_code == 200
        assert response.json["stock"] == None

        assert len(product_offer.activeStocks) == 0
        assert confirmed_booking.status == bookings_models.BookingStatus.CANCELLED
        assert used_booking.status == bookings_models.BookingStatus.USED

    def test_update_subcategory_raises_error(self, individual_offers_api_provider, client):
        api_key = offerers_factories.ApiKeyFactory()
        product_offer = offers_factories.ThingOfferFactory(
            venue__managingOfferer=api_key.offerer,
            subcategoryId=subcategories.ABO_LUDOTHEQUE.id,
            lastProvider=individual_offers_api_provider,
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/offers/v1/products/{product_offer.id}",
            json={"categoryRelatedFields": {"category": "LIVRE_AUDIO_PHYSIQUE"}},
        )
        assert response.status_code == 400
        assert response.json == {"categoryRelatedFields.category": ["the category cannot be changed"]}


@pytest.mark.usefixtures("db_session")
class DeleteDateTest:
    def test_delete_date(self, individual_offers_api_provider, client):
        api_key = offerers_factories.ApiKeyFactory()
        event_offer = offers_factories.EventOfferFactory(
            venue__managingOfferer=api_key.offerer, lastProvider=individual_offers_api_provider
        )
        to_delete_stock = offers_factories.EventStockFactory(offer=event_offer)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).delete(
            f"/public/offers/v1/events/{event_offer.id}/dates/{to_delete_stock.id}",
        )

        assert response.status_code == 204
        assert response.json is None
        assert to_delete_stock.isSoftDeleted is True

    def test_404_if_already_soft_deleted(self, individual_offers_api_provider, client):
        api_key = offerers_factories.ApiKeyFactory()
        event_offer = offers_factories.EventOfferFactory(
            venue__managingOfferer=api_key.offerer, lastProvider=individual_offers_api_provider
        )
        already_deleted_stock = offers_factories.EventStockFactory(offer=event_offer, isSoftDeleted=True)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).delete(
            f"/public/offers/v1/events/{event_offer.id}/dates/{already_deleted_stock.id}",
        )

        assert response.status_code == 404
        assert response.json == {"date_id": ["The date could not be found"]}

    def test_404_if_others_offerer_offer(self, client):
        offerers_factories.ApiKeyFactory()
        others_stock = offers_factories.EventStockFactory()

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).delete(
            f"/public/offers/v1/events/{others_stock.offerId}/dates/{others_stock.id}",
        )

        assert response.status_code == 404
        assert response.json == {"event_id": ["The event could not be found"]}


@pytest.mark.usefixtures("db_session")
class PatchEventTest:
    def test_edit_product_offer_returns_404(self, individual_offers_api_provider, client):
        api_key = offerers_factories.ApiKeyFactory()
        thing_offer = offers_factories.ThingOfferFactory(
            venue__managingOfferer=api_key.offerer, isActive=True, lastProvider=individual_offers_api_provider
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/offers/v1/events/{thing_offer.id}",
            json={"isActive": False},
        )

        assert response.status_code == 404
        assert thing_offer.isActive is True

    def test_deactivate_offer(self, individual_offers_api_provider, client):
        api_key = offerers_factories.ApiKeyFactory()
        event_offer = offers_factories.EventOfferFactory(
            venue__managingOfferer=api_key.offerer, isActive=True, lastProvider=individual_offers_api_provider
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/offers/v1/events/{event_offer.id}",
            json={"isActive": False},
        )

        assert response.status_code == 200
        assert response.json["status"] == "INACTIVE"
        assert event_offer.isActive is False

    def test_sets_field_to_none_and_leaves_other_unchanged(self, individual_offers_api_provider, client):
        api_key = offerers_factories.ApiKeyFactory()
        event_offer = offers_factories.EventOfferFactory(
            subcategoryId="CONCERT",
            venue__managingOfferer=api_key.offerer,
            withdrawalDetails="Des conditions de retrait sur la sellette",
            withdrawalType=offers_models.WithdrawalTypeEnum.BY_EMAIL,
            withdrawalDelay=86400,
            bookingEmail="notify@example.com",
            lastProvider=individual_offers_api_provider,
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/offers/v1/events/{event_offer.id}",
            json={"itemCollectionDetails": None},
        )

        assert response.status_code == 200
        assert response.json["itemCollectionDetails"] is None
        assert event_offer.withdrawalDetails is None
        assert event_offer.bookingEmail == "notify@example.com"
        assert event_offer.withdrawalType == offers_models.WithdrawalTypeEnum.BY_EMAIL
        assert event_offer.withdrawalDelay == 86400

    def test_sets_accessibility_partially(self, individual_offers_api_provider, client):
        api_key = offerers_factories.ApiKeyFactory()
        event_offer = offers_factories.EventOfferFactory(
            venue__managingOfferer=api_key.offerer,
            audioDisabilityCompliant=True,
            mentalDisabilityCompliant=True,
            motorDisabilityCompliant=True,
            visualDisabilityCompliant=True,
            lastProvider=individual_offers_api_provider,
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/offers/v1/events/{event_offer.id}",
            json={"accessibility": {"audioDisabilityCompliant": False}},
        )

        assert response.status_code == 200
        assert response.json["accessibility"] == {
            "audioDisabilityCompliant": False,
            "mentalDisabilityCompliant": True,
            "motorDisabilityCompliant": True,
            "visualDisabilityCompliant": True,
        }
        assert event_offer.audioDisabilityCompliant is False
        assert event_offer.mentalDisabilityCompliant is True
        assert event_offer.motorDisabilityCompliant is True
        assert event_offer.visualDisabilityCompliant is True

    def test_update_extra_data_partially(self, individual_offers_api_provider, client):
        api_key = offerers_factories.ApiKeyFactory()
        event_offer = offers_factories.EventOfferFactory(
            venue__managingOfferer=api_key.offerer,
            subcategoryId="FESTIVAL_ART_VISUEL",
            extraData={
                "author": "Maurice",
                "stageDirector": "Robert",
                "performer": "Pink Pâtisserie",
            },
            lastProvider=individual_offers_api_provider,
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/offers/v1/events/{event_offer.id}",
            json={
                "categoryRelatedFields": {
                    "category": "FESTIVAL_ART_VISUEL",
                    "author": "Maurice",
                    "stageDirector": "Robert",
                    "performer": "Pink Pâtisserie",
                }
            },
        )

        assert response.status_code == 200
        assert response.json["categoryRelatedFields"] == {
            "author": "Maurice",
            "category": "FESTIVAL_ART_VISUEL",
            "performer": "Pink Pâtisserie",
        }
        assert event_offer.extraData == {
            "author": "Maurice",
            "performer": "Pink Pâtisserie",
            "stageDirector": "Robert",
        }

    def test_patch_all_fields(self, individual_offers_api_provider, client):
        api_key = offerers_factories.ApiKeyFactory()
        event_offer = offers_factories.EventOfferFactory(
            venue__managingOfferer=api_key.offerer,
            bookingEmail="notify@passq.com",
            subcategoryId="CONCERT",
            durationMinutes=20,
            isDuo=False,
            lastProvider=individual_offers_api_provider,
            withdrawalType=offers_models.WithdrawalTypeEnum.BY_EMAIL,
            withdrawalDelay=86400,
            withdrawalDetails="Around there",
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/offers/v1/events/{event_offer.id}",
            json={
                "ticketCollection": {"way": "on_site", "minutesBeforeEvent": 60},
                "bookingEmail": "test@myemail.com",
                "eventDuration": 40,
                "enableDoubleBookings": "true",
                "itemCollectionDetails": "Here !",
            },
        )
        assert response.status_code == 200
        assert event_offer.withdrawalType == offers_models.WithdrawalTypeEnum.ON_SITE
        assert event_offer.withdrawalDelay == 3600
        assert event_offer.durationMinutes == 40
        assert event_offer.isDuo == True
        assert event_offer.bookingEmail == "test@myemail.com"
        assert event_offer.withdrawalDetails == "Here !"


@pytest.mark.usefixtures("db_session")
class PatchDateTest:
    def test_find_no_stock_returns_404(self, individual_offers_api_provider, client):
        api_key = offerers_factories.ApiKeyFactory()
        event_offer = offers_factories.EventOfferFactory(
            venue__managingOfferer=api_key.offerer,
            lastProvider=individual_offers_api_provider,
        )
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/offers/v1/events/{event_offer.id}/dates/12",
            json={"beginningDatetime": "2022-02-01T12:00:00+02:00"},
        )
        assert response.status_code == 404
        assert response.json == {"date_id": ["No date could be found"]}

    @freezegun.freeze_time("2022-01-01 12:00:00")
    def test_update_all_fields_dates(self, individual_offers_api_provider, client):
        api_key = offerers_factories.ApiKeyFactory()
        event_stock = offers_factories.EventStockFactory(
            offer__venue__managingOfferer=api_key.offerer,
            offer__lastProvider=individual_offers_api_provider,
            quantity=10,
            price=12,
            bookingLimitDatetime=datetime.datetime(2022, 1, 7),
            beginningDatetime=datetime.datetime(2022, 1, 12),
        )
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/offers/v1/events/{event_stock.offer.id}/dates/{event_stock.id}",
            json={
                "beginningDatetime": "2022-02-01T15:00:00+02:00",
                "bookingLimitDatetime": "2022-01-20T12:00:00+02:00",
                "price": 2012,
                "quantity": 24,
            },
        )
        assert response.status_code == 200
        assert event_stock.bookingLimitDatetime == datetime.datetime(2022, 1, 20, 10)
        assert event_stock.beginningDatetime == datetime.datetime(2022, 2, 1, 13)
        assert event_stock.price == decimal.Decimal("20.12")
        assert event_stock.quantity == 24

    @freezegun.freeze_time("2022-01-01 12:00:00")
    def test_update_only_one_field(self, individual_offers_api_provider, client):
        api_key = offerers_factories.ApiKeyFactory()
        event_stock = offers_factories.EventStockFactory(
            offer__venue__managingOfferer=api_key.offerer,
            offer__lastProvider=individual_offers_api_provider,
            quantity=10,
            price=12,
            bookingLimitDatetime=datetime.datetime(2022, 1, 7),
            beginningDatetime=datetime.datetime(2022, 1, 12),
        )
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/offers/v1/events/{event_stock.offer.id}/dates/{event_stock.id}",
            json={
                "bookingLimitDatetime": "2022-01-09T12:00:00+02:00",
            },
        )
        assert response.status_code == 200
        assert event_stock.bookingLimitDatetime == datetime.datetime(2022, 1, 9, 10)
        assert event_stock.beginningDatetime == datetime.datetime(2022, 1, 12)
        assert event_stock.price == decimal.Decimal("12")
        assert event_stock.quantity == 10

    def test_update_with_error(self, individual_offers_api_provider, client):
        api_key = offerers_factories.ApiKeyFactory()
        event_stock = offers_factories.EventStockFactory(
            offer__venue__managingOfferer=api_key.offerer,
            offer__lastProvider=individual_offers_api_provider,
            quantity=10,
            dnBookedQuantity=8,
        )
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/offers/v1/events/{event_stock.offer.id}/dates/{event_stock.id}",
            json={
                "quantity": 3,
            },
        )
        assert response.status_code == 400
        assert response.json == {"quantity": ["Le stock total ne peut être inférieur au nombre de réservations"]}

    def test_does_not_accept_extra_fields(self, individual_offers_api_provider, client):
        api_key = offerers_factories.ApiKeyFactory()
        event_stock = offers_factories.EventStockFactory(
            offer__venue__managingOfferer=api_key.offerer,
            offer__lastProvider=individual_offers_api_provider,
        )
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/offers/v1/events/{event_stock.offer.id}/dates/{event_stock.id}",
            json={
                "testForbidField": "test",
            },
        )
        assert response.status_code == 400
        assert response.json == {"testForbidField": ["Vous ne pouvez pas changer cette information"]}
