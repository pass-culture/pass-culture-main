from unittest import mock

import pytest

import pcapi.core.providers.constants as providers_constants
from pcapi.connectors.big_query.importer.base import DeltaAction
from pcapi.connectors.big_query.importer.product import ProductImporter
from pcapi.connectors.big_query.queries.product import ProductDeltaModel
from pcapi.core.categories import subcategories
from pcapi.core.offers.factories import ProductFactory
from pcapi.core.offers.models import GcuCompatibilityType
from pcapi.core.offers.models import OfferExtraData
from pcapi.core.offers.models import Product
from pcapi.core.providers.factories import ProviderFactory
from pcapi.models import db


pytestmark = pytest.mark.usefixtures("db_session")


class UpdateProductsFromDeltaTest:
    @mock.patch("pcapi.connectors.big_query.queries.product.ProductDeltaQuery.execute")
    def test_add_action_creates_new_product(self, mock_product_delta_query):
        ProviderFactory(name=providers_constants.TITELIVE_ENRICHED_BY_DATA, isActive=True)
        new_product_ean = "9782070612827"
        new_product_data = ProductDeltaModel(
            name="Le Seigneur des Anneaux",
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            ean=new_product_ean,
            action=DeltaAction.ADD,
        )
        mock_product_delta_query.return_value = [new_product_data]

        ProductImporter().run_delta_update()

        assert db.session.query(Product).count() == 1
        created_product = db.session.query(Product).filter_by(ean=new_product_ean).one()
        assert created_product is not None
        assert created_product.name == "Le Seigneur des Anneaux"
        assert created_product.ean == new_product_ean

    @mock.patch("pcapi.connectors.big_query.queries.product.ProductDeltaQuery.execute")
    def test_remove_action_soft_deletes_product(self, mock_product_delta_query):
        ProviderFactory(name=providers_constants.TITELIVE_ENRICHED_BY_DATA, isActive=True)
        product_to_remove = ProductFactory(ean="1111111111111", gcuCompatibilityType=GcuCompatibilityType.COMPATIBLE)
        product_to_keep = ProductFactory(ean="2222222222222", gcuCompatibilityType=GcuCompatibilityType.COMPATIBLE)
        remove_action_data = ProductDeltaModel(
            ean=product_to_remove.ean,
            name="Nom non pertinent",
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            action=DeltaAction.REMOVE,
        )
        mock_product_delta_query.return_value = [remove_action_data]

        ProductImporter().run_delta_update()

        assert db.session.query(Product).count() == 2
        assert product_to_remove.gcuCompatibilityType == GcuCompatibilityType.PROVIDER_INCOMPATIBLE
        assert product_to_keep.gcuCompatibilityType == GcuCompatibilityType.COMPATIBLE

    @mock.patch("pcapi.connectors.big_query.queries.product.ProductDeltaQuery.execute")
    def test_update_action_modifies_product_and_merges_extra_data(self, mock_product_delta_query):
        ProviderFactory(name=providers_constants.TITELIVE_ENRICHED_BY_DATA, isActive=True)
        initial_extra_data = {
            "author": "J.R.R. Tolkien",
            "collection": "Édition Collector",
        }
        product_to_update = ProductFactory(ean="3333333333333", name="Ancien Nom", extraData=initial_extra_data)
        update_extra_data: OfferExtraData = {
            "author": "John Ronald Reuel Tolkien",
            "comment": "Version illustrée",
        }
        update_action_data = ProductDeltaModel(
            ean=product_to_update.ean,
            name="Nouveau Nom",
            subcategoryId=product_to_update.subcategoryId,
            extraData=update_extra_data,
            action=DeltaAction.UPDATE,
        )
        mock_product_delta_query.return_value = [update_action_data]

        ProductImporter().run_delta_update()

        assert db.session.query(Product).count() == 1
        assert product_to_update.name == "Nouveau Nom"
        assert product_to_update.extraData is not None
        assert product_to_update.extraData["author"] == "John Ronald Reuel Tolkien"
        assert product_to_update.extraData["comment"] == "Version illustrée"
        assert product_to_update.extraData["collection"] == "Édition Collector"
        assert len(product_to_update.extraData) == 3
