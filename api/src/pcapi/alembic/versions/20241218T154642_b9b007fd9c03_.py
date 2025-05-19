"""
Add artist image author
"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "b9b007fd9c03"
down_revision = "f8588023c126"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("artist", sa.Column("image_author", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("artist", "image_author")
