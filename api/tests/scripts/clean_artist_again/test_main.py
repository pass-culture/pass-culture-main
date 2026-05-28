import logging

import pytest

from pcapi.core.artist import factories as artist_factories
from pcapi.core.artist import models as artist_models
from pcapi.core.offers import factories as offers_factories
from pcapi.models import db
from pcapi.scripts.clean_artist_again.main import main


pytestmark = pytest.mark.usefixtures("db_session")


def _links_for(offer_id: int) -> list[artist_models.ArtistOfferLink]:
    return (
        db.session.query(artist_models.ArtistOfferLink)
        .filter_by(offer_id=offer_id)
        .order_by(artist_models.ArtistOfferLink.artist_type, artist_models.ArtistOfferLink.custom_name)
        .all()
    )


def test_creates_link_from_extra_data():
    offer = offers_factories.OfferFactory(extraData={"author": "Author Name"})

    main(commit=True, min_offer_id=offer.id, max_offer_id=offer.id)

    links = _links_for(offer.id)
    assert len(links) == 1
    assert links[0].artist_id is None
    assert links[0].custom_name == "Author Name"
    assert links[0].artist_type == artist_models.ArtistType.AUTHOR


def test_empty_values_produce_no_links():
    offer = offers_factories.OfferFactory(
        extraData={"author": "", "performer": "   ", "stageDirector": None},
    )

    main(commit=True, min_offer_id=offer.id, max_offer_id=offer.id)

    assert _links_for(offer.id) == []


def test_only_relevant_artist_types_are_kept():
    offer = offers_factories.OfferFactory(
        extraData={
            "author": "Author Name",
            "performer": "Performer Name",
            "stageDirector": "Stage Director Name",
            "musicSubType": "Music Sub Type",
        },
    )

    main(commit=True, min_offer_id=offer.id, max_offer_id=offer.id)

    links = _links_for(offer.id)
    assert {(link.artist_type, link.custom_name) for link in links} == {
        (artist_models.ArtistType.AUTHOR, "Author Name"),
        (artist_models.ArtistType.PERFORMER, "Performer Name"),
        (artist_models.ArtistType.STAGE_DIRECTOR, "Stage Director Name"),
    }


def test_delete_existing_links():
    offer = offers_factories.OfferFactory(extraData=None)
    any_artist = artist_factories.ArtistFactory(name="Artist Name")
    artist_factories.ArtistOfferLinkFactory(
        offer_id=offer.id,
        artist_id=any_artist.id,
        custom_name=None,
        artist_type=artist_models.ArtistType.AUTHOR,
    )
    artist_factories.ArtistOfferLinkFactory(
        offer_id=offer.id,
        artist_id=None,
        custom_name="Custom Name",
        artist_type=artist_models.ArtistType.AUTHOR,
    )

    main(commit=True, min_offer_id=offer.id, max_offer_id=offer.id)

    assert _links_for(offer.id) == []


def test_offer_with_product_links_are_not_recreated():
    product = offers_factories.ProductFactory(extraData={"author": "Product Author"})
    offer = offers_factories.OfferFactory(
        product=product,
        extraData={"author": "Product Author"},
    )
    artist_factories.ArtistOfferLinkFactory(
        offer_id=offer.id,
        artist_id=None,
        custom_name="Custom Name",
        artist_type=artist_models.ArtistType.AUTHOR,
    )

    main(commit=True, min_offer_id=offer.id, max_offer_id=offer.id)

    assert _links_for(offer.id) == []


def test_dry_run_does_not_persist_changes():
    offer = offers_factories.OfferFactory(extraData={"author": "Author Name"})
    pre_existing = artist_factories.ArtistOfferLinkFactory(
        offer_id=offer.id,
        artist_id=None,
        custom_name="Custom Name",
        artist_type=artist_models.ArtistType.AUTHOR,
    )
    pre_existing_id = pre_existing.id
    db.session.commit()

    main(commit=False, min_offer_id=offer.id, max_offer_id=offer.id)

    db.session.expire_all()
    links = _links_for(offer.id)
    assert len(links) == 1
    assert links[0].id == pre_existing_id
    assert links[0].custom_name == "Custom Name"


def test_processes_all_offers_in_range():
    offer_a = offers_factories.OfferFactory(extraData={"author": "Author A"})
    offer_b = offers_factories.OfferFactory(extraData={"performer": "Performer B"})

    main(commit=True, min_offer_id=offer_a.id, max_offer_id=offer_b.id)

    assert {link.custom_name for link in _links_for(offer_a.id)} == {"Author A"}
    assert {link.custom_name for link in _links_for(offer_b.id)} == {"Performer B"}


def test_min_offer_id_skips_earlier_offers():
    offer_a = offers_factories.OfferFactory(extraData={"author": "Author A"})
    offer_b = offers_factories.OfferFactory(extraData={"author": "Author B"})
    skipped_link = artist_factories.ArtistOfferLinkFactory(
        offer_id=offer_a.id,
        artist_id=None,
        custom_name="Custom Name",
        artist_type=artist_models.ArtistType.PERFORMER,
    )
    skipped_link_id = skipped_link.id

    main(commit=True, min_offer_id=offer_b.id, max_offer_id=offer_b.id)

    links_a = _links_for(offer_a.id)
    assert len(links_a) == 1
    assert links_a[0].id == skipped_link_id
    assert {link.custom_name for link in _links_for(offer_b.id)} == {"Author B"}


def test_max_offer_id_skips_later_offers():
    offer_a = offers_factories.OfferFactory(extraData={"author": "Author A"})
    offer_b = offers_factories.OfferFactory(extraData={"author": "Author B"})
    skipped_link = artist_factories.ArtistOfferLinkFactory(
        offer_id=offer_b.id,
        artist_id=None,
        custom_name="Custom Name",
        artist_type=artist_models.ArtistType.PERFORMER,
    )
    skipped_link_id = skipped_link.id

    main(commit=True, min_offer_id=offer_a.id, max_offer_id=offer_a.id)

    assert {link.custom_name for link in _links_for(offer_a.id)} == {"Author A"}
    links_b = _links_for(offer_b.id)
    assert len(links_b) == 1
    assert links_b[0].id == skipped_link_id


def test_verbose_logs_each_created_link(caplog):
    offer = offers_factories.OfferFactory(
        extraData={"author": "Author Name", "performer": "Performer Name"},
    )

    with caplog.at_level(logging.INFO):
        main(commit=True, min_offer_id=offer.id, max_offer_id=offer.id, verbose=True)

    assert {link.custom_name for link in _links_for(offer.id)} == {"Author Name", "Performer Name"}
    link_logs = [record.message for record in caplog.records if f"offre {offer.id} :" in record.message]
    assert sorted(link_logs) == [
        f"  offre {offer.id} : author = 'Author Name'",
        f"  offre {offer.id} : performer = 'Performer Name'",
    ]
