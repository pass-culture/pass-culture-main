from models import Product
from models.db import db

CHUNK_SIZE = 500


def add_isbn_in_product_extra_data():
    product_index = 0

    connection = db.engine.connect()
    number_of_products_in_base = connection.execute("""
        SELECT MAX(id)
        FROM product;
    """).scalar()
    print("%s products to check in base" % number_of_products_in_base)

    while product_index <= number_of_products_in_base:
        next_product_index = product_index + CHUNK_SIZE
        products_to_update = connection.execute("""
            SELECT *
            FROM product
            WHERE id > """ + str(product_index) + """
            AND id <= """ + str(next_product_index) + """
            AND type = 'ThingType.LIVRE_EDITION' 
            AND "idAtProviders" IS NOT NULL
            AND "extraData" IS NOT NULL
            AND "extraData"::jsonb ->> 'isbn' IS NULL
            ORDER BY id ASC;
        """).fetchall()

        for product_to_update in products_to_update:
            product_to_update['extraData']['isbn'] = product_to_update['idAtProviders']
            try:
                connection = db.engine.connect()
                statement = Product.__table__.update(). \
                    where(Product.id == product_to_update['id']). \
                    values(product_to_update)
                connection.execute(statement)
            except ValueError as e:
                print('ERROR during object update: '
                      + e.__class__.__name__ + ' ' + str(e))

        product_index += CHUNK_SIZE
        percentage_done = 100 * (min(product_index, number_of_products_in_base) / number_of_products_in_base)
        print("%s percent checked" % percentage_done)
    print("All products have been updated")
