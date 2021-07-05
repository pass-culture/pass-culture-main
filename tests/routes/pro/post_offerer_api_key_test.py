import pytest

from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.offerers.api import find_api_key
from pcapi.core.offerers.factories import ApiKeyFactory
from pcapi.core.offerers.models import ApiKey
from pcapi.core.offers.factories import UserOffererFactory
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


@pytest.mark.usefixtures("db_session")
def test_api_key_journey(client):
    booking = BookingFactory()
    user_offerer = UserOffererFactory(offerer=booking.stock.offer.venue.managingOfferer)

    response = (
        TestClient(client)
        .with_auth(user_offerer.user.email)
        .post(f"/offerers/{humanize(user_offerer.offerer.id)}/api_keys")
    )

    assert response.status_code == 200

    saved_key = find_api_key(response.json["apiKey"])
    assert saved_key.offererId == user_offerer.offerer.id

    # test generated api key grants authentication on bookings API
    response = TestClient(client).get(
        f"/v2/bookings/token/{booking.token.lower()}",
        headers={"Authorization": f"""Bearer {response.json["apiKey"]}"""},
    )
    assert response.status_code == 200

    # test user can delete the generated api key
    response = TestClient(client).with_auth(user_offerer.user.email).delete(f"/offerers/api_keys/{saved_key.prefix}")
    assert response.status_code == 204
    assert ApiKey.query.count() == 0


@pytest.mark.usefixtures("db_session")
def test_maximal_api_key_reached(client):
    booking = BookingFactory()
    user_offerer = UserOffererFactory(offerer=booking.stock.offer.venue.managingOfferer)
    for i in range(5):
        ApiKeyFactory(prefix=f"prefix_{i}", offerer=user_offerer.offerer)

    response = (
        TestClient(client)
        .with_auth(user_offerer.user.email)
        .post(f"/offerers/{humanize(user_offerer.offerer.id)}/api_keys")
    )

    assert response.status_code == 400
    assert response.json["api_key_count_max"] == "Le nombre de clés maximal a été atteint"
    assert ApiKey.query.count() == 5


@pytest.mark.usefixtures("db_session")
def test_delete_api_key_not_found(client):
    user_offerer = UserOffererFactory()

    response = TestClient(client).with_auth(user_offerer.user.email).delete("/offerers/api_keys/wrong-prefix")

    assert response.status_code == 404


@pytest.mark.usefixtures("db_session")
def test_delete_api_key_not_allowed(client):
    user_offerer = UserOffererFactory()
    api_key = ApiKeyFactory()

    response = TestClient(client).with_auth(user_offerer.user.email).delete(f"/offerers/api_keys/{api_key.prefix}")

    assert response.status_code == 403
