"""remove obsolete json field offer.extraData
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "ab181e95a4c4"
down_revision = "ab181e95a4c3"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column("offer", "extraData")


def downgrade():
    op.add_column(
        "offer", sa.Column("extraData", postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=True)
    )
