import pytest

from pcapi.core import testing
import pcapi.core.finance.factories as finance_factories
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.users.factories as users_factories
from pcapi.utils import human_ids


pytestmark = pytest.mark.usefixtures("db_session")


def test_get_reimbursement_points_by_admin(client):
    pro_reimbursement_point_z = offerers_factories.VenueFactory(
        businessUnit=None, reimbursement_point="self", name="Reimbursement Point Z"
    )
    finance_factories.BankInformationFactory(venue=pro_reimbursement_point_z)

    pro_reimbursement_point_a = offerers_factories.VenueFactory(
        businessUnit=None, reimbursement_point="self", name="Reimbursement Point A"
    )
    finance_factories.BankInformationFactory(venue=pro_reimbursement_point_a)

    admin = users_factories.AdminFactory()

    client = client.with_session_auth(admin.email)
    response = client.get("/finance/reimbursement-points")

    assert response.status_code == 200
    reimbursement_points = response.json
    assert len(reimbursement_points) == 2
    assert reimbursement_points[0]["name"] == "Reimbursement Point A"
    assert reimbursement_points[1]["name"] == "Reimbursement Point Z"


def test_get_reimbursement_points_by_pro(client):
    pro_reimbursement_point_1 = offerers_factories.VenueFactory(
        businessUnit=None,
        reimbursement_point="self",
        name="My Reimbursement Point",
        publicName="My Reimbursement Point Public Name",
    )
    finance_factories.BankInformationFactory(venue=pro_reimbursement_point_1)

    reimbursement_point_2 = offerers_factories.VenueFactory(businessUnit=None, reimbursement_point="self")
    finance_factories.BankInformationFactory(venue=reimbursement_point_2)
    pro = users_factories.ProFactory()
    offerers_factories.UserOffererFactory(offerer=pro_reimbursement_point_1.managingOfferer, user=pro)

    client = client.with_session_auth(pro.email)
    n_queries = testing.AUTHENTICATION_QUERIES
    n_queries += 1  # select reimbursement points
    with testing.assert_num_queries(n_queries):
        response = client.get("/finance/reimbursement-points")

    assert response.status_code == 200
    reimbursement_points = response.json
    assert len(reimbursement_points) == 1
    assert reimbursement_points[0] == {
        "id": pro_reimbursement_point_1.id,
        "name": "My Reimbursement Point",
        "publicName": "My Reimbursement Point Public Name",
    }


def test_get_reimbursement_points_by_pro_filtered_on_offerer_id(client):
    reimbursement_point_1 = offerers_factories.VenueFactory(
        businessUnit=None, reimbursement_point="self", name="My Reimbursement Point"
    )
    finance_factories.BankInformationFactory(venue=reimbursement_point_1)

    reimbursement_point_2 = offerers_factories.VenueFactory(businessUnit=None, reimbursement_point="self")
    finance_factories.BankInformationFactory(venue=reimbursement_point_2)
    pro = users_factories.ProFactory()
    offerers_factories.UserOffererFactory(offerer=reimbursement_point_1.managingOfferer, user=pro)
    offerers_factories.UserOffererFactory(offerer=reimbursement_point_2.managingOfferer, user=pro)

    client = client.with_session_auth(pro.email)
    params = {"offererId": human_ids.humanize(reimbursement_point_1.managingOffererId)}
    response = client.get("/finance/reimbursement-points", params=params)

    assert response.status_code == 200
    reimbursement_points = response.json
    assert len(reimbursement_points) == 1
    assert reimbursement_points[0]["id"] == reimbursement_point_1.id


def test_get_reimbursement_points_by_pro_unauthorized_offerer_id(client):
    reimbursement_point = offerers_factories.VenueFactory(businessUnit=None, reimbursement_point="self")
    finance_factories.BankInformationFactory(venue=reimbursement_point)
    pro = users_factories.ProFactory()

    client = client.with_session_auth(pro.email)
    params = {"offererId": human_ids.humanize(reimbursement_point.managingOffererId)}
    response = client.get("/finance/reimbursement-points", params=params)

    assert response.status_code == 403
