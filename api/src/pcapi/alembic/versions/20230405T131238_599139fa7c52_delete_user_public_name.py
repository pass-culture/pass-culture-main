"""Delete user.publicName column
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "599139fa7c52"
down_revision = "580466424daf"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("user", "publicName")


def downgrade() -> None:
    op.add_column("user", sa.Column("publicName", sa.VARCHAR(length=255), autoincrement=False, nullable=True))
