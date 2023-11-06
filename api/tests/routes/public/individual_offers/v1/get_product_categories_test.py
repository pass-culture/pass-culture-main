import pytest

from pcapi.core.offerers import factories as offerers_factories
from pcapi.routes.public.individual_offers.v1.serialization import ALLOWED_PRODUCT_SUBCATEGORIES

from . import utils


pytestmark = pytest.mark.usefixtures("db_session")


def test_returns_all_selectable_categories(client):
    utils.create_offerer_provider_linked_to_venue()

    response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
        "/public/offers/v1/products/categories"
    )

    assert response.status_code == 200
    assert set(subcategory["id"] for subcategory in response.json) == set(
        subcategory.id for subcategory in ALLOWED_PRODUCT_SUBCATEGORIES
    )


def test_category_serialization(client):
    utils.create_offerer_provider_linked_to_venue()

    response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
        "/public/offers/v1/products/categories"
    )

    assert response.status_code == 200
    assert all({"id", "conditionalFields"} == set(category_response.keys()) for category_response in response.json)

    concert_response = next(subcategory for subcategory in response.json if subcategory["id"] == "SPECTACLE_ENREGISTRE")
    assert concert_response["conditionalFields"] == {
        "author": False,
        "showSubType": True,
        "showType": True,
        "stageDirector": False,
        "performer": False,
    }
