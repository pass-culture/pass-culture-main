import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
from pcapi.local_providers.chunk_manager import save_chunks
from pcapi.models import db


pytestmark = pytest.mark.usefixtures("db_session")


# XXX: These unit tests are too much tied to what happens before
# `save_chunks()` is called, e.g. how ids are manually set on unsaved
# objects by peeking at the next sequence number. Tests try (too) hard
# to recreate that, with calls to session refresh and expunge and
# manual setting of ids.


def test_save_chunks_insert_1_offer_in_chunk():
    product = offers_factories.ProductFactory()
    venue = offerers_factories.VenueFactory()
    offer = offers_factories.OfferFactory.build(
        idAtProvider="1%12345678912345",
        productId=product.id,
        venueId=venue.id,
    )

    save_chunks({"1|Offer": offer}, chunk_to_update={})

    assert Offer.query.count() == 1


def test_save_chunks_insert_1_offer_and_1_stock_in_chunk():
    product = offers_factories.ProductFactory()
    venue = offerers_factories.VenueFactory()
    offer = offers_factories.OfferFactory.build(
        id=1,
        idAtProvider="1%12345678912345",
        productId=product.id,
        venueId=venue.id,
    )
    stock = offers_factories.StockFactory.build(id=1, offerId=1)

    chunk_to_insert = {
        "1|Offer": offer,
        "1|Stock": stock,
    }
    save_chunks(chunk_to_insert, chunk_to_update={})

    assert Offer.query.count() == 1
    assert Stock.query.count() == 1


def test_save_chunks_update_1_offer_in_chunk():
    other_offer = offers_factories.OfferFactory(idAtProvider="1%12345678912345", isDuo=False)
    offer = offers_factories.OfferFactory(idAtProvider="1%12345678912345", isDuo=False)

    db.session.refresh(offer)
    offer.isDuo = True
    chunk_to_update = {
        "1|Offer": offer,
    }
    db.session.expunge(offer)
    save_chunks(chunk_to_insert={}, chunk_to_update=chunk_to_update)

    assert Offer.query.get(offer.id).isDuo
    assert not Offer.query.get(other_offer.id).isDuo


def test_save_chunks_update_2_offers_and_1_stock_in_chunk():
    offer1 = offers_factories.OfferFactory(idAtProvider="1%12345678912345", isDuo=False)
    offer2 = offers_factories.OfferFactory(idAtProvider="2%12345678912345", isDuo=False)
    stock = offers_factories.StockFactory(offer=offer1, quantity=3)

    db.session.refresh(offer1)
    db.session.refresh(offer2)
    db.session.refresh(stock)
    offer1.isDuo = True
    offer2.isDuo = True
    stock.quantity = 2
    chunk_to_update = {
        "1|Offer": offer1,
        "1|Stock": stock,
        "2|Offer": offer2,
    }
    db.session.expunge(offer1)
    db.session.expunge(offer2)
    db.session.expunge(stock)

    save_chunks(chunk_to_insert={}, chunk_to_update=chunk_to_update)

    offers = Offer.query.all()
    assert len(offers) == 2
    assert all(offer.isDuo for offer in offers)
    stock = Stock.query.one()
    assert stock.quantity == 2
