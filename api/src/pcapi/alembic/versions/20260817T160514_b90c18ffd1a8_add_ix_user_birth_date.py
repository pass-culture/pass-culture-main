"""Add ix_user_birth_date expression index on user"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql import text

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "b90c18ffd1a8"
down_revision = "a476ac6809e6"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout='300s'")
        op.create_index(
            "ix_user_birth_date",
            "user",
            [sa.literal_column('coalesce("validatedBirthDate", CAST("dateOfBirth" AS DATE))')],
            unique=False,
            postgresql_concurrently=True,
            if_not_exists=True,
        )
        op.execute(
            text("SET SESSION statement_timeout=:statement_timeout").bindparams(
                statement_timeout=settings.DATABASE_STATEMENT_TIMEOUT,
            )
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout='300s'")
        op.drop_index(
            "ix_user_birth_date",
            table_name="user",
            postgresql_concurrently=True,
            if_exists=True,
        )
        op.execute(
            text("SET SESSION statement_timeout=:statement_timeout").bindparams(
                statement_timeout=settings.DATABASE_STATEMENT_TIMEOUT,
            )
        )
