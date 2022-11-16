from datetime import datetime
import random
import string
from typing import Iterable

from pcapi.core.categories import subcategories
from pcapi.core.offerers.models import Offerer
from pcapi.core.offers.models import Product


def create_product_with_thing_subcategory(
    thing_name: str = "Test Book",
    thing_subcategory_id: str = subcategories.LIVRE_PAPIER.id,
    author_name: str = "Test Author",
    is_national: bool = False,
    id_at_providers: str = None,
    idx: int = None,
    is_digital: bool = False,
    is_gcu_compatible: bool = True,
    is_synchronization_compatible: bool = True,
    is_offline_only: bool = False,
    date_modified_at_last_provider: datetime = None,
    last_provider_id: int = None,
    media_urls: Iterable[str] = ("test/urls",),
    description: str = None,
    thumb_count: int = 1,
    url: str = None,
    owning_offerer: Offerer = None,
    extra_data: dict = None,
) -> Product:
    product = Product()
    product.id = idx  # type: ignore [assignment]
    product.subcategoryId = thing_subcategory_id
    product.name = thing_name
    product.description = description
    if extra_data:
        product.extraData = extra_data
    else:
        product.extraData = {"author": author_name}
    product.isNational = is_national
    if id_at_providers is None:
        id_at_providers = "".join(random.choices(string.digits, k=13))
    product.dateModifiedAtLastProvider = date_modified_at_last_provider
    product.lastProviderId = last_provider_id
    product.idAtProviders = id_at_providers
    product.isGcuCompatible = is_gcu_compatible
    product.isSynchronizationCompatible = is_synchronization_compatible
    product.mediaUrls = media_urls  # type: ignore [call-overload]
    product.thumbCount = thumb_count
    product.url = url
    product.owningOfferer = owning_offerer  # type: ignore [assignment]
    product.description = description
    if is_digital:
        product.url = "fake/url"
    if is_offline_only:
        product.subcategoryId = subcategories.CARTE_CINE_MULTISEANCES.id
    return product
