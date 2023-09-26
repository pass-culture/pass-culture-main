"""Add column `experienceDetails` in individual_offerer_subscription table
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "bdb5f7cdd367"
down_revision = "ef07f9582155"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("individual_offerer_subscription", sa.Column("experienceDetails", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("individual_offerer_subscription", "experienceDetails")
