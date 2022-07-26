import pytest

import pcapi.core.bookings.factories as booking_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.routes.serialization import as_dict


class AsDictTest:
    def test_returns_model_keys(self):
        # given
        user = users_factories.UserFactory.build()
        USER_INCLUDES = []

        # when
        dict_result = as_dict(user, includes=USER_INCLUDES)

        # then
        assert "publicName" in dict_result
        assert "lastName" in dict_result
        assert "firstName" in dict_result

    def test_does_not_return_excluded_keys(self):
        # given
        user = users_factories.UserFactory.build()
        USER_INCLUDES = ["-password"]

        # when
        dict_result = as_dict(user, includes=USER_INCLUDES)

        # then
        assert "password" not in dict_result

    def test_does_not_return_properties_by_default(self):
        # given
        user = users_factories.UserFactory.build()
        USER_INCLUDES = []

        # when
        dict_result = as_dict(user, includes=USER_INCLUDES)

        # then
        assert "hasPhysicalVenues" not in dict_result

    def test_returns_included_properties(self):
        # given
        user = users_factories.UserFactory.build()
        USER_INCLUDES = ["hasPhysicalVenues"]

        # when
        dict_result = as_dict(user, includes=USER_INCLUDES)

        # then
        assert "hasPhysicalVenues" in dict_result

    def test_returns_included_properties_on_joined_relationships(self):
        mediation = offers_factories.MediationFactory.build()
        includes = [{"key": "mediations", "includes": ["thumbUrl"]}]
        dict_ = as_dict(mediation.offer, includes=includes)
        assert "thumbUrl" in dict_["mediations"][0]

    def test_does_not_return_excluded_keys_on_joined_relationships(self):
        mediation = offers_factories.MediationFactory.build()
        includes = [{"key": "mediations", "includes": ["-isActive"]}]
        dict_ = as_dict(mediation.offer, includes=includes)
        assert "isActive" not in dict_["mediations"][0]

    def test_returns_humanized_ids_for_primary_keys(self):
        # given
        user = users_factories.UserFactory.build(id=12)

        # when
        dict_result = as_dict(user, includes=[])

        # then
        assert dict_result["id"] == "BQ"

    @pytest.mark.usefixtures("db_session")
    def test_returns_humanized_ids_for_foreign_keys(self):
        # given
        user = users_factories.BeneficiaryGrant18Factory(id=12)
        booking = booking_factories.BookingFactory(user=user)

        # when
        dict_result = as_dict(booking, includes=[])

        # then
        assert dict_result["userId"] == "BQ"
