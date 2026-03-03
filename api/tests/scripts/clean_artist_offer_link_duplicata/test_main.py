from unittest.mock import patch

import pytest

from pcapi.core.artist import factories as artist_factories
from pcapi.core.artist import models as artist_models
from pcapi.core.offers import factories as offers_factories
from pcapi.models import db
from pcapi.scripts.clean_artist_offer_link_duplicata.main import main


pytestmark = pytest.mark.usefixtures("db_session")


@patch("pcapi.scripts.clean_artist_offer_link_duplicata.main.read_csv_file")
def test_basic(mock_read_csv):
    offer = offers_factories.OfferFactory()
    offer_id = offer.id
    artist = artist_factories.ArtistFactory(name="Goliarda Sapienza")
    artist_id = artist.id
    artist_type = artist_models.ArtistType.AUTHOR
    existing_link_with_artist = artist_factories.ArtistOfferLinkFactory(
        offer_id=offer.id, artist_id=artist_id, custom_name=None, artist_type=artist_type
    )
    existing_link_with_artist_id = existing_link_with_artist.id
    artist_factories.ArtistOfferLinkFactory(
        offer_id=offer.id, artist_id=None, custom_name="Goliarda Sapienza", artist_type=artist_type
    )  # existing link with custom name
    artist_factories.ArtistOfferLinkFactory(
        offer_id=offer.id, artist_id=None, custom_name="goliarda sapienza", artist_type=artist_type
    )  # another existing link with custom name but no caps
    mock_read_csv.return_value = [
        {
            "offer_id": str(offer_id),
        },
    ]

    main(commit=True, filename="mock_filename")

    query = db.session.query(artist_models.ArtistOfferLink).filter_by(offer_id=offer_id)
    assert query.count() == 1
    remaining_link = query.one()
    assert remaining_link.id == existing_link_with_artist_id


@patch("pcapi.scripts.clean_artist_offer_link_duplicata.main.read_csv_file")
def test_should_keep_first_custom_name(mock_read_csv):
    offer = offers_factories.OfferFactory()
    offer_id = offer.id
    artist_type = artist_models.ArtistType.STAGE_DIRECTOR
    first_link = artist_factories.ArtistOfferLinkFactory(
        offer_id=offer.id, artist_id=None, custom_name="Sharon Eyal", artist_type=artist_type
    )
    first_link_id = first_link.id
    artist_factories.ArtistOfferLinkFactory(
        offer_id=offer.id, artist_id=None, custom_name="sharon eyal", artist_type=artist_type
    )
    mock_read_csv.return_value = [
        {
            "offer_id": str(offer_id),
        },
    ]

    main(commit=True, filename="mock_filename")

    query = db.session.query(artist_models.ArtistOfferLink).filter_by(offer_id=offer_id)
    assert query.count() == 1
    remaining_link = query.one()
    assert remaining_link.id == first_link_id


@patch("pcapi.scripts.clean_artist_offer_link_duplicata.main.read_csv_file")
def test_should_keep_only_artist_entry(mock_read_csv):
    offer = offers_factories.OfferFactory()
    offer_id = offer.id
    artist = artist_factories.ArtistFactory(name="Greta Gerwig")
    artist_id = artist.id

    artist_offer_link_with_artist = artist_factories.ArtistOfferLinkFactory(
        offer_id=offer.id, artist_id=artist_id, custom_name=None, artist_type=artist_models.ArtistType.STAGE_DIRECTOR
    )
    artist_offer_link_with_artist_id = artist_offer_link_with_artist.id
    artist_factories.ArtistOfferLinkFactory(
        offer_id=offer.id,
        artist_id=None,
        custom_name="Greta Gerwig",
        artist_type=artist_models.ArtistType.STAGE_DIRECTOR,
    )
    mock_read_csv.return_value = [
        {
            "offer_id": str(offer_id),
        },
    ]

    main(commit=True, filename="mock_filename")

    query = db.session.query(artist_models.ArtistOfferLink).filter_by(offer_id=offer_id)
    assert query.count() == 1
    remaining_link = query.one()
    assert remaining_link.id == artist_offer_link_with_artist_id


@patch("pcapi.scripts.clean_artist_offer_link_duplicata.main.read_csv_file")
def test_should_keep_different_artist_types(mock_read_csv):
    offer = offers_factories.OfferFactory()
    offer_id = offer.id
    artist = artist_factories.ArtistFactory(name="Greta Gerwig")
    artist_id = artist.id

    artist_factories.ArtistOfferLinkFactory(
        offer_id=offer.id, artist_id=artist_id, custom_name=None, artist_type=artist_models.ArtistType.STAGE_DIRECTOR
    )
    artist_factories.ArtistOfferLinkFactory(
        offer_id=offer.id, artist_id=None, custom_name="Greta Gerwig", artist_type=artist_models.ArtistType.PERFORMER
    )
    mock_read_csv.return_value = [
        {
            "offer_id": str(offer_id),
        },
    ]

    main(commit=True, filename="mock_filename")

    assert db.session.query(artist_models.ArtistOfferLink).filter_by(offer_id=offer_id).count() == 2
