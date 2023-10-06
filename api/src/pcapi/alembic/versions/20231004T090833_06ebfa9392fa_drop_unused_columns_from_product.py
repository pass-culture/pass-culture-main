"""
Drop unused columns from Product
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "06ebfa9392fa"
down_revision = "d01ad12d4c78"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("product", "mediaUrls")
    op.drop_column("product", "ageMin")
    op.drop_column("product", "ageMax")
    op.drop_column("product", "conditions")


def downgrade() -> None:
    op.add_column("product", sa.Column("conditions", sa.VARCHAR(length=120), autoincrement=False, nullable=True))
    op.add_column("product", sa.Column("ageMax", sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column("product", sa.Column("ageMin", sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column(
        "product", sa.Column("mediaUrls", postgresql.ARRAY(sa.VARCHAR(length=220)), autoincrement=False, nullable=True)
    )
