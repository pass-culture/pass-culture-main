"""remove obsolete json field product.extraData
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "ab181e95a4c6"
down_revision = "ab181e95a4c5"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column("product", "extraData")


def downgrade():
    op.add_column(
        "product", sa.Column("extraData", postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=True)
    )
