import base64
from unittest import mock

import pytest
import sqlalchemy.orm as sa_orm

from pcapi.core import testing
from pcapi.core.categories import subcategories
from pcapi.core.geography import factories as geography_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import schemas as offerers_schemas
from pcapi.core.offers import exceptions as offers_exceptions
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import validation as offers_validation
from pcapi.core.videos import exceptions as videos_exceptions
from pcapi.models import api_errors
from pcapi.routes.public import utils as public_utils
from pcapi.routes.public.individual_offers.v1 import constants
from pcapi.routes.public.individual_offers.v1 import serialization
from pcapi.routes.public.individual_offers.v1 import utils
from pcapi.routes.public.individual_offers.v1.serializers import events as events_serializers
from pcapi.utils import image_conversion


pytestmark = pytest.mark.usefixtures("db_session")


class ExtractOffererAddressFromLocationTest:
    GET_ADDRESS = "pcapi.routes.public.utils.get_address_or_raise_404"
    GET_VENUE_LOCATION = "pcapi.core.offers.api.get_or_create_offerer_address_from_address_body"
    GET_OFFER_LOCATION = "pcapi.core.offerers.api.get_or_create_offer_location"

    # --- No location sent

    @mock.patch(GET_ADDRESS)
    def test_should_return_no_offerer_address_when_no_location_is_sent(self, get_address_or_raise_404):
        venue = offerers_factories.VenueFactory()

        assert utils.extract_offerer_address_from_location(None, venue=venue) is None
        get_address_or_raise_404.assert_not_called()

    # --- Physical and digital locations

    @pytest.mark.parametrize(
        "build_location",
        [
            lambda venue: serialization.PhysicalLocation(venue_id=venue.id),
            lambda venue: serialization.DigitalLocation(venue_id=venue.id, url="https://example.com"),
        ],
        ids=["physical", "digital"],
    )
    @mock.patch(GET_ADDRESS)
    @mock.patch(GET_VENUE_LOCATION)
    def test_should_reuse_the_venue_location_without_looking_up_an_address(
        self, get_or_create_offerer_address_from_address_body, get_address_or_raise_404, build_location
    ):
        venue = offerers_factories.VenueFactory()

        offerer_address = utils.extract_offerer_address_from_location(build_location(venue), venue=venue)

        get_address_or_raise_404.assert_not_called()
        get_or_create_offerer_address_from_address_body.assert_called_once_with(
            offerers_schemas.LocationOnlyOnVenueModel(), venue
        )
        assert offerer_address == get_or_create_offerer_address_from_address_body.return_value

    # --- Address location

    @mock.patch(GET_ADDRESS)
    def test_should_look_the_address_up_by_the_id_sent_in_the_location(self, get_address_or_raise_404):
        venue = offerers_factories.VenueFactory()
        address = geography_factories.AddressFactory()
        get_address_or_raise_404.return_value = address

        utils.extract_offerer_address_from_location(
            serialization.AddressLocation(venue_id=venue.id, address_id=address.id, address_label="Salle Jean Vilar"),
            venue=venue,
        )

        get_address_or_raise_404.assert_called_once_with(address.id)

    @mock.patch(GET_OFFER_LOCATION)
    @mock.patch(GET_ADDRESS)
    def test_should_create_an_offer_location_when_the_address_differs_from_the_venue_one(
        self, get_address_or_raise_404, get_or_create_offer_location
    ):
        venue = offerers_factories.VenueFactory()
        address = geography_factories.AddressFactory()
        get_address_or_raise_404.return_value = address

        offerer_address = utils.extract_offerer_address_from_location(
            serialization.AddressLocation(venue_id=venue.id, address_id=address.id, address_label="Salle Jean Vilar"),
            venue=venue,
        )

        get_or_create_offer_location.assert_called_once_with(
            offerer_id=venue.managingOffererId,
            venue_id=venue.id,
            address_id=address.id,
            label="Salle Jean Vilar",
        )
        assert offerer_address == get_or_create_offer_location.return_value

    @mock.patch(GET_OFFER_LOCATION)
    @mock.patch(GET_ADDRESS)
    def test_should_create_an_offer_location_when_only_the_label_differs_from_the_venue_public_name(
        self, get_address_or_raise_404, get_or_create_offer_location
    ):
        venue = offerers_factories.VenueFactory()
        get_address_or_raise_404.return_value = venue.offererAddress.address

        utils.extract_offerer_address_from_location(
            serialization.AddressLocation(
                venue_id=venue.id,
                address_id=venue.offererAddress.addressId,
                address_label="Salle Jean Vilar",
            ),
            venue=venue,
        )

        get_or_create_offer_location.assert_called_once_with(
            offerer_id=venue.managingOffererId,
            venue_id=venue.id,
            address_id=venue.offererAddress.addressId,
            label="Salle Jean Vilar",
        )

    @mock.patch(GET_VENUE_LOCATION)
    @mock.patch(GET_ADDRESS)
    def test_should_reuse_the_venue_location_when_the_address_and_the_label_match_the_venue_ones(
        self, get_address_or_raise_404, get_or_create_offerer_address_from_address_body
    ):
        venue = offerers_factories.VenueFactory()
        get_address_or_raise_404.return_value = venue.offererAddress.address

        offerer_address = utils.extract_offerer_address_from_location(
            serialization.AddressLocation(
                venue_id=venue.id,
                address_id=venue.offererAddress.addressId,
                address_label=venue.publicName,
            ),
            venue=venue,
        )

        get_or_create_offerer_address_from_address_body.assert_called_once_with(
            offerers_schemas.LocationOnlyOnVenueModel(), venue
        )
        assert offerer_address == get_or_create_offerer_address_from_address_body.return_value

    @mock.patch(GET_OFFER_LOCATION)
    @mock.patch(GET_VENUE_LOCATION)
    @mock.patch(GET_ADDRESS)
    def test_should_create_an_offer_location_when_no_label_is_sent_and_the_venue_has_a_public_name(
        self, get_address_or_raise_404, get_or_create_offerer_address_from_address_body, get_or_create_offer_location
    ):
        venue = offerers_factories.VenueFactory()
        get_address_or_raise_404.return_value = venue.offererAddress.address

        utils.extract_offerer_address_from_location(
            serialization.AddressLocation(
                venue_id=venue.id, address_id=venue.offererAddress.addressId, address_label=None
            ),
            venue=venue,
        )

        get_or_create_offerer_address_from_address_body.assert_not_called()
        get_or_create_offer_location.assert_called_once_with(
            offerer_id=venue.managingOffererId,
            venue_id=venue.id,
            address_id=venue.offererAddress.addressId,
            label=None,
        )


class GetVenueWithOffererAddressTest:
    def test_should_return_the_venue_matching_the_id(self):
        venue = offerers_factories.VenueFactory()
        offerers_factories.VenueFactory()

        assert utils.get_venue_with_offerer_address(venue.id) == venue

    def test_should_raise_when_no_venue_matches_the_id(self):
        venue = offerers_factories.VenueFactory()

        with pytest.raises(sa_orm.exc.NoResultFound):
            utils.get_venue_with_offerer_address(venue.id + 1000)

    def test_should_load_the_offerer_address_along_with_the_venue(self):
        venue = offerers_factories.VenueFactory()

        venue_id = venue.id

        with testing.assert_num_queries(1):
            fetched_venue = utils.get_venue_with_offerer_address(venue_id)
            assert fetched_venue.offererAddress.addressId


class CheckOfferStaysInItsVenueTest:
    def test_should_accept_a_body_that_carries_no_location(self):
        offer = offers_factories.OfferFactory()

        utils.check_offer_stays_in_its_venue(offer, None)

    @pytest.mark.parametrize(
        "build_location",
        [
            lambda venue_id: serialization.PhysicalLocation(venue_id=venue_id),
            lambda venue_id: serialization.AddressLocation(venue_id=venue_id, address_id=1),
            lambda venue_id: serialization.DigitalLocation(venue_id=venue_id, url="https://example.com"),
        ],
        ids=["physical", "address", "digital"],
    )
    def test_should_accept_a_location_naming_the_venue_the_offer_already_has(self, build_location):
        offer = offers_factories.OfferFactory()

        utils.check_offer_stays_in_its_venue(offer, build_location(offer.venueId))

    @pytest.mark.parametrize(
        "build_location",
        [
            lambda venue_id: serialization.PhysicalLocation(venue_id=venue_id),
            lambda venue_id: serialization.AddressLocation(venue_id=venue_id, address_id=1),
            lambda venue_id: serialization.DigitalLocation(venue_id=venue_id, url="https://example.com"),
        ],
        ids=["physical", "address", "digital"],
    )
    def test_should_refuse_a_location_naming_another_venue(self, build_location):
        offer = offers_factories.OfferFactory()
        other_venue = offerers_factories.VenueFactory()

        with pytest.raises(api_errors.ApiErrors) as error:
            utils.check_offer_stays_in_its_venue(offer, build_location(other_venue.id))

        assert error.value.errors == {"location.venueId": ["An offer cannot be moved to another venue"]}
        assert error.value.status_code == 400


class CheckOfferSubcategoryTest:
    def test_should_accept_a_body_that_carries_no_category_related_fields(self):
        body = events_serializers.EventOfferEdition(name="Jules et Jim")

        utils.check_offer_subcategory(body, subcategories.SEANCE_CINE.id)

    def test_should_accept_the_subcategory_the_offer_already_has(self):
        body = events_serializers.EventOfferEdition(category_related_fields={"category": "SEANCE_CINE"})

        utils.check_offer_subcategory(body, subcategories.SEANCE_CINE.id)

    def test_should_refuse_another_subcategory_for_an_event(self):
        body = events_serializers.EventOfferEdition(category_related_fields={"category": "SEANCE_CINE"})

        with pytest.raises(api_errors.ApiErrors) as error:
            utils.check_offer_subcategory(body, subcategories.CONCERT.id)

        assert error.value.errors == {"categoryRelatedFields.category": ["The category cannot be changed"]}
        assert error.value.status_code == 400


class SaveImageTest:
    GET_BYTES = "pcapi.routes.public.utils.get_bytes_from_base64_string"
    CREATE_MEDIATION = "pcapi.core.offers.api.create_mediation"

    def build_image_body(self, **overrides):
        defaults = {"file": base64.b64encode(b"an image").decode(), "credit": "Jane Doe"}
        return serialization.ImageBody(**{**defaults, **overrides})

    @mock.patch(CREATE_MEDIATION)
    def test_should_create_a_mediation_from_the_decoded_image(self, create_mediation):
        offer = offers_factories.OfferFactory()

        utils.save_image(self.build_image_body(), offer)

        create_mediation.assert_called_once_with(
            user=None,
            offer=offer,
            credit="Jane Doe",
            image_as_bytes=b"an image",
            min_width=constants.MIN_IMAGE_WIDTH,
            min_height=constants.MIN_IMAGE_HEIGHT,
            max_width=constants.MAX_IMAGE_WIDTH,
            max_height=constants.MAX_IMAGE_HEIGHT,
            aspect_ratio=constants.ASPECT_RATIO,
        )

    @mock.patch(CREATE_MEDIATION)
    @mock.patch(GET_BYTES)
    def test_should_refuse_a_file_that_is_not_base64(self, get_bytes_from_base64_string, create_mediation):
        get_bytes_from_base64_string.side_effect = public_utils.InvalidBase64Exception()

        with pytest.raises(api_errors.ApiErrors) as error:
            utils.save_image(self.build_image_body(), offers_factories.OfferFactory())

        assert error.value.errors == {"imageFile": ["The value must be a valid base64 string."]}
        create_mediation.assert_not_called()

    @pytest.mark.parametrize(
        "raised_error,expected_message",
        [
            (offers_exceptions.ImageTooSmall(400, 600), "The image is too small. It must be above 400x600 pixels."),
            (offers_exceptions.ImageTooLarge(800, 1200), "The image is too large. It must be below 800x1200 pixels."),
            (
                offers_exceptions.UnacceptedFileType(offers_validation.ACCEPTED_THUMBNAIL_FORMATS, "gif"),
                f"The image format is not accepted. It must be in {offers_validation.ACCEPTED_THUMBNAIL_FORMATS}.",
            ),
            (offers_exceptions.UnidentifiedImage(), "The file is not a valid image."),
            (
                offers_exceptions.FileSizeExceeded(10_000_000),
                "The file is too large. It must be less than 10000000 bytes.",
            ),
            (offers_exceptions.MissingImage(), "The image is not valid."),
            (
                image_conversion.ImageRatioError(expected=0.6666666, found=1.3333333),
                "Bad image ratio: expected 0.66, found 1.33",
            ),
        ],
        ids=["too small", "too large", "bad format", "not an image", "too heavy", "other", "bad ratio"],
    )
    @mock.patch(CREATE_MEDIATION)
    def test_should_translate_the_image_errors(self, create_mediation, raised_error, expected_message):
        create_mediation.side_effect = raised_error

        with pytest.raises(api_errors.ApiErrors) as error:
            utils.save_image(self.build_image_body(), offers_factories.OfferFactory())

        assert error.value.errors == {"imageFile": expected_message}


class UpdateOrDeleteVideoTest:
    UPSERT_VIDEO = "pcapi.core.videos.api.upsert_video_and_metadata"
    REMOVE_VIDEO = "pcapi.core.videos.api.remove_video_data_from_offer_metadata"
    VIDEO_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    @mock.patch(UPSERT_VIDEO)
    def test_should_upsert_the_video_when_a_url_is_sent(self, upsert_video_and_metadata):
        offer = offers_factories.OfferFactory()

        utils.update_or_delete_video(self.VIDEO_URL, offer, provider_id=12)

        upsert_video_and_metadata.assert_called_once_with(self.VIDEO_URL, offer, 12)

    @mock.patch(UPSERT_VIDEO)
    def test_should_refuse_a_video_that_cannot_be_found_on_youtube(self, upsert_video_and_metadata):
        upsert_video_and_metadata.side_effect = videos_exceptions.YoutubeVideoNotFound()

        with pytest.raises(offers_exceptions.OfferException) as error:
            utils.update_or_delete_video(self.VIDEO_URL, offers_factories.OfferFactory(), provider_id=12)

        assert error.value.errors == {
            "videoUrl": [
                "This video cannot be found on youtube. It is most likely a private video. Please check your URL."
            ]
        }

    @mock.patch(REMOVE_VIDEO)
    def test_should_delete_the_video_when_no_url_is_sent(self, remove_video_data_from_offer_metadata):
        meta_data = offers_factories.OfferMetaDataFactory(videoUrl=self.VIDEO_URL)
        offer = meta_data.offer

        utils.update_or_delete_video(None, offer, provider_id=12)

        remove_video_data_from_offer_metadata.assert_called_once_with(
            meta_data, offer.id, offer.venueId, self.VIDEO_URL, 12
        )

    @mock.patch(REMOVE_VIDEO)
    @mock.patch(UPSERT_VIDEO)
    def test_should_do_nothing_when_no_url_is_sent_and_the_offer_has_no_metadata(
        self, upsert_video_and_metadata, remove_video_data_from_offer_metadata
    ):
        utils.update_or_delete_video(None, offers_factories.OfferFactory(), provider_id=12)

        upsert_video_and_metadata.assert_not_called()
        remove_video_data_from_offer_metadata.assert_not_called()

    @mock.patch(REMOVE_VIDEO)
    def test_should_do_nothing_when_no_url_is_sent_and_the_offer_carries_no_video(
        self, remove_video_data_from_offer_metadata
    ):
        meta_data = offers_factories.OfferMetaDataFactory(videoUrl=None)

        utils.update_or_delete_video(None, meta_data.offer, provider_id=12)

        remove_video_data_from_offer_metadata.assert_not_called()
