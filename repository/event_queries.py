from models import Product


def find_by_id(product_id: str) -> Product:
    return Product.query.filter_by(id=product_id).one()
