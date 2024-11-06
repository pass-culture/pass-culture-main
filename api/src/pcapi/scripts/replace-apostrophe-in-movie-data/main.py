from pcapi.app import app
from pcapi.core.categories import subcategories_v2
from pcapi.core.offers.models import Product
from pcapi.repository import db


with app.app_context():
    products = Product.query.filter(Product.subcategoryId == subcategories_v2.SEANCE_CINE.id)
    for product in products:
        if product.description:
            product.description = product.description.replace("&#039;", "\u2019")

        if product.extraData.get("synopsis"):
            product.extraData["synopsis"] = product.extraData["synopsis"].replace("&#039;", "\u2019")

        db.session.add(product)

    db.session.commit()
