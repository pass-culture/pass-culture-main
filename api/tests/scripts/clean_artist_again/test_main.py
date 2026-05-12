from unittest.mock import patch

import pytest

from pcapi.core.artist import factories as artist_factories
from pcapi.core.artist import models as artist_models
from pcapi.core.offers import factories as offers_factories
from pcapi.models import db
from pcapi.scripts.clean_artist_again.main import main


pytestmark = pytest.mark.usefixtures("db_session")


@patch("pcapi.scripts.clean_artist_again.main.read_csv_file")
def test_with_artist_id(mock_read_csv):
    offer = offers_factories.OfferFactory()
    artist = artist_factories.ArtistFactory(name="Goliarda Sapienza")
    artist_factories.ArtistOfferLinkFactory(offer=offer, artist=artist, custom_name="")
    offer_id = offer.id
    artist_id = artist.id
    mock_read_csv.return_value = [
        {
            "offer_id": str(offer_id),
            "artist_id": str(artist_id),
            "custom_name": "",
        },
    ]

    main(commit=True, filename="mock_filename")

    link = db.session.query(artist_models.ArtistOfferLink).filter_by(offer_id=offer_id).first()
    assert link is not None
    assert link.offer_id == offer_id
    assert link.artist_id == None
    assert link.custom_name == "Goliarda Sapienza"
    assert link.artist_name == "Goliarda Sapienza"


@patch("pcapi.scripts.clean_artist_again.main.read_csv_file")
def test_with_custom_name(mock_read_csv):
    offer = offers_factories.OfferFactory()
    artist = artist_factories.ArtistFactory(name="Goliarda Sapienza")
    artist_factories.ArtistOfferLinkFactory(offer=offer, custom_name="Naomi Novik", artist=artist)
    offer_id = offer.id
    mock_read_csv.return_value = [
        {"offer_id": str(offer.id), "custom_name": "Naomi Novik", "artist_id": str(artist.id)}
    ]

    main(commit=True, filename="mock_filename")

    link = db.session.query(artist_models.ArtistOfferLink).filter_by(offer_id=offer_id).first()
    assert link is not None
    assert link.offer_id == offer_id
    assert link.custom_name == "Naomi Novik"
    assert link.artist_id is None
    assert link.artist_name == "Naomi Novik"


@patch("pcapi.scripts.clean_artist_again.main.read_csv_file")
def test_with_custom_name_and_artist_id(mock_read_csv):
    offer = offers_factories.OfferFactory()
    artist = artist_factories.ArtistFactory(name="Ursula K. Le Guin")
    artist_factories.ArtistOfferLinkFactory(offer=offer, custom_name="Ursula K. Le Guin", artist=artist)

    offer_id = offer.id
    artist_id = artist.id
    mock_read_csv.return_value = [
        {
            "offer_id": str(offer_id),
            "custom_name": "Ursula K. Le Guin",
            "artist_id": str(artist_id),
        }
    ]

    main(commit=True, filename="mock_filename")

    link = db.session.query(artist_models.ArtistOfferLink).filter_by(offer_id=offer_id).first()
    assert link is not None
    assert link.offer_id == offer_id
    assert link.artist_id == None
    assert link.custom_name == "Ursula K. Le Guin"
    assert link.artist_name == "Ursula K. Le Guin"


@patch("pcapi.scripts.clean_artist_again.main.read_csv_file")
def test_without_artist_id_should_not_update(mock_read_csv):
    offer = offers_factories.OfferFactory()
    artist = artist_factories.ArtistFactory(name="Mariana Enriquez")
    artist_factories.ArtistOfferLinkFactory(
        offer=offer, custom_name="Ursula K. Le Guin", artist=None
    )  # should not change

    offer_id = offer.id
    artist_id = artist.id
    mock_read_csv.return_value = [
        {
            "offer_id": str(offer_id),
            "custom_name": "Mariana Enriquez",
            "artist_id": str(artist_id),
        }
    ]

    main(commit=True, filename="mock_filename")

    link = db.session.query(artist_models.ArtistOfferLink).filter_by(offer_id=offer_id).first()
    assert link is not None
    assert link.offer_id == offer_id
    assert link.artist_id == None
    assert link.custom_name == "Ursula K. Le Guin"
    assert link.artist_name == "Ursula K. Le Guin"
