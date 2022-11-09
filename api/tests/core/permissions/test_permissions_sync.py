import enum
from unittest import mock

from pcapi.core.permissions import models as perm_models


def test_sync_first_perms(db_session):
    # given
    class TestPermissions(enum.Enum):
        FOO = "foo"
        BAR = "bar"

    perm_models.RolePermission.query.delete()
    db_session.query(perm_models.Permission).delete()
    assert db_session.query(perm_models.Permission.id).count() == 0

    # when
    perm_models.sync_enum_with_db_field(db_session, TestPermissions, perm_models.Permission.name)

    # then
    assert set(p.name for p in db_session.query(perm_models.Permission.name).all()) == set(
        p.name for p in TestPermissions
    )


def test_sync_new_perms(db_session):
    # given
    class TestPermissions(enum.Enum):
        FOO = "foo"
        BAR = "bar"
        BAZ = "baz"

    perm_models.RolePermission.query.delete()
    db_session.query(perm_models.Permission).delete()
    db_session.add(perm_models.Permission(name="FOO"))
    db_session.add(perm_models.Permission(name="BAR"))
    assert db_session.query(perm_models.Permission.id).count() == 2

    # when
    perm_models.sync_enum_with_db_field(db_session, TestPermissions, perm_models.Permission.name)

    # then
    assert set(p.name for p in db_session.query(perm_models.Permission.name).all()) == set(
        p.name for p in TestPermissions
    )


def test_sync_removed_perms(db_session):
    # given
    class TestPermissions(enum.Enum):
        FOO = "foo"
        BAR = "bar"

    perm_models.RolePermission.query.delete()
    db_session.query(perm_models.Permission).delete()
    db_session.add(perm_models.Permission(name="FOO"))
    db_session.add(perm_models.Permission(name="BAR"))
    db_session.add(perm_models.Permission(name="BAZ"))
    assert db_session.query(perm_models.Permission.id).count() == 3

    # when
    with mock.patch.object(perm_models.logger, "warning") as warn_mock:
        perm_models.sync_enum_with_db_field(db_session, TestPermissions, perm_models.Permission.name)

    # then
    assert warn_mock.call_count == 1
    assert "BAZ" in warn_mock.call_args.args[1]
    assert set(p.name for p in db_session.query(perm_models.Permission.name).all()) == {"FOO", "BAR", "BAZ"}
