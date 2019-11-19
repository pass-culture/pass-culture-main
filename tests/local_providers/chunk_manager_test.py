from sqlalchemy import Sequence

from local_providers.chunk_manager import save_chunks
from models import PcObject, Offer, Stock
from models.db import db
from tests.conftest import clean_database
from tests.test_utils import create_offer_with_thing_product, create_offerer, create_venue, \
    create_product_with_thing_type, create_stock


class SaveChunksTest:
    @clean_database
    def test_save_chunks_insert_1_offer_in_chunk(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        product = create_product_with_thing_type()
        PcObject.save(venue, product)

        offer = create_offer_with_thing_product(venue,
                                                product=product,
                                                id_at_providers='1%12345678912345')
        chunk_to_insert = {
            '1|Offer': offer
        }
        db.session.expunge(offer)

        chunk_to_update = {}

        # When
        save_chunks(chunk_to_insert, chunk_to_update)

        # Then
        assert Offer.query.count() == 1

    @clean_database
    def test_save_chunks_insert_1_offer_and_1_stock_in_chunk(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        product = create_product_with_thing_type()
        PcObject.save(venue, product)

        offer = create_offer_with_thing_product(venue,
                                                product=product,
                                                id_at_providers='1%12345678912345')
        offer_id = db.session.execute(Sequence('offer_id_seq'))
        offer.id = offer_id

        stock = create_stock(offer=offer)
        stock.offerId = offer_id

        chunk_to_insert = {
            '1|Offer': offer,
            '1|Stock': stock,
        }
        db.session.expunge(offer)
        db.session.expunge(stock)

        chunk_to_update = {}

        # When
        save_chunks(chunk_to_insert, chunk_to_update)

        # Then
        assert Offer.query.count() == 1
        assert Stock.query.count() == 1

    @clean_database
    def test_save_chunks_update_1_offer_in_chunk(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        product = create_product_with_thing_type()
        offer = create_offer_with_thing_product(venue,
                                                product=product,
                                                id_at_providers='1%12345678912345')
        PcObject.save(venue, product, offer)

        db.session.refresh(offer)
        offer.isDuo = True
        chunk_to_update = {
            '1|Offer': offer,
        }
        db.session.expunge(offer)

        chunk_to_insert = {}

        # When
        save_chunks(chunk_to_insert, chunk_to_update)

        # Then
        assert Offer.query.count() == 1

    @clean_database
    def test_save_chunks_update_1_offer_and_1_stock_in_chunk(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        product = create_product_with_thing_type()
        offer = create_offer_with_thing_product(venue,
                                                product=product,
                                                id_at_providers='1%12345678912345')
        stock = create_stock(offer=offer)
        PcObject.save(venue, product, offer, stock)

        db.session.refresh(offer)
        db.session.refresh(stock)
        offer.isDuo = True
        stock.available = 2
        chunk_to_update = {
            '1|Offer': offer,
            '1|Stock': stock,
        }
        db.session.expunge(offer)
        db.session.expunge(stock)

        chunk_to_insert = {}

        # When
        save_chunks(chunk_to_insert, chunk_to_update)

        # Then
        assert Offer.query.count() == 1
        assert Stock.query.count() == 1

# @clean_database
# def test_insert_chunk_perf(app):
#     # Given
#     chunk_to_insert = {}
#
#     offerer = create_offerer()
#     venue = create_venue(offerer)
#     product = create_product_with_thing_type()
#     PcObject.save(venue, product)
#
#     chunk_size = 1000
#
#     for index in range(chunk_size):
#         offer = create_offer_with_thing_product(venue,
#                                                 product=product,
#                                                 id_at_providers=f'{index}|{venue.siret}')
#         chunk_to_insert[f'{index}|Offer'] = offer
#         db.session.expunge(offer)
#
#     # When
#     start_time = time.time()
#     insert_chunk(chunk_to_insert)
#     print(f"Total time {time.time() - start_time}")
#
#     # Then
#     assert Offer.query.count() == chunk_size

# @clean_database
# def test_update_chunk_perf(app):
#     # Given
#     chunk_to_update = {}
#     created_offers = []
#
#     offerer = create_offerer()
#     venue = create_venue(offerer)
#
#     chunk_size = 10
#
#     for index in range(1, chunk_size):
#         offer = create_offer_with_thing_product(venue)
#         offer.isDuo = False
#         PcObject.save(offer)
#         created_offers.append(offer)
#         offer.isDuo = True
#         chunk_to_update[f'{index}|Offer'] = offer
#
#     # When
#     update_chunk(chunk_to_update, None)
#
#     # Then
#     assert any(offer.isDuo for offer in Offer.query.all())
#
#
#
#
# def test_sort_chunk_keys():
#     # Given
#     chunk_to_update = {
#         '1 | Offer': {
#             'id': 1
#         },
#         '1 | Stock': {
#             'id': 2
#         },
#         '2 | Stock': {
#             'id': 3
#         },
#         '3 | Offer': {
#             'id': 4
#         },
#     }
#
#     # When
#     custom_list = sorted(chunk_to_update.keys(), key=lambda i: i.split('|')[1])
#
#     # Then
#     assert custom_list[0] == '1 | Offer'
#     assert custom_list[1] == '3 | Offer'
#     assert custom_list[2] == '1 | Stock'
#     assert custom_list[3] == '2 | Stock'
