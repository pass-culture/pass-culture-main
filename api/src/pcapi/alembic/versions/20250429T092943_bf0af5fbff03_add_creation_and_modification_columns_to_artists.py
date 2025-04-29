"""add `date_created` and `date_modified` columns to `artist` table"""

from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "bf0af5fbff03"
down_revision = "38128af23ab7"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("artist", sa.Column("date_created", sa.DateTime, nullable=False, server_default=sa.func.now()))
    op.add_column("artist", sa.Column("date_modified", sa.DateTime, nullable=True, onupdate=sa.func.now()))


def downgrade() -> None:
    op.drop_column("artist", "date_created")
    op.drop_column("artist", "date_modified")
