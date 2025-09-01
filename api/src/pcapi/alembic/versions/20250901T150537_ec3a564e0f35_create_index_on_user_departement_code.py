"""Create index on user.departementCode"""

import sqlalchemy as sa
from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "ec3a564e0f35"
down_revision = "0171499fda14"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
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
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            "ix_user_departementCode",
            table_name="user",
            postgresql_where=sa.text('"departementCode" IS NOT NULL'),
            postgresql_concurrently=True,
            if_exists=True,
        )
