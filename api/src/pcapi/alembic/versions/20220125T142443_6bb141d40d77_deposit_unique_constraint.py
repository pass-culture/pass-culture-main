"""deposit unique constraint on ("userId", "type")
"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "6bb141d40d77"
down_revision = "dc678612fef4"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        ALTER TABLE deposit ADD CONSTRAINT "unique_type_per_user" UNIQUE USING INDEX "ix_user_type"
        """
    )


def downgrade():
    op.drop_constraint("unique_type_per_user", table_name="deposit")
