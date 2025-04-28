import datetime
import time

import sqlalchemy as sa
from sqlalchemy.orm import contains_eager
from sqlalchemy.orm import load_only

from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import PriceCategory
from pcapi.core.offers.models import Stock
from pcapi.models import db
from pcapi.repository import transaction


# Les price categories des offres allocine qui ont été migrées de VO/VF ne pointent pas vers la bonne offre
# Actuellement :
# PriceCategory -----------> Film VO/VF offer (inactif)
#   ^
#   \- Stock VO, Stock VF --> Film offer

# Voulu :
# PriceCategory ------------\   Film VO/VF offer (inactif)
#   ^                        v
#   \- Stock VO, Stock VF -- Film offer


def re_attach_price_categories_to_new_allocine_offers(dry_run: bool = True) -> None:
    before = time.time()

    stocks = (
        db.session.query(Stock)
        .join(Stock.priceCategory)
        .join(PriceCategory.offer)
        .filter(
            Stock.id > 100_000_000,  # I roughly estimated that no stocks are relevant before that id
            Stock.lastProviderId == 22,
            Stock.beginningDatetime > datetime.datetime.utcnow(),
            Offer.isActive.is_(False),
            sa.or_(Offer.name.endswith(" - VO"), Offer.name.endswith(" - VF")),
        )
        .options(load_only(Stock.offerId))
        .options(contains_eager(Stock.priceCategory))
        .all()
    )
    print(f"query executed in {time.time() - before:.2f}s")

    before_update = time.time()
    n_stocks = 0
    updated = 0

    with transaction():
        for stock in stocks:
            n_stocks += 1
            price_category = stock.priceCategory
            print(f"{price_category.id = }")
            if price_category.offerId != stock.offerId:
                updated += 1
                if not dry_run:
                    price_category.offerId = stock.offerId

    print(f"{n_stocks} stocks found")
    print(f"{updated} price categories updated")
    print(f"Update executed in {time.time() - before_update:.2f}s")
    print(f"Total time {time.time() - before:.2f}s")
