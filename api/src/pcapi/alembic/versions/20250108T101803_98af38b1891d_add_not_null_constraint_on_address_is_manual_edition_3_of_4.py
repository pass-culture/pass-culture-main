"""Add NOT NULL constraint on address."isManualEdition" (step 3 of 4)"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "98af38b1891d"
down_revision = "02d9fd145348"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.alter_column(
        "address",
        "isManualEdition",
        existing_type=sa.BOOLEAN(),
        nullable=False,
        existing_server_default=False,
    )


def downgrade() -> None:
    op.alter_column(
        "address",
        "isManualEdition",
        existing_type=sa.BOOLEAN(),
        nullable=True,
        existing_server_default=False,
    )
