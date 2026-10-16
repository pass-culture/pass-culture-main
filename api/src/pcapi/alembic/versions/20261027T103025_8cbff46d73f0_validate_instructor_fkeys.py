"""Validate instructor foreign keys"""

import sqlalchemy as sa
from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "8cbff46d73f0"
down_revision = "782c052e7408"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("SET SESSION statement_timeout='300s'")
    op.execute(
        """ALTER TABLE collective_offer_template_instructor VALIDATE CONSTRAINT "collective_offer_template_instructor_instructorId_fkey" """
    )
    op.execute(
        """ALTER TABLE collective_offer_template_instructor VALIDATE CONSTRAINT "collective_offer_template_instructor_collectiveTemplateId_fkey" """
    )
    op.execute(
        """ALTER TABLE collective_offer_instructor VALIDATE CONSTRAINT "collective_offer_instructor_instructorId_fkey" """
    )
    op.execute(
        """ALTER TABLE collective_offer_instructor VALIDATE CONSTRAINT "collective_offer_instructor_collectiveOfferId_fkey" """
    )
    op.execute("""ALTER TABLE offer_instructor VALIDATE CONSTRAINT "offer_instructor_instructorId_fkey" """)
    op.execute("""ALTER TABLE offer_instructor VALIDATE CONSTRAINT "offer_instructor_offerId_fkey" """)
    op.execute(
        sa.text("SET SESSION statement_timeout=:statement_timeout").bindparams(
            statement_timeout=settings.DATABASE_STATEMENT_TIMEOUT
        )
    )


def downgrade() -> None:
    pass
