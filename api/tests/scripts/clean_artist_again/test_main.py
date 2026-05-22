from unittest.mock import patch

import pytest

from pcapi.core.artist import factories as artist_factories
from pcapi.core.artist import models as artist_models
from pcapi.core.offers import factories as offers_factories
from pcapi.models import db
from pcapi.scripts.clean_artist_again.main import main
from pcapi.scripts.clean_artist_again.main import slugify_name


pytestmark = pytest.mark.usefixtures("db_session")


def test_slugify():
    name = "Lucía Sánchez Saornil"
    assert slugify_name(name) == "lucia sanchez saornil"


@patch("pcapi.scripts.clean_artist_again.main.read_csv_file")
def test_with_artist_id(mock_read_csv):
    offer = offers_factories.OfferFactory()
    offer_id = offer.id
    artist = artist_factories.ArtistFactory(name="Goliarda Sapienza")
    artist_id = artist.id
    artist_factories.ArtistOfferLinkFactory(
        offer_id=offer_id, artist_id=artist_id, custom_name=None, artist_type=artist_models.ArtistType.AUTHOR
    )
    mock_read_csv.return_value = [
        {
            "offer_id": str(offer_id),
            "artist_id": str(artist_id),
            "artist_type": artist_models.ArtistType.AUTHOR,
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
    offer_id = offer.id
    artist = artist_factories.ArtistFactory(name="Goliarda Sapienza")
    artist_id = artist.id
    artist_factories.ArtistOfferLinkFactory(
        offer_id=offer_id, artist_id=artist_id, custom_name="Naomi Novik", artist_type=artist_models.ArtistType.AUTHOR
    )

    mock_read_csv.return_value = [
        {
            "offer_id": str(offer.id),
            "custom_name": "naomi novik",
            "artist_id": str(artist_id),
            "artist_type": artist_models.ArtistType.AUTHOR,
        }
    ]

    main(commit=True, filename="mock_filename")

    link = db.session.query(artist_models.ArtistOfferLink).filter_by(offer_id=offer_id).first()
    assert link is not None
    assert link.offer_id == offer_id
    assert link.custom_name == "Goliarda Sapienza"
    assert link.artist_id is None
    assert link.artist_name == "Goliarda Sapienza"


@patch("pcapi.scripts.clean_artist_again.main.read_csv_file")
def test_with_custom_name_and_artist_id(mock_read_csv):
    offer = offers_factories.OfferFactory()
    offer_id = offer.id
    artist = artist_factories.ArtistFactory(name="Ursula K. Le Guin")
    artist_id = artist.id
    artist_factories.ArtistOfferLinkFactory(
        offer_id=offer_id,
        artist_id=artist_id,
        custom_name="Ursula K. Le Guin",
        artist_type=artist_models.ArtistType.AUTHOR,
    )

    mock_read_csv.return_value = [
        {
            "offer_id": str(offer_id),
            "custom_name": "ursula k. le guin",
            "artist_id": str(artist_id),
            "artist_type": artist_models.ArtistType.AUTHOR,
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
    offer_id = offer.id
    artist = artist_factories.ArtistFactory(name="Mariana Enriquez")
    artist_id = artist.id
    artist_factories.ArtistOfferLinkFactory(
        offer_id=offer_id,
        custom_name="Ursula K. Le Guin",
        artist=None,
        artist_type=artist_models.ArtistType.AUTHOR,
    )  # should not change

    mock_read_csv.return_value = [
        {
            "offer_id": str(offer_id),
            "custom_name": "Mariana Enriquez",
            "artist_id": str(artist_id),
            "artist_type": artist_models.ArtistType.AUTHOR,
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
def test_handle_duplicates(mock_read_csv):
    offer = offers_factories.OfferFactory()
    another_offer = offers_factories.OfferFactory()
    offer_id = offer.id
    another_offer_id = another_offer.id

    artist = artist_factories.ArtistFactory(name="Lena Dunham")
    another_artist = artist_factories.ArtistFactory(name="Lena dunham")
    artist_id = artist.id
    another_artist_id = another_artist.id

    link_to_update = artist_factories.ArtistOfferLinkFactory(
        offer_id=offer_id, custom_name=None, artist_id=artist_id, artist_type=artist_models.ArtistType.AUTHOR
    )  # a garder
    link_to_delete = artist_factories.ArtistOfferLinkFactory(
        offer_id=offer_id, custom_name=None, artist_id=another_artist_id, artist_type=artist_models.ArtistType.AUTHOR
    )  # a supprimer : même artist type, mais artist_id différent
    link_different_type = artist_factories.ArtistOfferLinkFactory(
        offer_id=offer_id,
        custom_name="lena dunham",
        artist_id=artist_id,
        artist_type=artist_models.ArtistType.PERFORMER,
    )  # à garder: l'artist type est différent
    link_different_offer = artist_factories.ArtistOfferLinkFactory(
        offer_id=another_offer_id,
        custom_name=None,
        artist_id=another_artist_id,
        artist_type=artist_models.ArtistType.AUTHOR,
    )  # à garder: l'offre est différente

    link_to_update_id = link_to_update.id
    link_to_delete_id = link_to_delete.id
    link_different_type_id = link_different_type.id
    link_different_offer_id = link_different_offer.id

    mock_read_csv.return_value = [
        {
            "offer_id": str(offer_id),
            "custom_name": "lena dunham",
            "artist_id": str(artist.id),
            "artist_type": artist_models.ArtistType.AUTHOR,
        },  # on garde le link_to_update
        {
            "offer_id": str(offer_id),
            "custom_name": "lena dunham",
            "artist_id": str(another_artist.id),
            "artist_type": artist_models.ArtistType.AUTHOR,
        },  # cette ligne doit supprimer le link_to_delete
        {
            "offer_id": str(offer_id),
            "custom_name": "lena dunham",
            "artist_id": str(artist.id),
            "artist_type": artist_models.ArtistType.PERFORMER,
        },  # on garde également le link_different_type
        {
            "offer_id": str(another_offer_id),
            "custom_name": "lena dunham",
            "artist_id": str(another_artist.id),
            "artist_type": artist_models.ArtistType.AUTHOR,
        },  # on garde car c'est une autre offre
    ]

    main(commit=True, filename="mock_filename")

    db.session.expire_all()

    offer_links = db.session.query(artist_models.ArtistOfferLink).filter_by(offer_id=offer_id).all()
    another_offer_links = db.session.query(artist_models.ArtistOfferLink).filter_by(offer_id=another_offer_id).all()

    assert len(offer_links) == 2
    assert len(another_offer_links) == 1

    assert db.session.get(artist_models.ArtistOfferLink, link_to_update_id) is not None
    assert db.session.get(artist_models.ArtistOfferLink, link_different_type_id) is not None
    assert db.session.get(artist_models.ArtistOfferLink, link_different_offer_id) is not None

    assert db.session.get(artist_models.ArtistOfferLink, link_to_delete_id) is None

    for link in offer_links:
        assert link.artist_id is None
        assert link.custom_name == "Lena Dunham"

    for link in another_offer_links:
        assert link.artist_id is None
        assert link.custom_name == "Lena dunham"
