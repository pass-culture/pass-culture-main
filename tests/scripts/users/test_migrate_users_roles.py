from collections import Counter

import pytest

import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.core.users.models import UserRole
from pcapi.scripts.users.migrate_users_roles import migrate_users_roles


pytestmark = pytest.mark.usefixtures("db_session")


def test_migrate_beneficiary_with_no_roles():
    # Given
    user = users_factories.UserFactory(isBeneficiary=True)

    # When
    migrate_users_roles()

    # Then
    assert user.has_beneficiary_role
    assert user.roles == [UserRole.BENEFICIARY]


def test_migrate_beneficiary_with_beneficiary_role():
    # Given
    user = users_factories.BeneficiaryGrant18Factory()

    # When
    migrate_users_roles()

    # Then
    assert user.has_beneficiary_role
    assert user.roles == [UserRole.BENEFICIARY]


def test_migrate_beneficiary_with_pro_role():
    # Given
    user = users_factories.ProFactory(isBeneficiary=True)
    offers_factories.UserOffererFactory(user=user)

    # When
    migrate_users_roles()

    # Then
    assert user.has_beneficiary_role
    assert Counter(user.roles) == Counter([UserRole.BENEFICIARY, UserRole.PRO])


def test_does_not_migrate_user_with_no_roles_when_attachment_is_not_validated():
    # Given
    user = users_factories.UserFactory()
    offers_factories.UserOffererFactory(user=user, validationToken="TOKEN")

    # When
    migrate_users_roles()

    # Then
    assert not user.has_pro_role
    assert user.roles == []


def test_does_not_migrate_user_with_no_roles_when_offerer_is_not_validated():
    # Given
    user = users_factories.UserFactory()
    offers_factories.UserOffererFactory(user=user, offerer__validationToken="TOKEN")

    # When
    migrate_users_roles()

    # Then
    assert not user.has_pro_role
    assert user.roles == []


def test_migrate_pro_with_no_roles_when_attachment_and_offerer_are_validated():
    # Given
    user = users_factories.UserFactory()
    offers_factories.UserOffererFactory(user=user)

    # When
    migrate_users_roles()

    # Then
    assert user.has_pro_role
    assert user.roles == [UserRole.PRO]


def test_migrate_pro_with_beneficiary_role():
    # Given
    user = users_factories.BeneficiaryGrant18Factory()
    offers_factories.UserOffererFactory(user=user)

    # When
    migrate_users_roles()

    # Then
    assert user.has_pro_role
    assert Counter(user.roles) == Counter([UserRole.BENEFICIARY, UserRole.PRO])


def test_migrate_pro_with_admin_role():
    # Given
    user = users_factories.AdminFactory()
    offers_factories.UserOffererFactory(user=user)

    # When
    migrate_users_roles()

    # Then
    assert user.has_pro_role
    assert Counter(user.roles) == Counter([UserRole.ADMIN, UserRole.PRO])


def test_migrate_pro_with_pro_role():
    # Given
    user = users_factories.ProFactory()
    offers_factories.UserOffererFactory(user=user)

    # When
    migrate_users_roles()

    # Then
    assert user.has_pro_role
    assert user.roles == [UserRole.PRO]


def test_migrate_admin_with_no_roles():
    # Given
    user = users_factories.UserFactory(isAdmin=True)

    # When
    migrate_users_roles()

    # Then
    assert user.has_admin_role
    assert user.roles == [UserRole.ADMIN]


def test_migrate_admin_with_pro_role():
    # Given
    user = users_factories.ProFactory(isAdmin=True)
    offers_factories.UserOffererFactory(user=user)

    # When
    migrate_users_roles()

    # Then
    assert user.has_admin_role
    assert Counter(user.roles) == Counter([UserRole.ADMIN, UserRole.PRO])


def test_migrate_admin_with_admin_role():
    # Given
    user = users_factories.AdminFactory()

    # When
    migrate_users_roles()

    # Then
    assert user.has_admin_role
    assert user.roles == [UserRole.ADMIN]


def test_remove_duplicated_roles():
    # Given
    user = users_factories.UserFactory(roles=[UserRole.BENEFICIARY, UserRole.PRO, UserRole.PRO])
    offers_factories.UserOffererFactory(user=user)

    # When
    migrate_users_roles()

    # Then
    assert user.has_beneficiary_role
    assert user.has_pro_role
    assert Counter(user.roles) == Counter([UserRole.BENEFICIARY, UserRole.PRO])


def test_remove_pro_role_for_users_with_unvalidated_offerer_attachment():
    # Given
    user = users_factories.ProFactory()
    user.add_beneficiary_role()
    offers_factories.UserOffererFactory(user=user, validationToken="TOKEN")

    # When
    migrate_users_roles()

    # Then
    assert not user.has_pro_role
    assert user.has_beneficiary_role
    assert user.roles == [UserRole.BENEFICIARY]


def test_remove_pro_role_for_users_with_unvalidated_offerer():
    # Given
    user = users_factories.ProFactory()
    user.add_beneficiary_role()
    offers_factories.UserOffererFactory(user=user, offerer__validationToken="TOKEN")

    # When
    migrate_users_roles()

    # Then
    assert not user.has_pro_role
    assert user.has_beneficiary_role
    assert user.roles == [UserRole.BENEFICIARY]


def test_does_not_remove_pro_role_for_users_with_unvalidated_offerer_and_other_validated_offerer():
    # Given
    user = users_factories.ProFactory()
    user.add_beneficiary_role()
    offers_factories.UserOffererFactory(user=user, offerer__validationToken="TOKEN")
    offers_factories.UserOffererFactory(user=user)

    # When
    migrate_users_roles()

    # Then
    assert user.has_pro_role
    assert user.has_beneficiary_role
    assert Counter(user.roles) == Counter([UserRole.BENEFICIARY, UserRole.PRO])
