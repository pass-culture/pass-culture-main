"""add column wikipedia_url to artist table"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "4abc630a7f7c"
down_revision = "44890ce1925d"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("artist", sa.Column("wikipedia_url", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("artist", "wikipedia_url")
