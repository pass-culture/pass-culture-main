"""Drop NOT NULL constraint on user.publicName (before deletion)
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "49ed95a60b07"
down_revision = "66c2977b3cfe"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("user", "publicName", existing_type=sa.VARCHAR(length=255), nullable=True)


def downgrade() -> None:
    # Do not restore NOT NULL constraint. It will cause downtime on such a large and frequently modified table.
    pass
