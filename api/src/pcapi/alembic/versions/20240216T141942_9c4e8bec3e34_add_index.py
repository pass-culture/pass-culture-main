"""Add index
"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "9c4e8bec3e34"
down_revision = "88d300a290b1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(op.f("ix_deposit_expirationDate"), "deposit", ["expirationDate"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_deposit_expirationDate"), table_name="deposit")
