"""Remove unused isGcuCompatible column
"""

from alembic import op
import sqlalchemy as sa


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "1b973a88081d"
down_revision = "69f58f589e88"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_column("product", "isGcuCompatible")


def downgrade() -> None:
    op.add_column(
        "product",
        sa.Column("isGcuCompatible", sa.BOOLEAN(), server_default=sa.text("true"), autoincrement=False, nullable=False),
    )
