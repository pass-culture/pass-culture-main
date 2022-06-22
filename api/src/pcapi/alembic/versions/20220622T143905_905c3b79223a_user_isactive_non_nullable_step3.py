"""Make user.isActive not nullable (step 3 of 4)."""
from alembic import op


# revision identifiers, used by Alembic.
revision = "905c3b79223a"
down_revision = "d12acf29a74d"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("user", "isActive", nullable=False)


def downgrade():
    op.alter_column("user", "isActive", nullable=True)
