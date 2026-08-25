import logging
from unittest import mock

import pytest

import pcapi.core.artist.factories as artist_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.artist import exceptions as artist_exceptions
from pcapi.core.artist import models as artist_models
from pcapi.core.artist.api import ArtistOfferLinkKey
from pcapi.core.artist.api import check_artist_offer_links
from pcapi.core.artist.api import create_artist_offer_link
from pcapi.core.artist.api import get_artist_image_url
from pcapi.core.artist.api import upsert_artist_offer_links
from pcapi.core.categories import subcategories
from pcapi.models import api_errors
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
        offer = offers_factories.OfferFactory(subcategoryId=subcategories.CONCERT.id)
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
        offer = offers_factories.OfferFactory(subcategoryId=subcategories.CONCERT.id)
        artist_factories.ArtistOfferLinkFactory(artist_id=artist.id, offer_id=offer.id)

        upsert_artist_offer_links([], offer)

        links = db.session.query(artist_models.ArtistOfferLink).all()
        assert len(links) == 0

    def test_patch_offer_with_existing_link(self):
        artist = artist_factories.ArtistFactory()
        offer = offers_factories.OfferFactory(subcategoryId=subcategories.CONCERT.id)
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
        offer = offers_factories.OfferFactory(subcategoryId=subcategories.CONCERT.id)
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


@pytest.mark.usefixtures("db_session")
class UpsertArtistOfferLinksValidationTest:
    def _link(self, artist_type: artist_models.ArtistType) -> artist_serialize.ArtistOfferLinkBodyModel:
        artist = artist_factories.ArtistFactory()
        return artist_serialize.ArtistOfferLinkBodyModel(
            artist_id=artist.id, artist_type=artist_type, artist_name=artist.name
        )

    def test_check_the_links_against_the_resulting_subcategory(self):
        # a performer is refused by the subcategory of the offer, but allowed by the one it moves to
        offer = offers_factories.OfferFactory(subcategoryId=subcategories.SEANCE_CINE.id)

        upsert_artist_offer_links(
            [self._link(artist_models.ArtistType.PERFORMER)],
            offer,
            subcategory_id=subcategories.CONCERT.id,
        )

        assert len(db.session.query(artist_models.ArtistOfferLink).all()) == 1

    def test_refuse_the_links_the_subcategory_does_not_allow(self):
        offer = offers_factories.OfferFactory(subcategoryId=subcategories.SEANCE_CINE.id)

        with pytest.raises(api_errors.ApiErrors) as error:
            upsert_artist_offer_links([self._link(artist_models.ArtistType.PERFORMER)], offer)

        assert error.value.errors == {
            "artistOfferLinks": ["Le type d'artiste n'est pas autorisé pour cette sous catégorie"]
        }

    def test_log_created_and_deleted_links(self, caplog):
        offer = offers_factories.OfferFactory(subcategoryId=subcategories.SEANCE_CINE.id)

        with caplog.at_level(logging.INFO):
            upsert_artist_offer_links([self._link(artist_models.ArtistType.AUTHOR)], offer)

        created_logs = [record for record in caplog.records if "Artist offer links have been created" in record.message]
        assert len(created_logs) == 1
        assert created_logs[0].technical_message_id == "offer.artistOfferLinks.created"
        assert created_logs[0].extra["offer_id"] == offer.id

        with caplog.at_level(logging.INFO):
            upsert_artist_offer_links([], offer)

        deleted_logs = [record for record in caplog.records if "Artist offer links have been deleted" in record.message]
        assert len(deleted_logs) == 1
        assert deleted_logs[0].technical_message_id == "offer.artistOfferLinks.deleted"


class CheckArtistOfferLinksTest:
    def test_check_artist_offer_links_should_not_raise(self):
        artist_offer_links = [
            artist_serialize.ArtistOfferLinkBodyModel(
                artist_id="any-id",
                artist_type=artist_models.ArtistType.AUTHOR,
                artist_name="any-name",
            )
        ]
        check_artist_offer_links(artist_offer_links, subcategories.SEANCE_CINE)

    def test_check_artist_offer_links_should_raise(self):
        artist_offer_links = [
            artist_serialize.ArtistOfferLinkBodyModel(
                artist_id="any-id",
                artist_type=artist_models.ArtistType.PERFORMER,
                artist_name="any-name",
            )
        ]
        with pytest.raises(api_errors.ApiErrors) as exc:
            check_artist_offer_links(artist_offer_links, subcategories.SEANCE_CINE)

        assert exc.value.errors == {
            "artistOfferLinks": ["Le type d'artiste n'est pas autorisé pour cette sous catégorie"]
        }
