"""
Remove the isPublicApi column from collective_offer.
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "49e118a9dd48"
down_revision = "4fb121d642ef"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("collective_offer", "isPublicApi")


def downgrade() -> None:
    op.add_column(
        "collective_offer",
        sa.Column("isPublicApi", sa.BOOLEAN(), server_default=sa.text("false"), autoincrement=False, nullable=False),
    )
