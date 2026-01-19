import pytest

import pcapi.core.artist.factories as artist_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.artist import exceptions as artist_exceptions
from pcapi.core.artist import models as artist_models
from pcapi.core.artist.api import create_artist_offer_link
from pcapi.core.artist.api import get_artist_image_url
from pcapi.models import db
from pcapi.routes.serialization import artist_serialize


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

        link_data = artist_serialize.ArtistOfferResponseModel(
            artist_id=artist.id,
            artist_type=artist_models.ArtistType.PERFORMER,
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

        link_data = artist_serialize.ArtistOfferResponseModel(
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

        link_data = artist_serialize.ArtistOfferResponseModel(
            artist_id=None,
            artist_type=artist_models.ArtistType.PERFORMER,
            custom_name=None,
        )

        with pytest.raises(artist_exceptions.MissingArtistDataException):
            create_artist_offer_link(offer.id, link_data)

    def test_create_artist_offer_link_with_duplicate_artist(self):
        offer = offers_factories.OfferFactory()
        artist = artist_factories.ArtistFactory()

        link_data = artist_serialize.ArtistOfferResponseModel(
            artist_id=artist.id,
            artist_type=artist_models.ArtistType.PERFORMER,
            custom_name=None,
        )
        create_artist_offer_link(offer.id, link_data)

        with pytest.raises(artist_exceptions.DuplicateArtistException):
            create_artist_offer_link(offer.id, link_data)

    def test_create_artist_offer_link_with_duplicate_custom_name(self):
        offer = offers_factories.OfferFactory()

        link_data = artist_serialize.ArtistOfferResponseModel(
            artist_id=None,
            artist_type=artist_models.ArtistType.AUTHOR,
            custom_name="John Doe",
        )
        create_artist_offer_link(offer.id, link_data)

        with pytest.raises(artist_exceptions.DuplicateCustomArtistException):
            create_artist_offer_link(offer.id, link_data)

    def test_create_artist_offer_link_with_invalid_artist_id(self):
        offer = offers_factories.OfferFactory()

        link_data = artist_serialize.ArtistOfferResponseModel(
            artist_id="invalid_artist_id",
            artist_type=artist_models.ArtistType.PERFORMER,
            custom_name=None,
        )

        with pytest.raises(artist_exceptions.InvalidArtistDataException):
            create_artist_offer_link(offer.id, link_data)
