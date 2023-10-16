"""validate constraint on user_iris_france_fk without locking the table"""
from alembic import op
import sqlalchemy as sa

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "d97c79fdee03"
down_revision = "c2b7386d4962"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("SET SESSION statement_timeout = '300s'")
    op.execute(sa.text('ALTER TABLE "user" VALIDATE CONSTRAINT user_iris_france_fk'))
    op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    pass
