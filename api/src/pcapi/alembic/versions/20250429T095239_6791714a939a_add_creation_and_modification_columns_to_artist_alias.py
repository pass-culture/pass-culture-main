"""add `date_created` and `date_modified` columns to `artist_alias` table"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "6791714a939a"
down_revision = "bf0af5fbff03"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("artist_alias", sa.Column("date_created", sa.DateTime, nullable=False, server_default=sa.func.now()))
    op.add_column("artist_alias", sa.Column("date_modified", sa.DateTime, nullable=True, onupdate=sa.func.now()))


def downgrade() -> None:
    op.drop_column("artist_alias", "date_created")
    op.drop_column("artist_alias", "date_modified")
