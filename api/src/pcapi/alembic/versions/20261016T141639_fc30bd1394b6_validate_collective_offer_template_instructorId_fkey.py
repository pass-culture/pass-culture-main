"""Validate CollectiveOfferTemplate.instructorId fkey"""

import sqlalchemy as sa
from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "fc30bd1394b6"
down_revision = "6c4e70ca76d9"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("SET SESSION statement_timeout='300s'")
    op.execute(
        """ALTER TABLE collective_offer_template VALIDATE CONSTRAINT "collective_offer_template_instructorId_fkey" """
    )
    op.execute(
        sa.text("SET SESSION statement_timeout=:statement_timeout").bindparams(
            statement_timeout=settings.DATABASE_STATEMENT_TIMEOUT
        )
    )


def downgrade() -> None:
    pass
