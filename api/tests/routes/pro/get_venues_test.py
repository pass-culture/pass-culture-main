import pytest

from pcapi.core.educational.factories import CollectiveOfferFactory
from pcapi.core.educational.factories import CollectiveOfferTemplateFactory
from pcapi.core.finance.factories import BankInformationFactory
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offers.factories import OfferFactory
from pcapi.core.testing import assert_no_duplicated_queries
import pcapi.core.users.factories as users_factories
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


@pytest.mark.usefixtures("db_session")
def test_response_serialization(app):
    user_offerer = offerers_factories.UserOffererFactory(
        user__email="user.pro@test.com",
    )
    venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)

    # when
    response = TestClient(app.test_client()).with_session_auth(user_offerer.user.email).get("/venues")

    # then
    assert response.status_code == 200

    assert "venues" in response.json
    assert len(response.json["venues"]) == 1

    assert response.json["venues"][0] == {
        "id": humanize(venue.id),
        "nonHumanizedId": venue.id,
        "managingOffererId": humanize(venue.managingOffererId),
        "collectiveSubCategoryId": venue.collectiveSubCategoryId,
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
        "siret": venue.siret,
        "hasMissingReimbursementPoint": True,
        "hasCreatedOffer": False,
    }


@pytest.mark.usefixtures("db_session")
def test_response_missing_reimbursement_point_serialization(app):
    user_offerer = offerers_factories.UserOffererFactory(
        user__email="user.pro@test.com",
    )

    offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer, reimbursement_point=None, name="A")
    venue_with_pending_application = offerers_factories.VenueFactory(
        managingOfferer=user_offerer.offerer, reimbursement_point=None, name="B"
    )
    BankInformationFactory(venue=venue_with_pending_application, applicationId=4, status="DRAFT")
    offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer, reimbursement_point="self", name="C")

    # when
    response = TestClient(app.test_client()).with_session_auth(user_offerer.user.email).get("/venues")

    # then
    assert response.status_code == 200

    assert "venues" in response.json
    assert len(response.json["venues"]) == 3

    assert response.json["venues"][0]["hasMissingReimbursementPoint"] == True
    assert response.json["venues"][1]["hasMissingReimbursementPoint"] == False
    assert response.json["venues"][2]["hasMissingReimbursementPoint"] == False


@pytest.mark.usefixtures("db_session")
def test_response_created_offer_serialization(app):
    user_offerer = offerers_factories.UserOffererFactory(
        user__email="user.pro@test.com",
    )

    venue_with_offer = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
    OfferFactory(venue=venue_with_offer)

    venue_with_collective_offer = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
    CollectiveOfferFactory(venue=venue_with_collective_offer)

    venue_with_collective_offer_template = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
    CollectiveOfferTemplateFactory(venue=venue_with_collective_offer_template)

    offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)

    # when
    response = TestClient(app.test_client()).with_session_auth(user_offerer.user.email).get("/venues")

    # then
    assert response.status_code == 200

    assert "venues" in response.json
    assert len(response.json["venues"]) == 4

    assert response.json["venues"][0]["hasCreatedOffer"] == True
    assert response.json["venues"][1]["hasCreatedOffer"] == True
    assert response.json["venues"][2]["hasCreatedOffer"] == True
    assert response.json["venues"][3]["hasCreatedOffer"] == False


@pytest.mark.usefixtures("db_session")
def test_default_call(app, requests_mock):
    user_offerer = offerers_factories.UserOffererFactory(
        user__email="user.pro@test.com",
    )
    offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)

    # when
    response = TestClient(app.test_client()).with_session_auth(user_offerer.user.email).get("/venues")

    # then
    assert response.status_code == 200


@pytest.mark.usefixtures("db_session")
def test_default_admin_call(app):
    admin_user = users_factories.AdminFactory(email="admin.pro@test.com")

    # when
    response = TestClient(app.test_client()).with_session_auth(admin_user.email).get("/venues")

    # then
    assert response.status_code == 200


@pytest.mark.usefixtures("db_session")
def test_admin_call_num_queries(app):
    admin_user = users_factories.AdminFactory(email="admin.pro@test.com")

    user_offerers = offerers_factories.UserOffererFactory.create_batch(3)

    offerers_factories.VenueFactory(managingOfferer=user_offerers[0].offerer)
    offerers_factories.VenueFactory(managingOfferer=user_offerers[1].offerer)
    offerers_factories.VenueFactory(managingOfferer=user_offerers[2].offerer)

    client = TestClient(app.test_client()).with_session_auth(admin_user.email)

    # when
    with assert_no_duplicated_queries():
        response = client.get("/venues")

    # then
    assert response.status_code == 200
    assert len(response.json["venues"]) == 3


@pytest.mark.usefixtures("db_session")
def test_invalid_offerer_id(app):
    pro_user = users_factories.ProFactory(email="user.pro@test.com")
    offerer = offerers_factories.OffererFactory()
    offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
    offerers_factories.VenueFactory(managingOfferer=offerer)

    query_params = ["offererId=666"]

    # when
    response = TestClient(app.test_client()).with_session_auth(pro_user.email).get(f"/venues?{'&'.join(query_params)}")

    # then
    assert response.status_code == 200

    assert "venues" in response.json
    assert len(response.json["venues"]) == 0


@pytest.mark.usefixtures("db_session")
def test_full_valid_call(app):
    pro_user = users_factories.ProFactory(email="user.pro@test.com")
    offerer = offerers_factories.OffererFactory()
    offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)

    query_params = [
        "validated=true",
        f"offererId={offerer.id}",
        "activeOfferersOnly=true",
    ]

    # when
    response = TestClient(app.test_client()).with_session_auth(pro_user.email).get(f"/venues?{'&'.join(query_params)}")

    # then
    assert response.status_code == 200


@pytest.mark.usefixtures("db_session")
def test_full_valid_call_with_false(app):
    pro_user = users_factories.ProFactory(email="user.pro@test.com")
    offerer = offerers_factories.OffererFactory()
    offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)

    query_params = [
        "validated=false",
        f"offererId={offerer.id}",
        "activeOfferersOnly=false",
    ]

    # when
    response = TestClient(app.test_client()).with_session_auth(pro_user.email).get(f"/venues?{'&'.join(query_params)}")

    # then
    assert response.status_code == 200


@pytest.mark.usefixtures("db_session")
def test_invalid_validated(app):
    pro_user = users_factories.ProFactory(email="user.pro@test.com")

    query_params = [
        "validated=toto",
    ]

    # when
    response = TestClient(app.test_client()).with_session_auth(pro_user.email).get(f"/venues?{'&'.join(query_params)}")

    # then
    assert response.status_code == 400


@pytest.mark.usefixtures("db_session")
def test_invalid_active_offerer_only(app):
    pro_user = users_factories.ProFactory(email="user.pro@test.com")

    query_params = [
        "activeOfferersOnly=tata",
    ]

    # when
    response = TestClient(app.test_client()).with_session_auth(pro_user.email).get(f"/venues?{'&'.join(query_params)}")

    # then
    assert response.status_code == 400
