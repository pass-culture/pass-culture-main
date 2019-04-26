from models import Product


# TODO Merge event_queries and thing_queries into a single repositories
def find_by_id(product_id: str) -> Product:
    return Product.query.filter_by(id=product_id).one()
