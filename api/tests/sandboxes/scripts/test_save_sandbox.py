from datetime import timedelta
from unittest.mock import patch

import pytest

import pcapi.core.artist.factories as artist_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.offers.models as offers_models
from pcapi.core.artist import models as artist_models
from pcapi.core.categories import subcategories
from pcapi.core.discoveries import models as discoveries_models
from pcapi.models import db
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_works import create_industrial_works
from pcapi.sandboxes.scripts.save_sandbox import _index_all_offers
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
class CreateIndustrialWorksTest:
    @pytest.mark.parametrize(
        "subcategory,media_type",
        [
            (subcategories.LIVRE_PAPIER, discoveries_models.WorkMediaType.BOOK),
            (subcategories.SEANCE_CINE, discoveries_models.WorkMediaType.FILM),
            (subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD, discoveries_models.WorkMediaType.MUSIC),
            (subcategories.SUPPORT_PHYSIQUE_MUSIQUE_VINYLE, discoveries_models.WorkMediaType.MUSIC),
        ],
    )
    def test_creates_work_for_product(self, subcategory, media_type):
        product = offers_factories.ProductFactory(subcategoryId=subcategory.id, name="A cultural work")

        create_industrial_works()

        assert product.work.title == product.name
        assert product.work.media_type == media_type
        assert product.work.external_ids == {}

    def test_shares_work_between_music_formats_and_preserves_artist_links(self):
        artist = artist_factories.ArtistFactory()
        cd = offers_factories.ProductFactory(
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id, name="An album"
        )
        vinyl = offers_factories.ProductFactory(
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE_VINYLE.id, name="An album"
        )
        for product in (cd, vinyl):
            artist_factories.ArtistProductLinkFactory(
                artist_id=artist.id, product_id=product.id, artist_type=artist_models.ArtistType.PERFORMER
            )

        create_industrial_works()
        create_industrial_works()

        assert cd.work == vinyl.work
        assert db.session.query(discoveries_models.Work).count() == 1
        link = db.session.query(discoveries_models.WorkArtist).one()
        assert link.work == cd.work
        assert link.artist == artist
        assert link.role == "performer"

    def test_preserves_existing_work_and_ignores_other_subcategories(self):
        work = discoveries_models.Work(title="Original title", media_type=discoveries_models.WorkMediaType.BOOK)
        product = offers_factories.ProductFactory(work=work, subcategoryId=subcategories.LIVRE_PAPIER.id)
        other_product = offers_models.Product(name="Museum pass", subcategoryId=subcategories.CARTE_MUSEE.id)
        db.session.add(other_product)
        db.session.flush()

        create_industrial_works()

        assert product.work == work
        assert other_product.work is None
        assert db.session.query(discoveries_models.Work).count() == 1
