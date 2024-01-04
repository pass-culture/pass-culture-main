"""Delete legacy collective columns from stock table."""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "0685904b0d5b"
down_revision = "48e05c743111"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("stock", "rawProviderQuantity")
    op.drop_column("stock", "numberOfTickets")
    op.drop_column("stock", "educationalPriceDetail")


def downgrade() -> None:
    op.add_column("stock", sa.Column("educationalPriceDetail", sa.TEXT(), autoincrement=False, nullable=True))
    op.add_column("stock", sa.Column("numberOfTickets", sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column("stock", sa.Column("rawProviderQuantity", sa.INTEGER(), autoincrement=False, nullable=True))
