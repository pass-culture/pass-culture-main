"""Add EAN column in product table"""

from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "1b5deb8e094c"
down_revision = "066c0b3fadd6"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("product", sa.Column("ean", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("product", "ean")
