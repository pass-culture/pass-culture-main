"""Make user.isActive not nullable (step 2 of 4)."""
from alembic import op

from pcapi import settings


# revision identifiers, used by Alembic.
revision = "d12acf29a74d"
down_revision = "d6082bf14ca2"
branch_labels = None
depends_on = None


CONSTRAINT = "user_isactive_not_null_constraint"


def upgrade():
    op.execute("COMMIT")
    op.execute("SET SESSION statement_timeout = '900s'")
    op.execute(f'ALTER TABLE "user" VALIDATE CONSTRAINT "{CONSTRAINT}"')
    op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade():
    pass
