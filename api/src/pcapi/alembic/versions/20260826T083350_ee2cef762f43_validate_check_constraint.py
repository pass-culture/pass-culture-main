"""Validate check constraint on collective_offer_template"""

import sqlalchemy as sa
from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "ee2cef762f43"
down_revision = "04f1b080b16c"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("SET SESSION statement_timeout='300s'")

    op.execute(
        """ALTER TABLE collective_offer_template VALIDATE CONSTRAINT "collective_offer_tmpl_contact_request_form_data_constraint" """
    )

    op.execute(
        sa.text("SET SESSION statement_timeout=:statement_timeout").bindparams(
            statement_timeout=settings.DATABASE_STATEMENT_TIMEOUT,
        )
    )


def downgrade() -> None:
    pass
