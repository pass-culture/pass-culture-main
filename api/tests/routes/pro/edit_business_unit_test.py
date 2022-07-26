import pytest

import pcapi.core.finance.models as finance_models
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.users.factories as users_factories


pytestmark = pytest.mark.usefixtures("db_session")


def test_edit_business_unit(client):
    venue = offerers_factories.VenueFactory(
        businessUnit__siret=None, managingOfferer__siren="123456789", siret="12345678901234"
    )
    business_unit = venue.businessUnit
    pro = users_factories.ProFactory()
    offerers_factories.UserOffererFactory(user=pro, offerer=venue.managingOfferer)

    client = client.with_session_auth(pro.email)
    data = {"siret": "12345678901234"}
    response = client.patch(f"/finance/business-units/{business_unit.id}", data)

    assert response.status_code == 204
    business_unit = finance_models.BusinessUnit.query.one()
    assert business_unit.siret == "12345678901234"


def test_edit_business_unit_unauthorized_user(client):
    venue = offerers_factories.VenueFactory(businessUnit__siret=None)
    business_unit = venue.businessUnit
    pro = users_factories.ProFactory()

    client = client.with_session_auth(pro.email)
    data = {"siret": "12345678901234"}
    response = client.patch(f"/finance/business-units/{business_unit.id}", data)

    assert response.status_code == 403


def test_edit_business_unit_with_validation_error(client):
    venue = offerers_factories.VenueFactory(
        businessUnit__siret=None,
        managingOfferer__siren="123456789",
    )
    business_unit = venue.businessUnit
    pro = users_factories.ProFactory()
    offerers_factories.UserOffererFactory(user=pro, offerer=venue.managingOfferer)

    client = client.with_session_auth(pro.email)
    data = {"siret": "not-a-valid-siret"}
    response = client.patch(f"/finance/business-units/{business_unit.id}", data)

    assert response.status_code == 400
    assert response.json["siret"] == ["Ce SIRET n'est pas valide."]
