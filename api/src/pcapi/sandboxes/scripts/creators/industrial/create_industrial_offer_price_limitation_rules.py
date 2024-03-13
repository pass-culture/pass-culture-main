import decimal

from pcapi.core.categories import subcategories_v2
from pcapi.core.offers import factories as offers_factories


def create_industrial_offer_price_limitation_rules() -> None:
    offers_factories.OfferPriceLimitationRuleFactory(
        subcategoryId=subcategories_v2.ACHAT_INSTRUMENT.id, rate=decimal.Decimal(0.3)
    )
    offers_factories.OfferPriceLimitationRuleFactory(
        subcategoryId=subcategories_v2.LIVRE_PAPIER.id, rate=decimal.Decimal(0.15)
    )
    offers_factories.OfferPriceLimitationRuleFactory(
        subcategoryId=subcategories_v2.LIVRE_NUMERIQUE.id, rate=decimal.Decimal(0.1)
    )
