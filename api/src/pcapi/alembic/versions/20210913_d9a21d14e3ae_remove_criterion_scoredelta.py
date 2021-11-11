"""Remove Criterion.scoreDelta
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d9a21d14e3ae"
down_revision = "228a4b2e4213"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column("criterion", "scoreDelta")


def downgrade():
    op.add_column("criterion", sa.Column("scoreDelta", sa.INTEGER(), autoincrement=False, nullable=True))
