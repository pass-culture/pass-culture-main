"""Remove dsToken column on offerer table
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "ea442da9e07f"
down_revision = "041c43f6659c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("unique_offerer_dsToken", "offerer", type_="unique")
    op.drop_column("offerer", "dsToken")


def downgrade() -> None:
    op.add_column("offerer", sa.Column("dsToken", sa.TEXT(), autoincrement=False, nullable=True))
    op.create_unique_constraint("unique_offerer_dsToken", "offerer", ["dsToken"])
