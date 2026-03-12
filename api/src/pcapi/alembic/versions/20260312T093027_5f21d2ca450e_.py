"""add column volunteeringUrl to venue table bis"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "5f21d2ca450e"
down_revision = "82cca698fb4f"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("venue", sa.Column("volunteeringUrl", sa.Text(), nullable=True), if_not_exists=True)


def downgrade() -> None:
    op.drop_column("venue", "volunteeringUrl", if_exists=True)
