"""
Drop unused columns from Offer
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "d01ad12d4c78"
down_revision = "ba42ea4318a0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("offer", "mediaUrls")
    op.drop_column("offer", "ageMin")
    op.drop_column("offer", "ageMax")
    op.drop_column("offer", "conditions")


def downgrade() -> None:
    op.add_column("offer", sa.Column("conditions", sa.VARCHAR(length=120), autoincrement=False, nullable=True))
    op.add_column("offer", sa.Column("ageMax", sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column("offer", sa.Column("ageMin", sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column(
        "offer", sa.Column("mediaUrls", postgresql.ARRAY(sa.VARCHAR(length=220)), autoincrement=False, nullable=False)
    )
