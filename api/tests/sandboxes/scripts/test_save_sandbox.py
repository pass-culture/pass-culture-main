from datetime import timedelta
from unittest.mock import patch

import pytest

import pcapi.core.offers.factories as offers_factories
import pcapi.core.offers.models as offers_models
from pcapi import settings
from pcapi.core import object_storage
from pcapi.core.artist import models as artist_models
from pcapi.core.categories import subcategories
from pcapi.core.discoveries import models as discoveries_models
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.core.wishlists import models as wishlists_models
from pcapi.models import db
from pcapi.sandboxes.scripts.creators.tiny import save_tiny_sandbox
from pcapi.sandboxes.scripts.save_sandbox import _index_all_offers
from pcapi.sandboxes.scripts.utils.storage_utils import read_sandbox_mediation_asset
from pcapi.utils import date as date_utils


@pytest.mark.usefixtures("db_session")
class IndexAllOffersTest:
    def test_index_all_offers(self):
        publication_date = date_utils.get_naive_utc_now() - timedelta(days=3)
        booking_allowed_date = date_utils.get_naive_utc_now() + timedelta(days=14)

        # active, published, booking date in the future and active -> should be indexed
        offer_1 = offers_factories.StockFactory(
            offer__isActive=True,
            offer__publicationDatetime=publication_date,
            offer__bookingAllowedDatetime=booking_allowed_date,
        ).offer

        # active with bookable stock -> should be indexed
        offer_2 = offers_factories.StockFactory().offer

        # published with a booking date in the future, but inactive
        # -> should not be indexed
        offers_factories.StockFactory(
            offer__publicationDatetime=None,
            offer__bookingAllowedDatetime=booking_allowed_date,
        )

        # inactive or without any bookable stock -> should not indexed
        offers_factories.StockFactory(offer__publicationDatetime=None)
        offers_factories.OfferFactory(isActive=False)
        offers_factories.OfferFactory(isActive=True)

        with patch("pcapi.core.search.reindex_offer_ids") as mock_reindex_offer_ids:
            _index_all_offers()
            mock_reindex_offer_ids.assert_called_once()
            assert set(mock_reindex_offer_ids.call_args[0][0]) == {offer_1.id, offer_2.id}


@pytest.mark.usefixtures("db_session")
class CreateTinyWorksTest:
    def test_tiny_creates_works_artists_and_discoverable_individual_offer(self, client, mocker, tmp_path):
        mocker.patch.object(settings, "OBJECT_STORAGE_PROVIDER", "local")
        mocker.patch.object(settings, "LOCAL_STORAGE_DIR", tmp_path)
        mocker.patch("pcapi.sandboxes.scripts.creators.tiny.create_user_with_venue.offerers_api.save_venue_banner")
        mocker.patch("pcapi.sandboxes.scripts.creators.tiny.create_user_with_venue.add_image_to_offer")

        save_tiny_sandbox()
        db.session.expire_all()

        offer = db.session.query(offers_models.Offer).filter_by(name="Conférence gesticulée").one()
        assert offer.name == "Conférence gesticulée"
        assert offer.product.work.title == offer.name
        assert offer.product.work.media_type == discoveries_models.WorkMediaType.PERFORMING_ART
        works = db.session.query(discoveries_models.Work).all()
        assert {work.media_type for work in works} == {
            discoveries_models.WorkMediaType.PERFORMING_ART,
            discoveries_models.WorkMediaType.BOOK,
            discoveries_models.WorkMediaType.MUSIC,
            discoveries_models.WorkMediaType.FILM,
        }
        assert len(works) == 23
        image_subcategories = {
            discoveries_models.WorkMediaType.PERFORMING_ART: subcategories.CONFERENCE.id,
            discoveries_models.WorkMediaType.BOOK: subcategories.LIVRE_PAPIER.id,
            discoveries_models.WorkMediaType.MUSIC: subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id,
            discoveries_models.WorkMediaType.FILM: subcategories.SEANCE_CINE.id,
        }
        for work in works:
            assert work.visual_url == f"{settings.OBJECT_STORAGE_URL.rstrip('/')}/thumbs/works/{work.id}.jpg"
            assert object_storage.get_public_object("thumbs/works", f"{work.id}.jpg") == [
                read_sandbox_mediation_asset(image_subcategories[work.media_type])
            ]
        artists = db.session.query(artist_models.Artist).all()
        assert len(artists) == 13
        assert {"Hayao Miyazaki", "Haruki Murakami", "Camille Martin"} <= {artist.name for artist in artists}
        assert len(offer.product.work.artist_links) == 2
        assert len(offer.product.artistLinks) == 2
        assert len(offer.artistOfferLinks) == 2
        assert db.session.query(discoveries_models.WorkArtist).count() == 24

        beneficiary = db.session.query(users_models.User).filter_by(email="ouiche.tiny@example.com").one()
        assert beneficiary.is_beneficiary
        wishlists = db.session.query(wishlists_models.Wishlist).filter_by(user_id=beneficiary.id).all()
        assert {wishlist.name for wishlist in wishlists} == {
            "10 films à voir absolument",
            "Les livres m'ayant retourner le cerveau",
            "Découverte du Japon",
        }
        assert all(wishlist.visibility == wishlists_models.WishlistVisibility.PUBLIC for wishlist in wishlists)
        assert all(wishlist.items for wishlist in wishlists)
        for wishlist in wishlists:
            response = client.get(f"/native/v1/wishlists/{wishlist.id}")
            assert response.status_code == 200
            assert response.json["isOwner"] is False
            assert len(response.json["items"]) == len(wishlist.items)
        response = client.get("/native/v1/wishlists/search?q=films")
        assert response.status_code == 200
        assert response.json["nbResults"] == 1
        assert response.json["wishlists"][0]["name"] == "10 films à voir absolument"
        film_list = next(wishlist for wishlist in wishlists if wishlist.name == "10 films à voir absolument")
        assert len(film_list.items) == 10
        assert all(item.work.media_type == discoveries_models.WorkMediaType.FILM for item in film_list.items)
        assert all(
            [item.position for item in wishlist.items] == list(range(len(wishlist.items))) for wishlist in wishlists
        )
        assert any(item.artist for wishlist in wishlists for item in wishlist.items)
        assert db.session.query(discoveries_models.Discovery).filter_by(user_id=beneficiary.id).count() == 30
        new_offers = db.session.query(offers_models.Offer).filter(offers_models.Offer.id != offer.id).all()
        assert len(new_offers) == 6
        assert all(new_offer.venue == offer.venue and new_offer.product.work for new_offer in new_offers)
        assert all(new_offer.stocks and new_offer.mediations for new_offer in new_offers)
        for artist in artists:
            if artist.name not in {"Camille Martin", "Alex Dubois", "Lou Bernard"}:
                assert artist.image.startswith(settings.OBJECT_STORAGE_URL.rstrip("/") + "/thumbs/works/")
                assert object_storage.get_public_object("thumbs/works", artist.image.rsplit("/", 1)[1])

        client.with_token(users_factories.UserFactory())
        response = client.post("/native/v1/discoveries", json={"offerId": offer.id})
        assert response.status_code == 200
        assert response.json["workId"] == offer.product.work_id
        assert response.json["work"]["visualUrl"] == offer.product.work.visual_url
        assert response.json["work"]["mainArtist"]["name"] == "Camille Martin"
        for work in works:
            assert client.post("/native/v1/discoveries", json={"workId": work.id}).status_code == 200
        for artist in artists:
            assert client.post("/native/v1/discoveries", json={"artistId": artist.id}).status_code == 200
        assert db.session.query(discoveries_models.Discovery).count() == 66
        listing = client.get("/native/v1/users/me/discoveries?limit=100")
        assert listing.status_code == 200
        assert {discovery["work"]["visualUrl"] for discovery in listing.json["discoveries"] if discovery["work"]} == {
            work.visual_url for work in works
        }
