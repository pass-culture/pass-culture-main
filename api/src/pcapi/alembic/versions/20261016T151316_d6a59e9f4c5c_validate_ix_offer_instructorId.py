"""Validate Offer.instructorId index"""

import sqlalchemy as sa
from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "d6a59e9f4c5c"
down_revision = "a881a20cab97"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout='300s'")
        op.create_index(
            op.f("ix_offer_instructorId"),
            "offer",
            ["instructorId"],
            unique=False,
            if_not_exists=True,
            postgresql_concurrently=True,
        )
        op.execute(
            sa.text("SET SESSION statement_timeout=:statement_timeout").bindparams(
                statement_timeout=settings.DATABASE_STATEMENT_TIMEOUT
            )
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            op.f("ix_offer_instructorId"),
            table_name="offer",
            if_exists=True,
            postgresql_concurrently=True,
        )
