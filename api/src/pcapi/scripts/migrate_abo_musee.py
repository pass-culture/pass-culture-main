from pcapi.core import search
from pcapi.core.categories.subcategories_v2 import ABO_MUSEE
from pcapi.core.categories.subcategories_v2 import CARTE_MUSEE
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Product
from pcapi.models import db
from pcapi.settings import IS_PROD

def migrate_product_categorie(dry_run: bool=True):
    products = Product.query.filter(Product.subcategoryId == ABO_MUSEE.id)
    for product in products:
        product.subcategoryId = CARTE_MUSEE.id
    if not dry_run:
        db.session.commit()
    else:
        db.session.rollback()

def migrate_offer_categorie(dry_run: bool=True):
    offers = Offer.query.filter(Offer.subcategoryId == ABO_MUSEE.id)
    for offer in offers:
        offer.subcategoryId = CARTE_MUSEE.id
        if IS_PROD and not dry_run:
            search.reindex_offer_ids([offer.id])
    if not dry_run:
        db.session.commit()
    else:
        db.session.rollback()