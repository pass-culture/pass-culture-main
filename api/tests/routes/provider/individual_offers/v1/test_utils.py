import base64
import logging
from unittest import mock

import pytest
import sqlalchemy.orm as sa_orm
from flask import g

from pcapi.core import testing
from pcapi.core.artist import api as artist_api
from pcapi.core.artist import exceptions as artist_exceptions
from pcapi.core.artist import models as artist_models
from pcapi.core.categories import subcategories
from pcapi.core.geography import factories as geography_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers import schemas as offerers_schemas
from pcapi.core.offers import exceptions as offers_exceptions
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.offers import validation as offers_validation
from pcapi.core.providers import factories as providers_factories
from pcapi.core.videos import exceptions as videos_exceptions
from pcapi.models import api_errors
from pcapi.routes.provider import utils as provider_utils
from pcapi.routes.provider.individual_offers.v1 import constants
from pcapi.routes.provider.individual_offers.v1 import serialization
from pcapi.routes.provider.individual_offers.v1 import utils
from pcapi.routes.provider.individual_offers.v1.serializers import events as events_serializers
from pcapi.utils import image_conversion


pytestmark = pytest.mark.usefixtures("db_session")


class ExtractOffererAddressFromLocationTest:
    GET_ADDRESS = "pcapi.routes.provider.utils.get_address_or_raise_404"
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


class CheckLocationBelongsToOfferVenueTest:
    def test_should_accept_a_body_that_carries_no_location(self):
        offer = offers_factories.OfferFactory()

        utils.check_location_belongs_to_offer_venue(offer, None)

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

        utils.check_location_belongs_to_offer_venue(offer, build_location(offer.venueId))

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
            utils.check_location_belongs_to_offer_venue(offer, build_location(other_venue.id))

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
    GET_BYTES = "pcapi.routes.provider.utils.get_bytes_from_base64_string"
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
        get_bytes_from_base64_string.side_effect = provider_utils.InvalidBase64Exception()

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


class GetEditableFieldsTest:
    def test_should_not_restrict_an_offer_without_provider(self):
        assert utils.get_editable_fields(None) is None

    def test_should_answer_the_shared_set_for_a_plain_provider(self):
        provider = providers_factories.ProviderFactory()

        assert utils.get_editable_fields(provider) == utils.EDITABLE_FIELDS_FOR_OFFER_FROM_PROVIDER

    def test_should_answer_the_allocine_set_for_allocine(self):
        provider = providers_factories.AllocineProviderFactory(localClass="AllocineStocks")
        assert provider.isAllocine

        assert utils.get_editable_fields(provider) == utils.EDITABLE_FIELDS_FOR_ALLOCINE_OFFER

    def test_should_answer_the_api_set_for_an_integrator(self):
        provider = providers_factories.PublicApiProviderFactory()
        providers_factories.OffererProviderFactory(provider=provider)
        assert provider.hasOffererProvider

        assert utils.get_editable_fields(provider) == utils.EDITABLE_FIELDS_FOR_INDIVIDUAL_OFFERS_API_PROVIDER


class UpdateArtistOfferLinksTest:
    @mock.patch("pcapi.core.artist.api.upsert_artist_offer_links")
    @mock.patch("pcapi.core.artist.api.find_artist_by_music_platform_ids")
    @mock.patch("pcapi.core.artist.api.check_artist_type_is_allowed_for_subcategory")
    @mock.patch("pcapi.routes.provider.individual_offers.v1.utils.get_editable_fields")
    def test_should_link_the_artists_found_by_their_platform_ids(
        self, mocked_get_editable_fields, mocked_check_artist_type, mocked_find_artist, mocked_upsert_links
    ):
        offer = offers_models.Offer(id=1, venueId=2, subcategoryId=subcategories.CONCERT.id)
        performer = artist_models.Artist(id="performer-id")
        author = artist_models.Artist(id="author-id")

        mocked_get_editable_fields.return_value = utils.EDITABLE_FIELDS_FOR_INDIVIDUAL_OFFERS_API_PROVIDER
        mocked_find_artist.side_effect = [performer, author]

        utils.update_artist_offer_links(
            offer,
            [
                serialization.ArtistBody(artist_type="performer", spotify_id="performer-spotify-id"),
                serialization.ArtistBody(artist_type="author", spotify_id="unknown", deezer_id="author-deezer-id"),
            ],
        )

        assert mocked_check_artist_type.call_args_list == [
            mock.call(artist_models.ArtistType.PERFORMER, subcategories.CONCERT),
            mock.call(artist_models.ArtistType.AUTHOR, subcategories.CONCERT),
        ]
        assert mocked_find_artist.call_args_list == [
            mock.call({"spotify_id": "performer-spotify-id"}),
            mock.call({"spotify_id": "unknown", "deezer_id": "author-deezer-id"}),
        ]
        mocked_upsert_links.assert_called_once_with(
            offer,
            {
                artist_api.ArtistOfferLinkKey(
                    artist_type=artist_models.ArtistType.PERFORMER, artist_id="performer-id", custom_name=None
                ),
                artist_api.ArtistOfferLinkKey(
                    artist_type=artist_models.ArtistType.AUTHOR, artist_id="author-id", custom_name=None
                ),
            },
        )

    @mock.patch("pcapi.core.artist.api.upsert_artist_offer_links")
    @mock.patch("pcapi.core.artist.api.find_artist_by_music_platform_ids")
    @mock.patch("pcapi.core.artist.api.check_artist_type_is_allowed_for_subcategory")
    @mock.patch("pcapi.routes.provider.individual_offers.v1.utils.get_editable_fields", return_value=None)
    def test_should_unlink_every_artist_when_given_none(
        self, _, mocked_check_artist_type, mocked_find_artist, mocked_upsert_links
    ):
        offer = offers_models.Offer(id=1, venueId=2, subcategoryId=subcategories.CONCERT.id)

        utils.update_artist_offer_links(offer, None)

        mocked_check_artist_type.assert_not_called()
        mocked_find_artist.assert_not_called()
        mocked_upsert_links.assert_called_once_with(offer, set())

    @mock.patch("pcapi.core.artist.api.upsert_artist_offer_links")
    @mock.patch("pcapi.core.artist.api.find_artist_by_music_platform_ids")
    @mock.patch("pcapi.routes.provider.individual_offers.v1.utils.get_editable_fields", return_value=None)
    def test_should_ignore_an_artist_that_cannot_be_found_and_log_it(
        self, _, mocked_find_artist, mocked_upsert_links, caplog
    ):
        offer = offers_models.Offer(id=1, venueId=2, subcategoryId=subcategories.CONCERT.id)
        known_artist = artist_models.Artist(id="known-id")

        mocked_find_artist.side_effect = [known_artist, None]
        g.current_api_key = offerers_models.ApiKey(providerId=3)

        with caplog.at_level(logging.WARNING):
            utils.update_artist_offer_links(
                offer,
                [
                    serialization.ArtistBody(artist_type="performer", spotify_id="known"),
                    serialization.ArtistBody(artist_type="performer", spotify_id="unknown", deezer_id="unknown-too"),
                ],
            )

        mocked_upsert_links.assert_called_once_with(
            offer,
            {
                artist_api.ArtistOfferLinkKey(
                    artist_type=artist_models.ArtistType.PERFORMER, artist_id="known-id", custom_name=None
                )
            },
        )
        target_log_message = "No artist found for the music platform ids"
        log = next(record for record in caplog.records if record.message == target_log_message)

        assert log.technical_message_id == "offer.artistOfferLinks.not_found"
        log_extra_data = log.__dict__.get("extra")
        assert log_extra_data.get("offer_id") == 1
        assert log_extra_data.get("venue_id") == 2
        assert log_extra_data.get("provider_id") == 3
        assert log_extra_data.get("platform_ids") == {"spotify_id": "unknown", "deezer_id": "unknown-too"}

    @mock.patch("pcapi.core.artist.api.check_artist_type_is_allowed_for_subcategory")
    @mock.patch("pcapi.routes.provider.individual_offers.v1.utils.get_editable_fields", return_value=None)
    def test_should_raise_if_check_artist_type_raises(self, _, mocked_check_artist_type):
        offer = offers_models.Offer(id=1, venueId=2, subcategoryId=subcategories.SEANCE_CINE.id)
        mocked_check_artist_type.side_effect = artist_exceptions.ArtistException(
            "`performer` artists are not allowed for the `SEANCE_CINE` category"
        )

        with pytest.raises(api_errors.ApiErrors) as error:
            utils.update_artist_offer_links(
                offer, [serialization.ArtistBody(artist_type="performer", spotify_id="known")]
            )

        assert error.value.errors == {"artists": ["`performer` artists are not allowed for the `SEANCE_CINE` category"]}

    @mock.patch("pcapi.routes.provider.individual_offers.v1.utils.get_editable_fields", return_value=None)
    def test_should_raise_when_the_field_is_not_editable(self, mocked_get_editable_fields):
        offer = offers_models.Offer(id=1, venueId=2, subcategoryId=subcategories.CONCERT.id)
        mocked_get_editable_fields.return_value = utils.EDITABLE_FIELDS_FOR_OFFER_FROM_PROVIDER

        with pytest.raises(api_errors.ApiErrors) as error:
            utils.update_artist_offer_links(offer, None)

        assert error.value.errors == {"artists": ["You cannot update this field"]}

    @mock.patch("pcapi.routes.provider.individual_offers.v1.utils.get_editable_fields", return_value=None)
    def test_should_raise_for_an_event_linked_to_a_product(self, _):
        offer = offers_models.Offer(id=1, venueId=2, subcategoryId=subcategories.CONCERT.id, productId=4)

        with pytest.raises(api_errors.ApiErrors) as error:
            utils.update_artist_offer_links(offer, None)

        assert error.value.errors == {"artists": ["You cannot update this field for an event linked to a product"]}
