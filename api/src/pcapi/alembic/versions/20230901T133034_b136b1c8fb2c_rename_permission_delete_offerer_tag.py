"""rename permission MANAGE_TAGS_N2
"""
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "b136b1c8fb2c"
down_revision = "62cd1889b6ac"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE permission SET name = 'MANAGE_TAGS_N2' WHERE name = 'DELETE_OFFERER_TAG'")


def downgrade() -> None:
    op.execute("UPDATE permission SET name = 'DELETE_OFFERER_TAG' WHERE name = 'MANAGE_TAGS_N2'")
