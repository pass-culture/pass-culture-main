"""Add missing allocine_venue_provider check constraint"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "9f72924bf408"
down_revision = "ee2cef762f43"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_check_constraint(
        "check_price_is_not_negative",
        table_name="allocine_venue_provider",
        condition=sa.text("price >= 0"),
        postgresql_not_valid=True,
    )


def downgrade() -> None:
    op.drop_constraint(
        "check_price_is_not_negative",
        table_name="allocine_venue_provider",
    )
