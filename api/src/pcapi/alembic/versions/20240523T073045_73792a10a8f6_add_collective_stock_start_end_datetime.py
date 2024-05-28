"""Add startDatetime and endDatetime to CollectiveStock
"""

from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "73792a10a8f6"
down_revision = "cef3565151cc"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("collective_stock", sa.Column("startDatetime", sa.DateTime(), nullable=True))
    op.add_column("collective_stock", sa.Column("endDatetime", sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column("collective_stock", "endDatetime")
    op.drop_column("collective_stock", "startDatetime")
