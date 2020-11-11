"""add triggers to version user

Revision ID: 565f79cfa5b2
Revises: cff9e82d0558
Create Date: 2019-05-28 07:03:16.612332

"""
from alembic import op
from postgresql_audit.base import VersioningManager

# revision identifiers, used by Alembic.
from pcapi.models import UserSQLEntity


revision = "565f79cfa5b2"
down_revision = "c41e9543e851"
branch_labels = None
depends_on = None


def upgrade():
    versioning_manager = VersioningManager(schema_name="public")
    versioning_manager.create_audit_table(UserSQLEntity.__table__, op.get_bind())
    op.execute(
        """
    SELECT public.audit_table(oid, ARRAY['password', 'resetPasswordToken', 'validationToken']) 
    FROM pg_class 
    WHERE oid = 'user'::regclass;
    """
    )


def downgrade():
    op.execute(
        """
    DROP TRIGGER IF EXISTS audit_trigger_row ON "user";
    DROP TRIGGER IF EXISTS audit_trigger_delete ON "user";
    DROP TRIGGER IF EXISTS audit_trigger_insert ON "user";
    DROP TRIGGER IF EXISTS audit_trigger_update ON "user";
    """
    )
