import pytest

from pcapi.core import testing
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.users.factories as users_factories
from pcapi.utils import human_ids


pytestmark = pytest.mark.usefixtures("db_session")


def test_get_business_units_by_admin(client):
    offerers_factories.VenueFactory(businessUnit__name="Business unit Z")
    offerers_factories.VenueFactory(businessUnit__name="Business unit A")
    admin = users_factories.AdminFactory()

    client = client.with_session_auth(admin.email)
    response = client.get("/finance/business-units")

    assert response.status_code == 200
    business_units = response.json
    assert len(business_units) == 2
    assert business_units[0]["name"] == "Business unit A"
    assert business_units[1]["name"] == "Business unit Z"


def test_get_business_units_by_pro(client):
    venue1 = offerers_factories.VenueFactory(
        businessUnit__name="La business unit",
        businessUnit__siret="123456",
        businessUnit__bankAccount__iban="FR1234",
    )
    business_unit1 = venue1.businessUnit
    _other_venue_with_business_unit = offerers_factories.VenueFactory()
    pro = users_factories.ProFactory()
    offerers_factories.UserOffererFactory(offerer=venue1.managingOfferer, user=pro)

    client = client.with_session_auth(pro.email)
    n_queries = testing.AUTHENTICATION_QUERIES
    n_queries += 1  # select business units
    with testing.assert_num_queries(n_queries):
        response = client.get("finance/business-units")

    assert response.status_code == 200
    business_units = response.json
    assert len(business_units) == 1
    assert business_units[0] == {
        "id": business_unit1.id,
        "iban": "FR1234",
        "bic": "BDFEFRPP",
        "name": "La business unit",
        "siret": "123456",
    }


def test_get_business_units_by_pro_filtered_on_offerer_id(client):
    venue1 = offerers_factories.VenueFactory()
    business_unit1 = venue1.businessUnit
    venue2 = offerers_factories.VenueFactory()
    pro = users_factories.ProFactory()
    offerers_factories.UserOffererFactory(offerer=venue1.managingOfferer, user=pro)
    offerers_factories.UserOffererFactory(offerer=venue2.managingOfferer, user=pro)

    client = client.with_session_auth(pro.email)
    params = {"offererId": human_ids.humanize(venue1.managingOffererId)}
    response = client.get("/finance/business-units", params=params)

    assert response.status_code == 200
    business_units = response.json
    assert len(business_units) == 1
    assert business_units[0]["id"] == business_unit1.id


def test_get_business_units_by_pro_unauthorized_offerer_id(client):
    venue = offerers_factories.VenueFactory()
    pro = users_factories.ProFactory()

    client = client.with_session_auth(pro.email)
    params = {"offererId": human_ids.humanize(venue.managingOffererId)}
    response = client.get("/finance/business-units", params=params)

    assert response.status_code == 403
