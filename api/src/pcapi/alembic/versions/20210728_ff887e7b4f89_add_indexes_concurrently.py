"""Add indexes concurrently

Revision ID: ff887e7b4f89
Revises: 888f037beae1
Create Date: 2021-07-28 15:06:35.347980

"""
from alembic import op

from pcapi import settings


# revision identifiers, used by Alembic.
revision = "ff887e7b4f89"
down_revision = "888f037beae1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("COMMIT")
    op.execute(
        """
        SET SESSION statement_timeout = '300s'
        """
    )
    op.execute(
        """
        CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS "ix_booking_educationalBookingId" ON booking ("educationalBookingId")
        """
    )
    op.execute(
        """
        CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS "ix_booking_individualBookingId" ON booking ("individualBookingId")
        """
    )
    op.drop_constraint("booking_educationalBookingId_key", "booking", type_="unique")
    op.execute(
        f"""
        SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}
        """
    )


def downgrade() -> None:
    op.create_unique_constraint("booking_educationalBookingId_key", "booking", ["educationalBookingId"])
    op.drop_index(op.f("ix_booking_individualBookingId"), table_name="booking")
    op.drop_index(op.f("ix_booking_educationalBookingId"), table_name="booking")
