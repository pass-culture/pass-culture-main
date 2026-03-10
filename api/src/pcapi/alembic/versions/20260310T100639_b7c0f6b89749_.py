"""add column volunteeringUrl to venue table"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "b7c0f6b89749"
down_revision = "1efb0c9cdf36"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("venue", sa.Column("volunteeringUrl", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("venue", "volunteeringUrl")
