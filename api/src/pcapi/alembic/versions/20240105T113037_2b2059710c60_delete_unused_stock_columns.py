"""Delete legacy collective columns from stock table."""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "2b2059710c60"
down_revision = "b9f04189f351"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("stock", "numberOfTickets")
    op.drop_column("stock", "educationalPriceDetail")


def downgrade() -> None:
    op.add_column("stock", sa.Column("educationalPriceDetail", sa.TEXT(), autoincrement=False, nullable=True))
    op.add_column("stock", sa.Column("numberOfTickets", sa.INTEGER(), autoincrement=False, nullable=True))
