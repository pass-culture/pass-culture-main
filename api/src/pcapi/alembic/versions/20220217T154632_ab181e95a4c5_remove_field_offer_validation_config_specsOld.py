"""remove obsolete json field offer_validation_config.specsOld
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "ab181e95a4c5"
down_revision = "ab181e95a4c4"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column("offer_validation_config", "specsOld")


def downgrade():
    op.add_column(
        "offer_validation_config",
        sa.Column("specsOld", postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=True),
    )
