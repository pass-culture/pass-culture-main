import logging
from unittest import mock

import pytest

import pcapi.core.artist.factories as artist_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.artist import exceptions as artist_exceptions
from pcapi.core.artist import models as artist_models
from pcapi.core.artist.api import ArtistOfferLinkKey
from pcapi.core.artist.api import check_artist_type_is_allowed_for_subcategory
from pcapi.core.artist.api import create_artist_offer_link
from pcapi.core.artist.api import get_artist_image_url
from pcapi.core.artist.api import upsert_artist_offer_links
from pcapi.core.categories import subcategories
from pcapi.models import db


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

        with pytest.raises(artist_exceptions.ArtistException) as exc:
            create_artist_offer_link(offer.id, link_data)

        assert exc.value.message == "An artist offer link must have either an artist_id or a custom_name"

    def test_create_artist_offer_link_with_duplicate_artist(self):
        offer = offers_factories.OfferFactory()
        artist = artist_factories.ArtistFactory()

        link_data = ArtistOfferLinkKey(
            artist_id=artist.id,
            artist_type=artist_models.ArtistType.PERFORMER,
            custom_name=None,
        )
        create_artist_offer_link(offer.id, link_data)

        with pytest.raises(artist_exceptions.ArtistException) as exc:
            create_artist_offer_link(offer.id, link_data)

        assert exc.value.message == "An artist can only be linked once per type"

    def test_create_artist_offer_link_with_duplicate_custom_name(self):
        offer = offers_factories.OfferFactory()

        link_data = ArtistOfferLinkKey(
            artist_id=None,
            artist_type=artist_models.ArtistType.AUTHOR,
            custom_name="John Doe",
        )
        create_artist_offer_link(offer.id, link_data)

        with pytest.raises(artist_exceptions.ArtistException) as exc:
            create_artist_offer_link(offer.id, link_data)

        assert exc.value.message == "A custom name can only be linked once per type"

    def test_create_artist_offer_link_with_invalid_artist_id(self):
        offer = offers_factories.OfferFactory()

        link_data = ArtistOfferLinkKey(
            artist_id="invalid_artist_id",
            artist_type=artist_models.ArtistType.PERFORMER,
            custom_name="invalid_artist_name",
        )

        with pytest.raises(artist_exceptions.ArtistException) as exc:
            create_artist_offer_link(offer.id, link_data)

        assert exc.value.message == "Invalid artist id"


class UpsertArtistOfferLinksTest:
    def test_should_create_a_new_link(self):
        offer = offers_factories.OfferFactory(subcategoryId=subcategories.CONCERT.id)
        artist = artist_factories.ArtistFactory()
        key = ArtistOfferLinkKey(artist_type=artist_models.ArtistType.PERFORMER, artist_id=artist.id, custom_name=None)

        created_keys, deleted_keys = upsert_artist_offer_links(offer, {key})

        assert created_keys == [key]
        assert deleted_keys == []
        [link] = db.session.query(artist_models.ArtistOfferLink).all()
        assert link.offer_id == offer.id
        assert link.artist_id == artist.id
        assert link.artist_type == artist_models.ArtistType.PERFORMER
        assert link.custom_name is None

    def test_should_keep_an_existing_link(self):
        artist = artist_factories.ArtistFactory()
        offer = offers_factories.OfferFactory(subcategoryId=subcategories.CONCERT.id)
        existing_link = artist_factories.ArtistOfferLinkFactory(artist_id=artist.id, offer_id=offer.id)
        existing_link_id = existing_link.id
        key = ArtistOfferLinkKey(artist_type=artist_models.ArtistType.PERFORMER, artist_id=artist.id, custom_name=None)

        created_keys, deleted_keys = upsert_artist_offer_links(offer, {key})

        assert created_keys == []
        assert deleted_keys == []
        [link] = db.session.query(artist_models.ArtistOfferLink).all()
        assert link.id == existing_link_id

    def test_should_create_the_missing_links_and_delete_the_extra_ones(self):
        offer = offers_factories.OfferFactory(subcategoryId=subcategories.CONCERT.id)
        former_artist = artist_factories.ArtistFactory()
        kept_artist = artist_factories.ArtistFactory()
        new_artist = artist_factories.ArtistFactory()
        artist_factories.ArtistOfferLinkFactory(offer_id=offer.id, artist_id=former_artist.id)
        kept_link = artist_factories.ArtistOfferLinkFactory(offer_id=offer.id, artist_id=kept_artist.id)
        former_key = ArtistOfferLinkKey(
            artist_type=artist_models.ArtistType.PERFORMER, artist_id=former_artist.id, custom_name=None
        )
        kept_key = ArtistOfferLinkKey(
            artist_type=artist_models.ArtistType.PERFORMER, artist_id=kept_artist.id, custom_name=None
        )
        new_key = ArtistOfferLinkKey(
            artist_type=artist_models.ArtistType.AUTHOR, artist_id=new_artist.id, custom_name=None
        )

        created_keys, deleted_keys = upsert_artist_offer_links(offer, {kept_key, new_key})

        assert created_keys == [new_key]
        assert deleted_keys == [former_key]
        links = db.session.query(artist_models.ArtistOfferLink).order_by(artist_models.ArtistOfferLink.id).all()
        assert [(link.id, link.artist_id, link.artist_type) for link in links] == [
            (kept_link.id, kept_artist.id, artist_models.ArtistType.PERFORMER),
            (links[-1].id, new_artist.id, artist_models.ArtistType.AUTHOR),
        ]

    def test_should_delete_every_link_when_given_no_key(self):
        offer = offers_factories.OfferFactory(subcategoryId=subcategories.CONCERT.id)
        artist_factories.ArtistOfferLinkFactory(offer_id=offer.id, artist_id=artist_factories.ArtistFactory().id)
        artist_factories.ArtistOfferLinkFactory(offer_id=offer.id, custom_name="Claude")

        created_keys, deleted_keys = upsert_artist_offer_links(offer, set())

        assert created_keys == []
        assert len(deleted_keys) == 2
        assert db.session.query(artist_models.ArtistOfferLink).count() == 0

    def test_should_log_created_and_deleted_links(self, caplog):
        offer = offers_factories.OfferFactory(subcategoryId=subcategories.CONCERT.id)
        artist = artist_factories.ArtistFactory()
        key = ArtistOfferLinkKey(artist_type=artist_models.ArtistType.PERFORMER, artist_id=artist.id, custom_name=None)

        with caplog.at_level(logging.INFO):
            upsert_artist_offer_links(offer, {key})

        created_logs = [record for record in caplog.records if "Artist offer links have been created" in record.message]
        assert len(created_logs) == 1
        assert created_logs[0].technical_message_id == "offer.artistOfferLinks.created"
        assert created_logs[0].extra["offer_id"] == offer.id

        with caplog.at_level(logging.INFO):
            upsert_artist_offer_links(offer, set())

        deleted_logs = [record for record in caplog.records if "Artist offer links have been deleted" in record.message]
        assert len(deleted_logs) == 1
        assert deleted_logs[0].technical_message_id == "offer.artistOfferLinks.deleted"


class CheckArtistTypeIsAllowedForSubcategoryTest:
    @pytest.mark.parametrize(
        "artist_type,subcategory",
        [
            (artist_models.ArtistType.AUTHOR, subcategories.SEANCE_CINE),
            (artist_models.ArtistType.PERFORMER, subcategories.CONCERT),
        ],
    )
    def test_should_accept_the_types_listed_in_the_subcategory_conditional_fields(self, artist_type, subcategory):
        check_artist_type_is_allowed_for_subcategory(artist_type, subcategory)

    @pytest.mark.parametrize(
        "artist_type,subcategory",
        [
            (artist_models.ArtistType.PERFORMER, subcategories.SEANCE_CINE),
            (artist_models.ArtistType.STAGE_DIRECTOR, subcategories.CONCERT),
        ],
    )
    def test_should_refuse_the_other_types(self, artist_type, subcategory):
        with pytest.raises(artist_exceptions.ArtistException) as exc:
            check_artist_type_is_allowed_for_subcategory(artist_type, subcategory)

        assert exc.value.message == f"`{artist_type.value}` artists are not allowed for the `{subcategory.id}` category"
