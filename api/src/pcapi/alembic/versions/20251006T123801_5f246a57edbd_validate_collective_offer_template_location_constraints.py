"""Validate two contraints on collective_offer_template location fields"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "5f246a57edbd"
down_revision = "2235cbfa7c03"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("SET SESSION statement_timeout='300s'")
    op.execute(
        """ALTER TABLE collective_offer_template VALIDATE CONSTRAINT "collective_offer_template_location_type_and_address_constraint" """
    )
    op.execute(
        """ALTER TABLE collective_offer_template VALIDATE CONSTRAINT "collective_offer_template_location_type_and_comment_constraint" """
    )
    op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    pass
