"""Add remaining_amount to educational_deposit"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "dc178062bf79"
down_revision = "d4e5f6a7b8c9"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column(
        "educational_deposit", sa.Column("remaining_amount", sa.Numeric(precision=10, scale=2), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("educational_deposit", "remaining_amount")
