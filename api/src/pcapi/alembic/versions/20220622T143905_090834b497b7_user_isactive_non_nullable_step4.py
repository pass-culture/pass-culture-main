"""Make user.isActive not nullable (step 4 of 4)."""
from alembic import op


# revision identifiers, used by Alembic.
revision = "090834b497b7"
down_revision = "905c3b79223a"
branch_labels = None
depends_on = None


CONSTRAINT = "user_isactive_not_null_constraint"


def upgrade():
    op.drop_constraint(CONSTRAINT, table_name="user")


def downgrade():
    op.execute(f"""ALTER TABLE "user" ADD CONSTRAINT "{CONSTRAINT}" CHECK ("isActive" IS NOT NULL) NOT VALID""")
