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
def test_with_custom_name_and_artist_id(mock_read_csv):
    offer = offers_factories.OfferFactory(extraData={"author": "Ursula K. Le Guin"})
    offer_id = offer.id
    artist = artist_factories.ArtistFactory(name="ursula k. le guin")
    artist_id = artist.id
    artist_factories.ArtistOfferLinkFactory(
        offer_id=offer_id,
        artist_id=artist_id,
        custom_name="ursula k. le guin",
        artist_type=artist_models.ArtistType.AUTHOR,
    )

    mock_read_csv.return_value = [
        {
            "offer_id": str(offer_id),
            "custom_name": "ursula k. le guin",
            "artist_id": str(artist_id),
            "artist_type": artist_models.ArtistType.AUTHOR.value,
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
def test_with_custom_name_and_no_artist_id(mock_read_csv):
    offer = offers_factories.OfferFactory(
        extraData={"author": "Ursula K. Le Guin"},
    )
    offer_id = offer.id
    artist_factories.ArtistOfferLinkFactory(
        offer_id=offer_id,
        artist_id=None,
        custom_name="ursula k. le guin",
        artist_type=artist_models.ArtistType.AUTHOR,
    )

    mock_read_csv.return_value = [
        {
            "offer_id": str(offer_id),
            "custom_name": "ursula k. le guin",
            "artist_id": "",
            "artist_type": artist_models.ArtistType.AUTHOR.value,
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
def test_with_custom_name_and_no_artist_id_and_product(mock_read_csv):
    product = offers_factories.ProductFactory(extraData={"author": "Ursula K. Le Guin"})
    product_id = product.id
    offer = offers_factories.OfferFactory(productId=product_id)
    offer_id = offer.id
    artist_factories.ArtistOfferLinkFactory(
        offer_id=offer_id,
        artist_id=None,
        custom_name="ursula k. le guin",
        artist_type=artist_models.ArtistType.AUTHOR,
    )

    mock_read_csv.return_value = [
        {
            "offer_id": str(offer_id),
            "custom_name": "ursula k. le guin",
            "artist_id": "",
            "artist_type": artist_models.ArtistType.AUTHOR.value,
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
def test_without_artist_id_should_update(mock_read_csv):
    offer = offers_factories.OfferFactory(extraData={"author": "Mariana Enriquez"})
    offer_id = offer.id
    artist = artist_factories.ArtistFactory(name="mariana enriquez")
    artist_id = artist.id
    artist_factories.ArtistOfferLinkFactory(
        offer_id=offer_id,
        custom_name="mariana enriquez",
        artist=None,
        artist_type=artist_models.ArtistType.AUTHOR,
    )

    mock_read_csv.return_value = [
        {
            "offer_id": str(offer_id),
            "custom_name": "mariana enriquez",
            "artist_id": str(artist_id),
            "artist_type": artist_models.ArtistType.AUTHOR.value,
        }
    ]

    main(commit=True, filename="mock_filename")

    link = db.session.query(artist_models.ArtistOfferLink).filter_by(offer_id=offer_id).first()
    assert link is not None
    assert link.offer_id == offer_id
    assert link.artist_id == None
    assert link.custom_name == "Mariana Enriquez"
    assert link.artist_name == "Mariana Enriquez"


@patch("pcapi.scripts.clean_artist_again.main.read_csv_file")
def test_handle_duplicates(mock_read_csv):
    offer = offers_factories.OfferFactory(extraData={"author": "Lena Dunham", "performer": "Lena Dunham"})
    another_offer = offers_factories.OfferFactory(extraData={"author": "Lena dunham"})
    offer_id = offer.id
    another_offer_id = another_offer.id

    artist = artist_factories.ArtistFactory(name="lena dunham")
    another_artist = artist_factories.ArtistFactory(name="lena dunham")
    artist_id = artist.id
    another_artist_id = another_artist.id

    link_to_update = artist_factories.ArtistOfferLinkFactory(
        offer_id=offer_id, custom_name=None, artist_id=artist_id, artist_type=artist_models.ArtistType.AUTHOR
    )  # a garder
    link_to_delete = artist_factories.ArtistOfferLinkFactory(
        offer_id=offer_id,
        custom_name=None,
        artist_id=another_artist_id,
        artist_type=artist_models.ArtistType.AUTHOR,
    )  # a supprimer : doublon car artist_id est différent
    link_different_type = artist_factories.ArtistOfferLinkFactory(
        offer_id=offer_id,
        custom_name=None,
        artist_id=artist_id,
        artist_type=artist_models.ArtistType.PERFORMER,
    )  # à garder: l'artist type est différent
    link_different_offer = artist_factories.ArtistOfferLinkFactory(
        offer_id=another_offer_id,
        custom_name=None,
        artist_id=another_artist_id,
        artist_type=artist_models.ArtistType.AUTHOR,
    )  # à garder: l'offre est différente
    link_with_custom_name = artist_factories.ArtistOfferLinkFactory(
        offer_id=offer_id,
        custom_name="Lena dunham",
        artist_id=None,
        artist_type=artist_models.ArtistType.AUTHOR,
    )  # à supprimer : doublon avec link_to_update lorsqu'il sera mis à jour

    link_to_update_id = link_to_update.id
    link_to_delete_id = link_to_delete.id
    link_different_type_id = link_different_type.id
    link_different_offer_id = link_different_offer.id
    link_with_custom_name_id = link_with_custom_name.id

    mock_read_csv.return_value = [
        {
            "offer_id": str(offer_id),
            "custom_name": "lena dunham",
            "artist_id": str(artist.id),
            "artist_type": artist_models.ArtistType.AUTHOR.value,
        },  # on garde le link_to_update
        {
            "offer_id": str(offer_id),
            "custom_name": "lena dunham",
            "artist_id": str(another_artist.id),
            "artist_type": artist_models.ArtistType.AUTHOR.value,
        },  # cette ligne doit supprimer le link_to_delete
        {
            "offer_id": str(offer_id),
            "custom_name": "lena dunham",
            "artist_id": str(artist.id),
            "artist_type": artist_models.ArtistType.PERFORMER.value,
        },  # on garde également le link_different_type
        {
            "offer_id": str(another_offer_id),
            "custom_name": "lena dunham",
            "artist_id": str(another_artist.id),
            "artist_type": artist_models.ArtistType.AUTHOR.value,
        },  # on garde car c'est une autre offre
        {
            "offer_id": str(offer_id),
            "custom_name": "lena dunham",
            "artist_id": None,
            "artist_type": artist_models.ArtistType.AUTHOR.value,
        },  # on supprime car doublon avec link_to_update
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
    assert db.session.get(artist_models.ArtistOfferLink, link_with_custom_name_id) is None

    for link in offer_links:
        assert link.artist_id is None
        assert link.custom_name == "Lena Dunham"

    for link in another_offer_links:
        assert link.artist_id is None
        assert link.custom_name == "Lena dunham"
