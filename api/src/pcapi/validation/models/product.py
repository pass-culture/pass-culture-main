from pcapi.core.offers.models import Product
from pcapi.models.api_errors import ApiErrors


def validate(product: Product, api_errors: ApiErrors) -> ApiErrors:
    if product.isDigital and product.is_offline_only:
        api_errors.add_error(
            "url",
            f"Un produit de sous-catégorie {product.subcategoryId} ne peut pas être numérique",
        )

    return api_errors
