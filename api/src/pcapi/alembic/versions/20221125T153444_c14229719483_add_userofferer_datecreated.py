"""Add_UserOfferer_dateCreated
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "c14229719483"
down_revision = "8948db4edb75"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("user_offerer", sa.Column("dateCreated", sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column("user_offerer", "dateCreated")
