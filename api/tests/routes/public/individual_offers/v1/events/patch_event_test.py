import datetime
import logging
from unittest import mock

import pytest
import time_machine

from pcapi import settings
from pcapi.connectors import youtube
from pcapi.core import testing
from pcapi.core.categories import subcategories
from pcapi.core.geography import factories as geography_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.providers import factories as providers_factories
from pcapi.core.search.models import IndexationReason
from pcapi.models import db
from pcapi.utils import human_ids

from tests.routes import image_data
from tests.routes.public.helpers import PublicAPIVenueEndpointHelper


FROZEN_NOW = datetime.datetime(2026, 6, 25, 12, 30, tzinfo=datetime.UTC)

VIDEO_URL = "https://www.youtube.com/watch?v=fW6goBu8aP0"
VIDEO_METADATA = youtube.YoutubeVideoMetadata(
    id="fW6goBu8aP0",
    title="Les Quatre Cents Coups — bande-annonce",
    thumbnail_url="/thumbnails/fW6goBu8aP0.jpg",
    duration=131,
)

PREVIOUS_VIDEO_METADATA = {
    "videoUrl": "https://www.youtube.com/watch?v=ECNtXXewvHY",
    "videoExternalId": "ECNtXXewvHY",
    "videoTitle": "Jules et Jim — bande-annonce",
    "videoThumbnailUrl": "/thumbnails/ECNtXXewvHY.jpg",
    "videoDuration": 262,
}


def has_log(caplog: pytest.LogCaptureFixture, technical_message_id: str) -> bool:
    return any(getattr(record, "technical_message_id", None) == technical_message_id for record in caplog.records)


class PatchEventEndpointHelper(PublicAPIVenueEndpointHelper):
    endpoint_url = "/public/offers/v1/events/{event_id}"
    endpoint_method = "patch"
    default_path_params = {"event_id": 1}

    DEFAULT_EVENT_DATA = {
        # SEANCE_CINE because it is an event, accepts double bookings, and is not withdrawable
        "subcategoryId": subcategories.SEANCE_CINE.id,
        "name": "Les Quatre Cents Coups",
        "description": "Antoine Doinel, treize ans, fugue dans les rues de Paris.",
        "durationMinutes": 99,
        "bookingEmail": "notify@cinema.example.com",
        "bookingContact": "contact@cinema.example.com",
        "withdrawalDetails": "À retirer à la caisse du cinéma",
        "isDuo": True,
        "audioDisabilityCompliant": True,
        "mentalDisabilityCompliant": False,
        "motorDisabilityCompliant": True,
        "visualDisabilityCompliant": False,
        # `stageDirector` and `visa` are two of the three conditional fields for SEANCE_CINE
        "extraData": {"stageDirector": "François Truffaut", "visa": "22757"},
        # in the past relative to `FROZEN_NOW`, so the base event is published
        "publicationDatetime": datetime.datetime(2026, 1, 15, 10, 0),
        # in the past relative to `FROZEN_NOW`, so the base event is bookable
        "bookingAllowedDatetime": datetime.datetime(2026, 2, 1, 10, 0),
    }

    def setup_base_resource(self, venue=None, provider=None, **kwargs) -> offers_models.Offer:
        return offers_factories.EventOfferFactory(
            venue=venue or self.setup_venue(),
            lastProvider=provider,
            # `kwargs` always wins over `DEFAULT_EVENT_DATA`, including when it passes `None`
            **{**self.DEFAULT_EVENT_DATA, **kwargs},
        )

    def setup_product_based_resource(self, venue, provider) -> tuple[offers_models.Product, offers_models.Offer]:
        product = offers_factories.ProductFactory(
            subcategoryId=subcategories.SEANCE_CINE.id,
            name="Les Quatre Cents Coups",
            description="Le film de François Truffaut, restauré en 4K.",
            durationMinutes=99,
            extraData={"stageDirector": "François Truffaut", "visa": "22757"},
        )
        event = self.setup_base_resource(
            venue=venue,
            provider=provider,
            product=product,
            description=None,
            durationMinutes=None,
            extraData=None,
        )
        return product, event

    # redefined below so that they are not inherited by every class
    test_should_raise_404_because_has_no_access_to_venue = None
    test_should_raise_404_because_venue_provider_is_inactive = None
    test_should_raise_401_because_not_authenticated = None


@pytest.mark.usefixtures("db_session")
class Returns200Test(PatchEventEndpointHelper):
    # --- Plain fields

    @pytest.mark.parametrize(
        "request_field,column,new_value",
        [
            ("name", "name", "Jules et Jim"),
            ("description", "description", "Deux amis épris de la même femme."),
            ("bookingEmail", "bookingEmail", "nouvelle-adresse@cinema.example.com"),
            ("bookingContact", "bookingContact", "nouveau-contact@cinema.example.com"),
            ("itemCollectionDetails", "withdrawalDetails", "À retirer au distributeur du hall"),
            ("eventDuration", "durationMinutes", 105),
            ("externalTicketOfficeUrl", "externalTicketOfficeUrl", "https://cinema.example.com/billetterie"),
            ("idAtProvider", "idAtProvider", "seance-du-soir"),
        ],
    )
    def test_should_update_a_single_field(self, request_field, column, new_value):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        assert getattr(event, column) != new_value

        response = self.make_request(plain_api_key, {"event_id": event.id}, json_body={request_field: new_value})

        assert response.status_code == 200, response.json
        assert response.json[request_field] == new_value

        db.session.refresh(event)
        assert getattr(event, column) == new_value

    @pytest.mark.parametrize(
        "request_field,column",
        [
            ("description", "description"),
            ("bookingEmail", "bookingEmail"),
            ("bookingContact", "bookingContact"),
            ("itemCollectionDetails", "withdrawalDetails"),
            ("eventDuration", "durationMinutes"),
            ("idAtProvider", "idAtProvider"),
            ("publicationDatetime", "publicationDatetime"),
            ("bookingAllowedDatetime", "bookingAllowedDatetime"),
        ],
    )
    def test_should_clear_a_field_sent_as_null(self, request_field, column):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        assert getattr(event, column) is not None

        response = self.make_request(plain_api_key, {"event_id": event.id}, json_body={request_field: None})

        assert response.status_code == 200, response.json
        assert response.json[request_field] is None

        db.session.refresh(event)
        assert getattr(event, column) is None

    @pytest.mark.parametrize("new_value", [True, False], ids=["enable", "disable"])
    def test_should_toggle_double_bookings(self, new_value):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(
            venue=venue_provider.venue, provider=venue_provider.provider, isDuo=not new_value
        )

        response = self.make_request(
            plain_api_key, {"event_id": event.id}, json_body={"enableDoubleBookings": new_value}
        )

        assert response.status_code == 200, response.json
        assert response.json["enableDoubleBookings"] is new_value

        db.session.refresh(event)
        assert event.isDuo is new_value

    @time_machine.travel(FROZEN_NOW, tick=False)
    def test_should_update_many_fields_at_once(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(
            plain_api_key,
            {"event_id": event.id},
            json_body={
                "name": "Jules et Jim",
                "description": "Deux amis épris de la même femme.",
                "bookingEmail": "nouvelle-adresse@cinema.example.com",
                "bookingContact": "nouveau-contact@cinema.example.com",
                "itemCollectionDetails": "À retirer au distributeur du hall",
                "eventDuration": 105,
                "externalTicketOfficeUrl": "https://cinema.example.com/billetterie",
                "enableDoubleBookings": False,
                "idAtProvider": "seance-du-soir",
                "accessibility": {
                    "audioDisabilityCompliant": False,
                    "mentalDisabilityCompliant": True,
                    "motorDisabilityCompliant": False,
                    "visualDisabilityCompliant": True,
                },
                "categoryRelatedFields": {
                    "category": "SEANCE_CINE",
                    "stageDirector": "Jean-Luc Godard",
                    "visa": "27414",
                },
                # sent in Europe/Paris
                "publicationDatetime": "2026-08-01T08:00:00+02:00",
                "bookingAllowedDatetime": "2026-07-15T10:00:00+02:00",
            },
        )

        assert response.status_code == 200, response.json

        db.session.refresh(event)
        expected = {
            "name": "Jules et Jim",
            "description": "Deux amis épris de la même femme.",
            "bookingEmail": "nouvelle-adresse@cinema.example.com",
            "bookingContact": "nouveau-contact@cinema.example.com",
            "withdrawalDetails": "À retirer au distributeur du hall",
            "durationMinutes": 105,
            "externalTicketOfficeUrl": "https://cinema.example.com/billetterie",
            "isDuo": False,
            "idAtProvider": "seance-du-soir",
            "audioDisabilityCompliant": False,
            "mentalDisabilityCompliant": True,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": True,
            "extraData": {"stageDirector": "Jean-Luc Godard", "visa": "27414"},
        }
        assert {column: getattr(event, column) for column in expected} == expected
        # stored in UTC
        assert event.publicationDatetime == datetime.datetime(2026, 8, 1, 6, 0, tzinfo=datetime.UTC)
        assert event.bookingAllowedDatetime == datetime.datetime(2026, 7, 15, 8, 0, tzinfo=datetime.UTC)

    # --- Field name spellings

    def test_should_accept_a_snake_case_body(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        address = geography_factories.AddressFactory(street="28 boulevard des Capucines")

        response = self.make_request(
            plain_api_key,
            {"event_id": event.id},
            json_body={
                # `EventOfferEdition`
                "booking_email": "nouvelle-adresse@cinema.example.com",
                "event_duration": 105,
                # the only field with an explicit alias: `itemCollectionDetails`
                "withdrawal_details": "À retirer au distributeur du hall",
                # `PartialAccessibility`
                "accessibility": {"audio_disability_compliant": False},
                # `AddressLocation`
                "location": {
                    "type": "address",
                    "venue_id": venue_provider.venueId,
                    "address_id": address.id,
                },
                # the per-category model, whose only aliased field is `subcategory_id` -> `category`
                "category_related_fields": {
                    "subcategory_id": "SEANCE_CINE",
                    "stageDirector": "Jean-Luc Godard",
                },
            },
        )

        assert response.status_code == 200, response.json
        # the response stays camelCase, whatever spelling the request used
        assert response.json["bookingEmail"] == "nouvelle-adresse@cinema.example.com"

        db.session.refresh(event)
        expected = {
            "bookingEmail": "nouvelle-adresse@cinema.example.com",
            "durationMinutes": 105,
            "withdrawalDetails": "À retirer au distributeur du hall",
            "audioDisabilityCompliant": False,
            "extraData": {"stageDirector": "Jean-Luc Godard", "visa": "22757"},
        }
        assert {column: getattr(event, column) for column in expected} == expected
        assert event.offererAddress.addressId == address.id

    # --- `idAtProvider`

    def test_should_accept_an_id_at_provider_already_used_by_an_offer_of_another_venue(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        id_at_provider = "seance-du-soir"
        offers_factories.OfferFactory(venue=self.setup_venue(), idAtProvider=id_at_provider)

        response = self.make_request(plain_api_key, {"event_id": event.id}, json_body={"idAtProvider": id_at_provider})

        assert response.status_code == 200, response.json
        assert response.json["idAtProvider"] == id_at_provider

        db.session.refresh(event)
        assert event.idAtProvider == id_at_provider

    # --- `accessibility`

    def test_should_update_every_accessibility_field(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        flipped = {
            "audioDisabilityCompliant": False,
            "mentalDisabilityCompliant": True,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": True,
        }

        response = self.make_request(plain_api_key, {"event_id": event.id}, json_body={"accessibility": flipped})

        assert response.status_code == 200, response.json
        assert response.json["accessibility"] == flipped

        db.session.refresh(event)
        assert {column: getattr(event, column) for column in flipped} == flipped

    def test_should_update_accessibility_partially_and_leave_the_other_ones_unchanged(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        assert event.audioDisabilityCompliant is True

        response = self.make_request(
            plain_api_key,
            {"event_id": event.id},
            json_body={"accessibility": {"audioDisabilityCompliant": False}},
        )

        assert response.status_code == 200, response.json
        assert response.json["accessibility"] == {
            "audioDisabilityCompliant": False,
            "mentalDisabilityCompliant": self.DEFAULT_EVENT_DATA["mentalDisabilityCompliant"],
            "motorDisabilityCompliant": self.DEFAULT_EVENT_DATA["motorDisabilityCompliant"],
            "visualDisabilityCompliant": self.DEFAULT_EVENT_DATA["visualDisabilityCompliant"],
        }

        db.session.refresh(event)
        assert event.audioDisabilityCompliant is False

    # --- Withdrawal

    @pytest.mark.parametrize(
        "request_field,column,new_value",
        [
            ("itemCollectionDetails", "withdrawalDetails", "À retirer au guichet du théâtre"),
            ("bookingContact", "bookingContact", "nouveau-contact@theatre.example.com"),
        ],
    )
    def test_should_update_a_withdrawal_related_field_on_an_email_ticketed_event(
        self, request_field, column, new_value
    ):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        # CONCERT is withdrawable, and BY_EMAIL requires both a delay and a booking contact
        event = self.setup_base_resource(
            venue=venue_provider.venue,
            provider=venue_provider.provider,
            subcategoryId=subcategories.CONCERT.id,
            withdrawalType=offers_models.WithdrawalTypeEnum.BY_EMAIL,
            withdrawalDelay=86400,
        )
        assert getattr(event, column) != new_value

        response = self.make_request(plain_api_key, {"event_id": event.id}, json_body={request_field: new_value})

        assert response.status_code == 200, response.json
        assert response.json[request_field] == new_value

        db.session.refresh(event)
        assert getattr(event, column) == new_value

    def test_should_update_the_booking_contact_on_an_in_app_ticketed_event(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(
            venue=venue_provider.venue,
            provider=venue_provider.provider,
            subcategoryId=subcategories.CONCERT.id,
            withdrawalType=offers_models.WithdrawalTypeEnum.IN_APP,
        )
        assert venue_provider.provider.hasTicketingService

        response = self.make_request(
            plain_api_key,
            {"event_id": event.id},
            json_body={"bookingContact": "nouveau@theatre.fr"},
        )

        assert response.status_code == 200, response.json
        assert response.json["bookingContact"] == "nouveau@theatre.fr"

        db.session.refresh(event)
        assert event.bookingContact == "nouveau@theatre.fr"

    def test_should_update_the_booking_contact_when_the_ticketing_is_set_on_the_venue(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider(provider_has_ticketing_urls=False)
        providers_factories.VenueProviderExternalUrlsFactory(venueProvider=venue_provider)
        event = self.setup_base_resource(
            venue=venue_provider.venue,
            provider=venue_provider.provider,
            subcategoryId=subcategories.CONCERT.id,
            withdrawalType=offers_models.WithdrawalTypeEnum.IN_APP,
        )
        assert not venue_provider.provider.hasTicketingService
        assert venue_provider.hasTicketingService

        response = self.make_request(
            plain_api_key,
            {"event_id": event.id},
            json_body={"bookingContact": "nouveau@theatre.fr"},
        )

        assert response.status_code == 200, response.json

        db.session.refresh(event)
        assert event.bookingContact == "nouveau@theatre.fr"

    # --- `categoryRelatedFields`

    def test_should_update_category_related_fields(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(
            plain_api_key,
            {"event_id": event.id},
            json_body={
                "categoryRelatedFields": {
                    "category": "SEANCE_CINE",
                    "stageDirector": "Jean-Luc Godard",
                    "visa": "27414",
                }
            },
        )

        assert response.status_code == 200, response.json
        # `author` is the third conditional field of SEANCE_CINE
        assert response.json["categoryRelatedFields"] == {
            "category": "SEANCE_CINE",
            "author": None,
            "stageDirector": "Jean-Luc Godard",
            "visa": "27414",
        }

        db.session.refresh(event)
        assert event.extraData == {"stageDirector": "Jean-Luc Godard", "visa": "27414"}

    def test_should_keep_the_extra_data_subfields_that_are_not_sent(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(
            venue=venue_provider.venue,
            provider=venue_provider.provider,
            extraData={"stageDirector": "François Truffaut", "visa": "22757"},
        )

        response = self.make_request(
            plain_api_key,
            {"event_id": event.id},
            json_body={"categoryRelatedFields": {"category": "SEANCE_CINE", "visa": "27414"}},
        )

        assert response.status_code == 200, response.json
        assert response.json["categoryRelatedFields"]["stageDirector"] == "François Truffaut"

        db.session.refresh(event)
        assert event.extraData == {"stageDirector": "François Truffaut", "visa": "27414"}

    def test_should_store_an_empty_category_related_field_as_an_empty_string(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        assert event.extraData["stageDirector"] == "François Truffaut"

        response = self.make_request(
            plain_api_key,
            {"event_id": event.id},
            json_body={"categoryRelatedFields": {"category": "SEANCE_CINE", "stageDirector": ""}},
        )

        assert response.status_code == 200, response.json
        assert response.json["categoryRelatedFields"]["stageDirector"] == ""

        db.session.refresh(event)
        assert event.extraData == {"stageDirector": "", "visa": "22757"}

    @pytest.mark.parametrize(
        "category_related_fields",
        [None, {"category": "SEANCE_CINE"}],
        ids=["null", "category only"],
    )
    def test_should_keep_extra_data_when_no_subfield_is_sent(self, category_related_fields):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        before_update = event.dateUpdated

        response = self.make_request(
            plain_api_key, {"event_id": event.id}, json_body={"categoryRelatedFields": category_related_fields}
        )

        assert response.status_code == 200, response.json

        db.session.refresh(event)
        assert event.dateUpdated == before_update

    def test_should_ignore_an_unknown_category_related_field(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(
            plain_api_key,
            {"event_id": event.id},
            json_body={
                "categoryRelatedFields": {
                    "category": "SEANCE_CINE",
                    "stageDirector": "Jean-Luc Godard",
                    "producteur": "Marcel Berbert",
                }
            },
        )

        assert response.status_code == 200, response.json
        assert "producteur" not in response.json["categoryRelatedFields"]

        db.session.refresh(event)
        assert event.extraData == {"stageDirector": "Jean-Luc Godard", "visa": "22757"}

    def test_should_store_the_music_type_as_codes_and_return_it_as_a_slug(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(
            venue=venue_provider.venue,
            provider=venue_provider.provider,
            subcategoryId=subcategories.CONCERT.id,
            extraData={"author": "Ray Charles"},
        )

        response = self.make_request(
            plain_api_key,
            {"event_id": event.id},
            json_body={"categoryRelatedFields": {"category": "CONCERT", "musicType": "JAZZ-BLUES"}},
        )

        assert response.status_code == 200, response.json

        db.session.refresh(event)
        assert event.extraData == {
            "author": "Ray Charles",
            "gtl_id": "02000000",
            "musicType": "501",
            "musicSubType": "-1",
        }
        assert response.json["categoryRelatedFields"] == {
            "category": "CONCERT",
            "author": "Ray Charles",
            "musicType": "JAZZ-BLUES",
            "performer": None,
        }

    def test_should_store_the_show_type_as_codes_and_return_it_as_a_slug(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(
            venue=venue_provider.venue,
            provider=venue_provider.provider,
            subcategoryId=subcategories.SPECTACLE_REPRESENTATION.id,
            extraData={"showType": "1510", "showSubType": "1512"},
        )

        response = self.make_request(
            plain_api_key,
            {"event_id": event.id},
            json_body={
                "categoryRelatedFields": {"category": "SPECTACLE_REPRESENTATION", "showType": "OPERA-SINGSPIEL"}
            },
        )

        assert response.status_code == 200, response.json

        db.session.refresh(event)
        assert event.extraData == {"showType": "1510", "showSubType": "1516"}
        assert response.json["categoryRelatedFields"] == {
            "category": "SPECTACLE_REPRESENTATION",
            "showType": "OPERA-SINGSPIEL",
            "author": None,
            "stageDirector": None,
            "performer": None,
        }

    # --- `publicationDatetime`

    @time_machine.travel(FROZEN_NOW, tick=False)
    @pytest.mark.parametrize(
        "partial_body,expected_stored,expected_returned",
        [
            # sent in Europe/Paris, read back in UTC
            (
                {"publicationDatetime": "2026-08-01T08:00:00+02:00"},
                datetime.datetime(2026, 8, 1, 6, 0, tzinfo=datetime.UTC),
                "2026-08-01T06:00:00Z",
            ),
            # the `now` literal resolves to the current instant
            (
                {"publicationDatetime": "now"},
                datetime.datetime(2026, 6, 25, 12, 30, tzinfo=datetime.UTC),
                "2026-06-25T12:30:00Z",
            ),
        ],
    )
    def test_should_publish_the_event_at_the_requested_datetime(self, partial_body, expected_stored, expected_returned):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(plain_api_key, {"event_id": event.id}, json_body=partial_body)

        assert response.status_code == 200, response.json
        assert response.json["publicationDatetime"] == expected_returned

        db.session.refresh(event)
        assert event.publicationDatetime == expected_stored

    # --- `isActive` (deprecated)

    def test_should_ignore_deprecated_is_active_when_it_is_none(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        before_update = event.dateUpdated
        assert event.isActive is True

        response = self.make_request(plain_api_key, {"event_id": event.id}, json_body={"isActive": None})

        assert response.status_code == 200, response.json

        db.session.refresh(event)
        assert event.dateUpdated == before_update
        # `isActive` is derived from `publicationDatetime`, which was left untouched
        assert event.isActive is True

    def test_should_deactivate_with_deprecated_is_active_false(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        assert event.publicationDatetime is not None

        response = self.make_request(plain_api_key, {"event_id": event.id}, json_body={"isActive": False})

        assert response.status_code == 200, response.json
        assert response.json["publicationDatetime"] is None
        assert response.json["status"] == "INACTIVE"

        db.session.refresh(event)
        assert event.publicationDatetime is None

    @time_machine.travel(FROZEN_NOW, tick=False)
    def test_should_activate_with_deprecated_is_active_true(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(
            venue=venue_provider.venue, provider=venue_provider.provider, publicationDatetime=None
        )
        assert event.isActive is False

        response = self.make_request(plain_api_key, {"event_id": event.id}, json_body={"isActive": True})

        assert response.status_code == 200, response.json
        assert response.json["publicationDatetime"] == "2026-06-25T12:30:00Z"

        db.session.refresh(event)
        assert event.publicationDatetime == datetime.datetime(2026, 6, 25, 12, 30, tzinfo=datetime.UTC)
        assert event.isActive is True

    @time_machine.travel(FROZEN_NOW, tick=False)
    def test_should_let_publication_datetime_win_over_deprecated_is_active(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(
            plain_api_key,
            {"event_id": event.id},
            json_body={"isActive": False, "publicationDatetime": "2026-08-01T08:00:00+02:00"},
        )

        assert response.status_code == 200, response.json
        assert response.json["publicationDatetime"] == "2026-08-01T06:00:00Z"
        assert response.json["status"] == "SCHEDULED"

        db.session.refresh(event)
        assert event.publicationDatetime == datetime.datetime(2026, 8, 1, 6, 0, tzinfo=datetime.UTC)

    # --- `bookingAllowedDatetime`

    @time_machine.travel(FROZEN_NOW, tick=False)
    @mock.patch("pcapi.core.reminders.external.reminders_notifications.notify_users_offer_is_bookable")
    def test_should_delay_bookings_until_the_booking_allowed_datetime(self, notify_mock):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(
            # sent in Europe/Paris, read back in UTC
            plain_api_key,
            {"event_id": event.id},
            json_body={"bookingAllowedDatetime": "2026-07-15T10:00:00+02:00"},
        )

        assert response.status_code == 200, response.json
        assert response.json["bookingAllowedDatetime"] == "2026-07-15T08:00:00Z"
        # bookings are not open yet: users are notified when the datetime is reached
        notify_mock.assert_not_called()

        db.session.refresh(event)
        assert event.bookingAllowedDatetime == datetime.datetime(2026, 7, 15, 8, 0, tzinfo=datetime.UTC)

    @time_machine.travel(FROZEN_NOW, tick=False)
    @mock.patch("pcapi.core.reminders.external.reminders_notifications.notify_users_offer_is_bookable")
    def test_should_notify_users_when_bookings_are_opened_immediately(self, notify_mock):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(plain_api_key, {"event_id": event.id}, json_body={"bookingAllowedDatetime": None})

        assert response.status_code == 200, response.json
        assert response.json["bookingAllowedDatetime"] is None
        assert notify_mock.call_count == 1

        db.session.refresh(event)
        assert event.bookingAllowedDatetime is None

    # --- `location`

    def test_should_move_the_event_to_another_venue_with_a_physical_location(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        # a venue of another offerer: the only requirement is that it is linked to the calling provider
        other_venue = providers_factories.VenueProviderFactory(provider=venue_provider.provider).venue
        assert other_venue.managingOffererId != venue_provider.venue.managingOffererId
        offerer_address_id = event.offererAddressId

        response = self.make_request(
            plain_api_key,
            {"event_id": event.id},
            json_body={"location": {"type": "physical", "venueId": other_venue.id}},
        )

        assert response.status_code == 200, response.json

        db.session.refresh(event)
        assert event.offererAddress.addressId == other_venue.offererAddress.addressId
        assert event.offererAddress.label is None

        assert event.venueId == other_venue.id
        assert event.venue.managingOffererId == other_venue.managingOffererId

        assert event.offererAddressId != offerer_address_id

    def test_should_move_the_event_to_another_venue_with_an_address_location(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        other_venue = providers_factories.VenueProviderFactory(provider=venue_provider.provider).venue
        address = geography_factories.AddressFactory(street="28 boulevard des Capucines")

        response = self.make_request(
            plain_api_key,
            {"event_id": event.id},
            json_body={"location": {"type": "address", "venueId": other_venue.id, "addressId": address.id}},
        )

        assert response.status_code == 200, response.json

        db.session.refresh(event)
        assert event.venueId == other_venue.id
        assert event.offererAddress.addressId == address.id
        assert event.offererAddress.type is offerers_models.LocationType.OFFER_LOCATION
        # the offerer address is attached to the venue the event moves to, not to the one it leaves
        assert event.offererAddress.offererId == other_venue.managingOffererId

    @pytest.mark.parametrize("address_label", [None, "Salle Truffaut"])
    def test_should_update_the_offerer_address_with_an_address_location(self, address_label):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue = venue_provider.venue
        event = self.setup_base_resource(venue=venue, provider=venue_provider.provider)
        address = geography_factories.AddressFactory(street="28 boulevard des Capucines")
        assert address.id != venue.offererAddress.addressId
        offerer_address_id = event.offererAddressId

        location = {"type": "address", "venueId": venue.id, "addressId": address.id}
        if address_label is not None:
            location["addressLabel"] = address_label

        response = self.make_request(plain_api_key, {"event_id": event.id}, json_body={"location": location})

        assert response.status_code == 200, response.json
        # `get_location` reports an address location because the offerer address differs from
        # the venue one and its label differs from the venue public name
        assert response.json["location"] == {
            "type": "address",
            "venueId": venue.id,
            "addressId": address.id,
            "addressLabel": address_label,
        }

        db.session.refresh(event)
        assert event.offererAddress.addressId == address.id
        assert event.offererAddress.label == address_label
        assert event.offererAddress.type is offerers_models.LocationType.OFFER_LOCATION

        assert event.offererAddressId != offerer_address_id

    def test_should_drop_the_address_label_when_the_address_and_label_match_the_venue_ones(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue = venue_provider.venue
        event = self.setup_base_resource(venue=venue, provider=venue_provider.provider)
        offerer_address_id = event.offererAddressId
        before_update = event.dateUpdated

        response = self.make_request(
            plain_api_key,
            {"event_id": event.id},
            json_body={
                "location": {
                    "type": "address",
                    "venueId": venue.id,
                    "addressId": venue.offererAddress.addressId,
                    "addressLabel": venue.publicName,
                }
            },
        )

        assert response.status_code == 200, response.json

        db.session.refresh(event)
        assert event.offererAddress.label is None
        assert event.offererAddress.addressId == venue.offererAddress.addressId
        assert event.offererAddress.type is offerers_models.LocationType.OFFER_LOCATION
        assert event.offererAddress.id != venue.offererAddress.id
        assert event.offererAddressId == offerer_address_id
        assert event.dateUpdated == before_update

    def test_should_keep_the_address_label_when_it_differs_from_the_venue_public_name(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue = venue_provider.venue
        event = self.setup_base_resource(venue=venue, provider=venue_provider.provider)
        assert venue.publicName != "Salle Truffaut"
        offerer_address_id = event.offererAddressId

        response = self.make_request(
            plain_api_key,
            {"event_id": event.id},
            json_body={
                "location": {
                    "type": "address",
                    "venueId": venue.id,
                    "addressId": venue.offererAddress.addressId,
                    "addressLabel": "Salle Truffaut",
                }
            },
        )

        assert response.status_code == 200, response.json

        db.session.refresh(event)
        assert event.offererAddress.label == "Salle Truffaut"
        assert event.offererAddress.addressId == venue.offererAddress.addressId

        assert event.offererAddressId != offerer_address_id

    # --- `image`

    def test_should_add_an_image(self, clear_tests_assets_bucket):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        assert event.image is None
        before_update = event.dateUpdated

        response = self.make_request(
            plain_api_key,
            {"event_id": event.id},
            json_body={"image": {"file": image_data.GOOD_IMAGE, "credit": "Les Films du Carrosse"}},
        )

        assert response.status_code == 200, response.json

        db.session.refresh(event)
        mediation = db.session.query(offers_models.Mediation).one()
        expected_url = f"{settings.OBJECT_STORAGE_URL}/thumbs/mediations/{human_ids.humanize(mediation.id)}"
        assert event.image.url == expected_url
        assert response.json["image"] == {"url": expected_url, "credit": "Les Films du Carrosse"}
        # the image lives in its own Mediation row: the offer itself is left untouched
        assert event.dateUpdated == before_update

    def test_should_keep_the_image_when_it_is_explicitly_sent_as_none(self, clear_tests_assets_bucket):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        self.make_request(plain_api_key, {"event_id": event.id}, json_body={"image": {"file": image_data.GOOD_IMAGE}})
        mediation_id = db.session.query(offers_models.Mediation).one().id
        before_update = event.dateUpdated

        response = self.make_request(plain_api_key, {"event_id": event.id}, json_body={"image": None})

        assert response.status_code == 200, response.json

        db.session.refresh(event)
        assert db.session.query(offers_models.Mediation).one().id == mediation_id
        assert event.dateUpdated == before_update

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_should_reindex_the_event_when_an_image_is_added(
        self, mocked_async_index_offer_ids, clear_tests_assets_bucket
    ):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(
            plain_api_key, {"event_id": event.id}, json_body={"image": {"file": image_data.GOOD_IMAGE}}
        )

        assert response.status_code == 200, response.json
        mocked_async_index_offer_ids.assert_called_once_with([event.id], reason=IndexationReason.MEDIATION_CREATION)

    def test_should_not_log_an_offer_update_when_only_the_image_changed(self, caplog, clear_tests_assets_bucket):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        with caplog.at_level(logging.INFO):
            response = self.make_request(
                plain_api_key, {"event_id": event.id}, json_body={"image": {"file": image_data.GOOD_IMAGE}}
            )

        assert response.status_code == 200, response.json
        assert not has_log(caplog, "offer.updated")

    # --- `videoUrl`

    @mock.patch("pcapi.core.videos.api.get_video_metadata_from_cache")
    def test_should_add_a_video(self, get_video_metadata_mock):
        get_video_metadata_mock.return_value = VIDEO_METADATA
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        assert event.metaData is None
        before_update = event.dateUpdated

        response = self.make_request(plain_api_key, {"event_id": event.id}, json_body={"videoUrl": VIDEO_URL})

        assert response.status_code == 200, response.json
        assert response.json["videoUrl"] == VIDEO_URL

        db.session.refresh(event)
        assert event.metaData.videoUrl == VIDEO_URL
        assert event.metaData.videoExternalId == VIDEO_METADATA.id
        assert event.metaData.videoTitle == VIDEO_METADATA.title
        assert event.metaData.videoThumbnailUrl == VIDEO_METADATA.thumbnail_url
        assert event.metaData.videoDuration == VIDEO_METADATA.duration
        # the video lives in its own OfferMetaData row: the offer itself is left untouched
        assert event.dateUpdated == before_update

    @mock.patch("pcapi.core.videos.api.get_video_metadata_from_cache")
    def test_should_replace_the_existing_video(self, get_video_metadata_mock):
        get_video_metadata_mock.return_value = VIDEO_METADATA
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        offers_factories.OfferMetaDataFactory(offer=event, **PREVIOUS_VIDEO_METADATA)

        response = self.make_request(plain_api_key, {"event_id": event.id}, json_body={"videoUrl": VIDEO_URL})

        assert response.status_code == 200, response.json
        assert response.json["videoUrl"] == VIDEO_URL

        db.session.refresh(event)
        assert event.metaData.videoUrl == VIDEO_URL
        assert event.metaData.videoExternalId == VIDEO_METADATA.id
        assert event.metaData.videoTitle == VIDEO_METADATA.title
        assert event.metaData.videoThumbnailUrl == VIDEO_METADATA.thumbnail_url
        assert event.metaData.videoDuration == VIDEO_METADATA.duration

    def test_should_delete_the_video_when_video_url_is_none(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        offers_factories.OfferMetaDataFactory(offer=event, **PREVIOUS_VIDEO_METADATA)

        response = self.make_request(plain_api_key, {"event_id": event.id}, json_body={"videoUrl": None})

        assert response.status_code == 200, response.json
        assert response.json["videoUrl"] is None

        db.session.refresh(event)
        assert event.metaData.videoUrl is None
        assert event.metaData.videoExternalId is None
        assert event.metaData.videoTitle is None
        assert event.metaData.videoThumbnailUrl is None
        assert event.metaData.videoDuration is None

    def test_should_keep_the_video_when_video_url_is_not_sent(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        offers_factories.OfferMetaDataFactory(offer=event, **PREVIOUS_VIDEO_METADATA)

        response = self.make_request(plain_api_key, {"event_id": event.id}, json_body={"name": "Jules et Jim"})

        assert response.status_code == 200, response.json
        assert response.json["videoUrl"] == PREVIOUS_VIDEO_METADATA["videoUrl"]

        db.session.refresh(event)
        assert event.metaData.videoUrl == PREVIOUS_VIDEO_METADATA["videoUrl"]
        assert event.metaData.videoExternalId == PREVIOUS_VIDEO_METADATA["videoExternalId"]

    @pytest.mark.parametrize(
        "initial_metadata,sent_url,expected_message_id",
        [
            (None, VIDEO_URL, "offer.video.added"),
            ({}, VIDEO_URL, "offer.video.added"),
            (PREVIOUS_VIDEO_METADATA, VIDEO_URL, "offer.video.updated"),
            (PREVIOUS_VIDEO_METADATA, None, "offer.video.deleted"),
        ],
        ids=["no metadata row", "metadata without video", "replaced", "deleted"],
    )
    @mock.patch("pcapi.core.videos.api.get_video_metadata_from_cache")
    def test_should_log_the_video_change(
        self, get_video_metadata_mock, caplog, initial_metadata, sent_url, expected_message_id
    ):
        get_video_metadata_mock.return_value = VIDEO_METADATA
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        if initial_metadata is not None:
            offers_factories.OfferMetaDataFactory(offer=event, **initial_metadata)

        with caplog.at_level(logging.INFO):
            response = self.make_request(plain_api_key, {"event_id": event.id}, json_body={"videoUrl": sent_url})

        assert response.status_code == 200, response.json
        assert has_log(caplog, expected_message_id)

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    @mock.patch("pcapi.core.videos.api.get_video_metadata_from_cache")
    def test_should_not_reindex_the_event_when_only_the_video_changed(
        self, get_video_metadata_mock, mocked_async_index_offer_ids
    ):
        get_video_metadata_mock.return_value = VIDEO_METADATA
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(plain_api_key, {"event_id": event.id}, json_body={"videoUrl": VIDEO_URL})

        assert response.status_code == 200, response.json
        mocked_async_index_offer_ids.assert_not_called()

    @mock.patch("pcapi.core.videos.api.get_video_metadata_from_cache")
    def test_should_not_log_an_offer_update_when_only_the_video_changed(self, get_video_metadata_mock, caplog):
        get_video_metadata_mock.return_value = VIDEO_METADATA
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        with caplog.at_level(logging.INFO):
            response = self.make_request(plain_api_key, {"event_id": event.id}, json_body={"videoUrl": VIDEO_URL})

        assert response.status_code == 200, response.json
        assert not has_log(caplog, "offer.updated")

    # --- Events the calling provider did not create

    @pytest.mark.parametrize(
        "partial_body,expected_changes",
        [
            ({"name": "Jules et Jim"}, {"name": "Jules et Jim"}),
            (
                {"description": "Deux amis épris de la même femme."},
                {"description": "Deux amis épris de la même femme."},
            ),
            (
                {"externalTicketOfficeUrl": "https://cinema.example.com/billetterie"},
                {"externalTicketOfficeUrl": "https://cinema.example.com/billetterie"},
            ),
            ({"accessibility": {"audioDisabilityCompliant": False}}, {"audioDisabilityCompliant": False}),
        ],
    )
    def test_should_update_an_event_synchronized_by_another_provider(self, partial_body, expected_changes):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        synchronizing_provider = providers_factories.ProviderFactory()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=synchronizing_provider)
        assert not event.lastProvider.isAllocine
        assert not event.lastProvider.hasOffererProvider

        response = self.make_request(plain_api_key, {"event_id": event.id}, json_body=partial_body)

        assert response.status_code == 200, response.json

        db.session.refresh(event)
        assert {column: getattr(event, column) for column in expected_changes} == expected_changes

    def test_should_update_an_event_synchronized_by_another_public_api_provider(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        other_provider = providers_factories.PublicApiProviderFactory()
        providers_factories.OffererProviderFactory(provider=other_provider)
        event = self.setup_base_resource(venue=venue_provider.venue, provider=other_provider)
        assert event.lastProvider.hasOffererProvider

        # outside the base set, but part of `EDITABLE_FIELDS_FOR_INDIVIDUAL_OFFERS_API_PROVIDER`
        response = self.make_request(plain_api_key, {"event_id": event.id}, json_body={"eventDuration": 105})

        assert response.status_code == 200, response.json

        db.session.refresh(event)
        assert event.durationMinutes == 105

    def test_should_enable_double_bookings_on_an_allocine_event(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        allocine_provider = providers_factories.AllocineProviderFactory()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=allocine_provider, isDuo=False)
        assert event.lastProvider.isAllocine

        response = self.make_request(plain_api_key, {"event_id": event.id}, json_body={"enableDoubleBookings": True})

        assert response.status_code == 200, response.json
        assert response.json["enableDoubleBookings"] is True

        db.session.refresh(event)
        assert event.isDuo is True

    def test_should_accept_resending_the_current_value_of_a_field_locked_by_the_provider(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        synchronizing_provider = providers_factories.ProviderFactory()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=synchronizing_provider)
        assert not event.lastProvider.isAllocine
        assert not event.lastProvider.hasOffererProvider
        before_update = event.dateUpdated

        # `durationMinutes` is outside this provider's editable set
        response = self.make_request(
            plain_api_key, {"event_id": event.id}, json_body={"eventDuration": event.durationMinutes}
        )

        assert response.status_code == 200, response.json

        db.session.refresh(event)
        assert event.dateUpdated == before_update

    # --- Events linked to a product

    def test_should_update_an_event_linked_to_a_product(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product, event = self.setup_product_based_resource(venue_provider.venue, venue_provider.provider)

        response = self.make_request(plain_api_key, {"event_id": event.id}, json_body={"name": "Jules et Jim"})

        assert response.status_code == 200, response.json
        assert response.json["name"] == "Jules et Jim"
        assert response.json["description"] == product.description
        assert response.json["eventDuration"] == product.durationMinutes
        assert response.json["categoryRelatedFields"] == {
            "category": "SEANCE_CINE",
            "author": None,
            "stageDirector": "François Truffaut",
            "visa": "22757",
        }

        db.session.refresh(event)
        assert event.name == "Jules et Jim"

    @pytest.mark.parametrize(
        "request_field,column,new_value",
        [
            ("description", "description", "Deux amis épris de la même femme."),
            ("eventDuration", "durationMinutes", 105),
        ],
    )
    def test_should_ignore_a_field_owned_by_the_product(self, request_field, column, new_value):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        _, event = self.setup_product_based_resource(venue_provider.venue, venue_provider.provider)
        before_update = event.dateUpdated
        product_value = getattr(event, column)
        assert product_value != new_value

        response = self.make_request(plain_api_key, {"event_id": event.id}, json_body={request_field: new_value})

        assert response.status_code == 200, response.json
        # the response still exposes the product value, not the one that was just sent
        assert response.json[request_field] == product_value

        db.session.refresh(event)
        assert event.dateUpdated == before_update

    @pytest.mark.parametrize(
        "request_field,column",
        [("description", "description"), ("eventDuration", "durationMinutes")],
    )
    def test_should_ignore_a_field_owned_by_the_product_sent_as_null(self, request_field, column):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        _, event = self.setup_product_based_resource(venue_provider.venue, venue_provider.provider)
        before_update = event.dateUpdated
        product_value = getattr(event, column)
        assert product_value is not None

        response = self.make_request(plain_api_key, {"event_id": event.id}, json_body={request_field: None})

        assert response.status_code == 200, response.json
        assert response.json[request_field] == product_value

        db.session.refresh(event)
        assert event.dateUpdated == before_update

    def test_should_log_a_change_for_a_field_owned_by_the_product(self, caplog):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product, event = self.setup_product_based_resource(venue_provider.venue, venue_provider.provider)
        before_update = event.dateUpdated

        with caplog.at_level(logging.INFO):
            response = self.make_request(
                plain_api_key,
                {"event_id": event.id},
                json_body={"description": "Deux amis épris de la même femme."},
            )

        assert response.status_code == 200, response.json
        [update_log] = [
            record for record in caplog.records if getattr(record, "technical_message_id", None) == "offer.updated"
        ]
        assert update_log.extra["changes"] == {
            "description": {
                "oldValue": product.description,
                "newValue": "Deux amis épris de la même femme.",
            }
        }
        db.session.refresh(event)
        assert event.dateUpdated == before_update

    def test_should_accept_category_related_fields_identical_to_the_product_ones(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product, event = self.setup_product_based_resource(venue_provider.venue, venue_provider.provider)
        before_update = event.dateUpdated

        response = self.make_request(
            plain_api_key,
            {"event_id": event.id},
            json_body={"categoryRelatedFields": {"category": "SEANCE_CINE", **product.extraData}},
        )

        assert response.status_code == 200, response.json

        db.session.refresh(event)
        assert event.dateUpdated == before_update

    # --- Response

    def test_should_return_the_updated_event(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(plain_api_key, {"event_id": event.id}, json_body={"name": "Jules et Jim"})

        assert response.status_code == 200, response.json
        assert response.json == {
            "id": event.id,
            "name": "Jules et Jim",
            "description": "Antoine Doinel, treize ans, fugue dans les rues de Paris.",
            "accessibility": {
                "audioDisabilityCompliant": True,
                "mentalDisabilityCompliant": False,
                "motorDisabilityCompliant": True,
                "visualDisabilityCompliant": False,
            },
            "bookingContact": "contact@cinema.example.com",
            "bookingEmail": "notify@cinema.example.com",
            "categoryRelatedFields": {
                "category": "SEANCE_CINE",
                "author": None,
                "stageDirector": "François Truffaut",
                "visa": "22757",
            },
            "enableDoubleBookings": True,
            "eventDuration": 99,
            "externalTicketOfficeUrl": None,
            "hasTicket": False,
            "idAtProvider": event.idAtProvider,
            "image": None,
            "itemCollectionDetails": "À retirer à la caisse du cinéma",
            "location": {"type": "physical", "venueId": venue_provider.venueId},
            "priceCategories": [],
            "publicationDatetime": "2026-01-15T10:00:00Z",
            "bookingAllowedDatetime": "2026-02-01T10:00:00Z",
            "status": "SOLD_OUT",
            "videoUrl": None,
        }

    @time_machine.travel(FROZEN_NOW, tick=False)
    @pytest.mark.parametrize(
        "partial_body,expected_status",
        [
            ({"publicationDatetime": None}, "INACTIVE"),
            ({"publicationDatetime": "2026-08-01T08:00:00+02:00"}, "SCHEDULED"),
            ({"bookingAllowedDatetime": "2026-08-01T08:00:00+02:00"}, "PUBLISHED"),
            ({"name": "Jules et Jim"}, "ACTIVE"),
        ],
    )
    def test_should_return_the_new_status(self, partial_body, expected_status):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        offers_factories.EventStockFactory(offer=event)

        response = self.make_request(plain_api_key, {"event_id": event.id}, json_body=partial_body)

        assert response.status_code == 200, response.json
        assert response.json["status"] == expected_status

    # --- Side effects

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_should_reindex_the_event(self, mocked_async_index_offer_ids):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(
            plain_api_key,
            {"event_id": event.id},
            json_body={"name": "Jules et Jim", "bookingEmail": "nouvelle-adresse@cinema.example.com"},
        )

        assert response.status_code == 200, response.json
        mocked_async_index_offer_ids.assert_called_once_with(
            [event.id],
            reason=IndexationReason.OFFER_UPDATE,
            log_extra={"changes": {"name", "bookingEmail"}},
        )

    def test_should_log_the_update_with_its_changes(self, caplog):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        with caplog.at_level(logging.INFO):
            response = self.make_request(
                plain_api_key,
                {"event_id": event.id},
                json_body={"name": "Jules et Jim", "bookingEmail": "nouvelle-adresse@cinema.example.com"},
            )

        assert response.status_code == 200, response.json
        [update_log] = [
            record for record in caplog.records if getattr(record, "technical_message_id", None) == "offer.updated"
        ]
        assert update_log.extra == {
            "offer_id": event.id,
            "venue_id": event.venueId,
            "product_id": None,
            "changes": {
                "name": {"oldValue": "Les Quatre Cents Coups", "newValue": "Jules et Jim"},
                "bookingEmail": {
                    "oldValue": "notify@cinema.example.com",
                    "newValue": "nouvelle-adresse@cinema.example.com",
                },
            },
        }

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_should_change_nothing_when_body_is_empty(self, mocked_async_index_offer_ids, caplog):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        before_update = event.dateUpdated

        with caplog.at_level(logging.INFO):
            response = self.make_request(plain_api_key, {"event_id": event.id}, json_body={})

        assert response.status_code == 200, response.json
        mocked_async_index_offer_ids.assert_not_called()
        assert not has_log(caplog, "offer.updated")

        db.session.refresh(event)
        assert event.dateUpdated == before_update

    def test_should_not_issue_more_queries_than_expected(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        event_id = event.id

        num_queries = 1  # retrieve the API key, joining its provider
        num_queries += 1  # retrieve the event, joining its metadata, product, venue and addresses
        num_queries += 1  # selectinload the price categories
        num_queries += 1  # selectinload the mediations
        num_queries += 1  # selectinload the stocks
        num_queries += 1  # retrieve the venue provider
        num_queries += 1  # lazy-load `provider.offererProvider`, for `hasOffererProvider`
        num_queries += 1  # update the offer

        with testing.assert_num_queries(num_queries):
            response = self.make_request(plain_api_key, {"event_id": event_id}, json_body={"name": "Jules et Jim"})
            assert response.status_code == 200, response.json


@pytest.mark.usefixtures("db_session")
class Returns401Test(PatchEventEndpointHelper):
    def test_should_raise_401_because_not_authenticated(self):
        _plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        before_update = event.dateUpdated

        response = self.make_request(path_params={"event_id": event.id}, json_body={"name": "Jules et Jim"})

        assert response.status_code == 401
        assert response.json == {"auth": "API key required"}

        db.session.refresh(event)
        assert event.dateUpdated == before_update


@pytest.mark.usefixtures("db_session")
class Returns403Test(PatchEventEndpointHelper):
    def test_should_raise_403_because_the_provider_is_inactive(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        before_update = event.dateUpdated
        venue_provider.provider.isActive = False
        db.session.flush()

        response = self.make_request(plain_api_key, {"event_id": event.id}, json_body={"name": "Jules et Jim"})

        assert response.status_code == 403
        assert response.json == {"auth": ["Inactive provider"]}

        db.session.refresh(event)
        assert event.dateUpdated == before_update


@pytest.mark.usefixtures("db_session")
class Returns400Test(PatchEventEndpointHelper):
    # --- Request body schema

    def test_should_raise_400_because_an_unknown_field_is_sent(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(
            plain_api_key,
            {"event_id": event.id},
            json_body={"withdrawalDetails": "À retirer au guichet"},
        )

        assert response.status_code == 400
        assert response.json == {"withdrawalDetails": ["extra fields not permitted"]}

    @pytest.mark.parametrize(
        "name,expected_error",
        [
            ("", "ensure this value has at least 1 characters"),
            ("a" * 141, "ensure this value has at most 140 characters"),
        ],
        ids=["empty", "too long"],
    )
    def test_should_raise_400_because_name_length_is_out_of_bounds(self, name, expected_error):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(plain_api_key, {"event_id": event.id}, json_body={"name": name})

        assert response.status_code == 400
        assert response.json == {"name": [expected_error]}

    def test_should_raise_400_because_description_is_too_long(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(plain_api_key, {"event_id": event.id}, json_body={"description": "a" * 10_001})

        assert response.status_code == 400
        assert response.json == {"description": ["ensure this value has at most 10000 characters"]}

    @pytest.mark.parametrize("request_field", ["bookingEmail", "bookingContact"])
    def test_should_raise_400_because_an_email_field_is_invalid(self, request_field):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(
            plain_api_key, {"event_id": event.id}, json_body={request_field: "pas-une-adresse"}
        )

        assert response.status_code == 400
        assert response.json == {request_field: ["value is not a valid email address"]}

    @pytest.mark.parametrize(
        "url,expected_error",
        [
            ("https:bloup.com", "invalid or missing URL scheme"),
            (5, "invalid or missing URL scheme"),
            ("", "ensure this value has at least 1 characters"),
        ],
        ids=["missing scheme", "not a string", "empty"],
    )
    def test_should_raise_400_because_external_ticket_office_url_is_invalid(self, url, expected_error):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(plain_api_key, {"event_id": event.id}, json_body={"externalTicketOfficeUrl": url})

        assert response.status_code == 400
        assert response.json == {"externalTicketOfficeUrl": [expected_error]}

    def test_should_raise_400_because_id_at_provider_is_too_long(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(plain_api_key, {"event_id": event.id}, json_body={"idAtProvider": "a" * 71})

        assert response.status_code == 400
        assert response.json == {"idAtProvider": ["ensure this value has at most 70 characters"]}

    @time_machine.travel(FROZEN_NOW, tick=False)
    @pytest.mark.parametrize("request_field", ["publicationDatetime", "bookingAllowedDatetime"])
    def test_should_raise_400_because_the_datetime_is_not_timezone_aware(self, request_field):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(
            plain_api_key, {"event_id": event.id}, json_body={request_field: "2027-01-01T00:00:00"}
        )

        assert response.status_code == 400
        assert response.json == {request_field: ["The datetime must be timezone-aware."]}

    @pytest.mark.parametrize("request_field", ["publicationDatetime", "bookingAllowedDatetime"])
    def test_should_raise_400_because_the_datetime_is_in_the_past(self, request_field):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(
            plain_api_key, {"event_id": event.id}, json_body={request_field: "2021-01-01T00:00:00+00:00"}
        )

        assert response.status_code == 400
        assert response.json == {request_field: ["The datetime must be in the future."]}

    def test_should_raise_400_because_publication_datetime_literal_is_not_lowercase_now(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(plain_api_key, {"event_id": event.id}, json_body={"publicationDatetime": "NOW"})

        assert response.status_code == 400
        assert response.json == {
            "publicationDatetime": ["invalid datetime format", "unexpected value; permitted: 'now'"]
        }

    def test_should_raise_400_because_booking_allowed_datetime_does_not_accept_the_now_literal(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(plain_api_key, {"event_id": event.id}, json_body={"bookingAllowedDatetime": "now"})

        assert response.status_code == 400
        assert response.json == {"bookingAllowedDatetime": ["invalid datetime format"]}

    def test_should_raise_400_because_video_url_is_not_a_youtube_url(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(
            plain_api_key,
            {"event_id": event.id},
            json_body={"videoUrl": "https://peer.tube/w/jZ7ky5kZ4Bk3u88aCvRZPe"},
        )

        assert response.status_code == 400
        assert response.json == {
            "videoUrl": [
                "Your video must be from the Youtube plateform, it should be public and should not be a short nor a user's profile"
            ]
        }

    # --- `location`

    def test_should_raise_400_because_location_type_is_unknown(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(
            plain_api_key,
            {"event_id": event.id},
            json_body={"location": {"type": "hologram", "venueId": venue_provider.venueId}},
        )

        assert response.status_code == 400
        assert response.json == {
            "location": [
                "No match for discriminator 'type' and value 'hologram' "
                "(allowed values: 'physical', 'digital', 'address')"
            ]
        }

    def test_should_raise_400_because_address_location_address_id_is_not_an_integer(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(
            plain_api_key,
            {"event_id": event.id},
            json_body={"location": {"type": "address", "venueId": venue_provider.venueId, "addressId": "coucou"}},
        )

        assert response.status_code == 400
        assert response.json == {"location.AddressLocation.addressId": ["value is not a valid integer"]}

    @pytest.mark.parametrize(
        "address_label,expected_error",
        [
            ("", "ensure this value has at least 1 characters"),
            ("a" * 201, "ensure this value has at most 200 characters"),
        ],
        ids=["empty", "too long"],
    )
    def test_should_raise_400_because_address_location_label_length_is_out_of_bounds(
        self, address_label, expected_error
    ):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        address = geography_factories.AddressFactory(street="6 rue de la Paix")

        response = self.make_request(
            plain_api_key,
            {"event_id": event.id},
            json_body={
                "location": {
                    "type": "address",
                    "venueId": venue_provider.venueId,
                    "addressId": address.id,
                    "addressLabel": address_label,
                }
            },
        )

        assert response.status_code == 400
        assert response.json == {"location.AddressLocation.addressLabel": [expected_error]}

    def test_should_raise_400_because_location_has_an_extra_field(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        address = geography_factories.AddressFactory(street="6 rue de la Paix")

        response = self.make_request(
            plain_api_key,
            {"event_id": event.id},
            json_body={
                "location": {
                    "type": "address",
                    "venueId": venue_provider.venueId,
                    "addressId": address.id,
                    "adressLabel": "un seul d",
                }
            },
        )

        assert response.status_code == 400
        assert response.json == {"location.AddressLocation.adressLabel": ["extra fields not permitted"]}

    @pytest.mark.parametrize(
        "location,model",
        [
            ({"type": "physical"}, "PhysicalLocation"),
            ({"type": "digital", "url": "https://cinema.example.com/en-ligne"}, "DigitalLocation"),
            ({"type": "address", "addressId": 1}, "AddressLocation"),
        ],
        ids=["physical", "digital", "address"],
    )
    def test_should_raise_400_because_location_has_no_venue_id(self, location, model):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(plain_api_key, {"event_id": event.id}, json_body={"location": location})

        assert response.status_code == 400
        assert response.json == {f"location.{model}.venueId": ["field required"]}

    # --- Online / offline coherence

    def test_should_raise_400_because_a_digital_location_is_not_allowed_for_an_offline_only_event(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        assert subcategories.SEANCE_CINE.is_offline_only

        response = self.make_request(
            plain_api_key,
            {"event_id": event.id},
            json_body={
                "location": {
                    "type": "digital",
                    "venueId": venue_provider.venueId,
                    "url": "https://cinema.example.com/en-ligne",
                }
            },
        )

        assert response.status_code == 400
        assert response.json == {
            "url": ['Une offre de sous-catégorie "Séance de cinéma" ne peut contenir un champ `url`']
        }

    def test_should_raise_400_because_an_online_event_cannot_have_an_address(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(
            venue=venue_provider.venue,
            provider=venue_provider.provider,
            subcategoryId=subcategories.LIVESTREAM_MUSIQUE.id,
            url=None,
            offererAddress=None,
        )

        response = self.make_request(
            plain_api_key,
            {"event_id": event.id},
            json_body={
                "location": {
                    "type": "digital",
                    "venueId": venue_provider.venueId,
                    "url": "https://cinema.example.com/en-ligne",
                }
            },
        )

        assert response.status_code == 400
        assert response.json == {"offererAddress": ["Une offre numérique ne peut pas avoir d'adresse"]}

    def test_should_raise_400_because_an_online_event_must_keep_its_url(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(
            venue=venue_provider.venue,
            provider=venue_provider.provider,
            subcategoryId=subcategories.LIVESTREAM_MUSIQUE.id,
            url="https://cinema.example.com/en-ligne",
            offererAddress=None,
        )

        response = self.make_request(plain_api_key, {"event_id": event.id}, json_body={"name": "Jules et Jim"})

        assert response.status_code == 400
        assert response.json == {"url": ['Une offre de catégorie "Livestream musical" doit contenir un champ `url`']}

    # --- `categoryRelatedFields`

    def test_should_raise_400_because_the_category_cannot_be_changed(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(
            plain_api_key,
            {"event_id": event.id},
            json_body={"categoryRelatedFields": {"category": "CONCERT", "musicType": "JAZZ-BLUES"}},
        )

        assert response.status_code == 400
        assert response.json == {"categoryRelatedFields.category": ["The category cannot be changed"]}

    def test_should_raise_400_because_music_type_is_null(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(
            venue=venue_provider.venue,
            provider=venue_provider.provider,
            subcategoryId=subcategories.CONCERT.id,
            extraData={"author": "Ray Charles"},
        )

        response = self.make_request(
            plain_api_key,
            {"event_id": event.id},
            json_body={"categoryRelatedFields": {"category": "CONCERT", "musicType": None}},
        )

        assert response.status_code == 400
        assert response.json == {"categoryRelatedFields": ["If musicType is set, it cannot be NULL"]}

    @pytest.mark.parametrize("extra_data", [{}, {"musicType": ""}], ids=["missing", "empty"])
    def test_should_raise_400_because_a_concert_has_no_music_type(self, extra_data):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(
            venue=venue_provider.venue,
            provider=venue_provider.provider,
            subcategoryId=subcategories.CONCERT.id,
            extraData=extra_data,
        )

        response = self.make_request(
            plain_api_key,
            {"event_id": event.id},
            json_body={"categoryRelatedFields": {"category": "CONCERT", "author": "Ray Charles"}},
        )

        assert response.status_code == 400
        assert response.json == {"musicType": ["Ce champ est obligatoire"]}

    def test_should_raise_400_because_extra_data_of_an_event_linked_to_a_product_cannot_be_changed(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        _, event = self.setup_product_based_resource(venue_provider.venue, venue_provider.provider)

        response = self.make_request(
            plain_api_key,
            {"event_id": event.id},
            json_body={"categoryRelatedFields": {"category": "SEANCE_CINE", "stageDirector": "Jean-Luc Godard"}},
        )

        assert response.status_code == 400
        assert response.json == {"global": ["Les extraData des offres avec produit ne sont pas modifiables"]}

    # --- `image`

    def test_should_raise_400_because_the_image_is_invalid(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(
            plain_api_key, {"event_id": event.id}, json_body={"image": {"file": image_data.WRONG_IMAGE_SIZE}}
        )

        assert response.status_code == 400
        assert response.json == {"imageFile": "The image is too small. It must be above 400x600 pixels."}

    # --- `videoUrl`

    @pytest.mark.settings(YOUTUBE_API_BACKEND="pcapi.connectors.youtube.YoutubeNotFoundBackend")
    def test_should_raise_400_because_video_cannot_be_found_on_youtube(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(plain_api_key, {"event_id": event.id}, json_body={"videoUrl": VIDEO_URL})

        assert response.status_code == 400
        assert response.json == {
            "videoUrl": [
                "This video cannot be found on youtube. It is most likely a private video. Please check your URL."
            ]
        }

    # --- `name`

    def test_should_raise_400_because_name_is_null(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(plain_api_key, {"event_id": event.id}, json_body={"name": None})

        assert response.status_code == 400
        assert response.json == {"name": ["cannot be null"]}

    def test_should_raise_400_because_name_contains_an_ean(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(
            plain_api_key,
            {"event_id": event.id},
            json_body={"name": "Les Quatre Cents Coups - 9782070286256"},
        )

        assert response.status_code == 400
        assert response.json == {"name": ["Le titre d'une offre ne peut contenir l'EAN"]}

    # --- `accessibility`

    def test_should_raise_400_because_an_accessibility_field_is_null(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(
            plain_api_key,
            {"event_id": event.id},
            json_body={"accessibility": {"audioDisabilityCompliant": None}},
        )

        assert response.status_code == 400
        assert response.json == {"global": ["L’accessibilité de l’offre doit être définie"]}

    # --- `eventDuration`

    def test_should_raise_400_because_event_duration_is_24_hours_or_more(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(plain_api_key, {"event_id": event.id}, json_body={"eventDuration": 1_440})

        assert response.status_code == 400
        assert response.json == {
            "eventDuration": [
                "The duration must be under 1440 minutes (24 hours). For events lasting 24 hours or more "
                "(e.g., a 3-day festival pass), please leave this field empty."
            ]
        }

    # --- `enableDoubleBookings`

    def test_should_raise_400_because_the_category_does_not_allow_double_bookings(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        # LIVESTREAM_MUSIQUE is online-only, hence `url=None` to keep the url guard out of the way
        event = self.setup_base_resource(
            venue=venue_provider.venue,
            provider=venue_provider.provider,
            subcategoryId=subcategories.LIVESTREAM_MUSIQUE.id,
            isDuo=False,
            url=None,
        )
        assert not subcategories.LIVESTREAM_MUSIQUE.can_be_duo

        response = self.make_request(plain_api_key, {"event_id": event.id}, json_body={"enableDoubleBookings": True})

        assert response.status_code == 400
        assert response.json == {"enableDoubleBookings": ["the category chosen does not allow double bookings"]}

    # --- `idAtProvider`

    def test_should_raise_400_because_id_at_provider_is_already_taken_by_another_offer_of_the_venue(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        id_at_provider = "seance-du-soir"
        offers_factories.OfferFactory(venue=venue_provider.venue, idAtProvider=id_at_provider)

        response = self.make_request(plain_api_key, {"event_id": event.id}, json_body={"idAtProvider": id_at_provider})

        assert response.status_code == 400
        assert response.json == {"idAtProvider": [f"`{id_at_provider}` is already taken by another venue offer"]}

    def test_should_raise_400_because_id_at_provider_is_set_on_an_event_without_provider(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=None)
        assert event.lastProvider is None

        response = self.make_request(
            plain_api_key, {"event_id": event.id}, json_body={"idAtProvider": "seance-du-soir"}
        )

        assert response.status_code == 400
        assert response.json == {
            "idAtProvider": ["Une offre ne peut être créée ou éditée avec un idAtProvider si elle n'a pas de provider"]
        }

    # --- Withdrawal

    def test_should_raise_400_because_booking_contact_is_removed_on_a_withdrawable_event(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(
            venue=venue_provider.venue,
            provider=venue_provider.provider,
            subcategoryId=subcategories.CONCERT.id,
            withdrawalType=offers_models.WithdrawalTypeEnum.NO_TICKET,
        )

        response = self.make_request(plain_api_key, {"event_id": event.id}, json_body={"bookingContact": None})

        assert response.status_code == 400
        assert response.json == {
            "offer": ["Une offre qui a un ticket retirable doit avoir l'email du contact de réservation"]
        }

    def test_should_raise_400_because_neither_the_provider_nor_the_venue_supports_the_ticketing_interface(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider(provider_has_ticketing_urls=False)
        event = self.setup_base_resource(
            venue=venue_provider.venue,
            provider=venue_provider.provider,
            subcategoryId=subcategories.CONCERT.id,
            withdrawalType=offers_models.WithdrawalTypeEnum.IN_APP,
        )
        assert not venue_provider.provider.hasTicketingService
        assert not venue_provider.hasTicketingService

        response = self.make_request(
            plain_api_key,
            {"event_id": event.id},
            json_body={"bookingContact": "nouveau@theatre.fr"},
        )

        assert response.status_code == 400
        assert response.json == {
            "offer": ["Vous devez supporter l'interface de billeterie pour créer des offres avec billet"]
        }

    # --- Offer validation status

    @pytest.mark.parametrize(
        "validation_status",
        [offers_models.OfferValidationStatus.PENDING, offers_models.OfferValidationStatus.REJECTED],
        ids=["pending", "rejected"],
    )
    def test_should_raise_400_because_the_event_is_pending_or_rejected(self, validation_status):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(
            venue=venue_provider.venue, provider=venue_provider.provider, validation=validation_status
        )

        response = self.make_request(plain_api_key, {"event_id": event.id}, json_body={"name": "Jules et Jim"})

        assert response.status_code == 400
        assert response.json == {"global": ["Les offres refusées ou en attente de validation ne sont pas modifiables"]}

    # --- Fields locked by the provider

    @pytest.mark.parametrize(
        "provider_factory",
        [providers_factories.AllocineProviderFactory, providers_factories.ProviderFactory],
        ids=["allocine", "other provider"],
    )
    def test_should_raise_400_because_the_duration_cannot_be_changed_on_a_synchronized_event(self, provider_factory):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=provider_factory())

        response = self.make_request(plain_api_key, {"event_id": event.id}, json_body={"eventDuration": 105})

        assert response.status_code == 400
        assert response.json == {"durationMinutes": ["Vous ne pouvez pas modifier ce champ"]}

    def test_should_list_every_rejected_field_when_several_are_not_editable(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=providers_factories.ProviderFactory())

        response = self.make_request(
            plain_api_key,
            {"event_id": event.id},
            json_body={"eventDuration": 105, "enableDoubleBookings": False},
        )

        assert response.status_code == 400
        assert response.json == {
            "durationMinutes": ["Vous ne pouvez pas modifier ce champ"],
            "isDuo": ["Vous ne pouvez pas modifier ce champ"],
        }

    # --- Rollback

    def test_should_not_persist_any_change_when_the_request_is_rejected(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(
            venue=venue_provider.venue,
            provider=venue_provider.provider,
            subcategoryId=subcategories.LIVESTREAM_MUSIQUE.id,
            url=None,
            offererAddress=None,
        )
        before_update = event.dateUpdated

        response = self.make_request(
            plain_api_key,
            {"event_id": event.id},
            json_body={
                "name": "Jules et Jim",
                "location": {
                    "type": "digital",
                    "venueId": venue_provider.venueId,
                    "url": "https://cinema.example.com/en-ligne",
                },
            },
        )

        assert response.status_code == 400
        assert response.json == {"offererAddress": ["Une offre numérique ne peut pas avoir d'adresse"]}

        db.session.refresh(event)
        assert event.dateUpdated == before_update


@pytest.mark.usefixtures("db_session")
class Returns404Test(PatchEventEndpointHelper):
    EVENT_NOT_FOUND = {"event_id": ["The event offer could not be found"]}
    VENUE_NOT_FOUND = {"global": "Venue cannot be found"}

    # --- The event

    def test_should_raise_404_because_event_does_not_exist(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(plain_api_key, {"event_id": event.id + 1}, json_body={"name": "Jules et Jim"})

        assert response.status_code == 404
        assert response.json == self.EVENT_NOT_FOUND

    def test_should_raise_404_because_offer_is_not_an_event(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        thing_offer = offers_factories.ThingOfferFactory(
            venue=venue_provider.venue, lastProvider=venue_provider.provider
        )

        response = self.make_request(plain_api_key, {"event_id": thing_offer.id}, json_body={"name": "Jules et Jim"})

        assert response.status_code == 404
        assert response.json == self.EVENT_NOT_FOUND

    def test_should_raise_404_because_has_no_access_to_venue(self):
        plain_api_key, _ = self.setup_provider()
        event = self.setup_base_resource()

        response = self.make_request(plain_api_key, {"event_id": event.id}, json_body={"name": "Jules et Jim"})

        assert response.status_code == 404
        assert response.json == self.EVENT_NOT_FOUND

    def test_should_raise_404_because_venue_provider_is_inactive(self):
        plain_api_key, venue_provider = self.setup_inactive_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(plain_api_key, {"event_id": event.id}, json_body={"name": "Jules et Jim"})

        assert response.status_code == 404
        assert response.json == self.EVENT_NOT_FOUND

    def test_should_raise_404_because_event_belongs_to_another_provider(self):
        plain_api_key, _ = self.setup_active_venue_provider()
        other_venue_provider = providers_factories.VenueProviderFactory()
        event = self.setup_base_resource(venue=other_venue_provider.venue, provider=other_venue_provider.provider)

        response = self.make_request(plain_api_key, {"event_id": event.id}, json_body={"name": "Jules et Jim"})

        assert response.status_code == 404
        assert response.json == self.EVENT_NOT_FOUND

    # --- `location`

    def test_should_raise_404_because_venue_in_location_is_not_linked_to_provider(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        other_venue = self.setup_venue()
        before_update = event.dateUpdated

        response = self.make_request(
            plain_api_key,
            {"event_id": event.id},
            json_body={"location": {"type": "physical", "venueId": other_venue.id}},
        )

        assert response.status_code == 404
        assert response.json == self.VENUE_NOT_FOUND

        db.session.refresh(event)
        assert event.dateUpdated == before_update

    def test_should_raise_404_because_venue_provider_of_venue_in_location_is_inactive(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        inactive_link = providers_factories.VenueProviderFactory(provider=venue_provider.provider, isActive=False)

        response = self.make_request(
            plain_api_key,
            {"event_id": event.id},
            json_body={"location": {"type": "physical", "venueId": inactive_link.venue.id}},
        )

        assert response.status_code == 404
        assert response.json == self.VENUE_NOT_FOUND

    def test_should_raise_404_because_address_in_location_does_not_exist(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue = venue_provider.venue
        event = self.setup_base_resource(venue=venue, provider=venue_provider.provider)
        unknown_address_id = geography_factories.AddressFactory(street="6 rue de la Paix").id + 1
        before_update = event.dateUpdated

        response = self.make_request(
            plain_api_key,
            {"event_id": event.id},
            json_body={"location": {"type": "address", "venueId": venue.id, "addressId": unknown_address_id}},
        )

        assert response.status_code == 404
        assert response.json == {
            "location.AddressLocation.addressId": [f"There is no address with id {unknown_address_id}"]
        }

        db.session.refresh(event)
        assert event.dateUpdated == before_update
