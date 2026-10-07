"""Create index on: fraudulent_booking_tag.venueId"""

import sqlalchemy as sa
from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "38769750c0a2"
down_revision = "61bc7b2dc48b"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout='300s'")
        op.create_index(
            op.f("ix_fraudulent_booking_tag_venueId"),
            "fraudulent_booking_tag",
            ["venueId"],
            unique=False,
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
        op.drop_index(
            op.f("ix_fraudulent_booking_tag_venueId"),
            table_name="fraudulent_booking_tag",
            postgresql_concurrently=True,
            if_exists=True,
        )
