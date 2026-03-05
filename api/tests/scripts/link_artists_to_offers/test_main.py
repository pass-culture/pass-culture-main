from unittest.mock import patch

import pytest

from pcapi.core.artist import factories as artist_factories
from pcapi.core.artist import models as artist_models
from pcapi.core.offers import factories as offers_factories
from pcapi.models import db
from pcapi.scripts.link_artists_to_offers.main import main


pytestmark = pytest.mark.usefixtures("db_session")


@patch("pcapi.scripts.link_artists_to_offers.main.read_csv_file")
def test_with_artist_id(mock_read_csv):
    offer = offers_factories.OfferFactory()
    artist = artist_factories.ArtistFactory(name="Goliarda Sapienza")
    offer_id = offer.id
    artist_id = artist.id
    mock_read_csv.return_value = [
        {
            "offer_id": str(offer_id),
            "artist_id": str(artist_id),
            "artist_type": "author",
            "custom_name": "",
        },
    ]

    main(commit=True, filename="mock_filename")

    link = db.session.query(artist_models.ArtistOfferLink).filter_by(offer_id=offer_id).first()
    assert link is not None
    assert link.offer_id == offer_id
    assert link.artist_id == artist_id
    assert link.artist_type == artist_models.ArtistType.AUTHOR
    assert link.artist_name == "Goliarda Sapienza"
    assert link.custom_name == None


@patch("pcapi.scripts.link_artists_to_offers.main.read_csv_file")
def test_with_custom_name(mock_read_csv):
    offer = offers_factories.OfferFactory()
    offer_id = offer.id
    mock_read_csv.return_value = [
        {"offer_id": str(offer.id), "artist_type": "author", "custom_name": "Naomi Novik", "artist_id": ""}
    ]

    main(commit=True, filename="mock_filename")

    link = db.session.query(artist_models.ArtistOfferLink).filter_by(offer_id=offer_id).first()
    assert link is not None
    assert link.offer_id == offer_id
    assert link.custom_name == "Naomi Novik"
    assert link.artist_type == artist_models.ArtistType.AUTHOR
    assert link.artist_id is None
    assert link.artist_name == "Naomi Novik"


@patch("pcapi.scripts.link_artists_to_offers.main.read_csv_file")
def test_with_custom_name_and_artist_id(mock_read_csv, caplog):
    offer = offers_factories.OfferFactory()
    artist = artist_factories.ArtistFactory(name="Ursula K. Le Guin")
    offer_id = offer.id
    artist_id = artist.id
    mock_read_csv.return_value = [
        {
            "offer_id": str(offer_id),
            "artist_type": "author",
            "custom_name": "Mariana Enriquez",
            "artist_id": str(artist_id),
        }
    ]

    main(commit=True, filename="mock_filename")

    link = db.session.query(artist_models.ArtistOfferLink).filter_by(offer_id=offer_id).first()
    assert link is not None
    assert link.offer_id == offer_id
    assert link.custom_name == None
    assert link.artist_id == artist_id
    assert link.artist_name == "Ursula K. Le Guin"


@patch("pcapi.scripts.link_artists_to_offers.main.read_csv_file")
def test_skips_and_logs_wrong_enum_values(mock_read_csv, caplog):
    offer = offers_factories.OfferFactory()
    artist = artist_factories.ArtistFactory(name="Ursula K. Le Guin")
    offer_id = offer.id
    artist_id = artist.id
    mock_read_csv.return_value = [
        {
            "offer_id": str(offer_id),
            "artist_type": "perfomer",
            "custom_name": "Mariana Enriquez",
            "artist_id": str(artist_id),
        }
    ]
    main(commit=True, filename="mock_filename")

    assert "Artist Type perfomer is not a valid enum value" in caplog.text
    assert db.session.query(artist_models.ArtistOfferLink).count() == 1


@patch("pcapi.scripts.link_artists_to_offers.main.read_csv_file")
def test_skips_existing_artist_offer_link(mock_read_csv, caplog):
    offer = offers_factories.OfferFactory()
    artist = artist_factories.ArtistFactory()
    offer_id = offer.id
    artist_id = artist.id
    existing_link = artist_factories.ArtistOfferLinkFactory(offer=offer, artist=artist)
    mock_read_csv.return_value = [
        {
            "offer_id": str(offer_id),
            "artist_type": existing_link.artist_type,
            "custom_name": "Wendy Delorme",
            "artist_id": str(artist_id),
        }
    ]

    main(commit=True, filename="mock_filename")
    assert db.session.query(artist_models.ArtistOfferLink).count() == 1


@patch("pcapi.scripts.link_artists_to_offers.main.read_csv_file")
def test_incomplete_line_should_fail(mock_read_csv, caplog):
    offer = offers_factories.OfferFactory()
    offer_id = offer.id
    mock_read_csv.return_value = [
        {"offer_id": str(offer.id), "artist_type": "author", "custom_name": "", "artist_id": ""}
    ]

    main(commit=True, filename="mock_filename")

    assert f"Ligne ignorée : pas d'artist_id ni de custom_name pour offer_id {offer_id}" in caplog.text
    assert db.session.query(artist_models.ArtistOfferLink).count() == 0


@patch("pcapi.scripts.link_artists_to_offers.main.read_csv_file")
def test_offer_linked_to_product_should_not_be_linked_to_artist(mock_read_csv, caplog):
    product = offers_factories.ProductFactory()
    offer = offers_factories.OfferFactory(product=product)
    offer_id = offer.id
    mock_read_csv.return_value = [
        {"offer_id": str(offer.id), "artist_type": "author", "custom_name": "Chimamanda Ngozi Adichie", "artist_id": ""}
    ]

    main(commit=True, filename="mock_filename")

    assert f"Offer ID {offer_id} introuvable ou liée à un produit" in caplog.text
    assert db.session.query(artist_models.ArtistOfferLink).count() == 0


@patch("pcapi.scripts.link_artists_to_offers.main.read_csv_file")
def test_dry_run_should_not_commit(mock_read_csv):
    offer = offers_factories.OfferFactory()
    artist = artist_factories.ArtistFactory()
    offer_id = offer.id
    artist_id = artist.id
    mock_read_csv.return_value = [
        {"offer_id": str(offer_id), "artist_type": "performer", "custom_name": "", "artist_id": str(artist_id)}
    ]

    main(commit=False, filename="mock_filename")

    assert db.session.query(artist_models.ArtistOfferLink).count() == 0


@patch("pcapi.scripts.link_artists_to_offers.main.read_csv_file")
def test_missing_artist_should_raise(mock_read_csv, caplog):
    offer = offers_factories.OfferFactory()
    offer_id = offer.id
    mock_read_csv.return_value = [
        {
            "offer_id": str(offer_id),
            "artist_type": "performer",
            "custom_name": "",
            "artist_id": "abcdefgh-1234-1234-abcd-1234abcdedfg5678",
        }
    ]

    main(commit=False, filename="mock_filename")
    assert "Certains artistes de ce batch n'existent pas en base de données, il ne sera pas traîté" in caplog.text
    assert db.session.query(artist_models.ArtistOfferLink).count() == 0
