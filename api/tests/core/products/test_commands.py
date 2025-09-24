import logging

import pytest

import pcapi.core.chronicles.factories as chronicles_factories
from pcapi.core.products import factories as products_factories
from pcapi.models import db

from tests.test_utils import run_command


class ProductCommandsTest:
    @pytest.mark.usefixtures("clean_database")
    def test_command_check_product_counts_consistency(self, app, caplog):
        product_1 = products_factories.ProductFactory()
        product_2 = products_factories.ProductFactory()
        chronicles_factories.ChronicleFactory.create(products=[product_1, product_2])

        product_1.chroniclesCount = 0
        product_2.chroniclesCount = 0
        product_1_id = product_1.id
        product_2_id = product_2.id
        db.session.commit()

        with caplog.at_level(logging.ERROR):
            run_command(app, "check_product_counts_consistency")

        assert caplog.records[0].extra["product_ids"] == {product_1_id, product_2_id}
