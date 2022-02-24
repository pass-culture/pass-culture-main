"""remove ine hash whitelist table
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "5c3a992204ff"
down_revision = "70461af31b6e"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table("ine_hash_whitelist")


def downgrade():
    op.create_table(
        "ine_hash_whitelist", sa.Column("ine_hash", sa.TEXT(), nullable=False), sa.PrimaryKeyConstraint("ine_hash")
    )
