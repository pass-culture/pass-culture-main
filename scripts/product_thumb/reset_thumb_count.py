from models import Product, PcObject


def reset_thumb_count():
    are_products_to_check = True
    page_size = 1000
    page_index = 1

    while are_products_to_check:
        products = Product.query \
            .filter(Product.thumbCount > 0) \
            .paginate(page=page_index, per_page=page_size, error_out=False).items
        for product in products:
            product.thumbCount = 0
        PcObject.save(*products)
        page_index += 1
        print(f"Page: {page_index}")

        if len(products) < page_size:
            are_products_to_check = False
