import pytest

from pcapi.core.products import factories as products_factories
from pcapi.core.products import models as products_models
from pcapi.models import db
from pcapi.utils import human_ids


pytestmark = pytest.mark.usefixtures("db_session")


class ProductModelTest:
    def test_thumb_url(self):
        product = products_factories.ProductFactory(thumbCount=1)
        human_id = human_ids.humanize(product.id)
        assert product.thumbUrl == f"http://localhost/storage/thumbs/products/{human_id}"

    def test_no_thumb_url(self):
        product = products_models.Product(thumbCount=0)
        assert product.thumbUrl is None

    @pytest.mark.parametrize(
        "gcu_compatible, can_be_synchronized, product_count",
        [
            (products_models.GcuCompatibilityType.COMPATIBLE, True, 1),
            (products_models.GcuCompatibilityType.PROVIDER_INCOMPATIBLE, False, 0),
            (products_models.GcuCompatibilityType.FRAUD_INCOMPATIBLE, False, 0),
        ],
    )
    def test_gcu_compatible(self, gcu_compatible, can_be_synchronized, product_count):
        product = products_factories.ProductFactory(gcuCompatibilityType=gcu_compatible)

        assert product.can_be_synchronized == can_be_synchronized
        assert (
            db.session.query(products_models.Product).filter(products_models.Product.can_be_synchronized).count()
            == product_count
        )
