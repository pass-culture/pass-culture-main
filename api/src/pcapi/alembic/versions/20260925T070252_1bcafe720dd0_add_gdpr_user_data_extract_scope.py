"""Add "scope" column to "gdpr_user_data_extract" table"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "1bcafe720dd0"
down_revision = "48232008761a"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column(
        "gdpr_user_data_extract",
        sa.Column("scope", sa.Text(), server_default="public", nullable=False),
    )


def downgrade() -> None:
    op.drop_column("gdpr_user_data_extract", "scope")
