"""Add offer EAN column"""

from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "ab6fe51d82bb"
down_revision = "f0b5bf6e0d3f"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("offer", sa.Column("ean", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("offer", "ean")
