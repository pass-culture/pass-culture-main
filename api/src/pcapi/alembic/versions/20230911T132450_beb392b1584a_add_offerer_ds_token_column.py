"""
Add dsToken column to offerer table
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "beb392b1584a"
down_revision = "1f3334d5aee5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "offerer",
        sa.Column("dsToken", sa.Text(), nullable=True),
    )
    op.create_unique_constraint("unique_offerer_dsToken", "offerer", ["dsToken"])


def downgrade() -> None:
    op.drop_constraint("unique_offerer_dsToken", "offerer", type_="unique")
    op.drop_column("offerer", "dsToken")
