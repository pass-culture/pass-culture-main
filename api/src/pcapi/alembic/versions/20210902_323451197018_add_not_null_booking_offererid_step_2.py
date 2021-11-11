"""add_not_null_booking_offererid_step_2

Revision ID: 323451197018
Revises: ab2f58396aa5
Create Date: 2021-09-02 10:02:26.859428

"""
from alembic import op

# revision identifiers, used by Alembic.
from pcapi import settings


revision = "323451197018"
down_revision = "ab2f58396aa5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("COMMIT")
    op.execute(
        """
        SET SESSION statement_timeout = '300s'
        """
    )
    op.execute("ALTER TABLE booking VALIDATE CONSTRAINT offererid_not_null_constraint;")
    op.execute(
        f"""
        SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}
        """
    )


def downgrade() -> None:
    pass
