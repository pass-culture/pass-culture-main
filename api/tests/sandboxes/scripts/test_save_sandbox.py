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

        offer = db.session.query(offers_models.Offer).one()
        assert offer.name == "Conférence gesticulée"
        assert offer.product.work.title == offer.name
        assert offer.product.work.media_type == discoveries_models.WorkMediaType.PERFORMING_ART
        works = db.session.query(discoveries_models.Work).all()
        assert {work.media_type for work in works} == {
            discoveries_models.WorkMediaType.PERFORMING_ART,
            discoveries_models.WorkMediaType.BOOK,
            discoveries_models.WorkMediaType.MUSIC,
        }
        image_subcategories = {
            discoveries_models.WorkMediaType.PERFORMING_ART: subcategories.CONFERENCE.id,
            discoveries_models.WorkMediaType.BOOK: subcategories.LIVRE_PAPIER.id,
            discoveries_models.WorkMediaType.MUSIC: subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id,
        }
        for work in works:
            assert work.visual_url == f"{settings.OBJECT_STORAGE_URL.rstrip('/')}/thumbs/works/{work.id}.jpg"
            assert object_storage.get_public_object("thumbs/works", f"{work.id}.jpg") == [
                read_sandbox_mediation_asset(image_subcategories[work.media_type])
            ]
        artists = db.session.query(artist_models.Artist).all()
        assert {artist.name for artist in artists} == {"Camille Martin", "Alex Dubois", "Lou Bernard"}
        assert len(offer.product.work.artist_links) == 2
        assert len(offer.product.artistLinks) == 2
        assert len(offer.artistOfferLinks) == 2
        assert db.session.query(discoveries_models.WorkArtist).count() == 4

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
        assert db.session.query(discoveries_models.Discovery).count() == 6
        listing = client.get("/native/v1/users/me/discoveries")
        assert listing.status_code == 200
        assert {discovery["work"]["visualUrl"] for discovery in listing.json["discoveries"] if discovery["work"]} == {
            work.visual_url for work in works
        }
