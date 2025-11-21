import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.users.factories as users_factories
from pcapi.core import testing
from pcapi.models import db


pytestmark = pytest.mark.usefixtures("db_session")


def test_loads_all_venues_ids_and_names(client):
    user_offerer = offerers_factories.UserOffererFactory()
    venues = offerers_factories.VenueFactory.create_batch(2, managingOfferer=user_offerer.offerer)

    client = client.with_session_auth(user_offerer.user.email)

    num_queries = testing.AUTHENTICATION_QUERIES
    num_queries += 1  # select venues
    with testing.assert_num_queries(num_queries):
        response = client.get("/lite/venues")
        assert response.status_code == 200

    assert "venues" in response.json
    assert len(response.json["venues"]) == len(venues)

    expected = [{"id": v.id, "name": v.name} for v in venues]
    expected = sorted(expected, key=lambda item: item["id"])

    assert expected == sorted(response.json["venues"], key=lambda item: item["id"])


def test_invalid_offerer_id(client):
    pro_user = users_factories.ProFactory()
    offerer = offerers_factories.OffererFactory()
    offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
    offerers_factories.VenueFactory(managingOfferer=offerer)

    params = {"offererId": f"{offerer.id + 1}"}

    client = client.with_session_auth(pro_user.email)
    num_queries = testing.AUTHENTICATION_QUERIES
    num_queries += 1  # select venues
    with testing.assert_num_queries(num_queries):
        response = client.get("/lite/venues", params)
        assert response.status_code == 200

    assert "venues" in response.json
    assert len(response.json["venues"]) == 0


def test_invalid_validated(client):
    pro_user = users_factories.ProFactory()

    params = {"validated": "invalid"}

    client = client.with_session_auth(pro_user.email)
    with testing.assert_num_queries(testing.AUTHENTICATION_QUERIES):
        response = client.get("/lite/venues", params)
        assert response.status_code == 400


def test_invalid_active_offerer_only(client):
    pro_user = users_factories.ProFactory()

    params = {"activeOfferersOnly": "invalid"}

    client = client.with_session_auth(pro_user.email)
    with testing.assert_num_queries(testing.AUTHENTICATION_QUERIES):
        response = client.get("/lite/venues", params)
        assert response.status_code == 400


def test_only_return_non_softdeleted_venues(client):
    pro_user = users_factories.ProFactory()
    offerer = offerers_factories.OffererFactory()
    offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
    offerers_factories.VenueFactory(managingOfferer=offerer)
    soft_deleted_venue = offerers_factories.VenueFactory(managingOfferer=offerer)
    # We can't set the isSoftDeleted within the factories. It will crash due to the venue
    # not being found.
    soft_deleted_venue.isSoftDeleted = True
    db.session.add(soft_deleted_venue)
    db.session.flush()

    client = client.with_session_auth(pro_user.email)
    num_queries = testing.AUTHENTICATION_QUERIES
    num_queries += 1  # select venues
    with testing.assert_num_queries(num_queries):
        response = client.get("/lite/venues")
        assert response.status_code == 200

    assert "venues" in response.json
    assert len(response.json["venues"]) == 1
