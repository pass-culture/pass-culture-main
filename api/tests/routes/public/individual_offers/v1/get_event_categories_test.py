import pytest

from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.offerers import factories as offerers_factories

from . import utils


pytestmark = pytest.mark.usefixtures("db_session")


def test_returns_all_categories(client):
    utils.create_offerer_provider_linked_to_venue()

    response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
        "/public/offers/v1/events/categories"
    )

    assert response.status_code == 200
    assert set(subcategory["id"] for subcategory in response.json) == set(subcategories.EVENT_SUBCATEGORIES)


def test_category_serialization(client):
    utils.create_offerer_provider_linked_to_venue()

    response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
        "/public/offers/v1/events/categories"
    )

    assert response.status_code == 200
    assert all({"id", "conditionalFields"} == set(category_response.keys()) for category_response in response.json)

    concert_response = next(subcategory for subcategory in response.json if subcategory["id"] == "CONCERT")
    assert concert_response["conditionalFields"] == {
        "author": False,
        "musicSubType": True,
        "musicType": True,
        "performer": False,
    }
