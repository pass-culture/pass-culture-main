"""replace_awaiting_by_pending_on_offer_validation_status

Revision ID: e8d9aaa3890e
Revises: 719b8b8e632f
Create Date: 2021-04-14 13:43:11.560125

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "e8d9aaa3890e"
down_revision = "719b8b8e632f"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TYPE validation_status RENAME VALUE 'AWAITING' TO 'PENDING'")


def downgrade():
    op.execute("ALTER TYPE validation_status RENAME VALUE 'PENDING' TO 'AWAITING'")
