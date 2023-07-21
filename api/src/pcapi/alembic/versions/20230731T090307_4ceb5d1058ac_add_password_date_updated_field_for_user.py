"""
Add new field password_date_updated in User table
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "4ceb5d1058ac"
down_revision = "60d5208fd945"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("user", sa.Column("password_date_updated", sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column("user", "password_date_updated")
