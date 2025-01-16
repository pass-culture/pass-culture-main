"""Add product.ean column"""

from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "233e4f9dc483"
down_revision = "ab6fe51d82bb"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("product", sa.Column("ean", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("product", "ean")
