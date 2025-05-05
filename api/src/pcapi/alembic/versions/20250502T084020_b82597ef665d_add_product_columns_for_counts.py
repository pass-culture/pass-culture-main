"""Add product columns for counts"""

from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "b82597ef665d"
down_revision = "101e16ee5eeb"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("product", sa.Column("chroniclesCount", sa.Integer, nullable=True))
    op.add_column("product", sa.Column("headlinesCount", sa.Integer, nullable=True))
    op.add_column("product", sa.Column("likesCount", sa.Integer, nullable=True))


def downgrade() -> None:
    op.drop_column("product", "chroniclesCount")
    op.drop_column("product", "headlinesCount")
    op.drop_column("product", "likesCount")
