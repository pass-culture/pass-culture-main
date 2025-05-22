"""
Remove favorite.mediationId column
"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "6d2971ccc616"
down_revision = "88d300a290b1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("favorite", "mediationId")


def downgrade() -> None:
    op.add_column("favorite", sa.Column("mediationId", sa.BIGINT(), autoincrement=False, nullable=True))
