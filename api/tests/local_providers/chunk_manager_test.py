import pytest
from sqlalchemy import Sequence

from pcapi.local_providers.chunk_manager import save_chunks
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_stock
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.model_creators.specific_creators import create_product_with_thing_subcategory
from pcapi.models import Offer
from pcapi.models import Stock
from pcapi.models.db import db
from pcapi.repository import repository


class SaveChunksTest:
    @pytest.mark.usefixtures("db_session")
    def test_save_chunks_insert_1_offer_in_chunk(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        product = create_product_with_thing_subcategory()
        repository.save(venue, product)

        offer = create_offer_with_thing_product(venue, product=product, id_at_providers="1%12345678912345")
        offer.venueId = venue.id
        chunk_to_insert = {"1|Offer": offer}
        db.session.expunge(offer)

        chunk_to_update = {}

        # When
        save_chunks(chunk_to_insert, chunk_to_update)

        # Then
        assert Offer.query.count() == 1

    @pytest.mark.usefixtures("db_session")
    def test_save_chunks_insert_1_offer_and_1_stock_in_chunk(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        product = create_product_with_thing_subcategory()
        repository.save(venue, product)

        offer = create_offer_with_thing_product(venue, product=product, id_at_providers="1%12345678912345")
        offer.venueId = venue.id
        offer_id = db.session.execute(Sequence("offer_id_seq"))
        offer.id = offer_id

        stock = create_stock(offer=offer)
        stock.offerId = offer_id

        chunk_to_insert = {
            "1|Offer": offer,
            "1|Stock": stock,
        }
        db.session.expunge(offer)
        db.session.expunge(stock)

        chunk_to_update = {}

        # When
        save_chunks(chunk_to_insert, chunk_to_update)

        # Then
        assert Offer.query.count() == 1
        assert Stock.query.count() == 1

    @pytest.mark.usefixtures("db_session")
    def test_save_chunks_update_1_offer_in_chunk(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        product = create_product_with_thing_subcategory()
        offer = create_offer_with_thing_product(venue, product=product, id_at_providers="1%12345678912345")
        repository.save(venue, product, offer)

        db.session.refresh(offer)
        offer.isDuo = True
        chunk_to_update = {
            "1|Offer": offer,
        }
        db.session.expunge(offer)

        chunk_to_insert = {}

        # When
        save_chunks(chunk_to_insert, chunk_to_update)

        # Then
        assert Offer.query.count() == 1

    @pytest.mark.usefixtures("db_session")
    def test_save_chunks_update_2_offers_and_1_stock_in_chunk(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        product = create_product_with_thing_subcategory()
        offer1 = create_offer_with_thing_product(venue, product=product, id_at_providers="1%12345678912345")
        offer2 = create_offer_with_thing_product(venue, product=product, id_at_providers="2%12345678912345")
        stock = create_stock(offer=offer1)
        repository.save(venue, product, offer1, offer2, stock)

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

        chunk_to_insert = {}

        # When
        save_chunks(chunk_to_insert, chunk_to_update)

        # Then
        offers = Offer.query.all()
        assert len(offers) == 2
        assert any(offer.isDuo for offer in offers)
        assert Stock.query.count() == 1
