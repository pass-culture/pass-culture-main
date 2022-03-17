import pytest

from pcapi.core.bookings import factories as booking_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.users import factories as users_factories
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_user_offerer
from pcapi.repository import repository
from pcapi.routes.serialization import as_dict


class AsDictTest:
    @pytest.mark.usefixtures("db_session")
    def test_returns_model_keys(self, app):
        # given
        user = users_factories.UserFactory.build(postalCode=None)
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)
        repository.save(user_offerer)
        USER_INCLUDES = []

        # when
        dict_result = as_dict(user, includes=USER_INCLUDES)

        # then
        assert "publicName" in dict_result
        assert "lastName" in dict_result
        assert "firstName" in dict_result

    @pytest.mark.usefixtures("db_session")
    def test_does_not_return_excluded_keys(self, app):
        # given
        user = users_factories.UserFactory.build(postalCode=None)
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)
        repository.save(user_offerer)
        USER_INCLUDES = ["-password"]

        # when
        dict_result = as_dict(user, includes=USER_INCLUDES)

        # then
        assert "password" not in dict_result

    @pytest.mark.usefixtures("db_session")
    def test_does_not_return_properties_by_default(self, app):
        # given
        user = users_factories.UserFactory.build(postalCode=None)
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)
        repository.save(user_offerer)
        USER_INCLUDES = []

        # when
        dict_result = as_dict(user, includes=USER_INCLUDES)

        # then
        assert "hasPhysicalVenues" not in dict_result

    @pytest.mark.usefixtures("db_session")
    def test_returns_included_properties(self, app):
        # given
        user = users_factories.UserFactory.build(postalCode=None)
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)
        repository.save(user_offerer)
        USER_INCLUDES = ["hasPhysicalVenues"]

        # when
        dict_result = as_dict(user, includes=USER_INCLUDES)

        # then
        assert "hasPhysicalVenues" in dict_result

    @pytest.mark.usefixtures("db_session")
    def test_returns_model_keys_on_joined_relationships(self, app):
        # given
        user = users_factories.ProFactory.build()
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)
        repository.save(user_offerer)
        USER_INCLUDES = ["offerers"]

        # when
        dict_result = as_dict(user, includes=USER_INCLUDES)

        # then
        assert "offerers" in dict_result
        assert "name" in dict_result["offerers"][0]
        assert "siren" in dict_result["offerers"][0]

    @pytest.mark.usefixtures("db_session")
    def test_returns_included_properties_on_joined_relationships(self):
        mediation = offers_factories.MediationFactory.build()
        includes = [{"key": "mediations", "includes": ["thumbUrl"]}]
        dict_ = as_dict(mediation.offer, includes=includes)
        assert "thumbUrl" in dict_["mediations"][0]

    @pytest.mark.usefixtures("db_session")
    def test_does_not_return_excluded_keys_on_joined_relationships(self, app):
        mediation = offers_factories.MediationFactory.build()
        includes = [{"key": "mediations", "includes": ["-isActive"]}]
        dict_ = as_dict(mediation.offer, includes=includes)
        assert "isActive" not in dict_["mediations"][0]

    @pytest.mark.usefixtures("db_session")
    def test_returns_humanized_ids_for_primary_keys(self, app):
        # given
        user = users_factories.UserFactory.build(id=12, postalCode=None)

        # when
        dict_result = as_dict(user, includes=[])

        # then
        assert dict_result["id"] == "BQ"

    @pytest.mark.usefixtures("db_session")
    def test_returns_humanized_ids_for_foreign_keys(self, app):
        # given
        user = users_factories.BeneficiaryGrant18Factory(id=12)
        individual_booking = booking_factories.IndividualBookingFactory(individualBooking__user=user).individualBooking

        # when
        dict_result = as_dict(individual_booking, includes=[])

        # then
        assert dict_result["userId"] == "BQ"
