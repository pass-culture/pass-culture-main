"""Delete `unique_cashflow_pricing_association` constraint """
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "a24e2d695e7c"
down_revision = "18e001e42fbd"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        ALTER TABLE "cashflow_pricing" DROP CONSTRAINT IF EXISTS "unique_cashflow_pricing_association"
        """
    )


def downgrade():
    pass  # the constraint is useless, no need to restore it
