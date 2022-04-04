"""alter_has_seen_pro_rgs_to_not_null
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "11f137937ae5"
down_revision = "6ee927d299b1"
branch_labels = None
depends_on = None


def upgrade():
    op.execute('UPDATE "user" SET "hasSeenProRgs" = false')
    op.alter_column(
        "user", "hasSeenProRgs", existing_type=sa.BOOLEAN(), server_default=sa.text("false"), nullable=False
    )


def downgrade():
    op.alter_column("user", "hasSeenProRgs", existing_type=sa.BOOLEAN(), server_default=None, nullable=True)
