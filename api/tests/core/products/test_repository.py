from unittest.mock import patch

import pytest
import sqlalchemy.exc as sa_exc

from pcapi.core.products import factories as products_factories
from pcapi.core.products import repository as products_repository


@pytest.mark.usefixtures("db_session")
@patch(
    "pcapi.models.db.session.delete",
    side_effect=(sa_exc.IntegrityError(None, None, None), None),
)
def test_handles_offer_creation_while_product_merging(delete_mock):
    to_keep = products_factories.ProductFactory()
    to_delete = products_factories.ProductFactory()

    kept_product = products_repository.merge_products(to_keep, to_delete)

    assert delete_mock.call_count == 2
    assert kept_product == to_keep
