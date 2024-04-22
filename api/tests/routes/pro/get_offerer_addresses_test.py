import pytest

from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.users import factories as users_factories


@pytest.mark.usefixtures("db_session")
def test_get_offerer_addresses_success(client):
    user_offerer = offerers_factories.UserOffererFactory()
    pro = user_offerer.user
    offerer = user_offerer.offerer

    offerer_address_1 = offerers_factories.OffererAddressFactory(
        offerer=offerer,
        label="1ere adresse",
        address__street="1 boulevard Poissonnière",
        address__postalCode="75002",
        address__city="Paris",
    )
    offerer_address_2 = offerers_factories.OffererAddressFactory(
        offerer=offerer,
        label="2eme adresse",
        address__street="20 Avenue de Ségur",
        address__postalCode="75007",
        address__city="Paris",
        address__banId="75107_7560_00001",
    )
    offerers_factories.OffererAddressFactory(
        label="1ere adresse différent offerer",
        address__street="8 Boulevard du Port",
        address__postalCode="80000",
        address__city="Amiens",
        address__banId="80000_7560_00001",
    )

    response = client.with_session_auth(email=pro.email).get(f"/offerers/{offerer.id}/addresses")

    assert response.status_code == 200
    assert response.json == [
        {
            "city": "Paris",
            "id": offerer_address_1.id,
            "isEditable": True,
            "label": "1ere adresse",
            "postalCode": "75002",
            "street": "1 boulevard Poissonnière",
        },
        {
            "city": "Paris",
            "id": offerer_address_2.id,
            "isEditable": True,
            "label": "2eme adresse",
            "postalCode": "75007",
            "street": "20 Avenue de Ségur",
        },
    ]


@pytest.mark.usefixtures("db_session")
def test_access_by_unauthorized_pro_user(client):
    pro = users_factories.ProFactory()
    offerer = offerers_factories.OffererFactory()

    response = client.with_session_auth(email=pro.email).get(f"/offerers/{offerer.id}/addresses")

    assert response.status_code == 403
