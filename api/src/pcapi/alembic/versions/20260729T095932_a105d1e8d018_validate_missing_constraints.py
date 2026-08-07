"""Validate collective_offer_template and reaction check constraints"""

from alembic import op
from sqlalchemy.sql import text

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "a105d1e8d018"
down_revision = "2f3fe3269031"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("SET SESSION statement_timeout='300s'")

    op.execute(
        """ALTER TABLE collective_offer_template VALIDATE CONSTRAINT "collective_offer_tmpl_contact_request_form_data_constraint" """
    )
    op.execute("""ALTER TABLE reaction VALIDATE CONSTRAINT "reaction_offer_product_check" """)

    op.execute(
        text("SET SESSION statement_timeout=:statement_timeout").bindparams(
            statement_timeout=settings.DATABASE_STATEMENT_TIMEOUT,
        )
    )


def downgrade() -> None:
    pass
