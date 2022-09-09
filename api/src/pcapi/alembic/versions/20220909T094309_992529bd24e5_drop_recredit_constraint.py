"""drop_recredit_constraint
"""
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "992529bd24e5"
down_revision = "43d6625d1e4f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE recredit DROP CONSTRAINT IF EXISTS recredittype")
    op.execute(
        """
        ALTER TABLE recredit ALTER COLUMN "recreditType" type text
        """
    )


def downgrade() -> None:
    # do not execute otherwise it could fail if some rows have other types than RECREDIT_16 or RECREDIT_17
    pass
