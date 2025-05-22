"""Remove collectiveSubCategoryId from Venue"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "0fbfa18bdad2"
down_revision = "579ca0aff07d"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_column("venue", "collectiveSubCategoryId")


def downgrade() -> None:
    op.add_column("venue", sa.Column("collectiveSubCategoryId", sa.TEXT(), autoincrement=False, nullable=True))
