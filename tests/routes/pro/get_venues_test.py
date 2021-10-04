from unittest.mock import patch

import pytest

import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


@pytest.mark.usefixtures("db_session")
def test_response_serialization(app):
    user_offerer = offers_factories.UserOffererFactory(
        user__email="user.pro@test.com",
    )
    venue = offers_factories.VenueFactory(managingOfferer=user_offerer.offerer)

    # when
    response = TestClient(app.test_client()).with_session_auth(user_offerer.user.email).get("/venues")

    # then
    assert response.status_code == 200

    assert "venues" in response.json
    assert len(response.json["venues"]) == 1
    assert response.json["venues"][0] == {
        "id": humanize(venue.id),
        "managingOffererId": humanize(venue.managingOffererId),
        "name": venue.name,
        "offererName": user_offerer.offerer.name,
        "publicName": venue.publicName,
        "isVirtual": venue.isVirtual,
        "bookingEmail": venue.bookingEmail,
        "withdrawalDetails": venue.withdrawalDetails,
        "audioDisabilityCompliant": venue.audioDisabilityCompliant,
        "mentalDisabilityCompliant": venue.mentalDisabilityCompliant,
        "motorDisabilityCompliant": venue.motorDisabilityCompliant,
        "visualDisabilityCompliant": venue.visualDisabilityCompliant,
    }


@pytest.mark.usefixtures("db_session")
@patch("pcapi.core.offerers.repository.get_filtered_venues")
def test_default_call(mock_get_filtered_venues, app):
    user_offerer = offers_factories.UserOffererFactory(
        user__email="user.pro@test.com",
    )
    offers_factories.VenueFactory(managingOfferer=user_offerer.offerer)

    # when
    response = TestClient(app.test_client()).with_session_auth(user_offerer.user.email).get("/venues")

    # then
    assert response.status_code == 200
    mock_get_filtered_venues.assert_called_once_with(
        active_offerers_only=None,
        offerer_id=None,
        pro_user_id=user_offerer.user.id,
        user_is_admin=False,
        validated_offerer=None,
        validated_offerer_for_user=None,
    )


@pytest.mark.usefixtures("db_session")
@patch("pcapi.core.offerers.repository.get_filtered_venues")
def test_default_admin_call(mock_get_filtered_venues, app):
    admin_user = users_factories.AdminFactory(email="admin.pro@test.com")

    # when
    response = TestClient(app.test_client()).with_session_auth(admin_user.email).get("/venues")

    # then
    assert response.status_code == 200
    mock_get_filtered_venues.assert_called_once_with(
        active_offerers_only=None,
        offerer_id=None,
        pro_user_id=admin_user.id,
        user_is_admin=True,
        validated_offerer=None,
        validated_offerer_for_user=None,
    )


@pytest.mark.usefixtures("db_session")
@patch("pcapi.core.offerers.repository.get_filtered_venues")
def test_invalid_offerer_id(mock_get_filtered_venues, app):
    pro_user = users_factories.ProFactory(email="user.pro@test.com")
    offerer = offers_factories.OffererFactory()
    offers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
    offers_factories.VenueFactory(managingOfferer=offerer)

    query_params = [
        f"offererId={humanize(666)}",
    ]

    # when
    response = TestClient(app.test_client()).with_session_auth(pro_user.email).get(f"/venues?{'&'.join(query_params)}")

    # then
    # then
    assert response.status_code == 200
    mock_get_filtered_venues.assert_called_once_with(
        active_offerers_only=None,
        offerer_id=666,
        pro_user_id=pro_user.id,
        user_is_admin=False,
        validated_offerer=None,
        validated_offerer_for_user=None,
    )

    assert "venues" in response.json
    assert len(response.json["venues"]) == 0


@pytest.mark.usefixtures("db_session")
@patch("pcapi.core.offerers.repository.get_filtered_venues")
def test_full_valid_call(mock_get_filtered_venues, app):
    pro_user = users_factories.ProFactory(email="user.pro@test.com")
    offerer = offers_factories.OffererFactory()
    offers_factories.UserOffererFactory(user=pro_user, offerer=offerer)

    query_params = [
        "validated=true",
        "validatedForUser=true",
        f"offererId={humanize(offerer.id)}",
        "activeOfferersOnly=true",
    ]

    # when
    response = TestClient(app.test_client()).with_session_auth(pro_user.email).get(f"/venues?{'&'.join(query_params)}")

    # then
    assert response.status_code == 200
    mock_get_filtered_venues.assert_called_once_with(
        active_offerers_only=True,
        offerer_id=offerer.id,
        pro_user_id=pro_user.id,
        user_is_admin=False,
        validated_offerer=True,
        validated_offerer_for_user=True,
    )


@pytest.mark.usefixtures("db_session")
@patch("pcapi.core.offerers.repository.get_filtered_venues")
def test_full_valid_call_with_false(mock_get_filtered_venues, app):
    pro_user = users_factories.ProFactory(email="user.pro@test.com")
    offerer = offers_factories.OffererFactory()
    offers_factories.UserOffererFactory(user=pro_user, offerer=offerer)

    query_params = [
        "validated=false",
        "validatedForUser=false",
        f"offererId={humanize(offerer.id)}",
        "activeOfferersOnly=false",
    ]

    # when
    response = TestClient(app.test_client()).with_session_auth(pro_user.email).get(f"/venues?{'&'.join(query_params)}")

    # then
    assert response.status_code == 200
    mock_get_filtered_venues.assert_called_once_with(
        active_offerers_only=False,
        offerer_id=offerer.id,
        pro_user_id=pro_user.id,
        user_is_admin=False,
        validated_offerer=False,
        validated_offerer_for_user=False,
    )


@pytest.mark.usefixtures("db_session")
@patch("pcapi.core.offerers.repository.get_filtered_venues")
def test_invalid_validated(mock_get_filtered_venues, app):
    pro_user = users_factories.ProFactory(email="user.pro@test.com")

    query_params = [
        "validated=toto",
    ]

    # when
    response = TestClient(app.test_client()).with_session_auth(pro_user.email).get(f"/venues?{'&'.join(query_params)}")

    # then
    assert response.status_code == 400
    mock_get_filtered_venues.assert_not_called()


@pytest.mark.usefixtures("db_session")
@patch("pcapi.core.offerers.repository.get_filtered_venues")
def test_invalid_validated_for_user(mock_get_filtered_venues, app):
    pro_user = users_factories.ProFactory(email="user.pro@test.com")

    query_params = [
        "validatedForUser=43",
    ]

    # when
    response = TestClient(app.test_client()).with_session_auth(pro_user.email).get(f"/venues?{'&'.join(query_params)}")

    # then
    assert response.status_code == 400
    mock_get_filtered_venues.assert_not_called()


@pytest.mark.usefixtures("db_session")
@patch("pcapi.core.offerers.repository.get_filtered_venues")
def test_invalid_active_offerer_only(mock_get_filtered_venues, app):
    pro_user = users_factories.ProFactory(email="user.pro@test.com")

    query_params = [
        "activeOfferersOnly=tata",
    ]

    # when
    response = TestClient(app.test_client()).with_session_auth(pro_user.email).get(f"/venues?{'&'.join(query_params)}")

    # then
    assert response.status_code == 400
    mock_get_filtered_venues.assert_not_called()
