"""add_not_null_booking_venuid_step_2

Revision ID: e25793bed276
Revises: 289494f36088
Create Date: 2021-09-02 09:55:26.990760

"""
from alembic import op

# revision identifiers, used by Alembic.
from pcapi import settings


revision = "e25793bed276"
down_revision = "289494f36088"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("COMMIT")
    op.execute(
        """
        SET SESSION statement_timeout = '300s'
        """
    )
    op.execute("ALTER TABLE booking VALIDATE CONSTRAINT venueid_not_null_constraint;")
    op.execute(
        f"""
        SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}
        """
    )


def downgrade() -> None:
    pass
