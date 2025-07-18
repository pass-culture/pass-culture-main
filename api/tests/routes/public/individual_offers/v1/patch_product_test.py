import base64
import datetime
import pathlib

import pytest
import time_machine

from pcapi import settings
from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings import models as bookings_models
from pcapi.core.categories import subcategories
from pcapi.core.geography import factories as geography_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.providers import factories as providers_factories
from pcapi.core.testing import assert_num_queries
from pcapi.models import db
from pcapi.utils import human_ids
from pcapi.utils.date import format_into_utc_date

import tests
from tests.routes import image_data
from tests.routes.public.helpers import ProductEndpointHelper
from tests.routes.public.helpers import PublicAPIVenueEndpointHelper


@pytest.mark.usefixtures("db_session")
class PatchProductTest(PublicAPIVenueEndpointHelper, ProductEndpointHelper):
    endpoint_url = "/public/offers/v1/products"
    endpoint_method = "patch"

    def test_should_raise_404_because_has_no_access_to_venue(self, client):
        plain_api_key, _ = self.setup_provider()
        venue = self.setup_venue()
        product = self.create_base_product(venue)

        response = client.with_explicit_token(plain_api_key).patch(
            self.endpoint_url,
            json={"offerId": product.id, "isActive": False},
        )
        assert response.status_code == 404

    def test_should_raise_404_because_venue_provider_is_inactive(self, client):
        plain_api_key, venue_provider = self.setup_inactive_venue_provider()
        venue = venue_provider.venue
        product = self.create_base_product(venue)

        response = client.with_explicit_token(plain_api_key).patch(
            self.endpoint_url,
            json={"offerId": product.id, "isActive": False},
        )
        assert response.status_code == 404

    def test_deactivate_offer(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue = venue_provider.venue
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue,
            isActive=True,
            lastProvider=venue_provider.provider,
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
            ean="1234567890124",
        )

        response = client.with_explicit_token(plain_api_key).patch(
            self.endpoint_url,
            json={"offerId": product_offer.id, "isActive": False},
        )

        assert response.status_code == 200
        assert response.json["status"] == "INACTIVE"
        assert product_offer.isActive is False

    def test_sets_field_to_none_and_leaves_other_unchanged(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue = venue_provider.venue
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue,
            withdrawalDetails="Des conditions de retrait sur la sellette",
            bookingEmail="notify@example.com",
            lastProvider=venue_provider.provider,
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
            ean="1234567890124",
        )

        response = client.with_explicit_token(plain_api_key).patch(
            self.endpoint_url,
            json={"offerId": product_offer.id, "itemCollectionDetails": None},
        )

        assert response.status_code == 200
        assert response.json["itemCollectionDetails"] is None
        assert product_offer.withdrawalDetails is None
        assert product_offer.bookingEmail == "notify@example.com"

    def test_update_product_image(self, client, clear_tests_assets_bucket):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue = venue_provider.venue
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue, lastProvider=venue_provider.provider, subcategoryId=subcategories.ABO_BIBLIOTHEQUE.id
        )

        response = client.with_explicit_token(plain_api_key).patch(
            self.endpoint_url,
            json={"offerId": product_offer.id, "image": {"file": image_data.GOOD_IMAGE}},
        )

        assert response.status_code == 200
        assert db.session.query(offers_models.Mediation).one()
        assert (
            product_offer.image.url
            == f"{settings.OBJECT_STORAGE_URL}/thumbs/mediations/{human_ids.humanize(product_offer.activeMediation.id)}"
        )

    def test_updates_booking_email(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue = venue_provider.venue
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue,
            bookingEmail="notify@example.com",
            lastProvider=venue_provider.provider,
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
            ean="1234567890124",
        )

        response = client.with_explicit_token(plain_api_key).patch(
            self.endpoint_url,
            json={"offerId": product_offer.id, "bookingEmail": "spam@example.com"},
        )

        assert response.status_code == 200
        assert product_offer.bookingEmail == "spam@example.com"

    def test_sets_accessibility_partially(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue = venue_provider.venue
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue,
            audioDisabilityCompliant=True,
            mentalDisabilityCompliant=True,
            motorDisabilityCompliant=True,
            visualDisabilityCompliant=True,
            lastProvider=venue_provider.provider,
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
            ean="1234567890124",
        )

        response = client.with_explicit_token(plain_api_key).patch(
            self.endpoint_url,
            json={"offerId": product_offer.id, "accessibility": {"audioDisabilityCompliant": False}},
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

    def test_create_stock(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue = venue_provider.venue
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue,
            lastProvider=venue_provider.provider,
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
        )

        response = client.with_explicit_token(plain_api_key).patch(
            self.endpoint_url,
            json={"offerId": product_offer.id, "stock": {"price": 1000, "quantity": 1}},
        )

        assert response.status_code == 200
        assert product_offer.activeStocks[0].quantity == 1
        assert product_offer.activeStocks[0].price == 10
        assert response.json["stock"] == {
            "bookedQuantity": 0,
            "bookingLimitDatetime": None,
            "price": 1000,
            "quantity": 1,
        }

    def test_update_stock_quantity(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue = venue_provider.venue
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue,
            lastProvider=venue_provider.provider,
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
        )
        stock = offers_factories.StockFactory(offer=product_offer, quantity=30, price=10)

        response = client.with_explicit_token(plain_api_key).patch(
            self.endpoint_url,
            json={"offerId": product_offer.id, "stock": {"quantity": "unlimited"}},
        )
        assert response.status_code == 200
        assert response.json["stock"] == {
            "bookedQuantity": 0,
            "bookingLimitDatetime": None,
            "price": 1000,
            "quantity": "unlimited",
        }
        assert len(product_offer.activeStocks) == 1
        assert product_offer.activeStocks[0] == stock
        assert product_offer.activeStocks[0].quantity is None

    def test_error_if_no_offer_is_found(self, client):
        plain_api_key, _ = self.setup_active_venue_provider()

        response = client.with_explicit_token(plain_api_key).patch(
            self.endpoint_url,
            json={
                "offerId": "33",
                "stock": {"bookingLimitDatetime": None},
            },
        )
        assert response.status_code == 404
        assert response.json == {"offerId": ["The product offer could not be found"]}

    def test_remove_stock_booking_limit_datetime(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()

        product_offer = offers_factories.ThingOfferFactory(
            venue=venue_provider.venue,
            lastProvider=venue_provider.provider,
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
        )
        stock = offers_factories.StockFactory(offer=product_offer, bookingLimitDatetime="2021-01-15T00:00:00Z")

        response = client.with_explicit_token(plain_api_key).patch(
            self.endpoint_url,
            json={"offerId": product_offer.id, "stock": {"bookingLimitDatetime": None}},
        )
        assert response.status_code == 200
        assert response.json["stock"]["bookingLimitDatetime"] is None

        assert len(product_offer.activeStocks) == 1
        assert product_offer.activeStocks[0] == stock
        assert product_offer.activeStocks[0].bookingLimitDatetime is None

    def test_update_stock_booking_limit_datetime(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue_provider.venue,
            lastProvider=venue_provider.provider,
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
        )
        stock = offers_factories.StockFactory(offer=product_offer, bookingLimitDatetime=None)

        new_limit = datetime.datetime.now() + datetime.timedelta(minutes=1)

        response = client.with_explicit_token(plain_api_key).patch(
            self.endpoint_url,
            json={"offerId": product_offer.id, "stock": {"bookingLimitDatetime": format_into_utc_date(new_limit)}},
        )
        assert response.status_code == 200
        assert response.json["stock"]["bookingLimitDatetime"] == format_into_utc_date(new_limit)

        assert len(product_offer.activeStocks) == 1
        assert product_offer.activeStocks[0] == stock
        assert product_offer.activeStocks[0].bookingLimitDatetime == new_limit

    def test_delete_stock(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue_provider.venue,
            lastProvider=venue_provider.provider,
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
        )
        stock = offers_factories.StockFactory(offer=product_offer, bookingLimitDatetime=None)
        confirmed_booking = bookings_factories.BookingFactory(
            stock=stock, status=bookings_models.BookingStatus.CONFIRMED
        )
        used_booking = bookings_factories.BookingFactory(stock=stock, status=bookings_models.BookingStatus.USED)

        response = client.with_explicit_token(plain_api_key).patch(
            self.endpoint_url,
            json={"offerId": product_offer.id, "stock": None},
        )
        assert response.status_code == 200
        assert response.json["stock"] is None

        assert len(product_offer.activeStocks) == 0
        assert confirmed_booking.status == bookings_models.BookingStatus.CANCELLED
        assert used_booking.status == bookings_models.BookingStatus.USED

    @time_machine.travel(datetime.datetime(2025, 6, 25, 12, 30, tzinfo=datetime.timezone.utc), tick=False)
    @pytest.mark.parametrize(
        "partial_request_json,expected_publication_datetime,expected_response_publication_datetime",
        [
            # should set new value
            (
                {"publicationDatetime": "2025-08-01T08:00:00+02:00"},  # tz: Europe/Paris
                datetime.datetime(2025, 8, 1, 6),  # tz: utc
                "2025-08-01T06:00:00Z",
            ),
            (
                {"publicationDatetime": "now"},
                datetime.datetime(2025, 6, 25, 12, 30),
                "2025-06-25T12:30:00Z",
            ),
            # should unset previous value
            ({"publicationDatetime": None}, None, None),
            # should keep previous value
            ({}, datetime.datetime(2025, 5, 1, 3), "2025-05-01T03:00:00Z"),
        ],
    )
    def test_publication_datetime_param(
        self, client, partial_request_json, expected_publication_datetime, expected_response_publication_datetime
    ):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue_provider.venue,
            subcategoryId=subcategories.ABO_MEDIATHEQUE.id,
            lastProvider=venue_provider.provider,
            publicationDatetime=datetime.datetime(2025, 5, 1, 3),
        )

        partial_request_json["offerId"] = product_offer.id

        response = client.with_explicit_token(plain_api_key).patch(self.endpoint_url, json=partial_request_json)

        assert response.status_code == 200
        assert response.json["publicationDatetime"] == expected_response_publication_datetime

        update_offer = db.session.query(offers_models.Offer).filter_by(id=product_offer.id).one()
        assert update_offer.publicationDatetime == expected_publication_datetime

    @time_machine.travel(datetime.datetime(2025, 6, 25, 12, 30, tzinfo=datetime.timezone.utc), tick=False)
    @pytest.mark.parametrize(
        "partial_request_json,expected_booking_allowed_datetime,expected_response_booking_allowed_datetime",
        [
            # should set new value
            (
                {"bookingAllowedDatetime": "2025-08-01T08:00:00+02:00"},  # tz: Europe/Paris
                datetime.datetime(2025, 8, 1, 6),  # tz: utc
                "2025-08-01T06:00:00Z",
            ),
            # should unset value
            ({"bookingAllowedDatetime": None}, None, None),
            # should keep previous value
            ({}, datetime.datetime(2025, 5, 1, 3), "2025-05-01T03:00:00Z"),
        ],
    )
    def test_booking_allowed_datetime_param(
        self,
        client,
        partial_request_json,
        expected_booking_allowed_datetime,
        expected_response_booking_allowed_datetime,
    ):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue_provider.venue,
            subcategoryId=subcategories.ABO_MEDIATHEQUE.id,
            lastProvider=venue_provider.provider,
            bookingAllowedDatetime=datetime.datetime(2025, 5, 1, 3),
        )

        partial_request_json["offerId"] = product_offer.id

        response = client.with_explicit_token(plain_api_key).patch(self.endpoint_url, json=partial_request_json)

        assert response.status_code == 200
        assert response.json["bookingAllowedDatetime"] == expected_response_booking_allowed_datetime

        update_offer = db.session.query(offers_models.Offer).filter_by(id=product_offer.id).one()
        assert update_offer.bookingAllowedDatetime == expected_booking_allowed_datetime

    @pytest.mark.parametrize(
        "partial_request_json, expected_response_json",
        [
            # errors on name
            (
                {"name": "Le Visible et l'invisible - Suivi de notes de travail - 9782070286256"},
                {"name": ["Le titre d'une offre ne peut contenir l'EAN"]},
            ),
            (
                {"name": "Jean Tartine est de retour", "description": "A" * 10_001},
                {"description": ["ensure this value has at most 10000 characters"]},
            ),
            # errors on datetimes
            (
                {"bookingAllowedDatetime": "2021-01-01T00:00:00"},
                {"bookingAllowedDatetime": ["The datetime must be timezone-aware."]},
            ),
            (
                {"bookingAllowedDatetime": "2021-01-01T00:00:00+00:00"},
                {"bookingAllowedDatetime": ["The datetime must be in the future."]},
            ),
            (
                {"publicationDatetime": "2021-01-01T00:00:00"},
                {"publicationDatetime": ["The datetime must be timezone-aware."]},
            ),
            (
                {"publicationDatetime": "2021-01-01T00:00:00+00:00"},
                {"publicationDatetime": ["The datetime must be in the future."]},
            ),
            (
                {"publicationDatetime": "NOW"},
                {"publicationDatetime": ["invalid datetime format", "unexpected value; permitted: 'now'"]},
            ),
            # errors on idAtProvider
            (
                {"idAtProvider": "a" * 71},
                {"idAtProvider": ["ensure this value has at most 70 characters"]},
            ),
            (
                {"idAtProvider": "c'est déjà pris :'("},
                {"idAtProvider": ["`c'est déjà pris :'(` is already taken by another venue offer"]},
            ),
            # errors on image
            (
                {
                    "image": {
                        "file": base64.b64encode(
                            (pathlib.Path(tests.__path__[0]) / "files" / "mouette_square.jpg").read_bytes()
                        ).decode()
                    }
                },
                {"imageFile": "Bad image ratio: expected 0.66, found 1.0"},
            ),
            (
                {"image": {"file": image_data.WRONG_IMAGE_SIZE}},
                {"imageFile": "The image is too small. It must be above 400x600 pixels."},
            ),
            # errors on stock
            (
                {
                    "stock": {"bookingLimitDatetime": "2021-01-01T00:00:00", "price": 10, "quantity": 10},
                },
                {"stock.bookingLimitDatetime": ["The datetime must be timezone-aware."]},
            ),
            (
                {
                    "stock": {"bookingLimitDatetime": "2021-01-01T00:00:00+00:00", "price": 10, "quantity": 10},
                },
                {"stock.bookingLimitDatetime": ["The datetime must be in the future."]},
            ),
            ({"stock": {"price": 12.34, "quantity": "unlimited"}}, {"stock.price": ["value is not a valid integer"]}),
            (
                {"stock": {"price": -1200, "quantity": "unlimited"}},
                {"stock.price": ["ensure this value is greater than or equal to 0"]},
            ),
            (
                {"stock": {"price": 1200, "quantity": -1}},
                {
                    "stock.quantity": [
                        "ensure this value is greater than or equal to 0",
                        "unexpected value; permitted: 'unlimited'",
                    ]
                },
            ),
            # `stock.bookingLimitDatetime` and `publicationDatetime` not coherent
            (
                {
                    "stock": {
                        "bookingLimitDatetime": (
                            datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=3)
                        ).isoformat(),
                        "price": 10,
                        "quantity": 10,
                    },
                    "publicationDatetime": (
                        datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=100)
                    ).isoformat(),
                },
                {"__root__": ["`stock.bookingLimitDatetime` must be after `publicationDatetime`"]},
            ),
            # `stock.bookingLimitDatetime` and `bookingLimitDatetime` not coherent
            (
                {
                    "stock": {
                        "bookingLimitDatetime": (
                            datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=3)
                        ).isoformat(),
                        "price": 10,
                        "quantity": 10,
                    },
                    "bookingAllowedDatetime": (
                        datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=100)
                    ).isoformat(),
                },
                {"__root__": ["`stock.bookingLimitDatetime` must be after `bookingAllowedDatetime`"]},
            ),
            # additional properties not allowed
            ({"tkilol": ""}, {"tkilol": ["extra fields not permitted"]}),
        ],
    )
    def test_incorrect_payload_should_return_400(self, client, partial_request_json, expected_response_json):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue_provider.venue,
            subcategoryId=subcategories.ABO_LIVRE_NUMERIQUE.id,
            lastProvider=venue_provider.provider,
        )
        offers_factories.OfferFactory(venue=venue_provider.venue, idAtProvider="c'est déjà pris :'(")

        partial_request_json["offerId"] = product_offer.id

        response = client.with_explicit_token(plain_api_key).patch(self.endpoint_url, json=partial_request_json)

        assert response.status_code == 400
        assert response.json == expected_response_json

    def test_update_subcategory_raises_error(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue_provider.venue,
            subcategoryId=subcategories.ABO_LUDOTHEQUE.id,
            lastProvider=venue_provider.provider,
        )

        response = client.with_explicit_token(plain_api_key).patch(
            self.endpoint_url,
            json={"offerId": product_offer.id, "categoryRelatedFields": {"category": "LIVRE_AUDIO_PHYSIQUE"}},
        )

        assert response.status_code == 400
        assert response.json == {
            "product.subcategory": [
                "Only ABO_BIBLIOTHEQUE, ABO_CONCERT, ABO_LIVRE_NUMERIQUE, ABO_MEDIATHEQUE, ABO_PLATEFORME_MUSIQUE, ABO_PLATEFORME_VIDEO, ABO_PRATIQUE_ART, ABO_PRESSE_EN_LIGNE, ABO_SPECTACLE, ACHAT_INSTRUMENT, APP_CULTURELLE, AUTRE_SUPPORT_NUMERIQUE, CAPTATION_MUSIQUE, CARTE_JEUNES, CARTE_MUSEE, LIVRE_AUDIO_PHYSIQUE, LIVRE_NUMERIQUE, LOCATION_INSTRUMENT, PARTITION, PLATEFORME_PRATIQUE_ARTISTIQUE, PODCAST, PRATIQUE_ART_VENTE_DISTANCE, SPECTACLE_ENREGISTRE, SUPPORT_PHYSIQUE_FILM, TELECHARGEMENT_LIVRE_AUDIO, TELECHARGEMENT_MUSIQUE, VISITE_VIRTUELLE, VOD products can be edited"
            ]
        }

    def test_update_unallowed_subcategory_product_raises_error(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue_provider.venue,
            bookingEmail="notify@example.com",
            lastProvider=venue_provider.provider,
            subcategoryId=subcategories.CARTE_CINE_ILLIMITE.id,
        )

        response = client.with_explicit_token(plain_api_key).patch(
            self.endpoint_url,
            json={"offerId": product_offer.id, "bookingEmail": "spam@example.com"},
        )

        assert response.status_code == 400
        assert response.json == {
            "product.subcategory": [
                "Only ABO_BIBLIOTHEQUE, ABO_CONCERT, ABO_LIVRE_NUMERIQUE, ABO_MEDIATHEQUE, ABO_PLATEFORME_MUSIQUE, ABO_PLATEFORME_VIDEO, ABO_PRATIQUE_ART, ABO_PRESSE_EN_LIGNE, ABO_SPECTACLE, ACHAT_INSTRUMENT, APP_CULTURELLE, AUTRE_SUPPORT_NUMERIQUE, CAPTATION_MUSIQUE, CARTE_JEUNES, CARTE_MUSEE, LIVRE_AUDIO_PHYSIQUE, LIVRE_NUMERIQUE, LOCATION_INSTRUMENT, PARTITION, PLATEFORME_PRATIQUE_ARTISTIQUE, PODCAST, PRATIQUE_ART_VENTE_DISTANCE, SPECTACLE_ENREGISTRE, SUPPORT_PHYSIQUE_FILM, TELECHARGEMENT_LIVRE_AUDIO, TELECHARGEMENT_MUSIQUE, VISITE_VIRTUELLE, VOD products can be edited"
            ]
        }

    def test_update_name_and_description(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue_provider.venue,
            lastProvider=venue_provider.provider,
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
            ean="1234567890124",
        )

        offer_id = product_offer.id
        new_name = product_offer.name + " updated"
        new_desc = product_offer.description + " updated"

        expected_num_queries = 1  # get api key
        expected_num_queries += 1  # get offer

        expected_num_queries += 1  # get price categories
        expected_num_queries += 1  # get mediations
        expected_num_queries += 1  # get stocks

        expected_num_queries += 1  # select oa
        expected_num_queries += 1  # update offer

        expected_num_queries += 1  # check venue offerer address
        expected_num_queries += 1  # FF WIP_REFACTO_FUTURE_OFFER
        with assert_num_queries(expected_num_queries):
            response = client.with_explicit_token(plain_api_key).patch(
                self.endpoint_url,
                json={"offerId": offer_id, "name": new_name, "description": new_desc},
            )

            assert response.status_code == 200
            assert response.json["name"] == new_name
            assert response.json["description"] == new_desc

        assert product_offer.name == new_name
        assert product_offer.description == new_desc

    def test_update_location_with_physical_location(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider(provider_has_ticketing_urls=True)
        product = self.create_base_product(
            venue=venue_provider.venue, provider=venue_provider.provider, subcategoryId=subcategories.PARTITION.id
        )

        other_venue = providers_factories.VenueProviderFactory(provider=venue_provider.provider).venue
        json_data = {"location": {"type": "physical", "venueId": other_venue.id}}

        response = self.send_update_request(client, plain_api_key, product, json_data)
        assert response.status_code == 200

        assert product.venueId == other_venue.id
        assert product.venue.offererAddress.id == other_venue.offererAddress.id

    def test_update_location_for_digital_product(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider(provider_has_ticketing_urls=True)
        venue = venue_provider.venue
        product = self.create_base_product(
            venue=venue_provider.venue,
            provider=venue_provider.provider,
            subcategoryId=subcategories.LIVRE_NUMERIQUE.id,
            url="https://ebook.download",
        )

        other_venue = offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer)
        providers_factories.VenueProviderFactory(provider=venue_provider.provider, venue=other_venue)
        json_data = {"location": {"type": "digital", "venueId": other_venue.id, "url": "https://oops.fr"}}

        response = self.send_update_request(client, plain_api_key, product, json_data)
        assert response.status_code == 400
        assert response.json == {"offererAddress": ["Une offre numérique ne peut pas avoir d'adresse"]}

    def test_update_location_with_address(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider(provider_has_ticketing_urls=True)
        venue = venue_provider.venue
        product = self.create_base_product(venue=venue, provider=venue_provider.provider)
        product = self.create_base_product(
            venue=venue_provider.venue, provider=venue_provider.provider, subcategoryId=subcategories.PARTITION.id
        )

        other_venue = offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer)
        address = geography_factories.AddressFactory(
            latitude=50.63153,
            longitude=3.06089,
            postalCode=59000,
            city="Lille",
        )

        providers_factories.VenueProviderFactory(provider=venue_provider.provider, venue=other_venue)
        json_data = {"location": {"type": "address", "venueId": other_venue.id, "addressId": address.id}}

        response = self.send_update_request(client, plain_api_key, product, json_data)
        assert response.status_code == 200

        assert product.offererAddress.addressId == address.id

    def send_update_request(self, client, plain_api_key, product, json_data):
        url = self.endpoint_url
        return client.with_explicit_token(plain_api_key).patch(
            url,
            json={"offerId": product.id, **json_data},
        )
