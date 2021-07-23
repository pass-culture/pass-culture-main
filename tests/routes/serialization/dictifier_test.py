import pytest

from pcapi.core.users import factories as users_factories
from pcapi.model_creators.generic_creators import create_booking
from pcapi.model_creators.generic_creators import create_mediation
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_user_offerer
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_offer_with_event_product
from pcapi.model_creators.specific_creators import create_product_with_event_subcategory
from pcapi.models import Stock
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
    def test_returns_included_properties_on_joined_relationships(self, app):
        # given
        offerer = create_offerer()
        venue = create_venue(offerer)
        event_product = create_product_with_event_subcategory(event_name="My Event")
        offer = create_offer_with_event_product(venue, product=event_product)
        mediation = create_mediation(offer)
        repository.save(mediation)
        EVENT_INCLUDES = [{"key": "mediations", "includes": ["thumbUrl"]}]

        # when
        dict_result = as_dict(offer, includes=EVENT_INCLUDES)

        # then
        assert "thumbUrl" in dict_result["mediations"][0]

    @pytest.mark.usefixtures("db_session")
    def test_does_not_return_excluded_keys_on_joined_relationships(self, app):
        # given
        offerer = create_offerer()
        venue = create_venue(offerer)
        event_product = create_product_with_event_subcategory(event_name="My Event")
        offer = create_offer_with_event_product(venue, product=event_product)
        mediation = create_mediation(offer)
        repository.save(mediation)
        EVENT_INCLUDES = [{"key": "mediations", "includes": ["-isActive"]}]

        # when
        dict_result = as_dict(offer, includes=EVENT_INCLUDES)

        # then
        assert "isActive" not in dict_result["mediations"][0]

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
        user = users_factories.UserFactory.build(id=12, postalCode=None)
        booking = create_booking(user=user, stock=Stock(), idx=13)
        booking.userId = user.id

        # when
        dict_result = as_dict(booking, includes=[])

        # then
        assert dict_result["userId"] == "BQ"
