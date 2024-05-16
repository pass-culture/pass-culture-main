import pytest

from pcapi.core.offerers import models as offerers_models
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.testing import assert_num_queries
import pcapi.core.users.factories as users_factories


class PatchOffererAddressFailTest:
    # Fetch the session
    # Fetch the user
    # Check permission
    # retrieve offererAddress
    # rollback
    num_queries = 5

    @pytest.mark.usefixtures("db_session")
    def test_user_cant_change_offerer_address_he_doesnt_own(self, client):
        pro_user = users_factories.ProFactory()
        offerer_1 = offerers_factories.OffererFactory()
        offerer_2 = offerers_factories.OffererFactory()
        offerer_1_id = offerer_1.id
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer_1)
        offerers_factories.OffererAddressFactory(offerer=offerer_1)
        offerer_address_2 = offerers_factories.OffererAddressFactory(
            offerer=offerer_2, address__street="2 boulevard Poissonnière", address__banId="75102_7560_00002"
        )
        offerer_address_2_id = offerer_address_2.id
        new_label = {"label": "New label"}

        http_client = client.with_session_auth(pro_user.email)
        with assert_num_queries(self.num_queries):
            response = http_client.patch(f"/offerers/{offerer_1_id}/address/{offerer_address_2_id}", json=new_label)
            assert response.status_code == 404

        offerer_address = offerers_models.OffererAddress.query.filter_by(id=offerer_address_2_id)
        assert offerer_address.label != new_label["label"]

    @pytest.mark.usefixtures("db_session")
    def test_user_cant_change_offerer_address_on_foreign_offerer(self, client):
        pro_user = users_factories.ProFactory()
        offerer_1 = offerers_factories.OffererFactory()
        offerer_2 = offerers_factories.OffererFactory()
        offerer_2_id = offerer_2.id
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer_1)
        offerer_address = offerers_factories.OffererAddressFactory(offerer=offerer_2)
        offerer_address_id = offerer_address.id
        new_label = {"label": "New label"}

        http_client = client.with_session_auth(pro_user.email)
        # - retrieve offerer address
        with assert_num_queries(self.num_queries - 1):
            response = http_client.patch(f"/offerers/{offerer_2_id}/address/{offerer_address_id}", json=new_label)
            assert response.status_code == 403
        offerer_address = offerers_models.OffererAddress.query.one()
        assert offerer_address.label != new_label["label"]

    @pytest.mark.usefixtures("db_session")
    def test_user_cant_change_for_a_label_already_used_for_same_address(self, client):
        pro_user = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerer_id = offerer.id
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        offerer_address = offerers_factories.OffererAddressFactory(offerer=offerer)
        same_offerer_address_with_different_label = offerers_factories.OffererAddressFactory(
            offerer=offerer, address=offerer_address.address, label="Different label"
        )
        offerer_address_id = same_offerer_address_with_different_label.id
        new_label = {"label": offerer_address.label}

        http_client = client.with_session_auth(pro_user.email)

        with assert_num_queries(self.num_queries):
            response = http_client.patch(f"/offerers/{offerer_id}/address/{offerer_address_id}", json=new_label)
            assert response.status_code == 400

        assert response.json == {"label": "Une adresse identique utilise déjà ce libellé"}

        offerer_address = offerers_models.OffererAddress.query.filter_by(id=offerer_address_id)
        assert offerer_address.label != new_label["label"]

    @pytest.mark.usefixtures("db_session")
    def test_user_cant_change_label_for_not_editable_offereraddress(self, client):
        pro_user = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerer_id = offerer.id
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        offerer_address = offerers_factories.OffererAddressFactory(offerer=offerer)
        offerer_address_id = offerer_address.id
        offerers_factories.VenueFactory(managingOfferer=offerer, offererAddress=offerer_address)
        new_label = {"label": "Different label"}
        http_client = client.with_session_auth(pro_user.email)
        with assert_num_queries(self.num_queries):
            response = http_client.patch(f"/offerers/{offerer_id}/address/{offerer_address_id}", json=new_label)
            assert response.status_code == 400
        assert response.json == {"label": "Le libellé de cette adresse n'est pas modifiable"}
        offerer_address = offerers_models.OffererAddress.query.filter_by(id=offerer_address_id)
        assert offerer_address.label != new_label["label"]


class PatchOffererAddressSuccessTest:

    # Fetch the session
    # Fetch the user
    # Check permission
    # retrieve offererAddress
    num_queries = 4

    @pytest.mark.usefixtures("db_session")
    def test_user_can_change_offerer_address_label(self, client):
        pro_user = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerer_id = offerer.id
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        offerer_address = offerers_factories.OffererAddressFactory(offerer=offerer)
        offerer_address_id = offerer_address.id
        expected_data = {"label": "New label"}

        http_client = client.with_session_auth(pro_user.email)
        # + update offerer address
        with assert_num_queries(self.num_queries + 1):
            response = http_client.patch(f"/offerers/{offerer_id}/address/{offerer_address_id}", json=expected_data)
            assert response.status_code == 204

        offerer_address = offerers_models.OffererAddress.query.one()
        assert offerer_address.label == expected_data["label"]
