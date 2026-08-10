import datetime
from unittest import mock

import pytest
import time_machine

from pcapi.connectors import youtube
from pcapi.core.categories import subcategories
from pcapi.core.geography import factories as geography_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.providers import factories as providers_factories
from pcapi.models import db

from tests.routes import image_data
from tests.routes.public.helpers import PublicAPIVenueEndpointHelper


FROZEN_NOW = datetime.datetime(2026, 6, 25, 12, 30, tzinfo=datetime.timezone.utc)

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

    # --- `accessibility`


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

    @pytest.mark.parametrize("kept_stage_director", ["François Truffaut", ""])
    def test_should_keep_the_extra_data_subfields_that_are_not_sent(self, kept_stage_director):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(
            venue=venue_provider.venue,
            provider=venue_provider.provider,
            extraData={"stageDirector": kept_stage_director, "visa": "22757"},
        )

        response = self.make_request(
            plain_api_key,
            {"event_id": event.id},
            json_body={"categoryRelatedFields": {"category": "SEANCE_CINE", "visa": "27414"}},
        )

        assert response.status_code == 200, response.json
        assert response.json["categoryRelatedFields"]["stageDirector"] == kept_stage_director

        db.session.refresh(event)
        assert event.extraData == {"stageDirector": kept_stage_director, "visa": "27414"}

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


@pytest.mark.usefixtures("db_session")
class Returns401Test(PatchEventEndpointHelper):
    def test_should_raise_401_because_not_authenticated(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        before_update = event.dateUpdated

        response = self.make_request(path_params={"event_id": event.id}, json_body={"name": "Jules et Jim"})

        assert response.status_code == 401
        assert response.json == {"auth": "API key required"}

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


    def test_should_raise_400_because_description_is_too_long(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(plain_api_key, {"event_id": event.id}, json_body={"description": "a" * 10_001})

        assert response.status_code == 400
        assert response.json == {"description": ["ensure this value has at most 10000 characters"]}


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


    # --- `categoryRelatedFields`


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

    # --- `idAtProvider`

    def test_should_raise_400_because_id_at_provider_is_already_taken_by_another_offer_of_the_venue(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        id_at_provider = "seance-du-soir"
        offers_factories.OfferFactory(venue=venue_provider.venue, idAtProvider=id_at_provider)

        response = self.make_request(plain_api_key, {"event_id": event.id}, json_body={"idAtProvider": id_at_provider})

        assert response.status_code == 400
        assert response.json == {"idAtProvider": [f"`{id_at_provider}` is already taken by another venue offer"]}


@pytest.mark.usefixtures("db_session")
class Returns404Test(PatchEventEndpointHelper):
    EVENT_NOT_FOUND = {"event_id": ["The event offer could not be found"]}
    VENUE_NOT_FOUND = {"global": "Venue cannot be found"}

    # --- The event


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


