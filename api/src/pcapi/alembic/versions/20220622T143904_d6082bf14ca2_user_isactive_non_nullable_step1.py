"""Make user.isActive not nullable (step 1 of 4)."""
from alembic import op


# revision identifiers, used by Alembic.
revision = "d6082bf14ca2"
down_revision = "b9deaf12993c"
branch_labels = None
depends_on = None


CONSTRAINT = "user_isactive_not_null_constraint"


def upgrade():
    op.execute(
        f"""
        ALTER TABLE "user" DROP CONSTRAINT IF EXISTS "{CONSTRAINT}";
        ALTER TABLE "user" ADD CONSTRAINT "{CONSTRAINT}" CHECK ("isActive" IS NOT NULL) NOT VALID;
        """
    )


def downgrade():
    op.drop_constraint(CONSTRAINT, table_name="user")
