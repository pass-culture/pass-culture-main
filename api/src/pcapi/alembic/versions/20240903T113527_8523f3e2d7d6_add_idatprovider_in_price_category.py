"""Add idAtProvider in `price_category`"""

from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "8523f3e2d7d6"
down_revision = "869f0d3be788"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("price_category", sa.Column("idAtProvider", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("price_category", "idAtProvider")
