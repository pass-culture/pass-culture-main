from sqlalchemy.orm.attributes import flag_modified

from models import Product, PcObject


def add_isbn_in_product_extra_data():
    page = 0
    has_more_result = True

    query = Product.query \
        .filter(Product.idAtProviders != None) \
        .filter(Product.lastProviderId != None) \
        .filter(Product.extraData['isbn'] == None) \
        .order_by(Product.id.desc())

    while has_more_result:
        products = query.paginate(page, per_page=1000, error_out=False).items
        page += 1
        if len(products) == 0:
            has_more_result = False

        for product in products:
            product.extraData['isbn'] = product.idAtProviders
            flag_modified(product, 'extraData')

        print("Updating %s000 products" % page)
        PcObject.save(*products)
