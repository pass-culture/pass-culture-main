"""Add Address.timezone column"""

from alembic import op
import sqlalchemy as sa

from pcapi.utils.date import METROPOLE_TIMEZONE


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "fbe025155bfa"
down_revision = "59c9e4903310"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column(
        "address",
        sa.Column("timezone", sa.Text(), nullable=False, default=METROPOLE_TIMEZONE, server_default=METROPOLE_TIMEZONE),
    )
    op.execute(
        """ALTER TABLE address ADD CONSTRAINT "address_timezone_check" CHECK (length("timezone") <= 50) NOT VALID"""
    )


def downgrade() -> None:
    op.drop_column("address", "timezone")
