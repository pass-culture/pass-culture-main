"""Create index "ix_offer_venueId_validation_publicationDatetime_id" on "offer" table"""

import sqlalchemy as sa
from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "635a4b23fc44"
down_revision = "782c052e7408"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout=0")
        op.create_index(
            "ix_offer_venueId_validation_publicationDatetime_id",
            "offer",
            ["venueId", "validation", "publicationDatetime"],
            unique=False,
            postgresql_include=["id"],
            postgresql_concurrently=True,
            if_not_exists=True,
        )
        op.execute(
            sa.text("SET SESSION statement_timeout=:statement_timeout").bindparams(
                statement_timeout=settings.DATABASE_STATEMENT_TIMEOUT
            )
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout=0")
        op.drop_index(
            "ix_offer_venueId_validation_publicationDatetime_id",
            table_name="offer",
            postgresql_concurrently=True,
            if_exists=True,
        )
        op.execute(
            sa.text("SET SESSION statement_timeout=:statement_timeout").bindparams(
                statement_timeout=settings.DATABASE_STATEMENT_TIMEOUT
            )
        )
