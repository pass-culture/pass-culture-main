from unittest.mock import patch

import pytest

from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.models.api_errors import OBJECT_NOT_FOUND_ERROR_MESSAGE


pytestmark = pytest.mark.usefixtures("db_session")


@pytest.mark.features(WIP_CLOSE_VENUE=False)
def test_close_venue_returns_404_when_feature_flag_is_disabled(client):
    user_offerer = offerers_factories.UserOffererFactory()
    venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
    client = client.with_session_auth(email=user_offerer.user.email)

    response = client.post(f"/venues/{venue.id}/close")
    assert response.status_code == 404


@pytest.mark.features(WIP_CLOSE_VENUE=True)
@patch("pcapi.core.offerers.api.close_venue")
def test_close_venue_returns_404_when_user_has_no_access(mock_close_venue, client):
    user_offerer = offerers_factories.UserOffererFactory()
    venue = offerers_factories.VenueFactory()
    client = client.with_session_auth(email=user_offerer.user.email)

    response = client.post(f"/venues/{venue.id}/close")

    assert response.status_code == 404
    assert response.json == {"global": [OBJECT_NOT_FOUND_ERROR_MESSAGE]}
    mock_close_venue.assert_not_called()


@pytest.mark.features(WIP_CLOSE_VENUE=True)
@patch("pcapi.core.search.async_index_venue_ids")
@patch("pcapi.core.offerers.tasks.deactivate_venue_offers_task.delay")
def test_close_venue_closes_venue(mock_deactivate_venue_offers, mock_index_venue, client):
    user_offerer = offerers_factories.UserOffererFactory()
    venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
    client = client.with_session_auth(email=user_offerer.user.email)

    response = client.post(f"/venues/{venue.id}/close")

    assert response.status_code == 204
    assert venue.state == offerers_models.VenueState.CLOSING
