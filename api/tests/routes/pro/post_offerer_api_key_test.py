import pytest

from pcapi.core.bookings import factories as booking_factories
from pcapi.core.offerers.api import find_api_key
from pcapi.core.offerers.factories import ApiKeyFactory
from pcapi.core.offerers.models import ApiKey
from pcapi.core.offers.factories import UserOffererFactory
from pcapi.utils.human_ids import humanize


@pytest.mark.usefixtures("db_session")
def test_api_key_journey(client):
    booking = booking_factories.IndividualBookingFactory()
    user_offerer = UserOffererFactory(offerer=booking.offerer)
    client.with_session_auth(user_offerer.user.email)

    response = client.post(f"/offerers/{humanize(user_offerer.offerer.id)}/api_keys")

    assert response.status_code == 200

    saved_key = find_api_key(response.json["apiKey"])
    assert saved_key.offererId == user_offerer.offerer.id

    # test generated api key grants authentication on bookings API
    response = client.get(
        f"/v2/bookings/token/{booking.token.lower()}",
        headers={"Authorization": f"""Bearer {response.json["apiKey"]}"""},
    )
    assert response.status_code == 200

    # test user can delete the generated api key
    response = client.delete(f"/offerers/api_keys/{saved_key.prefix}")
    assert response.status_code == 204
    assert ApiKey.query.count() == 0


@pytest.mark.usefixtures("db_session")
def test_maximal_api_key_reached(client):
    user_offerer = UserOffererFactory()
    for i in range(5):
        ApiKeyFactory(prefix=f"prefix_{i}", offerer=user_offerer.offerer)

    client.with_session_auth(user_offerer.user.email)
    response = client.post(f"/offerers/{humanize(user_offerer.offerer.id)}/api_keys")

    assert response.status_code == 400
    assert response.json["api_key_count_max"] == "Le nombre de clés maximal a été atteint"
    assert ApiKey.query.count() == 5


@pytest.mark.usefixtures("db_session")
def test_delete_api_key_not_found(client):
    user_offerer = UserOffererFactory()

    client.with_session_auth(user_offerer.user.email)
    response = client.delete("/offerers/api_keys/wrong-prefix")

    assert response.status_code == 404


@pytest.mark.usefixtures("db_session")
def test_delete_api_key_not_allowed(client):
    user_offerer = UserOffererFactory()
    api_key = ApiKeyFactory()

    client.with_session_auth(user_offerer.user.email)
    response = client.delete(f"/offerers/api_keys/{api_key.prefix}")

    assert response.status_code == 403
