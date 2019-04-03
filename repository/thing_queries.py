from models import ThingType, Product


def find_by_id(id):
    return Product.query.get(id)


def find_thing_by_isbn_only_for_type_book(isbn):
    thing = Product.query.filter((Product.type == str(ThingType.LIVRE_EDITION)) &
                               (Product.idAtProviders == isbn)) \
                               .one_or_none()
    return thing
