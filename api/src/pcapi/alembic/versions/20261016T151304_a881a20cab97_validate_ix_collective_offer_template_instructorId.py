"""Validate CollectiveOfferTemplate.instructorId index"""

import sqlalchemy as sa
from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "a881a20cab97"
down_revision = "a42c8dfba69e"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout='300s'")
        op.create_index(
            op.f("ix_collective_offer_template_instructorId"),
            "collective_offer_template",
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
            op.f("ix_collective_offer_template_instructorId"),
            table_name="collective_offer_template",
            if_exists=True,
            postgresql_concurrently=True,
        )
