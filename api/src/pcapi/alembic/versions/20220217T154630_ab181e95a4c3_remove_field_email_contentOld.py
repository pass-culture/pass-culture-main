"""remove obsolete json field email.contentOld
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "ab181e95a4c3"
down_revision = "afafe32c82b3"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column("email", "contentOld")


def downgrade():
    op.add_column(
        "email", sa.Column("contentOld", postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=True)
    )
