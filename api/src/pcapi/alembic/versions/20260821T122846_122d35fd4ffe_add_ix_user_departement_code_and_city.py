"""Add ix_user_departementCode_and_city index on user"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql import text

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "122d35fd4ffe"
down_revision = "b90c18ffd1a8"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout='300s'")
        op.create_index(
            "ix_user_departementCode_and_city",
            "user",
            ["departementCode", sa.literal_column("lower(city)")],
            unique=False,
            postgresql_where=sa.text('"departementCode" IS NOT NULL'),
            postgresql_concurrently=True,
            if_not_exists=True,
        )
        op.drop_index(
            "ix_user_departementCode",
            table_name="user",
            postgresql_concurrently=True,
            if_exists=True,
        )
        op.execute(
            text("SET SESSION statement_timeout=:statement_timeout").bindparams(
                statement_timeout=settings.DATABASE_STATEMENT_TIMEOUT,
            )
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout='300s'")
        op.create_index(
            "ix_user_departementCode",
            "user",
            ["departementCode"],
            unique=False,
            postgresql_where=sa.text('"departementCode" IS NOT NULL'),
            postgresql_concurrently=True,
            if_not_exists=True,
        )
        op.drop_index(
            "ix_user_departementCode_and_city",
            table_name="user",
            postgresql_concurrently=True,
            if_exists=True,
        )
        op.execute(
            text("SET SESSION statement_timeout=:statement_timeout").bindparams(
                statement_timeout=settings.DATABASE_STATEMENT_TIMEOUT,
            )
        )
