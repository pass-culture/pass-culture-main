"""Validate two contraints on collective_offer location fields"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "5dd3836c9164"
down_revision = "25242898860f"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("SET SESSION statement_timeout='300s'")
    op.execute(
        """ALTER TABLE collective_offer VALIDATE CONSTRAINT "collective_offer_location_type_and_address_constraint" """
    )
    op.execute(
        """ALTER TABLE collective_offer VALIDATE CONSTRAINT "collective_offer_location_type_and_comment_constraint" """
    )
    op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    pass
