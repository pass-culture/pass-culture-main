import pytest

import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.users.factories import ProFactory
from pcapi.core.users.models import User
from pcapi.scripts.pro.fill_pro_department_code_with_offerer_postal_code import (
    fill_pro_department_code_with_offerer_postal_code,
)
from pcapi.scripts.pro.fill_pro_department_code_with_offerer_postal_code import _get_user_initial_linked_offerer


class FillProDepartmentCodeWithOffererPostalCodeTest:
    @pytest.mark.usefixtures("db_session")
    def should_not_modify_pro_user_department_code_when_user_not_in_93(self):
        # Given
        user = ProFactory(departementCode="72")
        offerers_factories.UserOffererFactory(user=user)

        # When
        fill_pro_department_code_with_offerer_postal_code()

        # Then
        updated_user = User.query.one()
        assert updated_user.departementCode == "72"

    @pytest.mark.usefixtures("db_session")
    def should_not_update_user_linked_to_offerer_with_postal_code_outside_75(self):
        # Given
        user = ProFactory(departementCode="72")
        offerers_factories.UserOffererFactory(user=user, offerer__postalCode="64000")

        # When
        fill_pro_department_code_with_offerer_postal_code()

        # Then
        updated_user = User.query.one()
        assert updated_user.departementCode == "72"

    @pytest.mark.usefixtures("db_session")
    def should_update_user_department_code_linked_to_offerer_with_postal_code_75(self):
        # Given
        user = ProFactory(departementCode="93")
        offerers_factories.UserOffererFactory(user=user, offerer__postalCode="75016")

        # When
        fill_pro_department_code_with_offerer_postal_code()

        # Then
        updated_user = User.query.one()
        assert updated_user.departementCode == "75"


class GetUserInitialLinkedOffererTest:
    @pytest.mark.usefixtures("db_session")
    def should_return_first_linked_offerer(self):
        # Given
        user = ProFactory(departementCode="93")
        offerer1 = offerers_factories.OffererFactory()
        offerer2 = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer2)
        offerers_factories.UserOffererFactory(user=user, offerer=offerer1)

        # When
        offerer = _get_user_initial_linked_offerer(user)

        # Then
        assert offerer == offerer2
