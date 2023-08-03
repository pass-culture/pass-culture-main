"""add urls column to Provider"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "b5652ab2625c"
down_revision = "60d5208fd945"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("provider", sa.Column("bookingExternalUrl", sa.Text(), nullable=True))
    op.add_column("provider", sa.Column("cancelExternalUrl", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("provider", "cancelExternalUrl")
    op.drop_column("provider", "bookingExternalUrl")
