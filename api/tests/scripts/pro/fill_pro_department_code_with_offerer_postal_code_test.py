import pytest

from pcapi.core.users.factories import ProFactory
from pcapi.core.users.models import User
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_user_offerer
from pcapi.repository import repository
from pcapi.scripts.pro.fill_pro_department_code_with_offerer_postal_code import (
    fill_pro_department_code_with_offerer_postal_code,
)
from pcapi.scripts.pro.fill_pro_department_code_with_offerer_postal_code import _get_user_initial_linked_offerer


class FillProDepartmentCodeWithOffererPostalCodeTest:
    @pytest.mark.usefixtures("db_session")
    def should_not_modify_pro_user_department_code_when_user_not_in_93(self, app):
        # Given
        user = ProFactory(departementCode="72")
        offerer = create_offerer()
        user_offerer = create_user_offerer(user=user, offerer=offerer)
        repository.save(user_offerer)

        # When
        fill_pro_department_code_with_offerer_postal_code()

        # Then
        updated_user = User.query.one()
        assert updated_user.departementCode == "72"

    @pytest.mark.usefixtures("db_session")
    def should_not_update_user_linked_to_offerer_with_postal_code_outside_75(self, app):
        # Given
        user = ProFactory(departementCode="72")
        offerer = create_offerer(postal_code="64000")
        user_offerer = create_user_offerer(user=user, offerer=offerer)
        repository.save(user_offerer)

        # When
        fill_pro_department_code_with_offerer_postal_code()

        # Then
        updated_user = User.query.one()
        assert updated_user.departementCode == "72"

    @pytest.mark.usefixtures("db_session")
    def should_update_user_department_code_linked_to_offerer_with_postal_code_75(self, app):
        # Given
        user = ProFactory(departementCode="93")
        offerer = create_offerer(siren="123456788", postal_code="75016")
        user_offerer = create_user_offerer(user=user, offerer=offerer)
        repository.save(user_offerer)

        # When
        fill_pro_department_code_with_offerer_postal_code()

        # Then
        updated_user = User.query.one()
        assert updated_user.departementCode == "75"


class GetUserInitialLinkedOffererTest:
    @pytest.mark.usefixtures("db_session")
    def should_return_first_linked_offerer(self, app):
        # Given
        user = ProFactory(departementCode="93")
        offerer1 = create_offerer(idx=1, siren="123456788", postal_code="75016")
        offerer2 = create_offerer(idx=2, siren="123456789", postal_code="23000")
        user_offerer1 = create_user_offerer(idx=2, user=user, offerer=offerer1)
        user_offerer2 = create_user_offerer(idx=1, user=user, offerer=offerer2)
        repository.save(user_offerer1, user_offerer2)

        # When
        offerer = _get_user_initial_linked_offerer(user)

        # Then
        assert offerer == offerer2
