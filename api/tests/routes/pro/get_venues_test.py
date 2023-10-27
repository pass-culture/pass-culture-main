import pytest

from pcapi.core.educational.factories import CollectiveOfferTemplateFactory
from pcapi.core.educational.factories import CollectiveStockFactory
from pcapi.core.finance.factories import BankInformationFactory
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offers.factories import StockFactory
from pcapi.core.testing import assert_no_duplicated_queries
import pcapi.core.users.factories as users_factories


pytestmark = pytest.mark.usefixtures("db_session")


def test_response_serialization(client):
    user_offerer = offerers_factories.UserOffererFactory()
    venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)

    # when
    client = client.with_session_auth(user_offerer.user.email)
    response = client.get("/venues")

    # then
    assert response.status_code == 200

    assert "venues" in response.json
    assert len(response.json["venues"]) == 1

    assert response.json["venues"][0] == {
        "id": venue.id,
        "managingOffererId": venue.managingOffererId,
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
        "venueTypeCode": venue.venueTypeCode.name,
        "hasMissingReimbursementPoint": True,
        "hasCreatedOffer": False,
        "hasNonFreeOffers": False,
    }


def test_response_missing_reimbursement_point_serialization(client):
    user_offerer = offerers_factories.UserOffererFactory()

    offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer, reimbursement_point=None, name="A")
    venue_with_pending_application = offerers_factories.VenueFactory(
        managingOfferer=user_offerer.offerer, reimbursement_point=None, name="B"
    )
    BankInformationFactory(venue=venue_with_pending_application, applicationId=4, status="DRAFT")
    offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer, reimbursement_point="self", name="C")

    # when
    client = client.with_session_auth(user_offerer.user.email)
    response = client.get("/venues")

    # then
    assert response.status_code == 200

    assert "venues" in response.json
    assert len(response.json["venues"]) == 3

    assert response.json["venues"][0]["hasMissingReimbursementPoint"] is True
    assert response.json["venues"][0]["hasNonFreeOffers"] is False
    assert response.json["venues"][1]["hasMissingReimbursementPoint"] is False
    assert response.json["venues"][1]["hasNonFreeOffers"] is False
    assert response.json["venues"][2]["hasMissingReimbursementPoint"] is False
    assert response.json["venues"][2]["hasNonFreeOffers"] is False


def test_response_created_offer_serialization(client):
    user_offerer = offerers_factories.UserOffererFactory()

    venue_with_offer = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
    StockFactory(offer__venue=venue_with_offer)

    venue_with_collective_offer = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
    CollectiveStockFactory(collectiveOffer__venue=venue_with_collective_offer)

    venue_with_collective_offer_template = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
    CollectiveOfferTemplateFactory(venue=venue_with_collective_offer_template)

    offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
    venue_with_free_offer = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
    StockFactory(offer__venue=venue_with_free_offer, price=0)

    # when
    client = client.with_session_auth(user_offerer.user.email)
    response = client.get("/venues")

    # then
    assert response.status_code == 200

    assert "venues" in response.json
    assert len(response.json["venues"]) == 5
    venues = sorted(response.json["venues"], key=lambda v: v["id"])

    assert venues[0]["hasCreatedOffer"] is True
    assert venues[0]["hasNonFreeOffers"] is True
    assert venues[1]["hasCreatedOffer"] is True
    assert venues[1]["hasNonFreeOffers"] is True
    assert venues[2]["hasCreatedOffer"] is True
    assert venues[2]["hasNonFreeOffers"] is False
    assert venues[3]["hasCreatedOffer"] is False
    assert venues[3]["hasNonFreeOffers"] is False
    assert venues[4]["hasCreatedOffer"] is True
    assert venues[4]["hasNonFreeOffers"] is False


def test_admin_call(client):
    admin_user = users_factories.AdminFactory(email="admin.pro@test.com")

    user_offerers = offerers_factories.UserOffererFactory.create_batch(3)

    offerers_factories.VenueFactory(managingOfferer=user_offerers[0].offerer)
    offerers_factories.VenueFactory(managingOfferer=user_offerers[1].offerer)
    offerers_factories.VenueFactory(managingOfferer=user_offerers[2].offerer)

    # when
    client = client.with_session_auth(admin_user.email)
    with assert_no_duplicated_queries():
        response = client.get("/venues")

    # then
    assert response.status_code == 200
    assert len(response.json["venues"]) == 3


def test_invalid_offerer_id(client):
    pro_user = users_factories.ProFactory()
    offerer = offerers_factories.OffererFactory()
    offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
    offerers_factories.VenueFactory(managingOfferer=offerer)

    params = {"offererId": "666"}

    # when
    client = client.with_session_auth(pro_user.email)
    response = client.get("/venues", params)

    # then
    assert response.status_code == 200

    assert "venues" in response.json
    assert len(response.json["venues"]) == 0


def test_full_valid_call(client):
    pro_user = users_factories.ProFactory()
    offerer = offerers_factories.OffererFactory()
    offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)

    params = {
        "validated": "true",
        "offererId": str(offerer.id),
        "activeOfferersOnly": "true",
    }

    # when
    client = client.with_session_auth(pro_user.email)
    response = client.get("/venues", params)

    # then
    assert response.status_code == 200


def test_full_valid_call_with_false(client):
    pro_user = users_factories.ProFactory()
    offerer = offerers_factories.OffererFactory()
    offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)

    params = {
        "validated": "false",
        "offererId": str(offerer.id),
        "activeOfferersOnly": "false",
    }

    # when
    client = client.with_session_auth(pro_user.email)
    response = client.get("/venues", params)

    # then
    assert response.status_code == 200


def test_invalid_validated(client):
    pro_user = users_factories.ProFactory()

    params = {"validated": "invalid"}

    # when
    client = client.with_session_auth(pro_user.email)
    response = client.get("/venues", params)

    # then
    assert response.status_code == 400


def test_invalid_active_offerer_only(client):
    pro_user = users_factories.ProFactory()

    params = {"activeOfferersOnly": "invalid"}

    # when
    client = client.with_session_auth(pro_user.email)
    response = client.get("/venues", params)

    # then
    assert response.status_code == 400
