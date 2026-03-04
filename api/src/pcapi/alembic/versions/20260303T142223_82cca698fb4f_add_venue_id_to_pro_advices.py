"""add column venueId for table pro_advice"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "82cca698fb4f"
down_revision = "ce60207187ae"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("pro_advice", sa.Column("venueId", sa.BigInteger()))


def downgrade() -> None:
    op.drop_column("pro_advice", "venueId")
