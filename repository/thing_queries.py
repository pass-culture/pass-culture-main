from models import ThingType, Product

# TODO Merge event_queries and thing_queries into a single repositories
def find_by_id(id) -> Product:
    return Product.query.get(id)


def find_thing_product_by_isbn_only_for_type_book(isbn) -> Product:
    product = Product.query.filter((Product.type == str(ThingType.LIVRE_EDITION)) &
                               (Product.idAtProviders == isbn)) \
                               .one_or_none()
    return product
