"""Add unique index on deposit and recredit type on recredit table"""

import sqlalchemy as sa
from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "c57138342120"
down_revision = "b7e8461b1da3"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION lock_timeout = '300s'")
        op.execute("SET SESSION statement_timeout = '300s'")
        op.create_index(
            "ix_unique_deposit_recredit_type",
            "recredit",
            ["depositId", "recreditType"],
            unique=True,
            postgresql_where=sa.text(
                "\"recreditType\" != 'MANUAL_MODIFICATION' AND \"recreditType\" != 'FINANCE_INCIDENT_RECREDIT'"
            ),
            if_not_exists=True,
            postgresql_concurrently=True,
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION lock_timeout = '300s'")
        op.execute("SET SESSION statement_timeout = '300s'")
        op.drop_index(
            "ix_unique_deposit_recredit_type",
            table_name="recredit",
            postgresql_where=sa.text(
                "\"recreditType\" != 'MANUAL_MODIFICATION' AND \"recreditType\" != 'FINANCE_INCIDENT_RECREDIT'"
            ),
            if_exists=True,
            postgresql_concurrently=True,
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")
