from models import Product, Offer
from models.db import db
from repository.providable_queries import _dict_to_object
from scripts.performance_toolkit import bulk_update_pc_objects

CHUNK_SIZE = 500


def add_isbn_in_product_and_offer_extra_data():
    product_index = 0
    nb_products_updated = 0

    connection = db.engine.connect()
    number_of_products_in_base = connection.execute("""
        SELECT MAX(id)
        FROM product;
    """).scalar()
    print("%s products to check in base" % number_of_products_in_base)

    while product_index <= number_of_products_in_base:
        next_product_index = product_index + CHUNK_SIZE
        products = connection.execute("""
            SELECT *
            FROM product
            WHERE id > """ + str(product_index) + """
            AND id <= """ + str(next_product_index) + """
            AND type = 'ThingType.LIVRE_EDITION'
            AND "idAtProviders" IS NOT NULL
            AND "extraData" IS NOT NULL
            AND (LENGTH("extraData"::JSONB ->> 'isbn') < 10
                OR "extraData"::JSONB ->> 'isbn' IS NULL)
            ORDER BY id ASC;
        """).fetchall()

        products_to_update = []

        for product in products:
            product_to_update = _dict_to_object(product, Product)
            product_to_update.extraData['isbn'] = product_to_update.idAtProviders
            products_to_update.append(product_to_update)

        bulk_update_pc_objects(products_to_update, Product)
        nb_products_updated += len(products_to_update)

        product_index += CHUNK_SIZE
        percentage_done = 100 * (min(product_index, number_of_products_in_base) / number_of_products_in_base)
        print("%s percent checked" % percentage_done)
    print(f"{nb_products_updated} products have been updated")

    offer_index = 0
    nb_offer_updated = 0
    number_of_offers_in_base = connection.execute("""
        SELECT MAX(id)
        FROM offer;
    """).scalar() or 0
    print("%s offer to check in base" % number_of_offers_in_base)

    while offer_index <= number_of_offers_in_base:
        next_offer_index = offer_index + CHUNK_SIZE
        offers = connection.execute("""
            SELECT *
            FROM offer
            WHERE id > """ + str(offer_index) + """
            AND id <= """ + str(next_offer_index) + """
            AND type = 'ThingType.LIVRE_EDITION' 
            AND "idAtProviders" IS NOT NULL
            AND "extraData" IS NOT NULL
            AND (LENGTH("extraData"::JSONB ->> 'isbn') < 10
                OR "extraData"::JSONB ->> 'isbn' IS NULL)
            ORDER BY id ASC;
        """).fetchall()

        offers_to_update = []

        for offer in offers:
            offer_to_update = _dict_to_object(offer, Offer)
            offer_to_update.extraData['isbn'] = _extract_isbn_from_offer_id_at_providers(offer_to_update.idAtProviders)
            offers_to_update.append(offer_to_update)

        bulk_update_pc_objects(offers_to_update, Offer)
        nb_offer_updated += len(offers_to_update)

        offer_index += CHUNK_SIZE
        if number_of_offers_in_base > 0:
            percentage_done = 100 * (min(offer_index, number_of_offers_in_base) / number_of_offers_in_base)
            print("%s percent checked" % percentage_done)
    print(f"{nb_offer_updated} offers have been updated")


def _extract_isbn_from_offer_id_at_providers(id_at_providers: str) -> str:
    return id_at_providers.split('@')[0]
