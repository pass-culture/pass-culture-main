from unittest.mock import Mock
from unittest.mock import call
from unittest.mock import patch

import pytest

from pcapi.core.artist.factories import ArtistAliasFactory
from pcapi.core.artist.factories import ArtistFactory
from pcapi.core.artist.factories import ArtistProductLinkFactory
from pcapi.core.artist.models import Artist
from pcapi.core.artist.models import ArtistAlias
from pcapi.core.artist.models import ArtistProductLink
from pcapi.core.offers.factories import OfferFactory
from pcapi.core.offers.factories import ProductFactory
from pcapi.models import db
from pcapi.scripts.reimport_all_artists.main import get_number_of_products
from pcapi.scripts.reimport_all_artists.main import reindex_artist_product_offers
from pcapi.scripts.reimport_all_artists.main import truncate_artist_tables


@pytest.mark.usefixtures("clean_database")
def test_truncate_tables() -> None:
    artist_id = ArtistFactory().id
    product_id = ProductFactory().id
    ArtistAliasFactory(artist_id=artist_id)
    ArtistProductLinkFactory(artist_id=artist_id, product_id=product_id)

    truncate_artist_tables()

    assert db.session.query(Artist).count() == 0
    assert db.session.query(ArtistAlias).count() == 0
    assert db.session.query(ArtistProductLink).count() == 0


@pytest.mark.usefixtures("clean_database")
def test_get_number_of_products() -> None:
    artist1_id = ArtistFactory().id
    artist2_id = ArtistFactory().id
    product1_id = ProductFactory().id
    product2_id = ProductFactory().id
    ArtistProductLinkFactory(artist_id=artist1_id, product_id=product1_id)
    ArtistProductLinkFactory(artist_id=artist2_id, product_id=product1_id)
    ArtistProductLinkFactory(artist_id=artist2_id, product_id=product2_id)

    assert get_number_of_products() == 2


@pytest.mark.usefixtures("clean_database")
@patch("pcapi.scripts.reimport_all_artists.main.reindex_related_offers")
def test_reindex_products_with_batches(mock_reindex_related_offers: Mock) -> None:
    artist_id = ArtistFactory().id
    product1_id = ProductFactory().id
    product2_id = ProductFactory().id
    product3_id = ProductFactory().id
    ArtistProductLinkFactory(artist_id=artist_id, product_id=product1_id)
    ArtistProductLinkFactory(artist_id=artist_id, product_id=product2_id)
    ArtistProductLinkFactory(artist_id=artist_id, product_id=product3_id)

    reindex_artist_product_offers(batch_size=2, not_dry=False)

    calls = [call([product1_id, product2_id], False), call([product3_id], False)]
    mock_reindex_related_offers.assert_has_calls(calls, any_order=True)


@pytest.mark.usefixtures("clean_database")
@patch("pcapi.core.search.reindex_offer_ids")
def test_reindex_offers(mock_reindex_offer_ids: Mock) -> None:
    artist_id = ArtistFactory().id
    product1_id = ProductFactory().id
    product2_id = ProductFactory().id
    offer1_id = OfferFactory(productId=product1_id).id
    offer2_id = OfferFactory(productId=product1_id).id
    offer3_id = OfferFactory(productId=product2_id).id
    ArtistProductLinkFactory(artist_id=artist_id, product_id=product1_id)
    ArtistProductLinkFactory(artist_id=artist_id, product_id=product2_id)

    reindex_artist_product_offers(batch_size=1, not_dry=True)

    calls = [call([offer1_id, offer2_id]), call([offer3_id])]
    mock_reindex_offer_ids.assert_has_calls(calls, any_order=True)
