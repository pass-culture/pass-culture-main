from unittest import mock
from unittest.mock import patch

import PIL.Image
import pytest

import pcapi.core.artist.factories as artist_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.artist import exceptions as artist_exceptions
from pcapi.core.artist import models as artist_models
from pcapi.core.artist.api import ArtistOfferLinkKey
from pcapi.core.artist.api import create_artist_offer_link
from pcapi.core.artist.api import get_artist_image_url
from pcapi.core.artist.api import store_mini_thumb
from pcapi.core.artist.api import upsert_artist_offer_links
from pcapi.models import db
from pcapi.routes.serialization import artist_serialize
from pcapi.utils.image_conversion import MINI_THUMB_WIDTH
from pcapi.utils.image_conversion import CropParams
from pcapi.utils.image_conversion import ImageRatio


pytestmark = pytest.mark.usefixtures("db_session")


class GetArtistImageUrlTest:
    def test_get_image_from_artist(self):
        artist = artist_factories.ArtistFactory()

        image_url = get_artist_image_url(artist)

        assert image_url == artist.image

    def test_get_image_from_product(self):
        artist = artist_factories.ArtistFactory(image=None)
        product_mediation = offers_factories.ProductMediationFactory()
        artist_factories.ArtistProductLinkFactory(artist_id=artist.id, product_id=product_mediation.product.id)

        image_url = get_artist_image_url(artist)

        assert image_url == product_mediation.url

    def test_get_image_from_most_popular_product(self):
        artist = artist_factories.ArtistFactory(image=None)
        least_popular_product_mediation = offers_factories.ProductMediationFactory(product__last_30_days_booking=None)
        artist_factories.ArtistProductLinkFactory(
            artist_id=artist.id, product_id=least_popular_product_mediation.product.id
        )
        medium_popular_product_mediation = offers_factories.ProductMediationFactory(product__last_30_days_booking=1)
        artist_factories.ArtistProductLinkFactory(
            artist_id=artist.id, product_id=medium_popular_product_mediation.product.id
        )
        most_popular_product_mediation = offers_factories.ProductMediationFactory(product__last_30_days_booking=2)
        artist_factories.ArtistProductLinkFactory(
            artist_id=artist.id, product_id=most_popular_product_mediation.product.id
        )

        image_url = get_artist_image_url(artist)

        assert image_url == most_popular_product_mediation.url

    def test_get_image_from_most_recent_product_if_equal_popularity(self):
        artist = artist_factories.ArtistFactory(image=None)
        first_product_mediation = offers_factories.ProductMediationFactory()
        artist_factories.ArtistProductLinkFactory(artist_id=artist.id, product_id=first_product_mediation.product.id)
        last_product_mediation = offers_factories.ProductMediationFactory()
        artist_factories.ArtistProductLinkFactory(artist_id=artist.id, product_id=last_product_mediation.product.id)

        image_url = get_artist_image_url(artist)

        assert image_url == last_product_mediation.url

    def test_return_none_if_no_image_available(self):
        artist = artist_factories.ArtistFactory(image=None)

        image_url = get_artist_image_url(artist)

        assert image_url is None


class CreateArtistOfferLinkTest:
    def test_create_artist_offer_link_with_artist_id(self):
        offer = offers_factories.OfferFactory()
        artist = artist_factories.ArtistFactory()

        link_data = ArtistOfferLinkKey(
            artist_type=artist_models.ArtistType.PERFORMER,
            artist_id=artist.id,
            custom_name=None,
        )

        create_artist_offer_link(offer.id, link_data)

        artist_links = db.session.query(artist_models.ArtistOfferLink).all()
        assert len(artist_links) == 1
        assert artist_links[0].offer_id == offer.id
        assert artist_links[0].artist_id == artist.id
        assert artist_links[0].artist_type == artist_models.ArtistType.PERFORMER
        assert artist_links[0].custom_name is None

    def test_create_artist_offer_link_with_custom_name(self):
        offer = offers_factories.OfferFactory()

        link_data = ArtistOfferLinkKey(
            artist_id=None,
            artist_type=artist_models.ArtistType.AUTHOR,
            custom_name="John Doe",
        )

        create_artist_offer_link(offer.id, link_data)

        artist_links = db.session.query(artist_models.ArtistOfferLink).all()
        assert len(artist_links) == 1
        assert artist_links[0].offer_id == offer.id
        assert artist_links[0].artist_id is None
        assert artist_links[0].artist_type == artist_models.ArtistType.AUTHOR
        assert artist_links[0].custom_name == "John Doe"

    def test_create_artist_offer_link_with_missing_artist_data(self):
        offer = offers_factories.OfferFactory()

        link_data = ArtistOfferLinkKey(
            artist_id=None,
            artist_type=artist_models.ArtistType.PERFORMER,
            custom_name=None,
        )

        with pytest.raises(artist_exceptions.MissingArtistDataException):
            create_artist_offer_link(offer.id, link_data)

    def test_create_artist_offer_link_with_duplicate_artist(self):
        offer = offers_factories.OfferFactory()
        artist = artist_factories.ArtistFactory()

        link_data = ArtistOfferLinkKey(
            artist_id=artist.id,
            artist_type=artist_models.ArtistType.PERFORMER,
            custom_name=None,
        )
        create_artist_offer_link(offer.id, link_data)

        with pytest.raises(artist_exceptions.DuplicateArtistException):
            create_artist_offer_link(offer.id, link_data)

    def test_create_artist_offer_link_with_duplicate_custom_name(self):
        offer = offers_factories.OfferFactory()

        link_data = ArtistOfferLinkKey(
            artist_id=None,
            artist_type=artist_models.ArtistType.AUTHOR,
            custom_name="John Doe",
        )
        create_artist_offer_link(offer.id, link_data)

        with pytest.raises(artist_exceptions.DuplicateCustomArtistException):
            create_artist_offer_link(offer.id, link_data)

    def test_create_artist_offer_link_with_invalid_artist_id(self):
        offer = offers_factories.OfferFactory()

        link_data = ArtistOfferLinkKey(
            artist_id="invalid_artist_id",
            artist_type=artist_models.ArtistType.PERFORMER,
            custom_name="invalid_artist_name",
        )

        with pytest.raises(artist_exceptions.InvalidArtistDataException):
            create_artist_offer_link(offer.id, link_data)


@pytest.mark.usefixtures("db_session")
class UpsertArtistOfferLinksTest:
    def test_patch_offer_with_new_link(self):
        offer = offers_factories.OfferFactory()
        artist = artist_factories.ArtistFactory()

        incoming_links = [
            artist_serialize.ArtistOfferLinkBodyModel(
                artist_id=artist.id, artist_type=artist_models.ArtistType.PERFORMER, artist_name=artist.name
            )
        ]

        upsert_artist_offer_links(incoming_links, offer)

        links = db.session.query(artist_models.ArtistOfferLink).all()
        assert len(links) == 1
        assert links[0].offer_id == offer.id
        assert links[0].artist_id == artist.id
        assert links[0].artist_type == artist_models.ArtistType.PERFORMER
        assert links[0].custom_name is None

    def test_patch_offer_without_link(self):
        artist = artist_factories.ArtistFactory()
        offer = offers_factories.OfferFactory()
        artist_factories.ArtistOfferLinkFactory(artist_id=artist.id, offer_id=offer.id)

        upsert_artist_offer_links([], offer)

        links = db.session.query(artist_models.ArtistOfferLink).all()
        assert len(links) == 0

    def test_patch_offer_with_existing_link(self):
        artist = artist_factories.ArtistFactory()
        offer = offers_factories.OfferFactory()
        existing_link = artist_factories.ArtistOfferLinkFactory(artist_id=artist.id, offer_id=offer.id)
        existing_link_id = existing_link.id

        incoming_links = [
            artist_serialize.ArtistOfferLinkBodyModel(
                artist_id=existing_link.artist_id,
                artist_type=existing_link.artist_type,
                artist_name=existing_link.artist_name,
            )
        ]
        upsert_artist_offer_links(incoming_links, offer)

        links = db.session.query(artist_models.ArtistOfferLink).all()
        assert len(links) == 1
        assert links[0].id == existing_link_id

    @mock.patch("pcapi.core.artist.api.create_artist_offer_link")
    def test_patch_offer_with_duplicate_link(self, mock_create_artist_offer_link):
        offer = offers_factories.OfferFactory()
        artist = artist_factories.ArtistFactory()

        incoming_links = [
            artist_serialize.ArtistOfferLinkBodyModel(
                artist_id=artist.id, artist_type=artist_models.ArtistType.PERFORMER, artist_name=artist.name
            ),
            artist_serialize.ArtistOfferLinkBodyModel(
                artist_id=artist.id, artist_type=artist_models.ArtistType.PERFORMER, artist_name=artist.name
            ),
        ]
        upsert_artist_offer_links(incoming_links, offer)
        mock_create_artist_offer_link.assert_called()
        len(mock_create_artist_offer_link.call_args_list) == 2


class StoreMiniThumbTest:
    @patch("pcapi.core.artist.api.thumb_storage.create_thumb")
    @patch("pcapi.core.artist.api.get_crop_params")
    @patch("pcapi.core.artist.api.PIL.Image.open")
    def test_calls_create_thumb_with_correct_params(self, mock_pil_open, mock_get_crop_params, mock_create_thumb):
        mock_image = PIL.Image.new("RGB", (400, 300), "red")
        mock_pil_open.return_value = mock_image
        mock_crop_params = CropParams()
        mock_get_crop_params.return_value = mock_crop_params

        store_mini_thumb(b"fake-image", "artist-123")

        mock_get_crop_params.assert_called_once_with(400, 300, ImageRatio.SQUARE)
        mock_create_thumb.assert_called_once_with(
            b"fake-image",
            ratio=ImageRatio.SQUARE,
            crop_params=mock_crop_params,
            object_id="72x72/artist-123",
            folder="thumbs/artist",
            max_width=MINI_THUMB_WIDTH,
        )
