import logging

import pytest

import pcapi.core.offerers.models as offerers_models
import pcapi.core.users.factories as users_factories


pytestmark = pytest.mark.usefixtures("db_session")


def test_wip_route(client, caplog):
    user = users_factories.UserFactory()

    body = {
        "name": "Pass Culture",
        "siret": "85331845900031",
        "target": "INDIVIDUAL",
        "venueType": offerers_models.VenueTypeCode.MOVIE.value,
        "webPresence": "www.example.com, instagram.com/example, @example@mastodon.example",
    }

    client = client.with_session_auth(user.email)
    with caplog.at_level(logging.INFO):
        response = client.post("/offerers/new", json=body)

    # then
    assert response.status_code == 204
    assert caplog.records[0].message == "WIP - offerer_creation_info"
    assert caplog.records[0].extra == {
        "address": "3 RUE DE VALOIS",
        "city": "Paris",
        "latitude": 2.308289,
        "longitude": 48.87171,
        "postalCode": "75001",
        "siren": "853318459",
        "target": offerers_models.Target.INDIVIDUAL,
        "venueType": "Cinéma - Salle de projections",
        "webPresence": "www.example.com, instagram.com/example, @example@mastodon.example",
        "offerer_name": "MINISTERE DE LA CULTURE",
    }
