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
