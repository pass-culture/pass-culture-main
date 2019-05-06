import pytest

from models import PcObject, UserOfferer
from scripts.clean_fnac_accounts import find_all_fnac_users, find_all_fnac_offerers, create_all_possible_user_offerers, \
    clear_all_existing_user_offerers
from tests.conftest import clean_database
from tests.test_utils import create_user, create_offerer, create_user_offerer

ALL_FNAC_SIREN = ['350127460', '434001954', '334473352', '343282380']

@pytest.mark.standalone
class FindAllFnacUsersTest:
    @clean_database
    def test_retrieves_users_with_email_ending_with_fnac_dot_com_and_fnacdarty_dot_com_only(self, app):
        # Given
        user_fnac = create_user(email='toto@fnac.com')
        user_fnacdarty = create_user(email='toto@fnacdarty.com')
        user_not_fnac = create_user(email='toto@cultura.com')

        PcObject.check_and_save(user_fnac, user_fnacdarty, user_not_fnac)

        # When
        users = find_all_fnac_users()

        # Then
        assert len(users) == 2
        assert user_not_fnac not in users


@pytest.mark.standalone
class FindAllFnacStructuresTest:
    @clean_database
    def test_only_retrieves_offerers_with_fnac_siren(self, app):
        # Given
        fnac_offerers = [create_offerer(siren=siren) for siren in ALL_FNAC_SIREN]
        other_offerer = create_offerer(siren='123456789')
        PcObject.check_and_save(*(fnac_offerers + [other_offerer]))

        # When
        offerers = find_all_fnac_offerers()

        # Then
        assert len(offerers) == 4
        assert other_offerer not in offerers


@pytest.mark.standalone
class CreateAllPossibleUserOfferersTest:
    @clean_database
    def test_should_create_user_offerers_linking_all_fnac_users_and_offerers_only_if_they_do_not_exist(self, app):
        # Given
        users = [create_user(email=f'{i}@toto.com') for i in range(2)]
        offerers = [create_offerer(siren=f'12345678{i}') for i in range(3)]
        user_offerer = create_user_offerer(users[0], offerers[0])
        PcObject.check_and_save(user_offerer)

        # When
        create_all_possible_user_offerers(users, offerers)

        # Then
        user_offerers = UserOfferer.query.all()
        assert len(user_offerers) == 6
        for user_offerer in user_offerers:
            assert user_offerer.user in users
            assert user_offerer.offerer in offerers


@pytest.mark.standalone
class ClearAllExistingUserOfferersTest:
    @clean_database
    def test_should_only_delete_user_offerers_linked_to_given_offerer(self, app):
        # Given
        offerer = create_offerer('123456789')
        other_offerer = create_offerer('987654321')

        user1 = create_user(email='1@email.com')
        user2 = create_user(email='2@email.com')

        user_offerer1 = create_user_offerer(user1, offerer)
        user_offerer2 = create_user_offerer(user2, offerer)
        other_user_offerer = create_user_offerer(user2, other_offerer)

        PcObject.check_and_save(user_offerer1, user_offerer2, other_user_offerer)

        # When
        clear_all_existing_user_offerers('123456789')

        # Then
        user_offerers = UserOfferer.query.all()
        assert len(user_offerers) == 1
        assert user_offerers[0].offerer.siren != '123456789'

