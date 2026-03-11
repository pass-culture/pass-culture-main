import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.users.factories as users_factories
from pcapi.core import testing
from pcapi.models import db


pytestmark = pytest.mark.usefixtures("db_session")


def test_loads_all_venues_ids_and_names(client):
    user_offerer = offerers_factories.UserOffererFactory()
    # Reverse-ordered to test sorting behavior
    second_venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer, publicName="Def")
    first_venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer, publicName="Abc")
    venues = [first_venue, second_venue]

    pending_offerer = offerers_factories.PendingUserOffererFactory(user=user_offerer.user).offerer
    with_pending_validation = offerers_factories.VenueFactory(managingOfferer=pending_offerer)

    client = client.with_session_auth(user_offerer.user.email)

    num_queries = testing.AUTHENTICATION_QUERIES
    num_queries += 1  # select user_offerers
    num_queries += 1  # select related offerers
    num_queries += 1  # select related managed venues
    with testing.assert_num_queries(num_queries):
        response = client.get("/lite/venues")
        assert response.status_code == 200

    assert "venues" in response.json
    assert len(response.json["venues"]) == len(venues)

    expected = [
        {
            "id": venue.id,
            "managingOffererId": venue.managingOffererId,
            "publicName": venue.publicName,
            "location": {
                "banId": "75102_7560_00001",
                "city": "Paris",
                "departmentCode": "75",
                "id": venue.offererAddress.addressId,
                "inseeCode": "75102",
                "isManualEdition": False,
                "isVenueLocation": True,
                "label": venue.publicName,
                "latitude": 48.87055,
                "longitude": 2.34765,
                "postalCode": "75002",
                "street": venue.offererAddress.address.street,
            },
        }
        for venue in sorted(venues, key=lambda v: v.id)
    ]

    assert sorted(response.json["venues"], key=lambda v: v["id"]) == expected
    assert response.json["venuesWithPendingValidation"] == [
        {
            "id": with_pending_validation.id,
            "managingOffererId": with_pending_validation.managingOffererId,
            "publicName": with_pending_validation.publicName,
            "location": {
                "banId": "75102_7560_00001",
                "city": "Paris",
                "departmentCode": "75",
                "id": with_pending_validation.offererAddress.addressId,
                "inseeCode": "75102",
                "isManualEdition": False,
                "isVenueLocation": True,
                "label": with_pending_validation.publicName,
                "latitude": 48.87055,
                "longitude": 2.34765,
                "postalCode": "75002",
                "street": with_pending_validation.offererAddress.address.street,
            },
        }
    ]


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
    num_queries += 1  # select user_offerers
    num_queries += 1  # select related offerers
    num_queries += 1  # select related managed venues
    with testing.assert_num_queries(num_queries):
        response = client.get("/lite/venues")
        assert response.status_code == 200

    assert "venues" in response.json
    assert len(response.json["venues"]) == 1
    assert not response.json["venuesWithPendingValidation"]
