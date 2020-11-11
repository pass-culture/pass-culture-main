from pcapi.models import Product
from pcapi.repository import repository


def reset_thumb_count(page_size: int = 1000):
    are_products_to_check = True
    page_index = 1

    while are_products_to_check:
        products = Product.query.filter(Product.thumbCount > 0).limit(page_size).all()
        for product in products:
            product.thumbCount = 0
        repository.save(*products)
        print(f"Page: {page_index}")
        page_index += 1

        if len(products) < page_size:
            are_products_to_check = False
