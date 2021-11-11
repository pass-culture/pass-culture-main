"""ine_whitelist_table
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "bf9641a0f5a8"
down_revision = "7376d1cdc5a7"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "ine_hash_whitelist", sa.Column("ine_hash", sa.TEXT(), nullable=False), sa.PrimaryKeyConstraint("ine_hash")
    )


def downgrade():
    op.drop_table("ine_hash_whitelist")
