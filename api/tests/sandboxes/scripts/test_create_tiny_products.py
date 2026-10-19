import pytest

from pcapi.core.categories import subcategories
from pcapi.core.offers import models as offers_models
from pcapi.models import db
from pcapi.routes.serialization.offers_serialize import GetProductInformations
from pcapi.sandboxes.scripts.creators.tiny.create_products import create_tiny_products


@pytest.mark.usefixtures("db_session")
def test_create_tiny_products():
    create_tiny_products()

    products = db.session.query(offers_models.Product).all()
    assert {product.ean: product.subcategoryId for product in products} == {
        "9780000000019": subcategories.LIVRE_PAPIER.id,
        "2000000000022": subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id,
        "2000000000039": subcategories.SUPPORT_PHYSIQUE_MUSIQUE_VINYLE.id,
    }
    for product in products:
        assert product.offers == []
        assert product.isGcuCompatible
        assert product.extraData
        assert product.extraData["gtl_id"]
        if product.subcategoryId == subcategories.LIVRE_PAPIER.id:
            assert product.extraData["author"]
        else:
            assert product.extraData["performer"]

        response = GetProductInformations.build(product)
        assert response.ean == product.ean
        assert response.gtl_id == product.extraData["gtl_id"]
        assert response.author == product.extraData.get("author", "")
        assert response.performer == product.extraData.get("performer", "")
