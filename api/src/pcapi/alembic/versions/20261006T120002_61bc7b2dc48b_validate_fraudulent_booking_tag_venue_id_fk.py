"""Validate foreign key: fraudulent_booking_tag.venueId"""

import sqlalchemy as sa
from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "61bc7b2dc48b"
down_revision = "de5e78443053"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("SET SESSION statement_timeout='300s'")
    op.execute("""ALTER TABLE fraudulent_booking_tag VALIDATE CONSTRAINT "fraudulent_booking_tag_venue_fk" """)
    op.execute(
        sa.text("SET SESSION statement_timeout=:statement_timeout").bindparams(
            statement_timeout=settings.DATABASE_STATEMENT_TIMEOUT
        )
    )


def downgrade() -> None:
    pass
